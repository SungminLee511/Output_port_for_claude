# QDASBS-001 — G6 gate handoff

**From:** Executor
**To:** PI
**Status:** halted at gate **G6** after Stage-6 item **8a**. Two rulings are requested; five items
(9–14) remain and three of them are blocked or reshaped by what 8a measured.
**Repo:** `voltwin-dev/test`, subdirectory `qdasbs`, commit `fbe0ae6`.
**Read-out of record:** `reports/REPORT_S6_ITEM8A.md`, generated from
`runs/stage6/grid/s6_item8a_grid.json` by `experiments/stage6/analyze_grid.py`.

---

## 0. The one-paragraph version

The declared 3,700-cell instrument-group grid ran to completion. The headline arm **P1
(Q-DASBS)** beats the two DM-family baselines **P2** and **P3** at every size with every paired
95 % CI disjoint from zero — and **loses to P4, weight-shared bit-DASBS, at `S ∈ {64,128,256}`
while P4 is simultaneously 43.3× cheaper there.** P4 is the opponent `PLAN_STAGE6` §5 says decides
the contribution, so the gate's own logic makes this the finding that matters. It is **not
attributable to the integrator or the state space**, because P1 carries 1,697 parameters against
P4's 19,073 and §1 forbids attributing a gap to capacity. Separately, three of the four cost and
quality columns the gate expected to use are **withdrawn on measurement** rather than cited. Nothing
here is a verdict; `g6_verdict()` is item 13.

---

## 1. What ran

| | |
|---|---|
| declared cells | **3,700** = 74 target-size cells × 5 seeds × the package's `smooth_lambda` levels (2 for P1/P3, 3 for P2/P4) → P1 740, P2 1,110, P3 740, P4 1,110 |
| dispatched | **3,700 / 3,700** |
| good | **3,650** |
| dropped | **50** (§4) |
| horizon | `epochs_run == 40` and `timed_out == False` on **every one of the 3,650** — the 18 h `QDASBS_GRID_MAX_SECONDS` hang guard never fired, so no row claims a horizon it did not reach |
| cost | **27.0 h wall, 2,394 CPU-h, 90 workers** on a 96-core / 866 GB host (**PI-17**: machine named, seconds reported and never asserted) |
| suites | `tests/test_s6_grid.py` (25), `test_s6_run_grid.py` (27), `test_s6_analyze_grid.py` (17); full repo suite **3,152 passed** in 753 s |

The quality axis every comparison below rests on is **deterministic**: `terminal_tv_final` is
`TV(p^u_1, ν)` computed by the T11 macrostep on the **exact** forward product
(`experiments/stage4/problem.terminal_tv`). No particles, no importance weights, no ESS. This is
why §3's collapse of the sampled column does not touch a single paired difference.

---

## 2. The result, and the reason it cannot be read as one

### 2.1 P1 wins against the DM baselines, unambiguously

Paired on `(target, S, seed, smooth_lambda)`; sign convention **positive = the other package has
higher TV**, i.e. positive = P1 better.

| contrast | range over the six sizes | significant |
|---|---|---|
| `P2 − P1` (corr-DM) | `+0.0215 … +0.2506` | **6/6, all CIs disjoint from zero** |
| `P3 − P1` (dense-geometry) | `+0.0523 … +0.1830` | **6/6, all CIs disjoint** |

### 2.2 P1 loses to P4 exactly where the contribution lives

| `S` | `P4 − P1` | who is better |
|---|---|---|
| 8 | `+0.0248` | P1 |
| 16 | `+0.0383` | P1 |
| 32 | `+0.0207` | P1 |
| 64 | **`−0.1182 ± 0.0297`** | **P4** |
| 128 | **`−0.0744 ± 0.0226`** | **P4** |
| 256 | **`−0.0730 ± 0.0189`** | **P4** |

A clean crossover with **both directions significant** — not an overlap, and therefore not
disposable under G5b's convention that a better mean with an overlapping interval asserts nothing.
**And P4 is `43.3×` cheaper at `S = 256`** (118 s vs P1's 5,085 s per cell), so above `S = 32` P4
dominates P1 on **both** of G6 condition (ii)'s axes at once.

### 2.3 …but the loss is confounded, and the confound is capacity

`n_parameters`: **P1 1,697 vs P4 19,073 — 11.2×.** §1 requires any gap be attributed *"to the
integrator or the state space, never to capacity"*, and **this grid cannot meet that.** The
capacity tie the plan cites was struck against P1's *inherited* configuration, which
`S6-P1RESEARCH` / [G6-A2] had already refuted and replaced (paired `+0.17104 ± 0.04624` in P1's
favour for the re-searched config). **The tie is stale.** Re-tying it is a new run, not a re-read of
this artefact.

**→ RULING REQUESTED (R-1).** Three options, and I do not think the choice is mine:

1. **Re-tie and re-run.** Grow P1 to ~19 k parameters (or shrink P4 to ~1.7 k) and re-run the
   `S ∈ {64,128,256}` slice only. Cost: the P1 `S = 256` cell is 5,085 s; that slice at 5 seeds ×
   2 smooth levels × 11 targets is ≈ 200 CPU-h at current capacity, more at 11×. Cheap against the
   2,394 CPU-h already spent, and it is the only option that produces an attributable number.
2. **Report the loss as confounded** and let item 13 read it that way — honest, and leaves G6
   condition (i) undecided against the decisive opponent.
3. **Rule the capacity axis out of scope** for G6 and compare at each package's own selected
   configuration. This is defensible *only* if the gate is about deliverable-at-equal-tuning-budget
   rather than about the integrator — and that is a reinterpretation of §1, so it is a PI call.

---

## 3. Three columns the gate expected, withdrawn on measurement

Each is withdrawn with a number, not a worry.

**(a) The sampled `log Ẑ` column dies for three of four packages.** CI coverage at `S = 256`:

| | P1 | P2 | P3 | P4 |
|---|---|---|---|---|
| `log_z_ci_coverage` | **0.183** | **0.956** | **0.175** | **0.278** |
| `ess_frac` median | **0.02** | 0.23 | **0.00** | **0.05** |

Item 6 constraint (a) pre-registered `ESS_frac ≈ 0.05` as the untrustworthiness floor. P1, P3 and
P4 are **at or below it**. Only P2 survives. No `log Ẑ` number for P1/P3/P4 at `S ≥ 64` is
admissible, and R6 must print `ess_frac` beside any coverage it quotes.

**(b) The memory column is a per-worker artefact, so half of G6 (ii) is unmeasured.**
`peak_rss_kb` comes from `ru_maxrss`, a per-**process** high-water mark, and pool workers are
reused: **94 distinct values across 3,650 rows**, with `peak_rss_delta_kb` either ~13.2 GB (a
worker's first cell) or exactly 0. G6 condition (ii)'s memory half must come from **item 9, run one
cell per process**. A test pins `< 200` distinct values so the claim stays falsifiable.

**(c) `s3_units` is constant in `S`.** P1 reads `1.02e4` at all six sizes while seconds move
`1000×`. It cannot order sizes even *within* a package — the one comparison **PI-18** still
permitted after item 1b withdrew it across packages.

**→ RULING REQUESTED (R-2), minor.** **PI-18** could be tightened to *"`s3_units` is a schedule
descriptor, not a cost axis"*, which is what the measurement says. I have not done this on my own
authority; the read-out currently names the column `s3_units_mean_within_package_only` so no
downstream reader can miss the restriction.

**PI-11, discharged negatively.** `n* = n_steps(S+1)` = **2,193** at `S = 128` and **4,369** at
`S = 256`. **No arm cleared it at either size** — short by `34.3× / 68.3×` (P1, P2),
`8.6× / 17.1×` (P3), `17.1× / 34.1×` (P4). Every cell is in the small-batch regime and is reported
as such.

---

## 4. The 50-cell drop (PI-15: excluded, not repaired)

All 50 failures are `tf_c_poisson` at `S = 256`, all five seeds, failing **deterministically before
training** in `targets.families.nu_from_energy`:

```
ValueError: the target law has a state of probability 0 -- log Phi* would be
infinite there (min nu = 0.000e+00)
```

The Poisson tail underflows `float64`:

| `S` | 8 | 16 | 32 | 64 | 128 | 256 |
|---|---|---|---|---|---|---|
| `min nu` | 1.87e-02 | 3.76e-06 | 1.28e-18 | 4.91e-53 | 5.50e-141 | **0.0** |

The drop is **package-symmetric** (P1 10, P2 15, P3 10, P4 15 — the same *target* leaves every
package, so nobody gains a target its rivals lose) and **seed-complete**. Every failed cell survives
in the artefact as a row with `ok: false` and its traceback, and **every ratio at `S = 256` states
the denominator `n = 73` of 74 targets** rather than dividing by the declared 74.

Not repaired, deliberately: clipping `nu` to a floor or moving `nu_from_energy` to log-space would
change the target law every earlier stage was measured against, **at one size only**. That is a
different experiment. Memo: `reports/MEMO_S6_ITEM8A_POISSON_S256.md`.

---

## 5. Things that needed no ruling, settled by measurement

* **The `DECISION_G5` / [G6-A2] `smooth_lambda` disagreement is immaterial.** 5 of 6 within-package
  contrasts against that package's **own** `0.0` straddle zero. The single significant effect (P2 at
  `1e-3`, `−0.00033 ± 0.00030`) is **`1/63`** of the smallest significant package gap (`+0.0207`,
  P4−P1 at `S = 32`) and **`1/358`** of the P4 crossover at `S = 64`. The conflict needs no ruling
  to read this report.
* **P3 consumed 89.7 % of the grid's compute and lost at every size to every rival**, driven by
  `core.rb.eta_recip_table`'s `(S+1,S+1,S+1,2)` triple-loop build (≈`S^3.2`; 220 s and 271 MB per
  time slice at `S = 256`). Its `mode_collapse` count is 165 of 730 cells (22.6 %) against P2's 0.
* **C2 mode diagnostics** (item 6 constraint (b)): `mode_collapse` = **43 / 0 / 165 / 64** for P1–P4.

---

## 6. Two process notes, because they cost real hours

* **My cost model was wrong four times** (18.8 h → 25.6 h → 31 h predicted, 27.0 h actual). Measured
  cause: the cost probe ran at **24** workers and the grid at **90** — the measured contention factor
  is **1.54–1.58×** — and the dominant pair was extrapolated rather than measured.
* **A one-epoch `P3|S256` probe read 3,400.8 s/epoch against the grid's own measured ~1,245 s/epoch**
  (2.6× pessimistic: single-thread contention, a frozen rather than declared `smooth_lambda`, and
  epoch 1 paying cache-build costs that amortise). It nearly caused a healthy 13-hour run to be
  killed. **The grid's own rows are the measurement of record; no probe overrides them.**

---

## 7. What remains, and what 8a changed about it

| item | status after 8a |
|---|---|
| **8b — case-group grid, `D ∈ {8,64}`** | **HELD, blocking.** See R-3 below. |
| 9 — `S = 1024` memory / wall-clock | **now load-bearing**, not a formality: it is the *only* source for G6 (ii)'s memory half, and per §6.1 it **must** run one cell per process. |
| 10 — [G6-N1] read-out (`B_c` vs `KL(·‖Bin)`) | unblocked; reuses grid output, no new runs. Runs on 4 of 6 sizes (declared deviation from item 5). |
| 11 — ctrl-DM mini-grid (stronger P2) | unblocked, and **lower priority than it was**: P2 is no longer the opponent that matters — P4 is. |
| 12 — [G6-A3] GPU probe, ≤ 20 GPU-h | conditional on §6.1's trigger. |
| 13 — `g6_verdict()`, R6, claims delta | needs R-1 resolved first, or it renders a verdict on a confounded comparison. |
| 14 — HALT at G6 | — |

**→ RULING REQUESTED (R-3), the blocking one.** Item 8 as written is **unsatisfiable**: there is no
`D > 1` arm. All four packages sit on `Stage4Problem`, whose arrays are `(M+1, S+1)` — one count
lattice — and `targets/stage6.py` (which owns `TFE(S,D,…)` and `CMEToggle(D,…)`) is imported by **no
arm module**. This is not an engineering gap: `dm_weight="oracle"` is built from the exact endpoint
solve, which at `D > 1` is over `(S+1)^D` states and is precisely what the case group is *defined by
not having*; and the unweighted fallback is provably degenerate — `losses/dm.py` measures by exact
enumeration that the ctrl-DM population target is identically 1 in every slot to `1e-14`, so an
all-ones controller is already its global optimum and never moves. So P2 and P4 have neither their
oracle weight nor an honest unweighted mode at `D > 1`. The choice (filed in
`reports/MEMO_S6_ITEM8_DBRIDGE.md`) is between **(i)** building the `D`-coordinate arm stack with an
approximate DM weight whose error is measured (P3's `radiality`, generalised to P2 and P4), and
**(ii)** deferring the `D > 1` stack to Stage 7/8. **Recorded consequence either way: 8a alone cannot
discharge G6 condition (i) on a case target, and therefore cannot discharge §6's GPU-unlock
criterion (b).**

---

## 8. What is explicitly NOT claimed

* **No Pareto figure and no gate verdict.** G6 is `g6_verdict()` at item 13; §2 is the measurement
  it will read.
* **No claim that P4's win is a property of weight sharing or of the bit state space** — capacity is
  confounded (§2.3).
* **No memory claim in either direction** (§3b).
* **No claim about `D > 1`, the case group, or condition (i) on a case target** (§7).
* **No cost claim in `s3_units`**, cross-package or within (§3c).
* **No claim that the `log Ẑ` column is admissible at `S ≥ 64` for P1, P3 or P4** (§3a).
* **No claim that 40 epochs is convergence.** It is the horizon the configurations were *selected*
  at (`BUDGET.epochs_per_run`), asserted equal to it by
  `test_the_grid_runs_at_the_horizon_the_configurations_were_selected_at`. Every TV above is a
  40-epoch number and the packages may not be equally far from their asymptotes.

---

## 9. The three asks, in one place

| | ask | blocks |
|---|---|---|
| **R-1** | How to handle the **P1/P4 capacity confound** — re-tie and re-run the `S ≥ 64` slice (≈200 CPU-h), report the loss as confounded, or rule capacity out of scope for G6. | item 13 |
| **R-2** | Whether to tighten **PI-18** to *"`s3_units` is a schedule descriptor, not a cost axis"*, which is what the constancy in `S` measures. | nothing; hygiene |
| **R-3** | **8b**: approximate DM weight with measured error, or defer the `D > 1` stack to Stage 7/8. | G6 (i) on a case target, §6 GPU-unlock (b) |
