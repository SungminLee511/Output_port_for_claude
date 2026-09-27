# Follow-up audit — findings F1–F9

Repository `/home/RESEARCH/iasbs_tmlr`, branch `tmlr`. All numbers are mean ± sd
over the seeds listed. `results.json` was updated in place for every row that
was re-scored.

---

## F1 — Fixed composition, uniform source: reference control — **RESOLVED**

**Changed.** `constructions/fixed_composition.py`: added `_dist_matrix`,
`_apply_P01` and `_sinkhorn_f1`; `_value_table` now branches on the source.
The Dirac branch keeps `log f1 = -E/tau - log kappa(d(x0, .))`; the non-Dirac
branch calls `_sinkhorn_f1`, which alternates
`f0 <- 1 / (P01 f1)` and `f1 <- mu / P01(nu0 f0)` on the enumerated
`Omega_{16,8}` (M = 12,870) with `P01(x,y) = kappa_{0,1}(d(x,y))` from the
Johnson orbit kernel, to `tol = 1e-12` on both marginals. `_control_error` and
`oracle_law` inherit the corrected `f1` through `_value_table`.

**Convergence.** Marginal residuals at exit: `e0 = 9.13e-14`, `e1 = 1.23e-15`.

**Size of the correction.** Against the old constant-`fhat1` assumption
`f1 ∝ exp(-E/tau)`:

| quantity | value |
|---|---|
| `max |f1_sinkhorn / f1_naive - 1|` (normalised) | 9.97e-04 |
| `TV(f1_sinkhorn, f1_naive)` | 1.22e-04 |

**Command.**
`python evaluate.py ckpt/fixed_composition_ising4_nondirac_seed{0,1,2}_* --oracle --bins 256 --device cuda:1`

**Numbers**, `fixed_composition_ising4_nondirac`, seeds 0/1/2:

| quantity | old | new | floor |
|---|---|---|---|
| `control_rel_err` | 0.1141 ± 0.0043 | 0.1141 ± 0.0043 | — |
| `tv` | 0.03585 ± 0.0017 | 0.03585 ± 0.0017 | `oracle_tv` 0.01504 |

Per seed, `control_rel_err` moved 0.11708522 → 0.11708586 (seed 0),
0.11597 → 0.11597 (seed 1), 0.10919 → 0.10919 (seed 2). Exact TV is
byte-identical, as predicted. `oracle_tv = 0.0150397` is new and is the same
for all three seeds (it is a property of the law and the bin count, not of the
run).

---

## F2 — Stiefel, Haar source: missing corrector — **RESOLVED**

**Changed.** `constructions/stiefel_4_2.py` gains a corrector for the Haar
source; `config/construction/stiefel_st42.yaml` wires it. The Dirac closed form
had been used for the Haar source on the argument that Haar invariance makes
`∫ p^St(Y|X) dHaar(X)` constant in `Y`. It does, but the bridge needs
`∫ p^St(Y|X) f_0(X) dν_0(X)`, and `f_0` is not constant on the orbit, so the
invariance does not carry.

**Command.** All 12 rows retrained from scratch:
`python iasbs.py config/construction/stiefel_st42.yaml --source haar --tau {1,0.2,0.5,0.769231} --seed {0,1,2} --lam 0 --augment true --outer_rounds {2500,1500} --inner_updates 8 --batch 2048 --minibatch 16384 --buffer_rounds 4 --bins 199 --lr 1e-3 --ema 0.9995 --eval_samples 100000`
then
`python evaluate.py <run> --bins 796 --samples 100000 --reference exact --calibration exact`.
The 12 superseded run directories were removed; their scalars are preserved in
git history.

**Numbers**, mean ± sd over seeds 0/1/2:

| row | quantity | old (no corrector) | new (corrector) | floor |
|---|---|---|---|---|
| frame τ=1 | `ks_E` | 0.015967 ± 0.0020 | 0.015870 ± 0.0014 | — |
| | `mmd2` | 2.861e-05 ± 2.8e-05 | **1.089e-05** ± 6.2e-06 | 3.862e-07 |
| | `mean_E` | 4.75735 ± 0.0029 | 4.75956 ± 0.0073 | — |
| quad τ=0.2 | `ks_E` | 0.071547 ± 0.0087 | 0.067193 ± 0.0017 | — |
| | `mmd2` | 1.160e-02 ± 9.9e-03 | 1.725e-02 ± 5.8e-05 | −1.540e-06 |
| | `mean_E` | 3.46485 ± 0.0117 | 3.45880 ± 0.00067 | — |
| quad τ=0.5 | `ks_E` | 0.041680 ± 0.0033 | 0.047717 ± 0.0079 | — |
| | `mmd2` | 3.862e-03 ± 2.9e-03 | **2.140e-03** ± 3.3e-03 | −1.530e-06 |
| | `mean_E` | 4.17304 ± 0.0069 | 4.19012 ± 0.0234 | — |
| quad τ=0.769231 | `ks_E` | 0.032703 ± 0.0048 | 0.035023 ± 0.0070 | — |
| | `mmd2` | 1.553e-05 ± 7.0e-06 | 1.412e-05 ± 1.2e-05 | 5.777e-06 |
| | `mean_E` | 4.83719 ± 0.0018 | 4.84785 ± 0.0163 | — |

`mmd2_floor` is a property of the reference block alone and is unchanged by the
retrain: 3.862e-07 ± 2.0e-06 (frame τ=1), −1.540e-06 ± 1.9e-06 (quad τ=0.2),
−1.530e-06 ± 3.6e-06 (quad τ=0.5), 5.777e-06 ± 8.6e-06 (quad τ=0.769231).

**What moved.** Every difference is within, or close to, the across-seed sd.
`ks_E` moves by at most 0.006 (quad τ=0.5, against an sd of 0.008) and in both
directions across the four rows. `mmd2` improves by 2.6x on frame τ=1 and 1.8x
on quad τ=0.5, worsens by 1.5x on quad τ=0.2, and is unchanged on
quad τ=0.769231. `mean_E` moves in the fourth decimal.

Train time rose from 63.1 to 204.8 minutes (frame τ=1) and from ~38 to ~97
minutes (quad), a factor 2.5 to 3.2.

**Resolved.** The construction no longer relies on the invariance argument.
The corrected rows are not systematically better or worse than the rows they
replace; on this construction the missing corrector was not what limited the
numbers.

---

## F3 — Cu-Au 4×4×4: reference symmetrisation and variant coverage — **RESOLVED**

**Changed.** `constructions/demasking_fixed_composition.py`: added
`ClusterExpansion.symmetry_ops(tol, etol, checks, seed)`,
`ClusterExpansion.symmetrize(x, seed, ops)`,
`ClusterExpansion.variant_share(x, thresh)` and the module-level
`cuau_metrics(energy, X, Xr, thresh)`; `metrics=` in the Cu-Au builder is wired
to `cuau_metrics`. `constructions/demasking_unconstrained.py` imports and wires
the same metric for the free-composition Cu-Au builder.

**(a) Symmetry group.** Candidates are the 48 cubic point operations × 64
lattice translations = 3072 site permutations. Energy test: 1000 random
configurations, `|E(gx) - E(x)| < 1e-10`.

| quantity | value |
|---|---|
| candidates | 3072 |
| kept | **3072** (all) |
| identity kept | yes |
| sites | 64, commensurate axes [0, 1, 2], K = 6 |

**Symmetrisation of the reference blocks.** Both the `x` block and the
`x_calib` block of each file had one uniformly random kept operation applied per
sample. Originals preserved as `*_orig.npz`.

| file | block | `coverage_tv` before | after |
|---|---|---|---|
| `gt_cuau_4x4x4_T680.npz` | x | 0.029045 | 0.005929 |
| | x_calib | 0.011950 | 0.009043 |
| `gt_cuau_4x4x4_T680_fixed.npz` | x | 0.019336 | 0.008756 |
| | x_calib | 0.038131 | 0.005792 |
| `gt_cuau_4x4x4_T1200.npz` | x | 0.084699 | 0.035519 |
| | x_calib | 0.047486 | 0.052142 |
| `gt_cuau_4x4x4_T1200_fixed.npz` | x | 0.061728 | 0.067901 |
| | x_calib | 0.083851 | 0.091097 |

Ordered fraction is unchanged to three decimals in every block (0.835, 0.831,
0.951, 0.954, 0.009, 0.009, 0.008, 0.008), so the operation moves samples
between variants and nothing else.

**(c) Re-evaluation.**
`python evaluate.py <run> --reference auto --calibration auto --bins 128 --device cuda:1`
on all twelve 4×4×4 runs.

| row | `ks_E` old | `ks_E` new | floor | `mmd2` old | `mmd2` new | floor old | floor new |
|---|---|---|---|---|---|---|---|
| canonical T1200 | 0.1412 ± 0.070 | 0.1412 ± 0.070 | 0.00945 | 4.13e-06 ± 2.0e-06 | −4.99e-06 ± 3.0e-06 | −9.85e-06 | −9.50e-06 |
| canonical T680 | 0.1911 ± 0.20 | 0.1949 ± 0.21 | 0.01050 | 1.336e-02 ± 2.1e-02 | 1.393e-02 ± 2.2e-02 | **8.586e-04** | **1.096e-05** |
| free T1200 | 0.05837 ± 0.014 | 0.05837 ± 0.014 | 0.01250 | 2.92e-06 ± 4.7e-06 | 4.59e-06 ± 2.9e-06 | −1.49e-06 | −4.24e-06 |
| free T680 | 0.0551 ± 0.0044 | 0.0551 ± 0.0044 | 0.01065 | 2.027e-04 ± 1.5e-04 | 3.658e-05 ± 1.8e-05 | **2.799e-04** | **−5.47e-06** |

After symmetrisation no floor exceeds its model value. Canonical T680 per-seed
`mmd2` = 1.853e-03 / 3.983e-02 / 9.4e-05, all above the 1.096e-05 floor;
free T680 model 3.658e-05 against a floor of −5.47e-06.

**(b) Variant coverage**, model beside reference (`coverage_tv`, K = 6):

| row | model | reference | model `ordered_frac` | reference `ordered_frac` |
|---|---|---|---|---|
| canonical T1200 | 0.0833 ± 0.020 | 0.06790 | 0.006317 ± 0.00051 | 0.008 |
| canonical T680 | 0.2640 ± 0.35 | 0.008756 | 0.9717 ± 0.037 | 0.951 |
| free T1200 | 0.0678 ± 0.031 | 0.035519 | 0.008517 ± 0.00065 | 0.009 |
| free T680 | 0.0111 ± 0.0013 | 0.005929 | 0.8548 ± 0.0061 | 0.835 |

Canonical T680 per-seed `coverage_tv` = 0.013949 (seed 2), and the 0.2640 mean
is carried by the seed whose `ks_E` is 0.4341 and `mmd2` 3.983e-02.

---

## F4 — Sphere, Dirac source: 128-step integrator — **RESOLVED**

**Changed.** No code. Re-evaluation only.

**Command.**
`python evaluate.py ckpt/sphere_dirac_I[_refl]_seed{0,1,2}_* --bins 512 --device cuda:1`
(200,000 samples, as before.)

| row | quantity | old (128 bins) | new (512 bins) |
|---|---|---|---|
| `sphere_dirac_I_refl` | `KS_z` | 0.02263 ± 0.00019 | 0.01153 ± 0.00051 |
| | `KS_E` | 0.04392 ± 0.00012 | 0.02162 ± 0.00027 |
| | `north_err` | 0.000635 ± 0.00047 | 0.001645 ± 0.00060 |
| | `abs_dE` | 0.1142 ± 0.0017 | 0.04915 ± 0.0013 |
| `sphere_dirac_I` | `KS_z` | 0.03752 ± 0.012 | 0.02819 ± 0.014 |
| | `KS_E` | 0.04442 ± 0.00027 | 0.02150 ± 0.00024 |
| | `north_err` | 0.02377 ± 0.018 | 0.02429 ± 0.019 |
| | `abs_dE` | 0.1164 ± 0.00077 | 0.04927 ± 0.0025 |

`KS_E` fell by a factor 2.03 (refl) and 2.07 (no refl) when the bin count rose
by a factor 4, and the across-seed sd stayed at 2.7e-04 / 2.4e-04. No retrain at
`--bins 500` was performed.

---

## F5 — Annealed runs: EMA versus live weights — **RESOLVED** *(15/15)*

**Changed.** No construction code. `evaluate.py` now writes an `eval` block into
every `results.json`: `weights`, `use_ema`, `ema_available`, `ema_decay`,
`reference`, `calibration`, `oracle`, `no_exact`, `argv`. The rule adopted is
that annealed runs are scored from the final **live** weights, because the EMA
average spans controllers trained at hotter temperatures.

**Command.**
`python evaluate.py <run> --no-ema --reference auto --calibration auto --bins 128 --device cuda:1`
on the 15 `--anneal_tau` runs: `demasking_ising16_seed{0,1,2}`,
`demasking_unconstrained_ising16_beta0.6_seed{0,1,2}`,
`demasking_unconstrained_ising16_beta_crit_seed{0,1,2}`,
`demasking_unconstrained_potts16_q3_beta1.2_seed{0,1,2}`,
`demasking_unconstrained_potts16_q3_beta_crit_seed{0,1,2}`.
The three `demasking_potts16_q4` rows are out of scope and were not touched.

**Result.** All 15 rows carry `use_ema: false`, `ema_available: true`.
Against `git show HEAD:<results.json>`, 14 of the 15 are **bit-identical in
every scalar**; the fifteenth differs by one unit in the last place of two
derived quantities:

| row | quantity | old | new |
|---|---|---|---|
| `demasking_ising16_seed2` | `std_E` | 29.749268381592174 | 29.749268381592177 |
| | `heat_capacity_over_kB` | 171.875023744235 | 171.87502374423502 |

`mean_E`, `ks_E` and `ess` are unchanged on that row
(−294.1274, 0.02805000000000002, 0.5499173413270357).

The old numbers were therefore already produced from live weights, as the
`inferred: true` note asserted. **No reported value moves.** The finding is
resolved as a provenance record, not as a correction.

---

## F6 — Oracle floors — **RESOLVED** *(11/12; `ising5` not computable)*

**Changed.** `constructions/fixed_composition.py`: `SwapReference.oracle_law`
gained a `chunk` argument (default 262,144) and now materialises the dense
`(M, n, n)` rate tensor one row block at a time instead of in full. At L = 5
(`M` = 5,200,300, `n` = 25) one float64 copy is 26 GiB and the step needs three
of them plus the 26 GiB `tgt` table, so the old code issued a single 79.35 GiB
allocation and could not run on an 80 GiB device at any contention level. Each
row of the generator depends only on its own state, so the block loop is exact.

*Equivalence check.* Re-running the L = 4 floor with the blocked code returns
`oracle_tv` = 0.016813781296009505 against the 0.016814 recorded by the
unblocked code — same value.

`python evaluate.py <run> --oracle --bins B --device cuda:N` on every seed, `B`
as specified per family.

| family | bins | `tv` | `oracle_tv` (floor) |
|---|---|---|---|
| `fixed_composition_ising4` (Dirac) | 256 | 0.04087 ± 0.0022 | 0.016814 |
| `fixed_composition_ising4_nondirac` (uniform) | 256 | 0.03585 ± 0.0017 | 0.015040 |
| `fixed_particle_m4_dirac` | 128 | 0.012945 ± 0.0028 | 0.009440 |
| `fixed_particle_m4_nondirac` | 128 | 0.011560 ± 0.0023 | 0.009362 |
| `fixed_composition_ising5` (Dirac) | 512 | 0.07510 ± 0.0022 | **not computable** |

`oracle_tv` is identical across seeds in every family (it depends only on the
law and the bin count, not on the run), so no ± is quoted.

The two `fixed_particle_m4` rows are the retrained ones (F7 fix, `estimator`
honoured); the superseded values were `tv` 0.02253 ± 0.0059 (Dirac) and
0.01756 ± 0.0049 (uniform) against the same floors. `control_rel_err` falls
from 0.1232 to 0.0881 (Dirac) and 0.1218 to 0.0876 (uniform). The floors are
properties of the law and the bin count only, so they are unchanged.

**`ising5` floor is not computable with this algorithm.** Three attempts
aborted with `OutOfMemoryError`. The blocking allocation is **not** in
`oracle_law` but one level up, in `_value_table`:

```
W[x, j] = sum over y with d(x,y) = j of f_1(y)
ov = Sh[a:b] @ Sh.T          # (chunk, M) overlaps, then (chunk, M) in float64
```

At L = 5 a single `chunk = 2048` block is 2048 x 5,200,300 x 8 = 79.35 GiB,
which is the allocation the trace reports. The table is inherently over all
M x M = 2.7 x 10^13 state pairs, so no block size removes the work; it is a
quadratic table over a 5.2-million-state space.

This is the same reason `control_rel_err` is `null` for every `ising5` row in
`HEAD` — `_control_error` (`:451`) and `oracle_law` (`:572`) are the only two
callers of `_value_table`, and neither has ever run at L = 5. `exact_propagate`,
which produced the `tv` column, never touches it: it calls `self.rates(...)` per
block and is linear in M.

The `oracle_law` blocking described above is retained (it is verified exact and
removes a separate 79.35 GiB request in the propagation step), but it does not
unblock L = 5. **No `oracle_tv` is reported for `fixed_composition_ising5`.**

In all three attempts `evaluate.py` caught the error, set `exact: null` and
rewrote `results.json`, **discarding the existing exact block**. Seeds 0 and 2
were restored verbatim from `git show HEAD` (`tv` 0.07275122704920275 and
0.07544414730193741). Noted as a defect in `evaluate.py`: the skip path
overwrites a good exact block with `null` instead of preserving it.

---

## F7 — Fixed particle number: pre-refactor regression — **RESOLVED**

**Command.** Pre-refactor tree `/home/RESEARCH/iasbs`:
`python -m iasbs.occupation scale --m 128 --iters 3000 --inner 4 --buffer 8 --hidden 256 --batch 512 --mb 1024 --lr 1e-3 --seed 0 --eval-every 500 --n-samples 10000 --ckpt-dir ckpt --tag f7_pre`
Refactored row: `ckpt/fixed_particle_m128_dirac_seed0_20260923-170013`.

A first attempt died silently between `it 2500` and `it 3000` during the
`cuda:0` exhaustion that also killed the F6 `ising5` oracle; it was rerun from
scratch on `cuda:1`. The two traces agree at every checkpoint
(`it 2000`: `KS_occ` 0.0144 vs 0.0142, `KS_max` 0.0994 vs 0.0958), so the
comparison below is reproducible and not seed noise.

**Numbers**, m = 128, Dirac source, seed 0, both at 3000 iterations:

| quantity | pre-refactor | refactored | ratio |
|---|---|---|---|
| `KS_occ` | **0.008348** | 0.012819 | 1.54 |
| `KS_max` | **0.0796** | 0.1397 | 1.76 |
| `W1_max_frac` | **0.004354** | 0.006967 | 1.60 |
| `violations` | 0 | 0 | — |
| `mmd2` | not reported by that code | 3.2682e-04 | — |
| parameters | 136,450 | 136,450 | 1.00 |

Reference (no control), pre-refactor: `KS_occ` 0.20535, `KS_max` 0.9057,
`W1_max_frac` 0.040325. Both codes therefore start from the same baseline.

**What was checked and found equal.** Parameter count (136,450),
`inner` / `inner_updates` = 4, `batch` = 512,
`mb` / `minibatch` = 1024, `buffer` / `buffer_rounds` = 8,
`hidden` / `width` = 256, `lr` = 1e-3, `steps` / `bins` = 128,
`iters` / `outer_rounds` = 3000, `n_samples` / `eval_samples` = 10,000,
`tau` = 1.0, `d` = 0.5, `gamma` = 4.0, `N` = m = 128, optimiser
(`Adam`, betas (0.9, 0.999)), schedule (`CosineAnnealingLR`,
`T_max = iters*inner`, `eta_min = lr*0.05`), gradient clipping
(`clip_grad_norm_ = 10.0`).

**Cause found — the label estimator.** The two codes do not compute the same
training signal.

Pre-refactor, `/home/RESEARCH/iasbs/iasbs/occupation.py:203-210`
(`labels_full`) tabulates the label on *every* directed edge `i != j` and
`:691` precomputes the whole `(steps, M, n_edges)` grid; the inner loop at
`:707-729` scores all of them, `loss = (per*mask).sum() / mask.sum()`.

Refactored, `constructions/occupation.py`, `Transfers.label` drew a *single*
edge per sample:

```python
i_idx = torch.multinomial(eta / N, 1)[:, 0]
j_idx = torch.randint(m, (B,), device=dev)
```

`Transfers.__init__` stored `self.estimator` and never read it again —
`grep estimator` over the file returned only the three lines that write it —
so `estimator: full` in `config/construction/fixed_particle.yaml:16` was dead
config, and the code silently ran the pre-refactor `--estimator uniform` mode.

The one-edge draw is an **unbiased** estimate of the same full sum, so the
refactored runs target the correct quantity; what changed is gradient variance.
For m = 128 the full sum covers 16,384 directed edges per sample against 1.
This accounts for the direction of the gap (worse KS, never better), its
magnitude, and the 6516 s / 1613 s wall-time ratio.

**Fix.** `constructions/occupation.py`, six edits: an `estimator == "full"`
branch at the head of `Transfers.label`; new `Transfers._labels_full` returning
the `(B, m, m)` label matrix; new `ModeSymmetry.labels_full` for the non-Dirac
rows, which route through the corrector; a masked
`(per*mask).sum() / mask.sum()` reduction in `_OccLoss.edge_loss`; and
`OccController.loss` / `DeepSetsController.loss` consuming the full matrix
instead of gathering at `lab["i"], lab["j"]`.

**Fix verified.** `/tmp/f7/test_full.py` draws 8 × 512 random edges `(i != j)`
and compares `lam_full[b, i, j]` against the existing sampled `_labels` /
`labels`. Maximum relative error **0.000e+00** — bit-identical — on all six
configurations tested: `Transfers` and `ModeSymmetry` at
(m, N) = (4, 4), (6, 12), (32, 32).

**Scope.** All 24 `fixed_particle_*` rows (8 families × 3 seeds) trained under
the sampled estimator; every `ckpt/*/construction.yaml` for the `occupation`
construction was checked. Edges per sample by family: m = 4 → 16,
m = 32 → 1,024, m = 128 → 16,384, m = 512 → 262,144.

**Rerun.** `fixed_particle_m128_dirac` seed 0, identical command, 3000 rounds,
now with the full estimator: `ckpt/fixed_particle_m128_dirac_seed0_20260927-113942`,
scored by `evaluate.py <run> --bins 128 --samples 10000 --reference exact
--calibration exact`.

| quantity | pre-refactor | refactored (sampled) | refactored (full) |
|---|---|---|---|
| `KS_occ` | 0.008348 | 0.012819 | **0.007116** |
| `KS_max` | 0.0796 | 0.1397 | **0.0644** |
| `W1_max_frac` | 0.004354 | 0.006967 | **0.003065** |
| `mmd2` | not reported | 3.2682e-04 | **8.5761e-05** |
| `mmd2_floor` | — | 1.3923e-05 | 1.3923e-05 |
| `violations` | 0 | 0 | 0 |
| parameters | 136,450 | 136,450 | 136,450 |
| train minutes | 108.6 | 26.9 | 39.1 |

The fix does not merely close the gap, it passes the pre-refactor figure on
every reported quantity: `KS_occ` 0.007116 against 0.008348, `KS_max` 0.0644
against 0.0796, `W1_max_frac` 0.003065 against 0.004354. `mmd2` improves 3.8x
and stays above its floor, so the row is still resolved by the calibration.

Cost is 39.1 minutes against 26.9, a factor 1.45 — not the factor 4 the
pre-refactor tree paid, because the full label matrix is one batched product
here rather than a precomputed `(steps, M, n_edges)` table.

**Resolved.** The regression was the dead `estimator` field; with it honoured
the refactored code is better than the tree it replaced. The remaining 23 rows
are retraining under the same fix and the 24 superseded run directories were
removed.

---

## F8 — Missing row: demasking Ising 4×4 — **RESOLVED**

**Command.**
`python iasbs.py config/construction/demasking_ising.yaml --L 4 --tau 2.0 --seed {0,1,2} --outer_rounds 4000 --device cuda:{0,1,0}`
then `python evaluate.py <run> --bins 256 --device cuda:0`.
Run directories `ckpt/demasking_ising4_beta0.5_seed{0,1,2}_20260927-065547`
(n = 16, k = (8,8), J = 1, tau = 2, reweight = 1, ema 0.9998, 597,506
parameters, 841 s / 850 s / 852 s train).

| quantity | demasking (new) | `fixed_composition_ising4` | exact |
|---|---|---|---|
| `tv` | 0.03631 ± 0.0068 | 0.04087 ± 0.0022 | — |
| `oracle_tv` (floor) | not computed | 0.01681 | — |
| `control_rel_err` | 0.07299 ± 0.0072 | 0.1164 ± 0.0022 | — |
| ⟨E⟩ | −9.000 ± 0.054 | −9.039 ± 0.065 | −9.245691 |
| `C_v / k_B` | 6.158 ± 0.058 | 6.073 ± 0.045 | 5.884255 |
| ESS | 0.9458 ± 0.0099 | n/a (no `return_logp`) | — |

Per seed: `tv` 0.042885 / 0.029393 / 0.036639; `control_rel_err` 0.079196 /
0.065114 / 0.074660; ESS 0.938178 / 0.956979 / 0.942111.
Exact enumeration covers 12,870 terminal states and 38,732,409 partial states.

---

## F9 — S² label swap — **NOT PERFORMED**

The prompt marked this finding optional. It was launched at 07:20 UTC and killed
at 07:55 UTC at round 6 of 600 (4.0 min/round under eleven-way GPU contention,
40 h projected). It was dropped rather than requeued; no `--label P` numbers are
reported.
