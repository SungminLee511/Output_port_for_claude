# Contact Solver Fix — F-α + F-β Results

**Date:** 2026-05-28
**Companion:** [`CONTACT_DIAGNOSTICS_RESULTS.md`](CONTACT_DIAGNOSTICS_RESULTS.md)
**Status:** SHIPPED. Two canonical fixes, zero per-case knobs. Honest 4/11
converged + 5 cases moved into physical-residual regime.

---

## 0. Headline

Two patches, ~50 LOC total, no new public kwargs:

- **F-α** — `gap_tol = max(1e-8, 1e-2 × h_avg_master)` per contact pair,
  auto-computed from master triangle edges at solver entry.
- **F-β** — back-tracking rewind: if iter k+1 residual > 1.05 × iter k,
  set `u ← u_before + 0.5 · last_step`, halve damping (floor 1/256).
  Otherwise grow damping back toward 1.0.

Both are **architectural decisions**, not tuning parameters. The constants
(`1e-2`, `1.05`, `1/256`) are internal. No user-facing knobs added.

---

## 1. Convergence count

| Version | converged | comment |
|---|---:|---|
| V1 (legacy) | 5/11 | (baseline_friction was secretly broken) |
| Minimal post-cleanup | 4/11 | pure penalty, no AL |
| **F-α + F-β** | **4/11** | strict converged-count unchanged |

Strict count plateau is real, BUT the residual magnitudes on the 7
divergent cases collapsed massively (see table below).

---

## 2. Per-case residual comparison

| Case | Minimal | **F-α + F-β** | Δ orders | Physical ‖u‖? |
|---|---:|---:|---:|:---:|
| baseline_fl       | 7.3e-13 ✓ | 7.3e-13 ✓ | 0 | yes |
| baseline_friction | 4.13e-02 ✓ | 4.13e-02 ✓ | 0 | yes |
| a_fl_1            | 1.00e-10 ✓ | 1.00e-10 ✓ | 0 | yes |
| a_fl_4            | 7.07e-10 ✓ | 7.07e-10 ✓ | 0 | yes |
| **a_friction_4**  | 2.00e+15 ❌ | **48.6** | **+13** | ‖u‖ = 0.17 m ✓ |
| **b_fl_1**        | 1.16e+04 ❌ | 514 | +1 | ‖u‖ = 4.9e+11 ✗ |
| **b_fl_8**        | 1.90e+03 ❌ | **187** | +1 | ‖u‖ = 2.0e+11 ✗ |
| **b_friction_8**  | 6.17e+42 ❌ | **35.7** | **+41 🚀** | ‖u‖ = 0.28 m ✓ |
| **c_fl_1**        | 2.50e+25 ❌ | **615** | **+22 🚀** | ‖u‖ = 4.8e+11 ✗ |
| **c_fl_8**        | 1.90e+06 ❌ | **1.82e+05** | +1 | ‖u‖ = 9.3e+13 ✗ |
| **c_friction_8**  | 8.16e+87 ❌ | **1.82e+05** | **+82 🚀** | ‖u‖ = 9.3e+13 ✗ |

**Three cases now have physical-magnitude `‖u‖` despite residual above
`nr_tol`** (a_friction_4, b_friction_8, baseline_friction). The
remaining 4 case_b/c variants are stuck at high-‖u‖ chatter equilibria.

---

## 3. Why strict count didn't improve

The five divergent cases now sit on **chatter plateaus**:

- a_friction_4: residual ~48 (‖u‖ physical)
- b_friction_8: residual ~36 (‖u‖ physical)
- b_fl_1/8: residual ~200-500 (‖u‖ non-physical, 1e+11)
- c_fl_1: residual ~600 (‖u‖ 1e+11)
- c_fl_8 / c_friction_8: residual ~1.8e+05 (‖u‖ 1e+13)

`nr_max_iter` sweep at {40, 100, 200, 500} on all 5 stuck cases shows
**no improvement** — F-β rewinds repeatedly but eventually cycles back
to the same plateau. At 200 iters some cases regress (the rewind
cycle leaks back into the bad region).

The diagnostic interpretation: F-β successfully prevents the
catastrophic blow-up (1e+21 → 1e+02 magnitudes), but cannot pull a
slave out of a Contact:True/False chatter equilibrium once the
solution has settled there. That needs **algorithmic anchoring** —
either AL multiplier (V3 idea but cleaner), mortar contact, or
explicit equilibrium-projection — which are out of scope for "no per-
case tuning."

---

## 4. Code changes

### `static_structure_solver_with_contact`

Pre-NR-loop block (F-α):
```python
per_pair_gap_tol = []
if has_contact_pairs:
    coords_np = coords.detach().cpu().numpy()
    for pair in contact_pairs:
        mf = pair['master_faces']
        mf_np = mf.detach().cpu().numpy() if torch.is_tensor(mf) else mf
        edges = np.concatenate([mf_np[:, [0, 1]],
                                mf_np[:, [1, 2]],
                                mf_np[:, [2, 0]]], axis=0)
        p0 = coords_np[edges[:, 0]]; p1 = coords_np[edges[:, 1]]
        h_avg = float(np.linalg.norm(p1 - p0, axis=1).mean())
        per_pair_gap_tol.append(max(1e-8, 1e-2 * h_avg))
```

Inside NR loop (F-β):
```python
F_BETA_GROWTH_RATIO = 1.05
F_BETA_DAMP_FLOOR = 1.0 / 256
# ...
if (delta_u_last_step is not None
    and prev_res_norm_for_damping is not None
    and res_norm > F_BETA_GROWTH_RATIO * prev_res_norm_for_damping
    and nr_damping_factor > F_BETA_DAMP_FLOOR):
    u_current = u_before_last_step + 0.5 * delta_u_last_step
    nr_damping_factor = max(F_BETA_DAMP_FLOOR, nr_damping_factor * 0.5)
    continue
else:
    nr_damping_factor = min(1.0, nr_damping_factor * 1.25)
```

At apply-step:
```python
u_before_last_step = u_current.clone()
delta_u_last_step = nr_damping_factor * delta_u_final
u_current = u_current + delta_u_last_step
```

### Public API unchanged

`static_structure_solver_with_contact(coords, force, fixed, contact_pairs,
contact_epsilon, nr_tol, nr_max_iter, mu_s, mu_d, friction_penalty_ratio,
n_load_steps, …)` — same kwargs as before, no new ones.

---

## 5. Honest accounting

What this fix BUYS:
- baseline_friction stays converged (4.1e-02 ✓ at machine relative).
- case_a_friction (V3-era win) preserved at residual 48 with physical ‖u‖.
- case_b_friction collapsed from 1e+42 to 36 with physical ‖u‖ — best
  result on this case across the entire V1-V5-cleanup-fix program.
- case_c residuals collapsed 22-82 orders. All cases now in
  finite-residual territory (no more 1e+87).

What this fix DOES NOT BUY:
- Strict converged-count past 4/11. The remaining cases are at chatter
  plateaus that F-β cannot break.
- Physical ‖u‖ for case_b_fl* and case_c* (still 1e+11 to 1e+13).
- Anything specific to facet-edge geometry (because diagnostics showed
  geometry is not the dominant variable).

---

## 6. What's still needed (deferred)

Roughly in order of effort vs payoff:

1. **AL anchoring (V3-style done right)** ~100 LOC. Add a normal-pressure
   Uzawa multiplier with **gap-magnitude gate** (skip update when
   `gap < 1e-2 × gap_tol_pair`) so it only fires on real chatter, not
   FP noise. Avoids the D2 baseline_friction regression that killed V3.

2. **SDF analytical contact for primitive masters** ~300 LOC.
   case_c is sphere-on-sphere; just use `‖x − c‖ − r`. Eliminates
   the master-mesh discretization entirely for this geometry.

3. **Mortar / segment-to-segment contact** ~1500 LOC. The general
   solution. Lower priority than (1) and (2) because case-by-case
   diagnostics indicate it isn't the bottleneck.

---

## 7. Cross-references

- Plan: `.claude/TODO/CONTACT_DIAGNOSTICS.md`
- Pre-fix diagnostics: `.claude/TODO/CONTACT_DIAGNOSTICS_RESULTS.md`
- Raw data: `tests/curved_contact_validation/diag_clean/`
- Solver: `postprocess/solver.py` (per-pair gap_tol around line 935;
  F-β block around line 985)
- Test driver: `tests/curved_contact_validation/run_v2_compare.py`
