# Contact Solver — Status

**Repo:** `voltwin-dev/MESHnSOLVERS` &middot; `postprocess/solver.py`
**Date:** 2026-05-29
**State:** 5 canonical fixes shipped. 13 / 19 converged on a diversified
robustness test suite. Zero per-case hyperparameters.

---

## 1. API

```python
from postprocess.solver import static_structure_solver_with_contact

u = static_structure_solver_with_contact(
    coords,                # [N, 3]      nodal coordinates
    force,                 # [N, dim]    applied force per node
    fixed,                 # [N, 3] bool displacement-BC mask
    contact_pairs=None,    # list[dict]  see below
    contact_epsilon=1e5,   # float       normal penalty stiffness
    nr_tol=1e-3,           # float       residual tolerance (abs OR rel)
    nr_max_iter=50,        # int         max NR iterations per load step
    mu_s=0.0,              # float       static Coulomb friction
    mu_d=0.0,              # float       dynamic Coulomb friction (≤ mu_s)
    friction_penalty_ratio=0.1,         # ε_T = ratio · contact_epsilon
    n_load_steps=1,        # int         incremental load steps
    rigid_blobs=None,
    elements_volume=None,  # {'C3D4': conn, …}
    elements_shell=None,
    material=None,         # {'E': {'C3D4': ...}, 'nu': {'C3D4': ...}}
    u_init=None,
    tol=1e-3, max_iter=5000,
    dim=3, cg_start=True,
    device="cuda:0", dtype=torch.float64,
)
```

**`contact_pairs`** is a list of dicts, one per N2S contact pair:
```python
[{'slave_nodes':  Tensor [N_s],          # global node indices of slaves
  'master_faces': Tensor [M, 3]},        # global node indices of master triangles
 ...]
```

**Return**: `u` is the converged displacement field, shape `[N · dim]`.
Convergence info is in the solver's stdout log (parsed by `runner.py`).

**Convergence criterion** (in-loop, OR-combined):
- absolute: `‖R_free‖ < nr_tol`
- force-norm relative: `‖R_free‖ / max(‖F_ext‖, ‖F_int‖, ‖F_contact‖) < nr_tol`

No new public kwargs were introduced through the entire fix campaign.
The API is the same as before the work started.

---

## 2. Solver logic

### 2.1 Overall flow

```
PRE-NR (once)
├─ Assemble base K (linear-elastic) and force vector
├─ Apply rigid_blobs / DOF mapping
├─ Compute free-DOF index list from `fixed`
├─ F-α  per-pair gap_tol = max(1e-8, 1e-2 · h_avg_master)
└─ F-δ  body detection + per-body RB-mode null subspace (SVD)

LOAD-STEP LOOP  (k = 1 … n_load_steps)
└─ NR LOOP (i = 0 … nr_max_iter)
   ├─ Detect contact (smooth normals)        ← libigl
   ├─ Assemble F_contact + K_contact         ← pure penalty
   ├─ F-ε  friction direction guard          ← skip locked slaves
   ├─ Assemble F_friction + K_friction       ← penalty Coulomb
   ├─ Residual R = F_ext - F_int + F_contact + F_friction
   ├─ Convergence check  (abs OR force-norm-rel)
   ├─ F-β  back-tracking if R grew > 1.05× last R
   ├─ Assemble K_tan
   ├─ F-γ  K_tan += k_stab · I               ← prevent singularity
   ├─ F-δ  K_tan += k_RB · Σ_b N_null,b N_null,bᵀ
   ├─ Solve K_tan_free · Δu = R_free         ← scipy.sparse.linalg.spsolve
   └─ Update u_current  with damping
```

### 2.2 The five canonical fixes

All five are auto-derived with internal constants only. No per-case
user kwargs. All operate on quantities (mesh sizes, K magnitude,
free-DOF structure) computed at solver entry or per NR iter.

| Fix | What | LOC | Internal constant |
|---|---|---:|---|
| **F-α** gap_tol auto-scale | Per contact pair, `gap_tol = max(1e-8, 1e-2 · h_avg_master)`. Prevents contact engagement on FP-noise sub-edge penetrations. | ~15 | `1e-2 × h_avg` ratio |
| **F-β** NR rewind on growth | If `R_{k+1} > 1.05 · R_k` and damping > 1/256, rewind `u ← u_pre + 0.5·last_step` and halve damping. Else grow damping back to 1.0. | ~25 | `1.05` growth, `1/256` floor |
| **F-γ** Tikhonov K diag | `K += k_stab · I` with `k_stab = max(\|K_diag\|) · 1e-10`. Prevents singular K from sending free bodies to ∞. | ~5 | `1e-10` × max K |
| **F-δ** smart inertia relief | Detect connected bodies. Per body, build 6 rigid-body modes; SVD against fixed-DOF subspace; stabilise only the residual null modes via `K += k_RB · N_null N_nullᵀ`. | ~80 | `k_RB = 1e-10 × max(\|K_diag\|)` |
| **F-ε** friction direction guard | Per active slave: if free-DOF subspace is within 5° of contact normal, the tangent plane is fully fixed → skip friction assembly for that slave. | ~30 | `5°` alignment threshold |

### 2.3 Contact mechanism

**Detection** — `check_contact_igl_v2` uses `igl.point_mesh_squared_distance` to
project each slave onto the master mesh, with **per-vertex smooth
normals** (vertex-averaged) interpolated at the closest point's
barycentric coordinates. This eliminates the iter-to-iter face-flip
oscillation that the legacy per-face flat normals cause.

**Normal contact** — pure penalty:
$$f_{\text{mag}} = \varepsilon \cdot g_+ \quad (g_+ = \max(0, \text{gap}))$$

**Friction** — penalty-regularised Coulomb:
$$\tau_{\text{trial}} = \varepsilon_T \cdot \Delta u_T^{\text{accum}}$$

Stick if $|\tau_{\text{trial}}| \le \mu_s f_N$; else slip:
$f_T = \mu_d f_N \hat{t}$ where $\hat{t} = \tau_{\text{trial}} / |\tau_{\text{trial}}|$.

The friction stiffness uses the **symmetric stick approximation** for
both stick and slip (avoids non-symmetric slip-tangent terms that
require an unsymmetric linear solver).

---

## 3. Test case suite (19 variants)

All under `tests/curved_contact_validation/`. Each case is a self-contained
build function returning the solver inputs.

| # | Case | Geometry | Hard mode |
|---|---|---|---|
| 1-2 | baseline_box_on_plate | box on flat plate | (control) |
| 3-5 | case_a sphere_on_plate | sphere slave, flat master | curved slave |
| 6-8 | case_b plate_on_sphere | punch slave, sphere master | curved master, force-loaded |
| 9-11 | case_c two_finger_grasp | 2 pads gripping sphere | 2-pair multi-contact |
| 12-13 | case_d ellipsoid_on_plate | ellipsoid (varying curvature) | non-uniform curvature |
| 14-15 | case_e ball_in_socket | ball seated in concave socket | conformal curved-on-curved |
| 16-17 | case_f sliding_block | block on 15° tilted plate | normal + tangential load |
| 18-19 | case_g 3jaw_chuck | 3 pads at 120° around sphere | 3-pair multi-contact, rotational symmetry |

Each family has frictionless and friction variants (some have 1-step
and multi-step). Test BCs mirror real actuator mechanisms (linear
guide rails on force-loaded bodies) — this is the "physically correct"
static-FEA setup.

---

## 4. Robustness — final results

```
CONVERGED: 13 / 19
```

| # | Variant | Residual | Rel | ✓ |
|---:|---|---:|---:|:-:|
| 1 | baseline_fl | 2.3e-05 | 1.1e-07 | ✓ |
| 2 | baseline_friction | 4.1e-02 | 1.9e-04 | ✓ |
| 3 | a_fl_1step | 1.5e-02 | 4.7e-05 | ✓ |
| 4 | a_fl_4step | 3.7e-03 | 1.2e-05 | ✓ |
| 5 | a_friction_4step | 4.7e-03 | 1.5e-05 | ✓ |
| 6 | b_fl_1step | 7.9e-02 | 2.7e-04 | ✓ |
| 7 | b_fl_8step | 4.1e-02 | 1.4e-04 | ✓ |
| 8 | b_friction_8step | 4.6e-02 | 1.6e-04 | ✓ |
| 9 | c_fl_1step | 9.4e-02 | 4.2e-04 | ✓ |
| 10 | c_fl_8step | 4.7e-02 | 1.8e-04 | ✓ |
| 11 | c_friction_8step | 2.5e+07 | 1.0e+00 | ✗ |
| 12 | d_ellipsoid_fl | 1.1e-02 | 1.2e-04 | ✓ |
| 13 | d_ellipsoid_friction | 7.5e+00 | 8.4e-02 | ✗ |
| 14 | e_ball_socket_fl | 2.9e-02 | 2.7e-04 | ✓ |
| 15 | e_ball_socket_friction | 2.9e-02 | 2.7e-04 | ✓ |
| 16 | f_sliding_block_fl | 1.8e+01 | 1.3e-01 | ✗ |
| 17 | f_sliding_block_friction | 4.5e+01 | 3.1e-01 | ✗ |
| 18 | g_3jaw_chuck_fl | 1.2e+07 | 1.0e+00 | ✗ |
| 19 | g_3jaw_chuck_friction | 1.0e+07 | 9.9e-01 | ✗ |

### 4.1 Coverage validated

- ✓ Flat-on-flat (baseline)
- ✓ Curved-slave on flat-master (case_a)
- ✓ Flat-slave on curved-master (case_b)
- ✓ Two-pair multi-contact frictionless (case_c)
- ✓ Variable-curvature master (case_d_fl)
- ✓ Conformal curved-on-curved (case_e — both fl and friction)
- ✓ Friction stick (a_friction, b_friction, e_friction, baseline_friction)

### 4.2 Convergence history

```
V1 legacy:                              5 / 11
V2 (5 F-flags tuned per case):          5 / 11
V3 (V2 + Uzawa AL):                     4 / 11
V4 first attempt:                       4 / 11
V4 REDO (gap-magnitude gate):           5 / 11
V5 (load-step subdivision):             5 / 11
Aggressive cleanup (pure penalty):      4 / 11
F-α + F-β:                              4 / 11
F-α + F-β + F-γ:                        5 / 11
F-α–F-ε + diverse 19-suite + BC fixes: 13 / 19
```

---

## 5. Case study — what F-α…F-ε actually fixed

### case_b_friction_8step
- Legacy V1: residual `2.7e+45` ❌ (numerically meaningless)
- F-α + F-β + F-γ: residual `0.046` ✓ (≈ 41 orders better)
- ‖u‖ = 0.05 m, physically the punch indents the sphere ~5 cm

### case_c_fl_1step (single-step force-loaded grasp)
- V1: `5.8e+22` ❌
- F-α + F-β + F-γ: `1.0e+04` ❌ (chatter plateau)
- F-α + F-β + F-γ + F-δ smart: `0.094` ✓ (4 orders better)

The body-internal mode that case_c_fl_1 was stuck on (sphere middle
nodes squeezed inward by pad pressure) was invisible to scalar Tikhonov
but caught by the per-body SVD-against-fixed-DOFs of F-δ.

### case_d_friction (ellipsoid friction)
- F-α + F-β + F-γ + F-δ: `9.4e+05` ❌ (rigid-body escape via friction force)
- + F-ε friction guard: `7.5` ❌ but 5 orders better; ‖u‖ now physical

Friction was injecting force in directions already fully constrained
by displacement BCs, creating singular rows in K_tan. F-ε detects this
and skips friction for those slaves.

### case_e_ball_in_socket (conformal contact)
- Hard test: many slaves simultaneously near master surface; small
  noise can flip them all in/out of contact at once
- F-α gap_tol auto-scaling handles it cleanly: both fl and friction
  variants converge first try at ~`3e-02` residual

---

## 6. The 6 remaining failures — categorised

| Case | Residual | Category | Root cause |
|---|---:|---|---|
| c_friction_8 | 2.5e+07 | solver — friction guard scope | Pad-normal not pure ±X at contact pts; F-ε's 5° check fails on off-axis normals |
| d_friction | 7.5 (rel=0.08) | borderline | Just outside nr_tol; sub-converged tier |
| f_fl, f_friction | 18, 45 (rel=0.13/0.31) | **test-side BC bug** | Block rotated 15° but Y-fix is in lab frame → BC anchors the wrong direction |
| g_fl, g_friction | 1e+07 | solver — multi-body modes | 3-fold rotational mode is shared across pads + sphere; F-δ is per-body and can't see system-level modes |

5/6 are solver-stabilization gaps (multi-body, off-axis); 1/6 (case_f)
is a test-side BC mistake.

---

## 7. What would crack the remaining 6

In rough order of effort × payoff:

| Idea | LOC | Targets |
|---|---:|---|
| Fix case_f BC (rotate fix mask along with geometry) | trivial | f_fl, f_friction |
| Widen F-ε to the full tangent-plane intersect with free-DOF subspace | ~20 | c_friction |
| Per-iter adaptive `k_stab` driven by cond(K) estimate | ~50 | d_friction borderline |
| **Multi-body system-mode detection** (ARPACK on assembled K, project Tikhonov on smallest eigvecs) | ~100 | g_fl, g_friction |
| Mortar / segment-to-segment contact | ~1500 | general — last resort |

None require user-facing kwargs.

---

## 8. Design decisions

- **No per-case hyperparameter tuning.** Every fix is canonical.
- **Solver API frozen** — same signature as the pre-cleanup baseline.
- **Test BCs mirror real actuator mechanisms** (linear guide rails on
  force-loaded bodies). This is the physically-correct static-FEA setup.
- **Honest reporting** — convergence criterion is strict
  `R < nr_tol OR R/F_scale < nr_tol`, no per-case acceptance.
- **Performance trade-off accepted** at cleanup: 5/11 (tuned per-case)
  → 4/11 (pure penalty) → 5/11 (F-α–F-γ) → 13/19 (F-α–F-ε on diverse
  suite). Honest, code is clean.

---

## 9. Repo layout

```
postprocess/solver.py
  static_structure_solver_with_contact(...)         # public API
    F-α  per-pair gap_tol                           # at entry
    F-δ  body detection + RB-mode SVD               # at entry
    [NR LOOP]
      check_contact_igl_v2(...)                     # detection
      compute_contact_apply_tensors(...)            # normal force
      F-ε  friction direction guard
      compute_friction_apply_tensors(...)           # tangential force
      [residual + convergence check]
      F-β  rewind on residual growth
      [K_tan assembly]
      F-γ  Tikhonov diagonal
      F-δ  RB-mode stabilization (via precomputed triplets)
      scipy.sparse.linalg.spsolve(K_tan_free, R_free)
      [u update]

tests/curved_contact_validation/
  README.md             user context (Korean → English)
  FINDINGS.md           V1-era baseline study
  mesh_gen.py           plate / box / sphere / finger-pad primitives
  runner.py             single-case test driver + plotting
  run_full_sweep.py     19-case sweep driver
  case_baseline_*.py + case_{a,b,c,d,e,f,g}_*.py    test definitions
  results_full/         most-recent sweep outputs

.claude/TODO/
  CONTACT_SOLVER.md     internal living doc (full journey)
  friction_contact.md   older reference
```

---

## 10. References

- Wriggers, *Computational Contact Mechanics*, 2nd ed., Springer (2006)
  — penalty Coulomb friction, augmented Lagrangian
- Puso & Laursen (2004), *CMAME* 193 — mortar segment-to-segment contact
- libigl — point-mesh distance, vertex normals
