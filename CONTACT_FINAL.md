# Contact Solver — Final State

**Date:** 2026-05-28
**Status:** 3 small canonical fixes shipped. 5/11 strict converged.
**Companion:** [`CONTACT_DIAGNOSTICS_RESULTS.md`](CONTACT_DIAGNOSTICS_RESULTS.md),
[`CONTACT_FIX_RESULTS.md`](CONTACT_FIX_RESULTS.md)

---

## Three canonical fixes (no per-case knobs)

### F-α — Element-size-scaled `gap_tol`

```python
# At solver entry, per contact pair
edges = np.concatenate([mf_np[:, [0,1]], mf_np[:, [1,2]], mf_np[:, [2,0]]])
h_avg = np.linalg.norm(coords[edges[:,0]] - coords[edges[:,1]], axis=1).mean()
gap_tol_pair = max(1e-8, 1e-2 * h_avg)
```
Prevents contact engagement on FP-noise sub-edge-length penetrations.
~15 LOC.

### F-β — NR back-tracking rewind on residual growth

```python
if res_norm > 1.05 * prev_res and damping > 1/256:
    u_current = u_before_last_step + 0.5 * last_step
    damping *= 0.5
    continue
else:
    damping = min(1.0, damping * 1.25)
```
Catches the iter-5-style blow-up where re-engagement explodes residual.
Internal constants only. ~25 LOC.

### F-γ — Tikhonov regularization for rigid-body null modes

```python
k_stab = max(|K_diag|.max() * 1e-10, 1e-12)
K_tan_free = K_tan_free + k_stab * I
```
Prevents force-loaded free bodies from accelerating to infinity when
contact briefly fails. 5 LOC.

---

## Final results (11 cases)

```
CONVERGED: 5 / 11
```

| Case | V1 legacy | Minimal cleanup | **F-α+F-β+F-γ** | OK |
|---|---:|---:|---:|:---:|
| baseline_fl | 7.3e-13 ✓ | 7.3e-13 ✓ | **8.7e-07 ✓** | ✓ |
| baseline_friction | 4.1e-02 ✓ | 4.1e-02 ✓ | **4.1e-02 ✓** | ✓ |
| a_fl_1 | 1.0e-10 ✓ | 1.0e-10 ✓ | **3.7e-05 ✓** | ✓ |
| a_fl_4 | 7.1e-10 ✓ | 7.1e-10 ✓ | **9.2e-06 ✓** | ✓ |
| **a_friction_4** | 1.1e+17 ❌ | 2.0e+15 ❌ | **1.7e-05 ✓** | ✓ |
| b_fl_1 | 3.0e+04 ❌ | 1.2e+04 | **47.1** ‖u‖=3.1e+04 | ❌ |
| b_fl_8 | 6.1e+05 ❌ | 1.9e+03 | **1.06e+03** ‖u‖=1.3e+05 | ❌ |
| **b_friction_8** | 2.7e+45 ❌ | 6.2e+42 | **80.6** ‖u‖=**0.06 m** | ❌ |
| c_fl_1 | 5.8e+22 ❌ | 2.5e+25 | **8.4e+06** ‖u‖=2.4e+03 | ❌ |
| c_fl_8 | 5.2e+54 ❌ | 1.9e+06 | **1.07e+06** ‖u‖=5.7e+04 | ❌ |
| c_friction_8 | 5.8e+79 ❌ | 8.2e+87 | **1.22e+08** ‖u‖=4.5e+03 | ❌ |

Highlights:
- **a_friction_4: 1e+17 → 1.7e-05** (22 orders, CROSSES) 🚀
- **b_friction_8: 6e+42 → 80.6 with ‖u‖=0.06m** (41 orders, physical)
- **c_friction_8: 8e+87 → 1.2e+08 with ‖u‖=4.5e+03** (79 orders)
- All `‖u‖` now finite (none > 1e+05)

---

## What the 6 remaining failures actually are

Per T2 visualization: the 6 remaining cases are **NOT contact chatter**.
They are **force-loaded rigid bodies in static FEA**:
- punch / pad has no displacement BC
- contact constraint is the only thing preventing rigid-body motion
- whenever contact engagement briefly fails (a single NR iter), K_tan
  has a rigid-body null space
- Tikhonov (F-γ) keeps the body bounded, but the residual still
  reflects the unbalanced applied force

In commercial FEA (Abaqus, Ansys), these cases require either:
- displacement BCs on the punch (prescribe position, measure force)
- a stabilizing mass + damping in a quasi-static dynamic solver
- artificial "weak springs" to ground (what F-γ does, but per-body)

Our 5/11 is the honest answer with the **minimum** set of stabilizers
that don't introduce per-case tuning.

---

## What is still possible (none implemented)

| Idea | LOC | Expected gain | Per-case knobs? |
|---|---:|---|:---:|
| Per-body weak ground spring (auto-detect force-loaded bodies) | ~50 | Tighten ‖u‖ on b_fl/c | no |
| AL anchoring with gap-magnitude gate | ~100 | Might close b_friction (already at 80) | no |
| SDF analytical contact for sphere primitive | ~300 | c_fl_1 (sphere-on-sphere) | no |
| Mortar contact (segment-to-segment) | ~1500 | General curved-master | no |
| Test-case BC cleanup (force → displacement) | trivial | Easy 5/11 → 11/11 | no (test definition) |

Test-case BC cleanup is the cheapest path to "11/11 converged"; it just
acknowledges the model setup needs proper static BCs.

---

## Solver API (unchanged from minimal cleanup)

```python
static_structure_solver_with_contact(
    coords, force, fixed,
    contact_pairs=None, contact_epsilon=1e5, nr_tol=1e-3, nr_max_iter=50,
    mu_s=0.0, mu_d=0.0, friction_penalty_ratio=0.1,
    n_load_steps=1,
    rigid_blobs=None, elements_volume=None, elements_shell=None, material=None,
    u_init=None, tol=1e-3, max_iter=5000, dim=3, cg_start=True,
    device="cuda:0", dtype=torch.float64,
)
```

F-α/F-β/F-γ are baked into the solver body; no user-facing kwargs.

---

## File summary

- `postprocess/solver.py`: 2828 lines (was 3373 pre-cleanup)
- `tests/curved_contact_validation/`: 11 cases, all running
  successfully (no exceptions, no inf, no nan)
- `.claude/TODO/`: diagnostics + fix design + this final doc
- `tests/curved_contact_validation/diag_clean/`: A/B/C/E/T1/T2/verify
  plots + JSON

---

## Convergence count summary across the project

```
V1 legacy:                    5/11 (baseline_friction quietly broken in V2/3/4/5)
V2 final:                     5/11
V3:                           4/11 actual (5/11 paper but baseline_friction broken)
V4 first attempt:             4/11
V4 REDO:                      5/11 (E2 fixed baseline_friction)
V5 (Phase G load subdivision): 5/11
Aggressive cleanup (minimal): 4/11
F-α + F-β:                    4/11 (residual collapses but no crossings)
F-α + F-β + F-γ:              5/11 ✓ (a_friction_4 crosses)
```

5/11 with **honest** mechanism + zero per-case knobs is the current
ship. The remaining 6 are model-side ill-posedness (force-loaded
rigid bodies in static FEA) not solver bugs.
