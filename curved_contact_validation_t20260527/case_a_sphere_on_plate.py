"""
CASE A — Sphere pressed onto a flat plate.

Slave  : bottom-hemisphere surface nodes of a solid tetrahedral sphere.
Master : flat plate triangles.

This is "curved slave, flat master". The master normals are uniform,
so the canonical normal-direction issue (curved master) does NOT show up here.
Expected behavior: contact concentrates near a single south-pole node, with
a few barycentric-weight discontinuities as the closest-face index flips.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))

import torch
from mesh_gen import (make_plate, make_solid_sphere_tet)
from runner import run_case

OUT = os.path.join(HERE, "results")
DEV = "cpu"
DTYPE = torch.float64


def build():
    # Plate
    plate_V, plate_F = make_plate(size=2.0, z=0.0, nx=4, ny=4,
                                  device=DEV, dtype=DTYPE)
    Nplate = plate_V.shape[0]

    # Sphere of radius 0.5, south pole touches z=0
    sphere_V, sphere_E, surf_nodes, surf_F, top_nodes, bot_nodes = make_solid_sphere_tet(
        radius=0.5, center=(0.0, 0.0, 0.5),
        level=2, n_interior_shells=2,
        device=DEV, dtype=DTYPE,
    )
    Nsphere = sphere_V.shape[0]

    # Concatenate sphere then plate
    coords = torch.cat([sphere_V, plate_V], dim=0)
    elements_volume = {'C3D4': sphere_E['C3D4']}

    # Master = plate triangles, shift indices
    master_faces = plate_F + Nsphere

    # Slave = bottom hemisphere of sphere (z < 0.5 in sphere = lower half)
    z_sphere = sphere_V[:, 2]
    is_lower_half = z_sphere < 0.5  # center is at z=0.5
    surf_mask = torch.zeros(Nsphere, dtype=torch.bool)
    surf_mask[surf_nodes] = True
    slave_mask = surf_mask & is_lower_half
    slave_nodes = torch.nonzero(slave_mask).squeeze(-1)

    # Force on top pole nodes
    N = coords.shape[0]
    fixed = torch.zeros(N, 3, device=DEV, dtype=torch.bool)
    fixed[Nsphere:Nsphere + Nplate, :] = True
    force = torch.zeros(N, 3, device=DEV, dtype=DTYPE)
    force[top_nodes, 2] = -300.0 / max(1, top_nodes.numel())

    # Material
    M = elements_volume['C3D4'].shape[0]
    material = {
        'E':  {'C3D4': torch.full((M,), 1e7, device=DEV, dtype=DTYPE)},
        'nu': {'C3D4': torch.full((M,), 0.3, device=DEV, dtype=DTYPE)},
    }

    # Mesh viz
    meshes_def = [
        {'tris_global': surf_F,
         'color': 'tab:orange', 'alpha': 0.30, 'name': 'sphere'},
        {'tris_global': master_faces,
         'color': 'tab:gray', 'alpha': 0.5, 'name': 'plate'},
    ]

    return dict(
        coords=coords, elements_volume=elements_volume,
        force=force, fixed=fixed,
        contact_pairs=[{'slave_nodes': slave_nodes, 'master_faces': master_faces}],
        material=material, output_dir=OUT,
        meshes_def=meshes_def,
        slave_idx_global=slave_nodes,
        master_faces_for_metric=master_faces,
    )


if __name__ == "__main__":
    cfg = build()
    # Frictionless, single load step
    u, m = run_case(
        name="case_a_sphere_on_plate_frictionless_1step",
        solver_kwargs=dict(
            contact_epsilon=1e6, nr_tol=1e-3, nr_max_iter=40,
            n_load_steps=1, mu_s=0.0, mu_d=0.0,
            dim=3, cg_start=False, device=DEV, dtype=DTYPE,
        ),
        **cfg,
    )
    # Frictionless, 4 load steps
    u, m = run_case(
        name="case_a_sphere_on_plate_frictionless_4step",
        solver_kwargs=dict(
            contact_epsilon=1e6, nr_tol=1e-3, nr_max_iter=40,
            n_load_steps=4, mu_s=0.0, mu_d=0.0,
            dim=3, cg_start=False, device=DEV, dtype=DTYPE,
        ),
        **cfg,
    )
    # Friction
    u, m = run_case(
        name="case_a_sphere_on_plate_friction_4step",
        solver_kwargs=dict(
            contact_epsilon=1e6, nr_tol=1e-3, nr_max_iter=40,
            n_load_steps=4, mu_s=0.3, mu_d=0.2,
            friction_penalty_ratio=0.1,
            dim=3, cg_start=False, device=DEV, dtype=DTYPE,
        ),
        **cfg,
    )
    print("\n=== CASE A DONE ===")
