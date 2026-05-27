"""
CASE B — Flat plate pressed down onto a sphere (sphere = curved MASTER).

Slave  : bottom-face nodes of a small flat box (acts like a punch).
Master : upper-hemisphere surface triangles of a solid tetrahedral sphere.

This is the **suspected failure mode** the user reported. The master is curved,
so per-face normals jump discretely between adjacent triangles and the
closest-face index for each slave node hops between iterations. Penalty + NR
with the symmetric stick tangent has well-known difficulties here.

The sphere is fixed at its south pole. The punch is loaded with a -Z force
on its top face.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))

import torch
from mesh_gen import (make_box_tet, make_solid_sphere_tet, extract_tet_boundary_faces)
from runner import run_case

OUT = os.path.join(HERE, "results")
DEV = "cpu"
DTYPE = torch.float64


def build():
    # Sphere of radius 0.5, centered at z=0.5 (so top is at z=1.0)
    sphere_V, sphere_E, surf_nodes, surf_F, top_nodes, bot_nodes = make_solid_sphere_tet(
        radius=0.5, center=(0.0, 0.0, 0.5),
        level=2, n_interior_shells=2,
        device=DEV, dtype=DTYPE,
    )
    Nsphere = sphere_V.shape[0]

    # Punch (small flat box), bottom face just above sphere top (z=1.0)
    # Initial small gap, will close on first iter.
    punch_V, punch_E, punch_bot, punch_top = make_box_tet(
        size=(0.6, 0.6, 0.2),
        center=(0.0, 0.0, 1.05),   # bottom at z=0.95, sphere top at z=1.0 → penetrating
        nx=2, ny=2, nz=1,
        device=DEV, dtype=DTYPE,
    )
    Npunch = punch_V.shape[0]

    # Concatenate sphere then punch
    coords = torch.cat([sphere_V, punch_V], dim=0)
    elements_volume = {'C3D4': torch.cat([sphere_E['C3D4'],
                                          punch_E['C3D4'] + Nsphere], dim=0)}

    # Master faces = upper hemisphere of sphere surface (z > 0.5)
    # Filter surf_F triangles whose centroid is in the upper hemisphere
    centroids = sphere_V[surf_F].mean(dim=1)
    upper_mask = centroids[:, 2] > 0.5
    master_faces = surf_F[upper_mask]   # already in sphere's local index space (which == global since sphere is first)

    # Slave = punch bottom nodes (shift by Nsphere)
    slave_nodes = punch_bot + Nsphere

    # BC: fix sphere south pole (a small disk of nodes near z = 0)
    N = coords.shape[0]
    fixed = torch.zeros(N, 3, device=DEV, dtype=torch.bool)
    # Pick nodes with z < 0.1 inside the sphere
    near_bottom = (sphere_V[:, 2] < 0.10)
    fixed_idx = torch.nonzero(near_bottom).squeeze(-1)
    if fixed_idx.numel() == 0:
        # Fallback to provided bot_nodes
        fixed_idx = bot_nodes
    fixed[fixed_idx, :] = True

    # Force: push punch down (force on punch top nodes)
    force = torch.zeros(N, 3, device=DEV, dtype=DTYPE)
    punch_top_global = punch_top + Nsphere
    force[punch_top_global, 2] = -200.0 / max(1, punch_top.numel())

    # Material
    M = elements_volume['C3D4'].shape[0]
    material = {
        'E':  {'C3D4': torch.full((M,), 1e7, device=DEV, dtype=DTYPE)},
        'nu': {'C3D4': torch.full((M,), 0.3, device=DEV, dtype=DTYPE)},
    }

    # Mesh viz
    punch_boundary = torch.tensor(extract_tet_boundary_faces(punch_E['C3D4']),
                                  device=DEV, dtype=torch.long) + Nsphere
    meshes_def = [
        {'tris_global': surf_F,
         'color': 'tab:orange', 'alpha': 0.30, 'name': 'sphere'},
        {'tris_global': punch_boundary,
         'color': 'tab:blue', 'alpha': 0.40, 'name': 'punch'},
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
    # Variant 1: frictionless, single load step (likely fails / oscillates)
    u, m = run_case(
        name="case_b_plate_on_sphere_frictionless_1step",
        solver_kwargs=dict(
            contact_epsilon=1e6, nr_tol=1e-3, nr_max_iter=50,
            n_load_steps=1, mu_s=0.0, mu_d=0.0,
            dim=3, cg_start=False, device=DEV, dtype=DTYPE,
        ),
        **cfg,
    )
    # Variant 2: frictionless, 8 load steps (should help)
    u, m = run_case(
        name="case_b_plate_on_sphere_frictionless_8step",
        solver_kwargs=dict(
            contact_epsilon=1e6, nr_tol=1e-3, nr_max_iter=40,
            n_load_steps=8, mu_s=0.0, mu_d=0.0,
            dim=3, cg_start=False, device=DEV, dtype=DTYPE,
        ),
        **cfg,
    )
    # Variant 3: friction, 8 load steps
    u, m = run_case(
        name="case_b_plate_on_sphere_friction_8step",
        solver_kwargs=dict(
            contact_epsilon=1e6, nr_tol=1e-3, nr_max_iter=40,
            n_load_steps=8, mu_s=0.3, mu_d=0.2,
            friction_penalty_ratio=0.1,
            dim=3, cg_start=False, device=DEV, dtype=DTYPE,
        ),
        **cfg,
    )
    # Variant 4: lower contact_epsilon (softer penalty)
    u, m = run_case(
        name="case_b_plate_on_sphere_softer_eps",
        solver_kwargs=dict(
            contact_epsilon=1e4, nr_tol=1e-3, nr_max_iter=40,
            n_load_steps=4, mu_s=0.0, mu_d=0.0,
            dim=3, cg_start=False, device=DEV, dtype=DTYPE,
        ),
        **cfg,
    )
    print("\n=== CASE B DONE ===")
