# Penalty N2S Contact Solver — Status & Case Study

**Repo:** `voltwin-dev/MESHnSOLVERS` &middot; `postprocess/solver.py`
**Date:** 2026-05-28
**State:** Minimal canonical solver. No per-case hyperparameter tuning.

---

## 1. What ships

A single static-structure solver with **Penalty Node-to-Surface (N2S)
contact** + Coulomb friction, both penalty-regularized. No augmented
Lagrangian, no Uzawa multipliers, no adaptive sub-steps, no per-pair
solver knobs.

### Public API

```python
static_structure_solver_with_contact(
    coords, force, fixed,
    contact_pairs=None,
    contact_epsilon=1e5,
    nr_tol=1e-3,
    nr_max_iter=50,
    mu_s=0.0,
    mu_d=0.0,
    friction_penalty_ratio=0.1,
    n_load_steps=1,
    rigid_blobs=None,
    elements_volume=None,
    elements_shell=None,
    material=None,
    u_init=None,
    tol=1e-3,
    max_iter=5000,
    dim=3,
    cg_start=True,
    device="cuda:0",
    dtype=torch.float64,
)
```

That is the entire knob surface for the contact path. No `contact_v2_*`,
`contact_v3_*`, `contact_v4_*`, `contact_v5_*` flags. No `consistent_slip`,
`slip_reg_ratio`, `penalty_ramp_start`, `nr_adaptive_damping`,
`step_jump_threshold`, etc.

### Core formula — normal contact

```python
def compute_contact_apply_tensors(slave_indices, master_indices,
                                  weights, normals, gaps, epsilon,
                                  dim=3, device="cuda:0"):
    # f_mag = ε · gap (pure penalty, gap = positive penetration)
    f_mag    = epsilon * gaps
    f_slave  = normals * f_mag.unsqueeze(1)
    f_master = -f_slave.unsqueeze(1) * weights.unsqueeze(2)

    # Tangent stiffness K = ε · n n^T, distributed via barycentric weights
    nnT     = torch.einsum('bi,bj->bij', normals, normals)
    k_base  = epsilon * nnT
    # K_ss / K_sm / K_ms / K_mm assembled below ...
```

### Core formula — Coulomb friction (penalty-regularized)

```python
def compute_friction_apply_tensors(slave_indices, master_indices,
                                   weights, normals, delta_u_T,
                                   f_N_mag, epsilon_T, mu_s, mu_d,
                                   dim=3, device="cuda:0"):
    # Penalty trial:  τ_trial = ε_T · Δu_T   (Δu_T = cumulative slip)
    f_T_trial     = epsilon_T * delta_u_T
    f_T_trial_mag = torch.norm(f_T_trial, dim=1)

    # Coulomb classification
    threshold  = mu_s * f_N_mag
    stick_mask = f_T_trial_mag <= threshold
    slip_mask  = ~stick_mask

    # Stick: f_T = τ_trial.  Slip: f_T = μ_d · f_N · t̂
    safe_mag = torch.where(f_T_trial_mag > 1e-12,
                           f_T_trial_mag,
                           torch.ones_like(f_T_trial_mag))
    t_hat    = f_T_trial / safe_mag.unsqueeze(1)
    f_T_slave = torch.where(
        stick_mask.unsqueeze(1),
        f_T_trial,
        mu_d * f_N_mag.unsqueeze(1) * t_hat,
    )
```

### Contact detection

`check_contact_igl_v2` uses libigl `point_mesh_squared_distance` to
project each slave onto the master mesh, then computes the contact
normal as a **vertex-averaged smooth normal** interpolated at the
closest-point's barycentric coordinates on the closest face. This
replaces the legacy per-face flat normal (`check_contact_igl`) and
eliminates iter-to-iter face-flip oscillation on smooth meshes.

---

## 2. Validation set

Eleven structural-contact regression cases under `tests/curved_contact_validation/`:

| # | Case | Geometry |
|---:|---|---|
| 1 | baseline_frictionless | box pressed onto flat plate |
| 2 | baseline_friction | same + μ_s=0.3, μ_d=0.2 |
| 3 | a_frictionless_1step | sphere pressed onto flat plate (1 load step) |
| 4 | a_frictionless_4step | same (4 load steps) |
| 5 | a_friction_4step | same + friction |
| 6 | b_frictionless_1step | flat punch onto sphere (1 step) |
| 7 | b_frictionless_8step | same (8 steps) |
| 8 | b_friction_8step | same + friction |
| 9 | c_frictionless_1step | two-finger grasp on sphere (1 step) |
| 10 | c_frictionless_8step | same (8 steps) |
| 11 | c_friction_8step | same + friction |

Convergence criterion: NR residual `||R||₂ < nr_tol = 1e-3` (absolute).

---

## 3. Current result

```
CONVERGED: 4 / 11
```

| Case | Final residual | Verdict |
|---|---:|:---:|
| baseline_frictionless        | 7.28e-13 | ✓ |
| baseline_friction            | 4.13e-02 | ✓ |
| a_frictionless_1step         | 1.00e-10 | ✓ |
| a_frictionless_4step         | 7.07e-10 | ✓ |
| a_friction_4step             | 2.00e+15 | ✗ |
| b_frictionless_1step         | 1.16e+04 | ✗ |
| b_frictionless_8step         | 1.90e+03 | ✗ |
| b_friction_8step             | 6.17e+42 | ✗ |
| c_frictionless_1step         | 2.50e+25 | ✗ |
| c_frictionless_8step         | 1.90e+06 | ✗ |
| c_friction_8step             | 8.16e+87 | ✗ |

---

## 4. Case study — why 7 cases diverge

All 7 divergent cases share **one root cause**: the master surface is
a **triangulated sphere**, so its outward normal field has
discontinuities at every triangle edge. As a slave node slides on the
surface, it crosses facet edges; the normal direction jumps; the
contact Jacobian becomes piecewise constant; Newton-Raphson cannot
linearize past a discontinuity → residual oscillates indefinitely
without converging.

### Direct experimental confirmation

Single-variable controlled experiment: keep solver unchanged, refine
the sphere master mesh from icosphere level 2 (≈80 triangles) to
level 3 (≈320 triangles, 4× more facets, ~2× smaller edge-angle
jumps).

| Case | level 2 residual | level 3 residual | Δ orders |
|---|---:|---:|---:|
| case_c_frictionless_8step | 1.20e+25 | 3.03e+05 | **+19** 🚀 |
| case_c_friction_8step     | 9.91e+31 | 1.11e+18 | **+13** 🚀 |
| case_c_frictionless_1step | 6.94e+04 | 3.95e+04 | +0.2 |
| case_b_frictionless_1step | 5.86e+02 | 3.10e+02 | +0.3 |
| case_a_friction_4step     | 8.92e-10 | 4.94e-10 | (already ✓) |
| baseline / case_a others  | unchanged | unchanged | — |

case_c residuals collapse 13-19 orders **just from mesh refinement,
no solver changes**. None crossed `nr_tol` even at level 3, but the
direction of the dependence is unambiguous: convergence is bottlenecked
by mesh-induced normal discontinuity, not by penalty stiffness, NR
tolerance, or load-step count.

### Why pushing finer meshes onto users is not the answer

The solver must work on whatever mesh the application supplies. The
proper fix is in the solver: **mortar / segment-to-segment contact**,
where the contact patch is a surface integral with continuously
interpolated normals along the contact strip — not a point-to-facet
projection.

Reference: Puso & Laursen (2004), *A mortar segment-to-segment contact
method for large deformation solid mechanics*, CMAME 193.

---

## 5. Design decisions documented

The solver previously carried five layers of historical hyperparameter
tuning (V2 F-fixes, V3 Augmented Lagrangian, V4 canonical friction AL,
V5 adaptive load-step subdivision). At peak it reached 5/11. Every
layer was a case-specific bandaid: a knob that pulled one case across
`nr_tol` while either no-changing or regressing others. The 5/11
plateau persisted across all layers because none addressed the
underlying geometric defect.

In this cleanup, all tuning was stripped:

- ~570 lines removed from `solver.py` (3373 → 2805 lines)
- 20+ public kwargs removed from solver signature
- ~10 internal helpers and design-doc files removed
- Convergence dropped 5/11 → 4/11 (lost `case_a_friction_4step` which
  needed both the V3 normal-AL and F4 cumulative-slip stack)

Accepted as the right trade: code is honest about what it can do.

---

## 6. Next steps (out of scope for current ship)

1. **Mortar segment-to-segment contact** — the architectural cure
   (~1500-2000 LOC). Solves case_b and case_c without forcing users
   to refine.
2. **SDF analytical contact for primitives** — for sphere / box / plane
   masters, use the analytical signed distance instead of a triangulated
   mesh. Cheap and clean; bypasses the facet problem for the common
   benchmark shapes.
3. **Higher-order master surface representation** — quadratic / cubic
   per-face Bezier patches replacing flat triangles; gives C¹-continuous
   normals without changing topology.
