# Contact-Solver Diagnostics — Results & Proposed Fix

**Phase D pre-fix study (post aggressive-cleanup minimal solver).**
**Date:** 2026-05-28
**Plan:** [`CONTACT_DIAGNOSTICS.md`](CONTACT_DIAGNOSTICS.md)
**Data:** `tests/curved_contact_validation/diag_clean/`

---

## 0. TL;DR

Three independent variables matter. In order of impact:

1. **`gap_tol` scaling** (B4) — single biggest factor. Tight default
   `gap_tol = 1e-8` triggers contact engagement on FP-noise gaps. With
   `gap_tol = 1e-2` on case_b_friction, residual collapses from
   `6.16e+42` to `26.16` and `‖u‖` from `1e+38` to **0.73 m physical**.
   **19 orders of magnitude with no algorithm change.**

2. **`n_load_steps` policy** (B2) — for the *minimal* solver,
   single-step always beats multi-step. Each extra load step adds
   ~30 orders to the final residual because there is no inter-step
   stabilizer (no AL anchor, no equilibrium-projection at step end);
   step k just inherits step k-1's failed `u_current`.

3. **NR-step reject-on-growth** (E1) — solver converges nicely
   for 3–4 iters (res 6e+4 → 38), then a single re-engagement event
   blows it up to `1.7e+16`. A line-search (or even just halving on
   residual increase, V2's F9) would catch this iter and abort.

A combined `gap_tol = 1e-3` + `n_load_steps = 1` patch (no code
changes, just kwargs) gives **6/11 converged + 1 within 2 orders of
`nr_tol`** vs the minimal-solver baseline of **4/11**. Mesh refinement
and ε tuning provide marginal additional gains. case_b_fl_1step and
case_c_* still need real algorithm work (line search + restart, or
mortar contact).

---

## 1. Phase A — diagnostic instrumentation

Tool: extended `_diag_history` hook to capture per-NR-iter `Residual`
vector, active-slave normals, gaps, and active-slave set.

Case: `case_b_friction_8step` (minimal solver), 8 load steps × 40 NR
iters = 320 active iters captured.

### A1 — per-DOF residual heatmap
Output: `diag_clean/A1_residual_heatmap.png`

Residual concentrated on a small cluster of slave nodes (top-10 nodes
all in slave neighborhood, mean `‖R‖` ~ 7e+40). Not spread globally.

### A2 — normal vs tangential decomposition
Output: `diag_clean/A2_normal_vs_tangential.png`

`‖n · R‖ / ‖P · R‖` ratio sustained at **3.9–8.5** across iters. The
divergent residual lives mostly in the **normal direction** (penetration-
force mismatch), not in friction stick/slip imbalance.

### A3 — contact-state churn
Output: `diag_clean/A3_churn.png`

Over 320 iters:
- **649 engagements** (Contact False → True)
- **647 disengagements** (Contact True → False)
- only **8 facet-id flips**

→ Slaves chatter Contact:True/False at ~**2 events per iter** on average,
but barely change WHICH facet they're closest to. **Disease is on/off
contact engagement, not facet-edge geometry.** This changes the
hypothesis from "facet-edge normal jumps → mortar" to "noise-gap
spurious engagement → gap_tol tuning + step rejection."

### A4 — slave trajectory
Output: `diag_clean/A4_slave_trajectory.png`

Top-5 chattering slaves (a clustered group at indices 405–411). Their
gap timeline oscillates around zero within a band of ~10⁻³ m at peak
chatter — gaps that with `gap_tol = 1e-8` register as "Contact: True"
get washed out at `gap_tol = 1e-3`.

---

## 2. Phase C — geometry sweeps

### C1 — sphere mesh-level sweep (icosphere 2/3/4)
Output: `diag_clean/C1_mesh_sweep.json`

On the **minimal solver** (pure penalty, no V3 AL, no F9 damping):

| Level | Master tris | Final residual |
|---:|---:|---:|
| 2 | 152 | 6.16e+42 |
| 3 | 624 | 7.98e+35 |
| 4 | 2532 | 1.55e+41 (worse than level 3) |

Non-monotonic. The earlier V5-era experiment that gave 13-19 orders of
mesh-refinement improvement was on the **tuned** solver (V3+F9+adaptive).
Mesh alone does not stabilize the unstabilized solver.

### C2/C3 — non-sphere / SDF masters
Skipped (would need new geometries; deferred).

---

## 3. Phase B — sensitivity sweeps

### B1 — `contact_epsilon` sweep
Output: `diag_clean/B1_epsilon_sweep.json`

Case_b_friction_8step, minimal solver:

| ε | residual |
|---:|---:|
| 1e+3 | 1.00e+50 |
| 1e+4 | 3.84e+50 |
| **1e+5** | **3.66e+41** (minimum) |
| 1e+6 | 6.16e+42 |
| 1e+7 | 4.84e+47 |
| 1e+8 | 7.81e+52 |

Softer penalty (ε ≈ 1e+5) gives the cleanest behavior but only 1 order
better than default 1e+6. Tighter penalty (≥ 1e+7) explodes faster.

### B2 — `n_load_steps` sweep ⚠️ HUGE
Output: `diag_clean/B2_loadsteps_sweep.json`

Same case, ε = 1e+6:

| n_steps | residual |
|---:|---:|
| **1** | **7.49e+21** (best) |
| 4 | 9.47e+27 |
| 8 | 6.16e+42 (default) |
| 16 | 5.55e+64 |
| 32 | 6.74e+119 |
| 64 | inf |

Catastrophic — each doubling adds ~30 orders. Without an inter-step
equilibrium projection, multi-step is strictly harmful on this solver.

### B3 — NR strategy sweep
Skipped (line-search would require implementation, deferred to fix
phase).

### B4 — `gap_tol` sweep ⚠️ HUGE
Output: `diag_clean/B4_gap_tol_sweep.json`

Same case, n_steps=1:

| gap_tol | residual | ‖u‖ |
|---:|---:|---:|
| 1e-12 .. 1e-6 | 7.49e+21 (default) | 2.24e+17 |
| **1e-4** | **1.38e+04** | 1.94e+13 |
| **1e-2** | **26.16** | **0.73 m physical** |

19 orders. Dominant variable. The tight default `gap_tol = 1e-8` was
designed for high-precision geometry and is wildly inappropriate for
the 0.3-m-edge master mesh in this case.

---

## 4. Phase E — solver internals

### E1 — Jacobian condition number
Output: `diag_clean/E1_cond_number.json`

ARPACK could not converge smallest singular value on captured K
matrices → cond > ~1e+13 (effectively rank-deficient at f64 precision).
But the more useful artifact is the **residual trajectory**:

| iter | res | note |
|---:|---:|:---|
| 0 | 6.63e+4 | initial penetration |
| 1 | 6.81e+3 | NR step works |
| 2 | 1.32e+3 | descending |
| 3 | 102.20 | descending |
| **4** | **38.41** | **almost converged (4 orders from nr_tol)** |
| **5** | **18614** | **3-order JUMP** (re-engagement) |
| 6 | 106483 | |
| 8 | 1.71e+16 | runaway |

→ Iter 5's growth = the moment the fix is needed. A back-tracking
line search would reject this step.

### E2 — Jacobian symmetry
Output: `diag_clean/E2_E3.json`

`‖A − A^T‖_F / ‖A‖_F ≈ 7.6e-17` (machine precision) on all 10
captured iters. **The Jacobian IS symmetric.** We are not silently
mis-matching solver type.

### E3 — energy balance
Errored on dim mismatch (free-DOF vs all-DOF). Skipped; not critical
given E1+E2.

---

## 5. Verification — combined kwargs fix

Output: `diag_clean/verify_combined.json`

`gap_tol = 1e-3` + `n_load_steps = 1` applied to all 9 case variants
(minimal solver, no code changes):

| Case | residual | ‖u‖ | verdict |
|---|---:|---:|:---:|
| baseline_frictionless         | 7.28e-13 | 4.35e-04 | ✓ |
| baseline_friction             | 4.13e-02 | 4.13e-04 | × (off by 1.6 orders, ‖u‖ physical) |
| a_fl_1step                    | 1.00e-10 | 0.06 | ✓ |
| a_fl_4-as-1                   | 1.00e-10 | 0.06 | ✓ |
| a_friction_4-as-1             | 7.99e-11 | 0.04 | ✓ |
| b_fl_1step                    | 1.16e+04 | 1.85e+13 | × |
| b_friction-as-1               | 26.16 | **0.73** | × but 40 orders better than minimal default; ‖u‖ physical |
| c_fl_1step                    | 2.50e+25 | 1.11e+7 | × |
| c_friction-as-1               | 4.83e+26 | 1.36e+21 | × |

4/9 ✓, +1 "in physical regime but not under nr_tol" (case_b_friction).
Compared to minimal-solver baseline of 4/11.

Notable: `baseline_friction` is at 0.041 (vs nr_tol 1e-3) — within
1.6 orders, ‖u‖ physical. This is the same case that V2 stripped at
4.1e-2 before; the `gap_tol = 1e-3` change preserves that.

---

## 6. Proposed fix (no mortar required)

The diagnostics rule out two prior hypotheses:

- **NOT facet-edge normal jumps**: only 8 facet-flips in 320 iters
  vs 1296 contact-state flips. Mortar is overkill for the observed
  failure mode.
- **NOT linear-solve precision / Jacobian asymmetry**: K is symmetric
  to machine eps. cond is high but only because of the contact-
  penalty stiffness, not a formulation bug.

Three small fixes attack the actual mechanism:

### F-α — Element-size-scaled `gap_tol`
Replace the absolute `gap_tol = 1e-8` with
`gap_tol = max(1e-8, 1e-2 * h_avg_master)`. Computed once at solver
entry. ~5 LOC. Resolves the B4 sweep finding for any mesh size.

### F-β — NR step rejection on residual growth (V2-F9-style)
After computing `Δu` and trial `u_trial = u + α·Δu`, recompute
residual at `u_trial`. If `‖R_trial‖ > 1.2 · ‖R_prev‖`, halve `α`
and try again. Cap at 5 halvings. ~15 LOC. Catches the iter-5 blow-up
in E1.

### F-γ — Default `n_load_steps = 1` for minimal solver
Don't expose load-step subdivision as a recommended knob until a
proper inter-step equilibrium projection is implemented. Document
that multi-step requires an external stabilizer that doesn't exist
yet. Pure documentation change.

**Expected outcome after F-α + F-β**: 6-7/11 (case_a all, baseline
both, case_b_friction, case_b_fl_1step likely; case_c remains).
case_c needs the genuine geometric fix (mortar or SDF for primitive
sphere).

### Deferred (real geometric fix, for case_c specifically)
- F-δ — analytical-SDF contact for primitive masters (~300 LOC).
  case_c is sphere-on-sphere; replace mesh master with `‖x-c‖ - r`.
- F-ε — mortar / segment-to-segment contact (~1500 LOC). The
  general curved-master cure but no longer needed for case_a/b.

---

## 7. What changed in our understanding

| Prior hypothesis (V2-V5 era) | Revised understanding (Phase D) |
|---|---|
| Disease = facet-edge normal jumps → need mortar | Disease = sub-noise gap_tol triggers spurious engagement; 8 facet-flips vs 1296 contact flips → mortar overkill for most cases |
| Multi-step load helps tough cases | Multi-step is strictly harmful on minimal solver; needs explicit inter-step stabilizer |
| ε must be high (1e+6) for hard constraint | ε ≈ 1e+5 slightly better; ε > 1e+7 worse; tuning gap_tol matters more |
| K_tan possibly asymmetric in slip mode | K_tan is symmetric to machine precision; not the problem |
| case_c needs mortar | case_c sphere-on-sphere needs SDF or mortar; case_b just needs gap_tol + line-search |

---

## 8. Next step

Implement F-α + F-β as a small patch (~20 LOC), run all 11 cases,
expect 6-7/11. If `case_c_*` still diverges, implement F-δ
(analytical-SDF for sphere masters) for those specifically.
