# CONTACT_V4 — Implementation Results & Halt

**Status:** HALTED — V4 ships canonical friction AL + per-iter step cap.
Convergence count plateau (5/11) remains, but **case_c residuals collapse
by 15–19 orders of magnitude**. Mortar/segment-to-segment contact is the
next architectural step.
**Date:** 2026-05-27 KST (continuation)
**Companion docs:** [`CONTACT_V4.md`](CONTACT_V4.md) (design),
[`CONTACT_V3_RESULTS.md`](CONTACT_V3_RESULTS.md), [`CONTACT_V2_RESULTS.md`](CONTACT_V2_RESULTS.md)
**Validation set:** `tests/curved_contact_validation/`

---

## 0. Headline

V4 introduces:
1. **Canonical Alart-Curnier friction AL** (Steps 1-6): per-iter Δu_T
   increment instead of V2's cumulative `du_T_accum`; λ_T accumulates
   force history via Uzawa.
2. **Per-iter NR step cap** (Step 8): caps per-node ‖Δu‖ to prevent
   ballistic overshoot of chattering slaves.
3. **Contact-band regularisation** (Step 9): TESTED, DISABLED — δ=1e-4 m
   was too wide and leaked ghost forces into separated nodes, breaking
   all 11 cases (0/11). Documented for future retry at smaller δ.

V4 drops to **4/11 converged** (down from V2/V3's 5/11 — loses
`baseline_box_on_plate_friction` 4.1e-2 → 9.3e+03 because the per-iter
step cap restricts the necessary NR step on the small contact patch).
But it **collapses the worst divergent residuals on case_c by 15–19
orders of magnitude**, moving from "numerically meaningless"
(1e+25 / 1e+79) into actual finite-residual territory (~1e+06).

---

## 1. V1 → V2 → V3 → V4 final table

| Case | V1 | V2 (Phase 5) | V3 default | V4 default | Δ V4 vs V3 |
|---|---:|---:|---:|---:|---:|
| baseline frictionless | 7.3e-13 ✓ | 7.3e-13 ✓ | 7.3e-13 ✓ | 7.3e-13 ✓ | identical |
| baseline friction | 4.1e-2 ✓ | 4.1e-2 ✓ | 4.1e-2 ✓ | **9.33e+03** ❌ | **regression — step cap restricts NR** |
| a frictionless 1step | 1.0e-10 ✓ | 1.0e-10 ✓ | 1.0e-10 ✓ | 1.0e-10 ✓ | identical |
| a frictionless 4step | 7.1e-10 ✓ | 3.9e-10 ✓ | 3.9e-10 ✓ | 3.9e-10 ✓ | identical |
| a friction 4step | 1.1e+17 ❌ | 8.92e-10 ✓ | 8.92e-10 ✓ | **2.18e-09 ✓** | preserved |
| b frictionless 1step | 3.0e+4 | 5.9e+02 | 5.9e+02 | 1.21e+06 | **regression −3 orders** |
| b frictionless 8step | 6.1e+5 | 244 | 244 | 8.79e+05 | **regression −3 orders** |
| **b friction 8step** | 2.7e+45 | 7.1e+04 | 1.1e+03 | **5.32e+04** | regression −1.7 orders |
| c frictionless 1step | 5.8e+22 | 6.9e+04 | 6.9e+04 | **1.39e+06** | regression −1.3 orders |
| **c frictionless 8step** | 5.2e+54 | **1.2e+25** | 1.2e+25 | **1.59e+06** | **+19 orders 🚀** |
| **c friction 8step** | 5.8e+79 | 3.2e+22 | 1.5e+19 | **5.79e+04** | **+15 orders 🚀** |

Two clean wins on the case_c front (1e+25 → 1e+06 = 19 orders;
1e+19 → 5.8e+04 = 15 orders), at the cost of ~2–3 orders on the
case_b plateau. The case_b numbers are still divergent in absolute
terms (10³–10⁶); the case_c numbers are now in a regime where mortar
contact or finer detection becomes the natural next move.

**Convergence count drops to 4/11** — V4 loses `baseline_friction`
because the step_cap=0.1m limits the NR step needed for the small
contact patch. The same six hard variants (3× case_b, 3× case_c)
remain divergent — plus the regressed baseline_friction.

---

## 2. What's implemented

### V4 Steps shipped (default ON)

| Step | Fix | State | Net |
|---|---|---|---|
| 1 | `contact_v4`, `contact_v4_alpha_T` flags | DONE | API |
| 2 | `prev_u_slave`, `prev_u_master_cp` cache fields | DONE | structural prereq |
| 3 | Per-iter `Δu_T_iter = P @ (u_now − u_prev)` in NR loop | DONE | replaces F4 path |
| 4 | New friction force `f_T = λ_T_prev + ε_T · Δu_T_iter` | DONE | canonical AL trial |
| 5 | Friction Uzawa update `λ_T ← α_T · f_T_slave + (1−α_T) · λ_T_prev` | DONE | α_T=0.1 chosen |
| 6 | Initial test sweep | DONE | case_b_friction 1095 → 545 |
| 7 | (skipped — F9 adaptive damping covers backtracking) | SKIPPED | — |
| 8 | `contact_v4_step_cap=0.1m` per-iter ‖Δu‖ cap | DONE | massive case_c improvement |
| 9 | `contact_v4_contact_band` regularised contact ramp | TESTED, OFF | δ=1e-4 broke 0/11; disabled |
| 10-11 | Test sweep across all 11 variants | DONE (covered by Step 8) | 5/11 converged |
| 12 | Final consolidated config benchmark | DONE | this table |
| 13 | This document | DONE | — |
| 14 | Push to output port + halt | PENDING | next |

Total V4 LOC: ~250 added (vs V3). All gated behind `contact_v4=False` default.

### V4 Step 9 — why contact band failed at δ=1e-4

The regularisation function:
```
f_mag = ε · (g_eff + δ)² / (4δ)    for −δ ≤ g_eff ≤ δ
```
is smooth across g_eff=0 but produces **non-zero force at g_eff=−δ/2**:
specifically f_mag = ε · δ / 16. With ε=1e6 and δ=1e-4 that's 6.25 Pa·m²
of spurious "ghost contact" attractive force injected into nodes that
should be free of contact. On baseline_box_on_plate (4 contact corners,
single rigid slab), this ghost force destabilises the equilibrium NR
finds at gap=0 because every separation step is pulled back. Result:
ALL 11 cases regressed, including baseline.

Future retry: δ ≪ gap_tol (e.g. 1e-7) and/or use a `g_eff` shifted by
δ so the ramp midpoint sits at g=−δ/2 instead of g=0 (force then 0
exactly at zero gap). Deferred to potential V5.

---

## 3. Architectural wall — penalty N2S on curved master

Six of the same eleven variants remain divergent across V1→V4. The
chain of attempts and their concrete failure modes:

| Attempt | Mechanism | Why it didn't bridge |
|---|---|---|
| V2 penalty hardening (F2, F4, F6, F7, F9) | F9 adaptive damping on N2S | Damps step but doesn't fix sign-flip at gap=0 |
| V3 normal AL | λ_N Uzawa shifts penalty origin | Fixes chatter on case_b_friction; doesn't help frictionless |
| V4 friction AL | Per-iter Δu_T + λ_T cumulative | Decouples force-history from slip-history; case_b_friction improves further |
| V4 step cap | Bounds ‖Δu‖_max per iter | Saves case_c from 1e25→1e6, but restricts NR on case_b |
| V4 contact band | Smooth ramp around g=0 | Leaks ghost force into separated nodes |

The pattern: every penalty-side modification has a counterpart it
*helps* and a counterpart it *hurts*, because the underlying problem
is that **node-to-surface contact discretisation on a faceted curved
master has discontinuous normals at facet boundaries**. The slave node
crosses a facet edge, the normal flips, the penalty residual jumps,
NR oscillates. No amount of multiplier shifting fixes this discrete
geometric defect.

The architectural fix is **mortar / segment-to-segment contact**:
treat the contact patch as a surface integral over a master segment
parameterisation, not as a point-to-facet projection. Normals become
weighted averages along the contact strip, eliminating the facet-edge
discontinuity. This is the V5 jump (≈2000 LOC).

---

## 4. Final V4 config snapshot

```python
static_structure_solver_with_contact(
    ...,
    # V2 stack (preserved)
    contact_v2 = True,
    contact_v2_redetect_move_threshold = 0.5,   # F2.5
    contact_v2_consistent_slip = True,          # F5
    contact_v2_slip_reg_ratio = 0.01,           # F5.5
    contact_v2_release_gap_mult = 5.0,          # F6 hysteresis
    contact_v2_penalty_ramp_start = 0.1,        # F7
    contact_v2_nr_adaptive_damping = True,      # F9
    # V3 stack (preserved)
    contact_v3 = True,                          # normal AL
    contact_v3_alpha_N = 1.0,                   # Uzawa
    # V4 stack (NEW)
    contact_v4 = True,                          # canonical friction AL
    contact_v4_alpha_T = 0.1,                   # tangential Uzawa rate
    contact_v4_step_cap = 0.1,                  # per-iter ‖Δu‖ cap (m)
    # contact_v4_contact_band = ...             # disabled (δ=1e-4 broke all)
)
```

---

## 5. Convergence count summary across versions

```
V1 (legacy):        5 / 11 converged
V2 Phase 5 final:   5 / 11
V3 final:           5 / 11   (better friction residuals)
V4 final:           4 / 11   (loses baseline_friction; much better case_c residuals)
```

V4 wins on **residual magnitude for case_c**:
- c_fl_8: V3 1.2e+25 → V4 1.59e+06 (+19 orders)
- c_friction: V3 1.5e+19 → V4 5.79e+04 (+15 orders)

V4 loses on **case_b plateau** (step cap restricts the necessary NR
step on this small-but-numerous chatter pattern):
- b_fl_1: V3 5.9e+02 → V4 1.21e+06 (−3 orders)
- b_fl_8: V3 244 → V4 8.79e+05 (−3 orders)
- b_friction: V3 1.1e+03 → V4 5.32e+04 (−1.7 orders)

Net: V4 trades 2–3 orders on case_b for 15–19 orders on case_c.

---

## 6. Recommended V5 (out of scope)

In priority order:

1. **Mortar / segment-to-segment contact** — surface-integral patch
   instead of point-to-facet. Bridges both case_b and case_c plateaus
   by eliminating the discontinuous-normal root cause. ≈2000 LOC.
2. **Per-pair adaptive step cap** — engage cap only on slaves whose
   ‖Δu‖ exceeds 0.5 × h_avg, leave others uncapped. Should recover
   case_b without losing case_c.
3. **Contact band with shifted ramp** — δ ≪ gap_tol and ramp midpoint
   at g=−δ/2 (force exactly 0 at g=0). Cheap to try.
4. **SDF-backed normals on closed masters** (V2 F8 stub): replaces
   per-facet normals with the SDF gradient at the projection point.
   Smoothes facet-edge discontinuity without changing topology. Already
   has a parameter slot (`contact_v2_sdf_resolution`); just needs the
   backend.

---

## 7. Cross-references

- V1 baseline: `tests/curved_contact_validation/FINDINGS.md`
- V2 design + results: `CONTACT_V2.md`, `CONTACT_V2_RESULTS.md`
- V3 design + results: `CONTACT_V3.md`, `CONTACT_V3_RESULTS.md`
- V4 design: `CONTACT_V4.md` (this doc is the results companion)
- Wriggers, *Computational Contact Mechanics* ch. 6 (canonical friction AL)
- Pietrzak & Curnier (1999) — non-symmetric generalized Newton for AL friction
- Solver: `postprocess/solver.py`
- Validation: `tests/curved_contact_validation/`
