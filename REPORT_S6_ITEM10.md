# Stage 6, item 10 — the [G6-N1] read-out: which mechanism explains the Ehrenfest advantage

`PLAN_STAGE6` §2.3 registers two mechanisms for the Stage-5 observation *"Ehrenfest helps on
heavy-tailed targets"* and one discriminating test:

> **Discrimination:** regress the response on `B_c` and on `KL(·‖Bin)` **separately and jointly**
> across all count-native cells.

Driver `experiments/stage6/item10_geometry.py`; artefact
`runs/stage6/item10/s6_item10_geometry.json` (schema `qdasbs/stage6/item10/1`, 1,040 rows, 582 KB).
Every number below is read out of that artefact.

**This report does not accept its own verdict.** The pre-registered decision rule fires
`KL_to_binomial` on both `p0` modes, and §4 below shows that outcome is produced entirely by the
`S = 128` block, which is the block whose Ehrenfest arm lost 16 cells to numerical divergence. The
PI questions are in §6.

---

## 0. Summary

**The grid ran to completion: 1,040/1,040 cells, 1,020 good, 20 hard failures, 92 divergences.**
25.3 min wall, 35.4 CPU-h, 90 workers.

| | result |
|---|---|
| **Pre-registered verdict, as computed** | `KL_to_binomial` on **both** `p0` modes — M2 carries it, M1 (the PI's prior) does not |
| **Joint KL coefficient** | `−0.319 [−0.561, −0.088]` (pi_ref), `−0.299 [−0.549, −0.033]` (uniform) |
| **Joint `B_2` coefficient** | `−0.007 [−0.274, +0.277]` (pi_ref), `+0.122 [−0.278, +0.409]` (uniform) — contains 0 |
| **Explanatory power** | `R²_joint` = **0.104 / 0.069**. Spearman on KL = `−0.238 / −0.159` |
| **Confound broken as designed** | VIF `1.73 → 1.31`, `corr(log B, log KL)` `0.648 → 0.487` when the two [G6-N1] cells enter |
| **Robustness — the finding of this report** | the sign of **both** regressors **flips** between `S ≤ 64` (`s_KL = +0.28`) and `S = 128` (`s_KL = −0.76`). The verdict is a `S = 128` effect |

---

## 1. What was run, and the declared deviation from §8

`PLAN_STAGE6` §8 lists item 10 as *"no — reuses grid output, no new runs"*, and `MEMO_G6_HANDOFF`
§7 records it as *"unblocked, no new runs"*. Both regressors are indeed on every item-8a row.
**The response is not.** §2.3 defines it as *"the Ehrenfest-minus-cyclic quality difference already
produced by the geometry section"*; item 8a has no cyclic arm, and the two [G6-N1] cells built
specifically to break the `B_c`/`KL` confound were added to the Stage-6 grid, where there is no
cyclic arm either. Reading out on Stage 5 alone would regress on four targets whose `B_c` and `KL`
order them identically — the two-point design `REPORT_S6_ITEM5` §4.1 rebuilt the grid to avoid.

**So the contrast was run here, with the Stage-5 estimator unchanged.**
`test_the_readout_reproduces_the_stage5_cell_exactly` builds one cell both ways and requires float
equality on `tv_learned`, `tv_exact_ctrl`, `tv_uncontrolled`, so this is the Stage-5 measurement
with more cells in it, not a second implementation whose agreement is hoped for. The deviation is
declared on the artefact (`deviation` field) and its cost is measured: **1,518 s wall, 127,367 CPU-s.**

Design: 13 targets × `S ∈ {32, 64, 128, 256}` × {ehrenfest, cyclic} × {pi_ref, uniform} × 5 seeds,
minus the [G6-N1] pair below `S = 32` (inadmissible — `REPORT_S6_ITEM5` §4.2 measured that the
design *inverts* there, PI-15). `advantage = tv_cyclic − tv_ehrenfest`, so **positive = Ehrenfest
better**.

**Operational note, recorded because it changes the cost line.** The first launch put 90 worker
processes on 96 cores with BLAS threading left at default: 99 threads per worker, ~8,900 runnable
threads, load average 8,274, and **0 of 1,040 cells completed in 11.7 min**. Pinning
`OMP/MKL/OPENBLAS/NUMEXPR_NUM_THREADS=1` and relaunching finished the same grid in 25.3 min. Any
future re-run of this module must pin the thread count.

---

## 2. What failed, and where

| | count | where |
|---|---|---|
| **hard failures** | **20** | `tf_c_poisson \| S256`, both arms, both `p0`, all 5 seeds — `ValueError: the target law has a state of probability 0 -- log Φ* would be inf`. Symmetric across geometry; see `MEMO_S6_ITEM8A_POISSON_S256` |
| **divergences** | **92** | **all on the Ehrenfest arm**: 76 at `S = 256`, **16 at `S = 128`**. `TV ~ 1e16`–`1e20` against a quantity bounded by 1 |
| **pairs broken by divergence** | 92 of 510 | the cyclic arm of the same cell returns a finite number every time |

The divergence is a property of the **Stage-5 potential fit at `nfe = 16`**, which was only ever
exercised at `S ∈ {16, 64}` — not of either geometry. But it **lands on one geometry and not the
other**, so it cannot be dropped cell-by-cell: *discarding Ehrenfest's worst cells is exactly how
one manufactures an Ehrenfest advantage.* The module therefore excludes `S = 256` **as a whole
size** and fits on `S ∈ {32, 64, 128}`.

**§4 is about the 16 divergences that rule did not catch.**

---

## 3. The fit, exactly as the pre-registered rule computes it

Primary statistic Spearman (invariant to the monotone transform of `B_c` and `KL` that §2.3 does
not fix and that spans twelve decades); joint standardised fit on `log B_2` and `log KL`; 95 %
bootstrap CIs resampled **over targets**, since seeds within a target are not independent evidence
about a mechanism.

| `p0` | set | n | `s_B` | `s_KL` | `R²_joint` | joint `B` | joint `KL` |
|---|---|---|---|---|---|---|---|
| pi_ref | all | 39 | −0.061 | −0.238 | 0.104 | −0.007 [−0.274, +0.277] | **−0.319 [−0.561, −0.088]** |
| pi_ref | no [G6-N1] | 33 | −0.031 | −0.282 | 0.122 | +0.115 [−0.189, +0.404] | **−0.413 [−0.637, −0.187]** |
| uniform | all | 38 | −0.067 | −0.159 | 0.069 | +0.122 [−0.278, +0.409] | **−0.299 [−0.549, −0.033]** |
| uniform | no [G6-N1] | 32 | −0.046 | −0.241 | 0.105 | +0.272 [−0.233, +0.599] | **−0.424 [−0.705, −0.107]** |

`verdict()` returns `KL_to_binomial` on both modes: KL's interval excludes zero, `B_2`'s does not.
The abort condition does not fire. Dropping the [G6-N1] pair *strengthens* KL, so the outcome is
not an artefact of the two new cells; what the pair does is break the confound it was built to
break (VIF 1.73 → 1.31).

**The sign is the direction M2 registered.** §2.3: *"the advantage tracks a divergence between the
target and `Bin(S,½)`"*, with Ehrenfest's stationary law being `Bin(S,½)` — closer target, less
work. A negative coefficient on `KL` says exactly that. So this is not a sign inversion against the
registered mechanism.

**It is, however, a sign inversion against the observation the sub-study exists to explain.** §2.3
anticipated this in one line: *"If the advantage were stationary-law match, negbin — the target
where the advantage was observed — is the target where it should be smallest."* Measured, at the
two sizes that carry no divergence:

| cell | `B_2` | `KL` | advantage |
|---|---|---|---|
| `tf_c_negbin \| S32` | 0.593 | 13.66 | **+0.0252** |
| `tf_c_negbin \| S64` | 0.593 | 34.07 | **+0.0245** |

The highest-`KL` cells in the design show the **largest positive** Ehrenfest advantage. M2's own
prediction for negbin is contradicted by the cell M2 was invoked to explain, while the pooled
regression that "confirms" M2 gets its slope from elsewhere.

---

## 4. Why the verdict should not be accepted as it stands

### 4.1 The sign of both regressors flips with `S`

| `p0` | subset | n | `s_B` | `s_KL` | mean advantage |
|---|---|---|---|---|---|
| pi_ref | `S ≤ 128` (**as fit**) | 39 | −0.061 | **−0.238** | −0.0039 |
| pi_ref | `S ≤ 64` | 26 | **+0.229** | **+0.280** | +0.0021 |
| pi_ref | `S = 128` only | 13 | **−0.703** | **−0.758** | −0.0161 |
| uniform | `S ≤ 128` (**as fit**) | 38 | −0.067 | −0.159 | −0.0096 |
| uniform | `S ≤ 64` | 26 | **+0.240** | **+0.253** | +0.0007 |
| uniform | `S = 128` only | 12 | **−0.559** | **−0.741** | −0.0319 |

The pooled negative slope that the verdict rests on **does not exist at `S ≤ 64`**, where both
regressors point the other way. It is produced by the 13-point `S = 128` block, in which `B_2` and
`KL` are *both* strongly negative and mutually correlated — i.e. the one block where the design
cannot discriminate the two mechanisms at all.

### 4.2 `S = 128` is the block with the unhandled survivorship

The whole-size exclusion rule was applied to `S = 256` because divergence there is
geometry-asymmetric. **The same asymmetry is present at `S = 128`: 16 divergences, all Ehrenfest,
0 cyclic.** They were dropped per-cell, which is the operation the module's own docstring names as
the way to manufacture a geometry advantage — here running in the opposite direction, since it is
the *Ehrenfest* cells that vanish. Two `S = 128` points also enter the fit with fewer than the
declared 5 seeds and equal weight:

- `tf_c_schloegl | S128` — **n_seeds = 1**, advantage `−0.0797`, `sd` undefined
- `tf_b_J2.0_h0.05 | S128` — n_seeds = 4, advantage `−0.0273`

Those two points are among the most negative in the design and sit in the block that produces the
verdict.

### 4.3 Two cells with the same regressors and opposite responses

`B_c` and `KL` cannot both be the mechanism, and this pair suggests neither is:

| cell | `B_2` | `KL` | advantage |
|---|---|---|---|
| `cw_J2_h0 \| S32` | 0.934 | 17.71 | **−0.0436** (cyclic better) |
| `tf_b_J2.0_h0.05 \| S32` | 0.947 | 18.53 | **+0.0306** (Ehrenfest better) |

Nearly identical on both regressors; the responses differ by 0.074, which is **19× the pooled mean
advantage** and larger than any fitted effect in §3. Whatever separates these two cells is not in
either regressor.

### 4.4 The effect being explained is close to zero

Over the 374 usable fit pairs, mean advantage `−0.0040` and **50.5 % of pairs favour Ehrenfest**.
Per-target means at `S ≤ 128` run from `−0.0347` (`tf_b_J1.2_h0.05`) to `+0.0128`
(`tf_b_J2.0_h0.05`) with the middle nine targets inside `±0.006`. `R²_joint ≤ 0.104`.

---

## 5. What is solid

- The run is complete, reproducible, and the estimator is the Stage-5 one at float equality.
- The [G6-N1] pair does what it was built to do: VIF `1.73 → 1.31`, `corr` `0.648 → 0.487`. The
  confound §2.3 was designed to break is broken, and this is the first place in the project where
  `B_c` and `KL` are separable at all.
- **M1 (the PI's prior) is not supported anywhere in this design.** `B_2`'s interval contains zero
  in all four fits, and the two cells built as M1's decisive test go the wrong way for it:
  `g6n1_shifted_binomial` (light tails, high boundary mass — M1 says the advantage appears) reads
  `−0.0053 / +0.0040 / +0.0028` across sizes, and `g6n1_interior_heavy` (heavy tails, low boundary
  mass — M1 says it disappears) reads `+0.0026 / −0.0003 / +0.0038`. Both are inside their own seed
  noise. That is a clean negative on M1 and does not depend on §4's objection.
- The `S = 256` divergence is documented per geometry rather than asserted small, and the whole-size
  exclusion is the conservative choice.

---

## 6. What I need the PI to rule on

1. **Does the `S = 128` block get the `S = 256` treatment?** 16 Ehrenfest-only divergences plus two
   under-seeded points sit inside the fit. Applying the module's own whole-size rule leaves
   `S ∈ {32, 64}`, where both regressors are **positive** and neither interval will exclude zero —
   i.e. the outcome becomes **"neither discriminated"** and §7's abort fires: *report descriptively
   and stop.* My reading is that consistency requires this. It is a change of outcome, not of
   emphasis, so I have not made it unilaterally.

2. **Is `KL_to_binomial` reportable when M2's own registered prediction fails on negbin?** §2.3
   says M2 predicts the advantage is *"absent on negbin"*; negbin has the design's highest `KL` and
   its second-largest positive advantage. The regression and the mechanism's own point prediction
   disagree, and `verdict()` only tests whether the interval excludes zero — it never checks the
   sign or the named cell.

3. **Does the run itself need re-doing at a stable estimator before any of this is read?** The
   divergence is a property of the Stage-5 potential fit at `nfe = 16`, not of a geometry. A larger
   `nfe` (or a guarded fit) at `S ∈ {128, 256}` would remove the survivorship question at its
   source and cost roughly the same 25 min. Everything in §4 is downstream of that one defect.

Until 1–3 are ruled on, **no claim from this item should enter `CLAIMS.md`**, and R6 should carry
the descriptive tables of §3–§5 without the verdict string.
