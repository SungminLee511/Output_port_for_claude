"""
CASE C — Two-finger robot grasp on a sphere.

Models the user's real use case: two fingertip pads pressing a sphere from
opposite sides. Each pad is a small flat box, slave = its inner face.
Master  = sphere upper-and-lower hemisphere triangles (one face set per finger).

The sphere is fixed at its top pole (acts as the held workpiece). Each pad
gets a horizontal force pushing inward; gravity is ignored.

Two `contact_pairs` are passed — one per finger.
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))

import torch
from mesh_gen import (make_solid_sphere_tet, make_finger_pad_tet, extract_tet_boundary_faces)
from runner import run_case

OUT = os.path.join(HERE, "results")
DEV = "cpu"
DTYPE = torch.float64


def build():
    # Sphere at origin, radius 0.5
    sphere_V, sphere_E, surf_nodes, surf_F, top_nodes, bot_nodes = make_solid_sphere_tet(
        radius=0.5, center=(0.0, 0.0, 0.0),
        level=2, n_interior_shells=2,
        device=DEV, dtype=DTYPE,
    )
    Nsphere = sphere_V.shape[0]

    # Finger pads (small boxes) at +X and -X
    # Inner face of +X pad faces -X, located at x ≈ +0.55 (initial gap 0.05)
    padR_V, padR_E, padR_inner, padR_outer = make_finger_pad_tet(
        size=(0.2, 0.5, 0.5),
        center=(0.55 + 0.1, 0.0, 0.0),  # bbox: x in [0.55, 0.75]
        nx=1, ny=2, nz=2,
        device=DEV, dtype=DTYPE,
    )
    NpadR = padR_V.shape[0]
    # +X pad's inner face is at the smallest-x side (minus_x in helper terms).
    # make_finger_pad_tet returns plus_x (=outer for the +X pad), minus_x (=inner).
    # Swap for +X pad: outer = plus_x, inner = minus_x
    padR_inner_idx = padR_outer  # was minus_x, which IS the inner face for +X pad
    padR_outer_idx = padR_inner  # plus_x is outer

    padL_V, padL_E, padL_inner_raw, padL_outer_raw = make_finger_pad_tet(
        size=(0.2, 0.5, 0.5),
        center=(-(0.55 + 0.1), 0.0, 0.0),  # bbox: x in [-0.75, -0.55]
        nx=1, ny=2, nz=2,
        device=DEV, dtype=DTYPE,
    )
    NpadL = padL_V.shape[0]
    # -X pad's inner face is its largest-x side (plus_x).
    padL_inner_idx = padL_inner_raw  # plus_x → inner for -X pad
    padL_outer_idx = padL_outer_raw  # minus_x → outer

    # Concatenate sphere, padR, padL
    coords = torch.cat([sphere_V, padR_V, padL_V], dim=0)

    # Build combined elements_volume
    elements_volume = {
        'C3D4': torch.cat([
            sphere_E['C3D4'],
            padR_E['C3D4'] + Nsphere,
            padL_E['C3D4'] + Nsphere + NpadR,
        ], dim=0)
    }

    # Sphere master surfaces split: +X half (for +X pad contact) and -X half (for -X pad)
    centroids = sphere_V[surf_F].mean(dim=1)
    plusX_mask = centroids[:, 0] > 0.0
    minusX_mask = centroids[:, 0] < 0.0
    master_faces_R = surf_F[plusX_mask]   # for +X pad
    master_faces_L = surf_F[minusX_mask]  # for -X pad

    # Slave node sets — pad inner faces
    slave_R = padR_inner_idx + Nsphere
    slave_L = padL_inner_idx + Nsphere + NpadR

    # BC: fix top pole of sphere (a few nodes near top)
    N = coords.shape[0]
    fixed = torch.zeros(N, 3, device=DEV, dtype=torch.bool)
    # Fix top nodes of sphere (z > 0.4)
    near_top = (sphere_V[:, 2] > 0.4)
    fixed_idx = torch.nonzero(near_top).squeeze(-1)
    if fixed_idx.numel() == 0:
        fixed_idx = top_nodes
    fixed[fixed_idx, :] = True

    # Force: pads pushed inward by force on their OUTER face
    # +X pad outer face gets -X force; -X pad outer face gets +X force.
    force = torch.zeros(N, 3, device=DEV, dtype=DTYPE)
    F_grip = 150.0  # total per pad
    padR_outer_global = padR_outer_idx + Nsphere
    padL_outer_global = padL_outer_idx + Nsphere + NpadR
    force[padR_outer_global, 0] = -F_grip / max(1, padR_outer_idx.numel())
    force[padL_outer_global, 0] = +F_grip / max(1, padL_outer_idx.numel())

    # Material
    M = elements_volume['C3D4'].shape[0]
    material = {
        'E':  {'C3D4': torch.full((M,), 1e7, device=DEV, dtype=DTYPE)},
        'nu': {'C3D4': torch.full((M,), 0.3, device=DEV, dtype=DTYPE)},
    }

    # Mesh viz
    padR_boundary = torch.tensor(extract_tet_boundary_faces(padR_E['C3D4']),
                                 device=DEV, dtype=torch.long) + Nsphere
    padL_boundary = torch.tensor(extract_tet_boundary_faces(padL_E['C3D4']),
                                 device=DEV, dtype=torch.long) + Nsphere + NpadR
    meshes_def = [
        {'tris_global': surf_F, 'color': 'tab:orange', 'alpha': 0.30, 'name': 'sphere'},
        {'tris_global': padR_boundary, 'color': 'tab:blue', 'alpha': 0.40, 'name': 'padR'},
        {'tris_global': padL_boundary, 'color': 'tab:green', 'alpha': 0.40, 'name': 'padL'},
    ]

    slave_all = torch.cat([slave_R, slave_L])
    master_all = torch.cat([master_faces_R, master_faces_L], dim=0)

    return dict(
        coords=coords, elements_volume=elements_volume,
        force=force, fixed=fixed,
        contact_pairs=[
            {'slave_nodes': slave_R, 'master_faces': master_faces_R},
            {'slave_nodes': slave_L, 'master_faces': master_faces_L},
        ],
        material=material, output_dir=OUT,
        meshes_def=meshes_def,
        slave_idx_global=slave_all,
        master_faces_for_metric=master_all,
    )


if __name__ == "__main__":
    cfg = build()
    # Variant 1: frictionless, single step
    u, m = run_case(
        name="case_c_grasp_frictionless_1step",
        solver_kwargs=dict(
            contact_epsilon=1e6, nr_tol=1e-3, nr_max_iter=50,
            n_load_steps=1, mu_s=0.0, mu_d=0.0,
            dim=3, cg_start=False, device=DEV, dtype=DTYPE,
        ),
        **cfg,
    )
    # Variant 2: frictionless, 8 steps
    u, m = run_case(
        name="case_c_grasp_frictionless_8step",
        solver_kwargs=dict(
            contact_epsilon=1e6, nr_tol=1e-3, nr_max_iter=40,
            n_load_steps=8, mu_s=0.0, mu_d=0.0,
            dim=3, cg_start=False, device=DEV, dtype=DTYPE,
        ),
        **cfg,
    )
    # Variant 3: friction, 8 steps  (real grasping needs friction)
    u, m = run_case(
        name="case_c_grasp_friction_8step",
        solver_kwargs=dict(
            contact_epsilon=1e6, nr_tol=1e-3, nr_max_iter=40,
            n_load_steps=8, mu_s=0.5, mu_d=0.3,
            friction_penalty_ratio=0.1,
            dim=3, cg_start=False, device=DEV, dtype=DTYPE,
        ),
        **cfg,
    )
    print("\n=== CASE C DONE ===")
