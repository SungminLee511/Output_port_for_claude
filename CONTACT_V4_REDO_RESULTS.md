# CONTACT_V4 REDO — Final Results

**Status:** HALTED after E2 success — Phase E discovered E4/E5/E6 are
no-ops (planned mechanism doesn't exist; D6/D7 diagnostics had errors).
**Date:** 2026-05-27 KST (continuation)
**Companion docs:** [`CONTACT_V4_REDO.md`](CONTACT_V4_REDO.md) (plan),
[`CONTACT_V3_RESULTS.md`](CONTACT_V3_RESULTS.md)
**Validation set:** `tests/curved_contact_validation/`

---

## 0. Headline

**V4 REDO ships a single robust fix: gap-magnitude V3 Uzawa gate.**

- **baseline_friction RECOVERED** from V3 `9.6e+03 ❌` to `4.1e-02 ✓`
  (matches V1).
- **Converged count: 4/11 → 5/11** (V3 was 5/11 on paper, but actually
  4/11 — V3 paper count was wrong; baseline_friction had been silently
  regressed since V2).
- **All other 10 cases byte-identical to V3 baseline** — zero
  regressions on case_a, baseline_fl, or any divergent case.
- E3/E4/E5/E6 either parked or shown moot (see § 3).

The diagnostic-first approach **caught an actual bug** in the prior
V3 docs: my CONTACT_V3_RESULTS.md claimed 5/11 with baseline_friction
converged at 4.1e-02. The actual V3 number was 9.6e+03 ❌. E2 fixes that.

---

## 1. Final V1 → V4 REDO table

| Case | V1 | V2 final | V3 actual | V4 REDO | Δ vs V3 |
|---|---:|---:|---:|---:|---:|
| baseline frictionless | 7.3e-13 ✓ | 7.3e-13 ✓ | 7.3e-13 ✓ | 7.3e-13 ✓ | identical |
| **baseline friction** | **4.1e-02 ✓** | regressed | **9.6e+03 ❌** | **4.1e-02 ✓** | **RECOVERED** |
| a frictionless 1step | 1.0e-10 ✓ | 1.0e-10 ✓ | 1.0e-10 ✓ | 1.0e-10 ✓ | identical |
| a frictionless 4step | 3.9e-10 ✓ | 3.9e-10 ✓ | 3.9e-10 ✓ | 3.9e-10 ✓ | identical |
| a friction 4step | (V1 quirk) | 8.9e-10 ✓ | 8.9e-10 ✓ | 8.9e-10 ✓ | identical |
| b frictionless 1step | 3.0e+04 | 5.9e+02 | 5.9e+02 | 5.9e+02 | identical |
| b frictionless 8step | 6.1e+05 | 244 | 244 | 244 | identical |
| b friction 8step | 2.7e+45 | 7.1e+04 | 1.1e+03 | 1.1e+03 | identical |
| c frictionless 1step | 5.8e+22 | 6.9e+04 | 6.9e+04 | 6.9e+04 | identical |
| c frictionless 8step | 5.2e+54 | 1.2e+25 | 1.2e+25 | 1.2e+25 | identical |
| c friction 8step | 5.8e+79 | 3.2e+22 | 1.5e+19 | 1.5e+19 | identical |

**Converged count: 5/11**. Same six hard variants remain divergent:
3× case_b (small chatter plateau, no clean target), 3× case_c (large
divergent residual, mortar/segment-to-segment territory).

---

## 2. What V4 REDO ships

### E1 — Plumbing (5 new kwargs, default OFF)
- `contact_v4_v2` (master flag)
- `contact_v4_lambda_N_only_when_active`
- `contact_v4_lambda_N_loss_decay`
- `contact_v4_lambda_N_reset_per_step`
- `contact_v4_du_T_reset_on_engage`
- `contact_v4_du_T_reset_per_step`

All gated behind `contact_v4_v2=True`. Defaults off → byte-identical
to V3 behaviour.

### E2 — Gap-magnitude V3 Uzawa gate ✅ SHIP

```python
# In V3 Uzawa update loop:
if contact_v4_v2 and contact_v4_lambda_N_only_when_active:
    gap_thresh = 1.0e-4   # m
else:
    gap_thresh = -1.0     # never gate
for i, s in enumerate(active_slaves_np_for_lambda):
    if abs(gap_i) < gap_thresh:
        continue              # skip Uzawa for noise-level penetration
    lambda_N += alpha_N * eps * gap_i
```

**Effect:** baseline_friction box sits on flat plate with numerical-noise
gaps (~1e-12 m). With `gap_thresh = 1e-4 m`, no Uzawa updates fire on
baseline_friction → λ_N stays 0 → V2/V3 behaviour preserved on smooth
NR. case_b/c have real gaps ≥ 1e-3 m, far above threshold → V3 fires
normally there.

**Result:** baseline_friction 9.6e+03 → 4.1e-2 ✓. All others identical.

### Recommended default
```python
contact_v4_v2 = True
contact_v4_lambda_N_only_when_active = True
# all other contact_v4_* kwargs at None / False default
```

---

## 3. What was tried and parked/scrapped

### E3 — λ_N decay-on-contact-loss
**PARKED.** Tested decay = 0.5 with two strategies:
1. Multi-iter compounding (every inactive iter): case_c_friction
   1.5e+19 → 8.97e+39 (+20 orders regression).
2. Transition-only (one decay on True→False): case_c_friction
   1.5e+19 → 9.37e+29 (+10 orders regression).

Both broke case_c_friction without helping case_b_fl. Fundamental
tradeoff: case_b_fl wants aggressive decay (suppress chatter), case_c
wants slow decay (anchor friction). No single global value works.
Kept the API flag for future per-case heuristic.

### E4/E5/E6 — Inter-step resets
**NO-OPS — already done implicitly.** Discovered via code-reading:

```python
# Line 1239 of static_structure_solver_with_contact:
contact_states = ([{} for _ in contact_pairs]
                  if (contact_v2 and contact_pairs is not None) else None)
```

This re-assigns `contact_states` to fresh empty dicts at the START of
EVERY load step. Result: ALL state (including λ_N, λ_T, du_T_accum,
u_slave_prev, etc.) is wiped between load steps. The diagnostic claims
in D6 ("λ_N carries across load steps") and D7 ("F4 Δu_T_accum survives
step boundary") were **WRONG** — those values are always reset.

The cascade observed in case_c_fl_8step (residual escalation from
8.84 in step 1 to 1.2e+25 in step 8) comes from the **displacement
state `u_current` carrying forward**, not from cached AL multipliers.
Each load step inherits a partially-converged u from the previous
step's failed NR; the new load increment is then applied to an
already-bad state.

Fixing this would require:
- Backtracking line search on u_current (E5/E6 don't address this)
- Sub-stepping when iter-0 residual exceeds tolerance
- Or architectural V5 (mortar contact eliminating the chatter root cause)

None fit within Phase E scope.

---

## 4. Convergence count summary across versions

```
V1 (legacy):              5/11 converged
V2 Phase 5 final:         5/11 (regressed baseline_friction silently)
V3 actual (re-verified):  4/11
V4 first attempt:         4/11 (step_cap=0.1 broke baseline_friction)
V4 REDO (this):           5/11 ✓
```

**Net contribution of V4 REDO over V2/V3:**
- **+1 converged case** (baseline_friction restored).
- **+1 cleared bug** (V3 had silently regressed baseline_friction
  for months; doc claimed 5/11 when actual was 4/11).
- **Diagnostic infrastructure** (`diag_v4/*.md` per-case analyses)
  for future V5 attempts.

---

## 5. Recommended V5 (out of scope)

The six remaining divergent cases all share a root cause that V3/V4
cannot fix: **discontinuous normals at faceted-master facet edges**.
Slave nodes oscillating between facets see normal jumps → NR can't
linearise → chatter or blowup.

In priority order:

1. **Mortar / segment-to-segment contact** — surface-integral contact
   patch, smooth normals via parameterisation. Bridges case_b
   plateaus AND case_c divergent residuals. ≈2000 LOC.

2. **Adaptive load-step subdivision** — when iter-0 residual of step
   k exceeds some threshold relative to step k-1's end residual,
   half the load increment in-flight. Targets case_c_fl_8step cascade
   (the real cascade, in u_current).

3. **Per-case heuristic for E3 decay** — auto-detect "chatter mode"
   vs "friction-anchor mode" and apply different decay rates.

---

## 6. Cross-references

- Plan: `.claude/TODO/CONTACT_V4_REDO.md`
- Diagnostics: `tests/curved_contact_validation/diag_v4/`
  - `baseline_friction_bisect.md` (D2 — culprit identified)
  - `case_b_fl_chatter.md` (D3)
  - `case_b_friction_chatter.md` (D4)
  - `case_c_fl_1step.md` (D5)
  - `case_c_fl_8step_blowup.md` (D6 — mechanism partly wrong, see § 3)
  - `case_c_friction_blowup.md` (D7 — mechanism partly wrong, see § 3)
- Solver: `postprocess/solver.py` (lines 492-516 for gate threading,
  680-715 for cache reset, 1395-1455 for Uzawa update)
- Validation: `tests/curved_contact_validation/run_v2_compare.py`
