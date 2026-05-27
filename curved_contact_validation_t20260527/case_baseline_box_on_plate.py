"""
BASELINE — Box pressed onto a flat plate.

This case should converge cleanly. It validates the user's claim that
right-angled (orthogonal) bodies in contact behave well.

Geometry:
    - Flat plate at z=0 (3x3 grid → 16 verts, 18 triangles), fully fixed.
    - Solid box (1x1x1) initially with bottom face at z=0 (touching), tets
      via structured grid (2x2x2 → 27 verts, 48 tets).
    - Slave nodes  : bottom face of box (9 nodes).
    - Master faces : plate triangles.
    - Load         : downward -Z force distributed on box top face.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))

import torch
from mesh_gen import (make_plate, make_box_tet, extract_tet_boundary_faces)
from runner import run_case

OUT = os.path.join(HERE, "results")
DEV = "cpu"
DTYPE = torch.float64


def build():
    # Plate
    plate_V, plate_F = make_plate(size=2.0, z=0.0, nx=3, ny=3,
                                  device=DEV, dtype=DTYPE)
    Nplate = plate_V.shape[0]

    # Box — bottom face at z=0 (touching plate, no initial gap)
    box_V, box_E, box_bot, box_top = make_box_tet(
        size=(1.0, 1.0, 1.0), center=(0.0, 0.0, 0.5),
        nx=2, ny=2, nz=2, device=DEV, dtype=DTYPE,
    )

    # Concatenate (plate first, then box) so the box keeps low indices ?
    # We'll do box-then-plate to keep slave/box indices simple.
    coords = torch.cat([box_V, plate_V], dim=0)
    Nbox = box_V.shape[0]

    # Reindex elements
    elements_volume = {'C3D4': box_E['C3D4']}  # box indices stay 0..Nbox-1

    # Plate master triangles — shift by Nbox
    master_faces = plate_F + Nbox

    # Slave nodes — box bottom (already 0..Nbox-1)
    slave_nodes = box_bot

    # Force & fixed
    N = coords.shape[0]
    fixed = torch.zeros(N, 3, device=DEV, dtype=torch.bool)
    # Fix plate
    fixed[Nbox:Nbox + Nplate, :] = True
    # Force: -Z on each top node
    force = torch.zeros(N, 3, device=DEV, dtype=DTYPE)
    force[box_top, 2] = -50.0  # N per node; total = -50*9 = -450 N

    # Material
    M = elements_volume['C3D4'].shape[0]
    material = {
        'E':  {'C3D4': torch.full((M,), 1e7, device=DEV, dtype=DTYPE)},  # softer steel
        'nu': {'C3D4': torch.full((M,), 0.3, device=DEV, dtype=DTYPE)},
    }

    # Mesh viz definitions
    box_boundary_F = torch.tensor(extract_tet_boundary_faces(box_E['C3D4']),
                                  device=DEV, dtype=torch.long)
    meshes_def = [
        {'tris_global': box_boundary_F,
         'color': 'tab:blue', 'alpha': 0.35, 'name': 'box'},
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
    # Try frictionless single-step first
    u, m = run_case(
        name="baseline_box_on_plate_frictionless",
        solver_kwargs=dict(
            contact_epsilon=1e6, nr_tol=1e-3, nr_max_iter=30,
            n_load_steps=1, mu_s=0.0, mu_d=0.0,
            dim=3, cg_start=False, device=DEV, dtype=DTYPE,
        ),
        **cfg,
    )

    # With friction
    u, m = run_case(
        name="baseline_box_on_plate_friction",
        solver_kwargs=dict(
            contact_epsilon=1e6, nr_tol=1e-3, nr_max_iter=30,
            n_load_steps=1, mu_s=0.3, mu_d=0.2,
            friction_penalty_ratio=0.1,
            dim=3, cg_start=False, device=DEV, dtype=DTYPE,
        ),
        **cfg,
    )
    print("\n=== BASELINE DONE ===")
