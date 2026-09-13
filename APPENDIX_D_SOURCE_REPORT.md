# Appendix D — Source Report (Tier 1: extraction-only, no GPU)

**Generated:** 2026-09-13 (UTC), repo `/home/RESEARCH/iasbs`
**Scope:** everything determinable from source, checkpoints, logs and JSON **without running new GPU work**.
Every claim below is tagged:

- **[E]** existing evidence (already on disk)
- **[N]** newly completed in this pass (CPU-only re-derivation / re-scoring / audit)
- **[G]** unresolved gap — requires new runs or a source edit

> **Standing caveat.** Where a fact is not recoverable from the repo, this report says
> **NOT DETERMINABLE FROM REPO** rather than guessing. Several such cases exist and are
> load-bearing for Appendix D; they are collected in §5.

---

## 1. Reproducibility

### 1.1 Entry points and CLI surface

| Component | File | Entry points |
|---|---|---|
| Occupation (Dirac) | `iasbs/occupation.py` | `run_train` :669–788, `run_scale` :1387–1492 |
| Occupation (non-Dirac) | `iasbs/occupation.py` | `run_train_nondirac` :791–962, `run_scale_nondirac` :1495–1691 |
| DAM core | `dam/core.py` | `rollout_ctmc` :78–153, `estimate_log_adjoint` :159–205, `gkl_loss` :214–264 |
| DAM driver | `dam/discrete.py` | `dam_step` :352–392, argparse :775–818 |
| Re-scoring | `iasbs/analysis/occ_rescore_mmd.py` | `mmd2_unbiased` :94–112, `median_bandwidth` :83–91 |

`iasbs/occupation.py` argparse is at :1836–1877 — **28 flags**. Notably **there is no `--device` flag**
(device is taken from `CUDA_VISIBLE_DEVICES` + a hard `cuda if available` selection) and
**no clamp-mode flag** (see §2.1). `dam/discrete.py` argparse is at :775–818 — **33 flags**.

### 1.2 Training budgets (as actually launched)

Occupation, m=512 queue (`/tmp/occ512_g0.sh`, representative of the current generation):

```
--m 512 --N 512 --d 0.5 --tau 1.0 --gamma 4.0 \
--steps 256 --iters 1500 --inner 4 --batch 512 --mb 512 --buffer 8 \
--hidden 256 --lr 1e-3 --loss bregman --estimator full --nu-skew 1.0 \
--inner-h 4 --lr-h 1e-2 --eval-every 250 --n-samples 10000
```

Dirac variant identical except `--batch 256`.

DAM defaults (`dam/discrete.py` argparse): `K=16, K_num=1, steps=128, iters=400, inner=4,
batch=256, mb=256, buffer=8, lr=1e-3, n_samples=20000, eval_every=50`,
`--a-clamp 0, --m-clip 30, --ess-min 0, --coef-cap 0`.
Adapter-level `a_clamp` defaults: ising / fs / occ = 20.0, **occupation-scale = 10.0** (`dam/discrete.py:271`).

**Optimisation.** Cosine LR schedule, `T_max = iters*inner`, `eta_min = lr*0.05`.
Gradient clipping: **10.0** for controllers, **1.0** for the scale h-net, **none** for the
m=4 `SourceCorrector`. **[E]**

### 1.3 Replay / time sampling

- Replay buffer of `--buffer 8` outer rounds; each outer round draws `--batch` trajectories,
  then performs `--inner` gradient passes of minibatch size `--mb` over the buffer.
- Time grid is uniform: `ts = arange(steps)/steps`. **This excludes `t = 1`.**
  There is **no `1 − ε` clamp anywhere in the repo** — the terminal singularity is avoided
  *structurally* by the half-open grid, not by an epsilon guard. **[E]**
- DAM rollouts use exact Gillespie within piecewise-constant control bins
  (`rollout_ctmc`), with `active = tau < 1.0 − 1e-14` (:106–109) and an iteration cap of
  **10,000,000** (:104). That cap is **not exposed as a CLI flag**. **[E]**

### 1.4 Architectures and parameter counts

| Net | Location | Input dim | Params |
|---|---|---|---|
| `OccController` | `occupation.py:329–353` | `m + 2 + 2·n_freq`, `n_freq = 4` hard-coded | 139,536 @ m=4, h=256 |
| `ScaleController` | `occupation.py:1197–1241` | 16 (DeepSets per-mode) | **136,450 for any m** @ h=256; **35,458** @ h=128 |

`ScaleController` is a rank-1 log-multiplier `a_ij = α_i + β_j` produced by a DeepSets trunk, so
its parameter count is **m-independent** — this is the mechanism that lets the same architecture
span m = 32 → 1000. Gauge is fixed by `s = β.mean(); return α + s, β − s`.
All nets are float32, 3 hidden SiLU layers, last layer zero-initialised. **[E]**

### 1.5 Evaluation settings

Two distinct evaluation paths exist and **must not be conflated**:

1. **In-training eval** — fires every `--eval-every` iterations, `--n-samples` draws,
   reports KS on the occupation marginal (`KS_occ`) and the max-coordinate KS (`KS_max`).
2. **Re-score** (`iasbs/analysis/occ_rescore_mmd.py`) — the protocol used for the headline table.
   - `n = 10,000` samples per seed.
   - Each run is re-scored **on its own original inference grid** (no regridding).
   - Target is **always a fresh, independent exact draw** (`:18–20`, `:224–225`), never a cached one.
   - MMD² is the **unbiased U-statistic** with an RBF kernel on the full ℝ^m occupation vector,
     diagonal zeroed, chunked at 2048 (`--chunk`).
   - Bandwidth: median of pairwise squared distances over **2000 exact samples**, seed `987654 + m`,
     then **frozen per m** across all methods and seeds (`median_bandwidth` :83–91).
   - Calibration / null MMD²: `--cal-reps 10`, seeds `1000*(r+1)+m` and `2000*(r+1)+m` (:190–205).
   - Seed derivation: `tag_seed` :274–278 uses `zlib.crc32((tag + str(salt))) % (2**31 − 1)`,
     with **salt 0 = model stream**, **salt 77 = fresh target draw**. **[E]**

Frozen bandwidths actually used:

| m | σ² | σ |
|---|---|---|
| 32 | 168.0 | 12.96148139681572 |
| 128 | 737.9999999999999 | 27.16615541441225 |
| 1000 | 5961.999999999999 | 77.21398836998384 |

Null / calibration MMD² (10 reps, n = 10,000):

| m | null MMD² mean ± sd |
|---|---|
| 32 | +9.721177964094884e-06 ± 1.643132895250483e-05 |
| 128 | −4.238251094723644e-06 ± 4.54652584931639e-06 |
| 1000 | −1.6047299739696542e-06 ± 2.486091936606076e-06 |

### 1.6 Headline re-score table **[N]**

`json/results_occ_rescore_mmd.json` was **repaired this pass**: an earlier `--ms 32` re-run had
truncated the file to the m=32 block only. The m=128 / m=1000 blocks were merged back from
backup while keeping the new 3-seed m=32 DAM rows. The file now holds **24 runs, 9 summary
entries, bandwidths for m ∈ {32, 128, 1000}**.

n = 10,000 per seed; each run on its own original inference grid:

| m | method | seeds | KS_occ | KS_max | MMD² |
|---|---|---|---|---|---|
| 32 | dam | 3 | 0.01116 ± 0.00140 | 0.03640 ± 0.00195 | +1.0267e-04 ± 1.33e-05 |
| 32 | iasbs_dirac | 3 | 0.00660 ± 0.00616 | 0.03797 ± 0.02526 | +1.2650e-04 ± 1.57e-04 |
| 32 | iasbs_nondirac | 3 | 0.01778 ± 0.00146 | 0.09943 ± 0.00471 | +4.0745e-04 ± 7.63e-05 |
| 128 | dam | 3 | 0.17466 ± 0.01266 | 0.89493 ± 0.04231 | +1.8031e-02 ± 1.16e-04 |
| 128 | iasbs_dirac | 3 | 0.00831 ± 0.00058 | 0.08063 ± 0.00076 | +1.4845e-04 ± 1.24e-05 |
| 128 | iasbs_nondirac | 3 | 0.00984 ± 0.00214 | 0.03513 ± 0.00340 | +1.5178e-04 ± 5.94e-05 |
| 1000 | dam | **0** | — | — | — |
| 1000 | iasbs_dirac | 3 | 0.01336 ± 0.00561 | 0.18097 ± 0.02266 | +1.8877e-04 ± 9.89e-05 |
| 1000 | iasbs_nondirac | 3 | 0.01097 ± 0.00350 | 0.28373 ± 0.18764 | +3.6704e-04 ± 3.75e-04 |

The m=1000 DAM cell is empty because **no DAM checkpoint was ever trained at m=1000**
(`occ_rescore_mmd.py:67`, `TAGS['dam'][1000] = []` with that exact comment). This is a
**deliberate omission recorded in source**, not a failed run. **[E]**

**Reading the MMD² column honestly.** All measured MMD² values (±1e-05 to ±1.5e-04) sit at the
same order as the split-half noise floors, and roughly half the audit values elsewhere in the repo
are negative. The correct statement is *"no distributional error detectable above a ~1e-04 noise
floor"*, **not** *"MMD² = 1.5e-04"*. The only cell that clears the floor by orders of magnitude is
**DAM at m=128 (1.8e-02)**, which is a genuine failure, not noise. **[N]**

### 1.7 Checkpoint / config / seed provenance

- Every occupation run dumps `vars(args)` into its results JSON at `occupation.py:1687`, so the
  full CLI of any run that used the current code path is recoverable from its JSON. **[E]**
- `MULTISEED_RESULTS.md` was last written **2026-09-12 04:24**, i.e. **before** four runs landed:
  `dam_occs128_K64_500_s1` / `_s2` (2026-09-13 03:49 / 04:00) and
  `dam_occs32_K64_1000_s1` / `_s2` (2026-09-13 08:22 / 08:20).
  Those four are **on disk but not yet aggregated** into the markdown summary. **[G — bookkeeping]**
- DAM Ising seeds 1 and 2 (L=4, L=5) were launched 2026-09-09 23:39 / 23:55 and **died immediately**:
  banner-only logs, no JSON produced. Any Ising multi-seed claim currently rests on seed 0 alone. **[E]**
- The seed-0 m=128 and m=1000 non-Dirac cells **predate** both `leaky_clamp` and the
  `bad_labels`/`skipped_steps` counters — those keys are simply absent from
  `results_occ_nd_s128.json` and `results_occ_nd_s1000.json`. Whether they used the hard or the
  leaky clamp is **NOT DETERMINABLE FROM REPO**. They must be **re-run**, not reused, for the
  bounded-vs-leaky ablation. **[G]**

---

## 2. Occupation stability — bounded vs leaky outputs

### 2.1 What exists in source

`leaky_clamp` is defined at `occupation.py:1244–1254` and is called at exactly **two sites**:

| Site | Line | Quantity | Bound | Leak |
|---|---|---|---|---|
| corrector | :1579 | `hv` | ±15 | 1e-2 |
| controller | :1633 | `av` | ±15 | 1e-2 |

Every other bound in the file is a **hard** `torch.clamp` (zero gradient outside the box):

| Line | Quantity | Bound |
|---|---|---|
| :723, :884 | controller output | ±20 |
| :1442 | Dirac scale output | ±15 |
| :1061–1062 | `ah`, `bh` | ±20 |
| :1063–1067 | `u`, `v` | ±60 |
| :1259–1260 | α, β | ±10 |
| :1270 | exponent | ≤ 20 |
| :1271 | departure probability | [0, 0.9] |

**Blocker.** There is **no CLI flag selecting hard vs leaky clamping.** The bounded arm of the
requested (m=128, 1000) × 3-seed ablation **cannot be launched without a source edit** — the two
`leaky_clamp` call sites at :1579 and :1633 would have to be swapped for `torch.clamp` behind a new
`--clamp-mode {hard,leaky}` flag. **[G — requires source edit + GPU]**

### 2.2 Counters: what they measure, and their denominators

```python
n_bad, n_skip = 0, 0                    # :1552   — ONE shared skip counter
...
n_skip += 1                             # :1585   — corrector update skipped
...
n_bad  += int(bad.sum())                # :1630   — non-finite LABEL ELEMENTS
n_skip += 1                             # :1640   — controller update skipped
```

Written to JSON as `history[k].bad_labels` / `history[k].skipped_steps` at :1655–1657;
logged as the string `bad {n_bad}/{n_skip}` at :1663.

Three problems, all of which Appendix D must state:

1. **`bad {n_bad}/{n_skip}` is not a fraction.** It is two independent counters printed with a
   slash. `n_bad` counts *label tensor elements*; `n_skip` counts *optimiser steps*.
2. **`n_skip` has two different denominators.** It is incremented from the corrector loop
   (denominator = `iters × inner_h`) and from the controller loop (denominator = `iters × inner`),
   but only one number is stored. Recovering a per-loop skip *rate* from existing JSON is
   **NOT DETERMINABLE FROM REPO**.
3. **Non-finite *loss* count is not tracked at all** — only non-finite labels are. A finite-label /
   non-finite-loss event is invisible.

**[G]** Fixing (1)–(3) is a small CPU-side instrumentation change: split into
`n_skip_h` / `n_skip_a` with their own denominators, and add `n_bad_loss`.

### 2.3 The counters demonstrably miss the failure mode **[E, critical]**

The one clearly documented saturation collapse in the repo is `iasbs/logs/occ_nd_s32.log` (m=32):
`loss_h` freezes at **exactly 315.0476** for roughly 1900 iterations after `it 1000`, and the run
ends at **KS_occ = 0.4008** (vs ~0.018 for a healthy m=32 non-Dirac run).

Throughout that collapse the log reports **`bad 0/0`**.

So the existing counters report a perfectly clean run while the model is pinned against a bound.
Consistently, **every `bad_labels` / `skipped_steps` value at m=128 and m=1000 is 0**. Appendix D
must not cite these zeros as evidence of stability — they are evidence that the instrument is
blind to the phenomenon being claimed.

The signature that *did* detect it was the frozen loss value (a constant `loss_h` to 4 decimals),
which is a *post-hoc log artefact*, not an instrumented metric.

### 2.4 Output saturation is measured nowhere **[G]**

`grep -rn 'saturat' iasbs/` returns **only the `leaky_clamp` docstring**. There is no
saturation fraction, no `|output| ≥ bound` rate, no histogram of controller outputs — at any m,
for any run, in any JSON. The requested "output saturation" column of the ablation table
therefore has **no existing source**; it requires a new instrumented run.

Minimal proposed instrument (CPU-cheap, added inside the two clamp sites):

```python
sat = (v.abs() >= bound - 1e-6).float().mean().item()   # fraction of saturated outputs
```
accumulated per eval window and written alongside `bad_labels`.

### 2.5 Summary of §2 status

| Requested quantity | Status |
|---|---|
| accuracy (KS_occ / KS_max / MMD²), leaky arm | **[E]** — §1.6 table (all current runs are leaky at :1579/:1633, *except* seed-0 m=128/1000 which predate it) |
| accuracy, bounded arm | **[G]** — needs `--clamp-mode hard` + 6 GPU runs |
| output saturation | **[G]** — not instrumented anywhere |
| negative / non-finite labels | **[E, partial]** — `bad_labels` exists but counts *elements*, and reads 0 even during a known collapse |
| non-finite losses | **[G]** — not tracked |
| skipped-update counts **with denominators** | **[G]** — single shared counter, two denominators, unrecoverable |

---

## 3. DAM (discrete adjoint matching) baseline

### 3.1 Exact estimator and corrections **[E]**

`rollout_ctmc` (`dam/core.py:78–153`) simulates the **exact** CTMC by Gillespie within each
piecewise-constant control bin. The importance weight accumulates two contributions:

```python
logw += (Ru - Rb) * step        # :134  — total-rate (action) correction over the holding interval
logw += -log_a                  # :137  — per-jump edge correction
```

`Ru` is the uncontrolled total rate, `Rb` the controlled (base × multiplier) total rate; `log_a`
is the log-multiplier on the edge actually taken. `TINY = 1e-300` (:67) guards the log.

**RNG note (reproducibility-relevant).** `sample_edge` is called on **every pass of the loop**,
whether or not a jump is accepted. It therefore consumes random numbers unconditionally, so the
RNG stream depends on the number of loop passes, not the number of jumps. Any attempt to
reproduce a rollout with a different `steps` value will diverge even at identical seed. **[E]**

`estimate_log_adjoint` (:159–205, `@torch.no_grad()`) is a self-normalised importance ratio:
`logsumexp` over `K_num` rollouts launched from `(t, y)` minus `logsumexp` over `K` rollouts
launched from `(t, x)`. ESS is the Kish effective sample size (:195–196).

### 3.2 gKL loss as implemented **[E]**

```python
LOG_M_CLIP = 30.0                                          # :211
m    = exp(clip(log_m, ±m_clip)).detach()                  # :255
coef = (r * exp(-log_q)).detach()                          # :256
per  = coef * (exp(a) - m * a)                             # gkl_loss :214–264
```

Only `a = ad.a_on_edge(net, t, Xt, edge)` (`discrete.py:383`) carries gradient; `m` and `coef` are
detached. `gkl_literal` (:267–273) exists solely for test **T5**, which verifies the gradient
identity between the implemented and literal forms to **rel. err < 1e-12**. That test is the
justification for the detach-and-clip rewrite, and Appendix D should cite it as such. **[E]**

### 3.3 Stabilisers and what they cost

`dam_step` signature (`discrete.py:352–392`):

```python
dam_step(ad, net, opt, sched, Xt, ti, steps, K, K_num,
         clip=10.0, m_clip=LOG_M_CLIP, ess_min=0.0, coef_cap=0.0)
```

| Stabiliser | Mechanism | Instrumented? |
|---|---|---|
| `m_clip` | clips `log_m` to ±`m_clip` before exponentiating | **yes**, `st["clipped"]` :376 |
| `ess_min` | discards rollout batches with Kish ESS below threshold | `st["dropped"]` :380 — **computed but NEVER read** |
| `coef_cap` | caps the detached `coef` | not separately reported |
| `a_clamp` | bounds the log-multiplier; adapter default 20.0 (occ-scale **10.0**) | no |

**Gap.** `st["dropped"]` is written by `dam_step` but is consumed by neither `_acc` (:395–400) nor
`_weight_report` (:403–410). The **ess_min discard fraction is therefore NOT DETERMINABLE FROM
REPO** for any existing run. Separately, `nonfinite_weights` in `_weight_report` is a
**hard-coded 0** at :409 — it is a placeholder, not a measurement. Appendix D must not quote it.
**[G — two-line fix, CPU-side]**

### 3.4 Why DAM fails at m=128 — measured **[E]**

| m | labels truncated by `m_clip=5` | ESS (of K=64) |
|---|---|---|
| 32 | 25.6 % / 18.9 % / 17.1 % (3 seeds) | 31.4 – 36.3 |
| 128 | **88.2 % / 88.9 % / 88.2 %** — 451,665 / 455,116 / 451,522 of 512,000 | **≈ 1.69**, p10 = 1.0009 |

At m=128 the adjoint estimator has effectively **one useful rollout out of 64** (p10 ESS of 1.0009
means at least 10 % of estimates are entirely dominated by a single sample), and ~89 % of labels
are saturated against the clip. The consequence is visible end-to-end: DAM at m=128 moves KS_occ
only from ≈0.205 (uncontrolled) to ≈0.175, against a 0.05 acceptance gate — i.e. it recovers
roughly **15 % of the gap it needs to close**, and the re-score MMD² (1.80e-02) is two orders of
magnitude above the noise floor.

This is the cleanest single quantitative statement in the DAM section and should anchor it.

### 3.5 Tuning history **[E, with one correction]**

`run_occs128_K64.sh:7–8` contains the comment that K=32 at m=128
*"starves the adjoint estimator outright (ESS 1.52/32)"*. **No log and no JSON exist for that
configuration.** It must be cited in Appendix D as a **code comment recording a design decision**,
not as a reported result. Quoting "ESS 1.52/32" as a measurement would be unsupported. **[G]**

Recorded moves that *do* have artifacts: K 16 → 64 at both m=32 and m=128; `m_clip` reduction to 5
(with the truncation rates in §3.4); `a_clamp` lowered to 10.0 for the occupation-scale adapter.

### 3.6 Proposal / rollout sensitivity at m=128 **[G — the main GPU-blocked item]**

The requested sweep (accuracy × ESS × runtime over proposal and rollout budget at m=128) has
**never been run**.

Measured cost of a single m=128 DAM run, from three completed runs:
**67,692.6 s / 67,124.3 s / 67,799.3 s → mean ≈ 18.76 h.**

A 12-configuration OFAT sweep × 3 seeds is therefore
**36 runs × 18.76 h ≈ 675 h ≈ 28 days serial** (≈ 834 h ≈ 35 days if the grid is widened as
originally specified). On two GPUs this is ~2 weeks minimum.

**Recommendation for Appendix D:** do not promise the full grid. Either
(a) report the sweep at **m=32** where runs are ~20× cheaper and the ESS is healthy, and state
explicitly that m=128 is extrapolated; or
(b) run a **reduced 4-config × 1-seed** probe at m=128 (≈ 75 h ≈ 3 days) reporting ESS and KS only,
and mark it single-seed. Option (b) is enough to demonstrate that no reachable (K, K_num) rescues
m=128, which is the actual claim the paper needs.

---

## 4. Continuous primitives

### 4.1 Scope — what actually exists **[E]**

Implemented manifolds: **S²** (Legendre spectral heat kernel) and **St(4,2)** (Stiefel, built from
two **S³** spin factors, S³ kernel via Chebyshev-U). **There is no Euclidean sampler in the repo.**
Any Appendix D sentence implying an ℝ^d baseline is unsupported — it must be removed or
accompanied by new code.

### 4.2 Generator / noise conventions **[E]**

The convention is uniform across every continuous sampler:

```
generator :  ½ σ² Δ                       (Laplace–Beltrami)
drift     :  diffusion² · score · dt
noise     :  diffusion · sqrt(dt) · ξ,    ξ ~ N(0, I) in the tangent space
```

Default `σ = √2`, hence `σ² = 2`, hence the clock runs at **r01 = 1.0** over `t ∈ [0,1]`.

### 4.3 Bridge update (pseudocode) **[E]**

Doob h-transform bridge on a compact symmetric space, per step:

```
for i, t in enumerate(ts):                 # ts = arange(steps)/steps, EXCLUDES t = 1
    dt    = 1/steps
    s     = score_log_heat(X, target, r = (1 - t))      # ∇_X log p_{1-t}(X → target)
    drift = diffusion**2 * s * dt
    xi    = randn_like_tangent(X)
    noise = diffusion * sqrt(dt) * xi
    V     = drift + noise                                # tangent vector at X
    X     = exp_map(X, V)                                # Lie/left action, see 4.4
```

For **St(4,2)** the tangent step is expressed in the **Killing basis of so(4)** and applied by
`matrix_exp` as a **left action** on the frame. The two S³ spin factors are advanced at clock
**r/2**, not r.

**Evidence for the r/2 convention** (test [12]): KS = **0.0042** when the spin factors run at
`r/2`, versus KS = **0.2675** at `r`. This is a 60× discrepancy and is the decisive check that the
double-cover normalisation is right. Cite test [12] explicitly. **[E]**

### 4.4 Endpoint handling **[E]**

- The grid `ts = arange(steps)/steps` is **half-open**: it contains `t = 0` but not `t = 1`.
  The bridge score `r = 1 - t` therefore never evaluates at `r = 0`.
- **There is no `1 − ε` clamp anywhere in the codebase.** The `r → 0` singularity is avoided
  *structurally*, by grid construction. Appendix D should say this explicitly, because "no epsilon
  guard" reads as an omission unless the mechanism is stated.
- **Known small mismatch:** the St(4,2) 199-step grid yields `t = 0.251 / 0.503 / 0.749`, not
  `0.25 / 0.5 / 0.75`. The reported "t = 0.25/0.5/0.75" column for the 199-step case is off by up
  to 0.003 in clock time. Uncorrected. **[G — cosmetic, but should be stated]**

### 4.5 Quadrature / series convergence **[E]**

`weakness5_verify.json`:

- **S²**: Chapman–Kolmogorov verified by quadrature; agreement to **~5e-09 relative**.
- **St(4,2)**: all **12 CK ratios** lie in **[0.9959, 1.0040]** — i.e. within 0.4 %.
- **`M_violations = 0` in all 24 cells** (no violation of the majorisation / positivity bound).

These are strong, and they are the right numbers to lead the continuous section with, because they
are *not* floor-limited (unlike the MMD² audits below).

### 4.6 Bridge-error audits — references and their defects **[E, critical]**

Three separate problems in the existing audit artifacts:

1. **`results_frame_law_audit.json` used a degenerate reference.**
   `ckpt/stiefel_frame_s5_b1_mcmc.pt` and `ckpt/stiefel_frame600_b1_mcmc.pt` hold
   **byte-identical sample tensors**. The "cross" floor computed from them was therefore a
   **second split-half of the same draw**, not an independent reference. Any number from that file
   labelled "cross" is invalid.
   **Fix already on disk:** `results_weakness5_refaudit.json`, which uses three genuinely distinct
   references (refA / refB / refC). **Appendix D must cite `results_weakness5_refaudit.json` and
   must not cite `results_frame_law_audit.json`.**

2. **R-ASBS checkpoints store the rotated frame `X_r = U X`.** Without applying the `Uᵀ` map
   before evaluating, `E[tr(CᵀX)]` reads **−0.3464** instead of the correct **0.5274**. This is a
   sign-flip-scale error large enough to invert a conclusion. Any downstream analysis must map back.

3. **`bridge_audit.py:216–220` reseeds to `seed + 1` before *both* the 128-step and the 1024-step
   bridge.** The two legs therefore share a random-number stream, so their difference is not an
   independent comparison. The commonly quoted **"ratio −4.28"** from that audit is
   **not meaningful** and must be dropped.

### 4.7 MMD² floor caveat (applies to all bridge audits) **[N]**

Every MMD² test in the repo is **floor-limited**: measured values span ±1e-05 to ±1.5e-04, which is
the same order as the split-half floors, and roughly half of them are **negative** (as an unbiased
U-statistic legitimately can be under H₀). The defensible claim is:

> *No bridge error is detectable above a ≈1e-04 MMD² noise floor at the sample sizes used.*

Not: *"the bridge error is 1.5e-04."* This distinction should appear once, prominently, in
Appendix D and then be referenced.

### 4.8 Test-suite status **[N]**

`iasbs/tests_math.py --fast`, CPU: **26 passed, 1 failed, 72.7 s.**

The single failure is **[A2.10] empirical bridge TV = 0.0314** and it is a **`--fast` tolerance
bug**, not a model defect:

```
_a2_tests.py:192   nS = 20000 if fast else 100000     # sample count scales with --fast
_a2_tests.py:212   tol = 0.02                          # tolerance does NOT scale
```

Re-run in full (non-fast) mode: **max TV = 0.0135 → passes.** The fix is to scale the tolerance
with `1/sqrt(nS)`. **[G — one-line fix]**

`dam/tests_math.py`, CPU: **T0, T8, T1, T2, T10, T3, T4, T5, T6 PASSED.**
**T7 was terminated after 12 min** — it hard-codes `n = 20000` rollouts and has **no `--fast`
path**. **T7, T9, T11+ are therefore unverified on this machine.** Appendix D should either report
the DAM suite as "9 of N tests verified" with the reason, or T7 should get a `--fast` path.
**[G]**

---

## 5. Consolidated status

### 5.1 Existing evidence — usable as-is **[E]**

| # | Claim | Artifact |
|---|---|---|
| E1 | Full 3-seed re-score table at m ∈ {32,128,1000} for IASBS-Dirac / non-Dirac, and DAM at 32/128 | `json/results_occ_rescore_mmd.json` |
| E2 | Frozen per-m bandwidths + 10-rep null MMD² calibration | same file, `bandwidth` / `calibration` |
| E3 | DAM gKL gradient identity vs literal form, rel. err < 1e-12 | `dam/tests_math.py` **T5** |
| E4 | DAM m=128 breakdown: 88 % label truncation, ESS ≈1.69/64 | DAM run logs / JSON, 3 seeds |
| E5 | S² CK-by-quadrature agreement ~5e-09 rel. | `weakness5_verify.json` |
| E6 | St(4,2) 12 CK ratios ∈ [0.9959, 1.0040]; `M_violations = 0` in 24/24 cells | `weakness5_verify.json` |
| E7 | Spin factors must run at clock r/2 (KS 0.0042 vs 0.2675) | `tests_math.py` test **[12]** |
| E8 | Corrected Stiefel frame-law audit with 3 independent references | `results_weakness5_refaudit.json` |
| E9 | Architecture parameter counts, incl. m-independence of `ScaleController` | `occupation.py:1197–1241` |
| E10 | Full CLI of every current-generation run | `vars(args)` dump, `occupation.py:1687` |

### 5.2 Newly completed this pass (CPU only) **[N]**

| # | Work | Result |
|---|---|---|
| N1 | Repaired truncated `results_occ_rescore_mmd.json` | 24 runs, 9 summary entries, m ∈ {32,128,1000} restored; new 3-seed m=32 DAM retained |
| N2 | Re-derived the headline table from the repaired file | §1.6 |
| N3 | Ran `iasbs/tests_math.py --fast` on CPU | 26/27 pass; sole failure diagnosed as a tolerance-scaling bug (§4.8) |
| N4 | Ran `dam/tests_math.py` on CPU as far as feasible | 9 tests pass; T7 non-terminating without `--fast` |
| N5 | Audited every clamp site in `occupation.py` | §2.1 table — 2 leaky, 7 hard, no CLI selector |
| N6 | Traced `n_bad` / `n_skip` denominators | §2.2 — one shared counter, two denominators, unrecoverable |
| N7 | Cross-checked audit references | found byte-identical checkpoints, `Uᵀ` omission, shared-RNG bridge legs (§4.6) |
| N8 | Established the MMD² floor reading | §4.7 |

### 5.3 Unresolved gaps **[G]**

Ordered by how much they block Appendix D.

| # | Gap | Cost to close |
|---|---|---|
| G1 | **Bounded-vs-leaky ablation cannot be launched** — no `--clamp-mode` flag exists | source edit (small) + 6 GPU runs at m=128/1000 |
| G2 | **Output saturation instrumented nowhere** (`grep saturat` → docstring only) | source edit (3 lines) + re-run |
| G3 | **Non-finite *loss* count not tracked**; `bad_labels` counts elements and reads 0 during a known collapse (`occ_nd_s32.log`, `loss_h` frozen at 315.0476, KS_occ 0.4008, `bad 0/0`) | source edit + re-run |
| G4 | **Skip-rate denominators unrecoverable** — `n_skip` shared between corrector (`iters×inner_h`) and controller (`iters×inner`) loops | split into `n_skip_h` / `n_skip_a` |
| G5 | **DAM m=128 proposal/rollout sweep never run**; 18.76 h/run measured ⇒ 36 runs ≈ 675 h serial | see §3.6 for the reduced-probe alternative |
| G6 | **`ess_min` discard fraction NOT DETERMINABLE** — `st["dropped"]` written, never read; `nonfinite_weights` hard-coded 0 | 2-line fix in `_weight_report` |
| G7 | **Seed-0 m=128/1000 non-Dirac clamp mode unknown** — keys predate `leaky_clamp`; must be re-run, not reused | 2 GPU runs |
| G8 | `run_occs128_K64.sh` "ESS 1.52/32" has **no log, no JSON** — cite as design comment only | 1 GPU run if it must be a result |
| G9 | **DAM Ising seeds 1/2 died on launch** (2026-09-09 23:39/23:55, banner-only logs) — Ising multi-seed rests on seed 0 | relaunch |
| G10 | **`MULTISEED_RESULTS.md` stale** (written 2026-09-12 04:24; 4 later runs unaggregated) | re-run aggregator, CPU |
| G11 | **T7/T9/T11+ of `dam/tests_math.py` unverified** — T7 hard-codes n=20000, no `--fast` | add `--fast` path |
| G12 | **`[A2.10]` tolerance does not scale with `--fast`** (`_a2_tests.py:192` vs `:212`) | 1-line fix |
| G13 | **No Euclidean continuous sampler exists** — only S² and St(4,2) | new code if the paper claims one |
| G14 | **St 199-step grid is t = 0.251/0.503/0.749**, not 0.25/0.5/0.75 | restate the column |

### 5.4 Claims that must be REMOVED or RESTATED in Appendix D

These are places where the current draft (or the obvious reading of the artifacts) would be wrong:

1. **Do not cite `results_frame_law_audit.json` "cross" numbers** — degenerate reference
   (byte-identical checkpoints). Cite `results_weakness5_refaudit.json`.
2. **Do not cite the bridge-audit "ratio −4.28"** — the 128-step and 1024-step legs share an RNG
   stream (`bridge_audit.py:216–220`).
3. **Do not cite `nonfinite_weights`** — hard-coded 0 (`discrete.py:409`).
4. **Do not cite `bad_labels = 0` / `skipped_steps = 0` as stability evidence** — the same counters
   read `0/0` through a documented collapse.
5. **Do not quote "ESS 1.52/32"** as a measurement — it is a shell-script comment with no artifact.
6. **Do not report MMD² point values as bridge error** — they are at the noise floor (§4.7).
7. **Do not report `E[tr(CᵀX)]` from raw R-ASBS checkpoints** — apply `Uᵀ` first (−0.3464 → 0.5274).

---

## 6. Reproducible commands and artifact paths

All commands are run from `/home/RESEARCH/iasbs` with conda env `cuau_env`
(`PY=/root/miniconda3/envs/cuau_env/bin/python`).

### 6.1 Re-score (CPU or 1 GPU; reproduces §1.6 exactly)

```bash
$PY -m iasbs.analysis.occ_rescore_mmd \
    --ms 32 128 1000 --n 10000 --cal-reps 10 --chunk 2048 \
    --out json/results_occ_rescore_mmd.json
```

Determinism: bandwidth seed `987654 + m`; model stream `crc32(tag + "0")`; fresh target draw
`crc32(tag + "77")`; calibration seeds `1000*(r+1)+m`, `2000*(r+1)+m`.

### 6.2 Occupation training (the m=512 generation)

```bash
CUDA_VISIBLE_DEVICES=0 $PY -m iasbs.occupation --mode scale-nondirac \
  --m 512 --N 512 --d 0.5 --tau 1.0 --gamma 4.0 \
  --steps 256 --iters 1500 --inner 4 --batch 512 --mb 512 --buffer 8 \
  --hidden 256 --lr 1e-3 --loss bregman --estimator full --nu-skew 1.0 \
  --inner-h 4 --lr-h 1e-2 --eval-every 250 --n-samples 10000 \
  --seed 0 --out json/results_occ_nd_s512.json
```

Dirac arm: `--mode scale`, `--batch 256`, otherwise identical.
Queue scripts: `/tmp/occ512_g0.sh` (GPU 0), `/tmp/occ512_g1.sh` (GPU 1).

### 6.3 DAM

```bash
CUDA_VISIBLE_DEVICES=0 $PY -m dam.discrete --problem occupation-scale \
  --m 128 --K 64 --K-num 1 --steps 128 --iters 500 --inner 4 \
  --batch 256 --mb 256 --buffer 8 --lr 1e-3 \
  --m-clip 5 --a-clamp 10 --ess-min 0 --coef-cap 0 \
  --eval-every 50 --n-samples 20000 --seed 0 \
  --out json/results_dam_occs128_K64_500.json
```

Measured wall-clock at m=128: 67,692.6 / 67,124.3 / 67,799.3 s (mean 18.76 h).

### 6.4 Tests

```bash
$PY iasbs/tests_math.py --fast      # 26 pass / 1 fail (A2.10 tolerance bug), 72.7 s CPU
$PY iasbs/tests_math.py             # full mode: A2.10 max TV 0.0135 → passes
$PY dam/tests_math.py               # T0,T8,T1,T2,T10,T3,T4,T5,T6 pass; T7 hangs (no --fast)
```

### 6.5 Artifact index

| Path | Contents |
|---|---|
| `json/results_occ_rescore_mmd.json` | headline re-score table, bandwidths, calibration (**repaired, 24 runs**) |
| `json/results_occ_nd_s128.json`, `…_s1000.json` | seed-0 non-Dirac; **lack** `bad_labels`/`skipped_steps` keys |
| `json/results_dam_occs128_K64_500{,_s1,_s2}.json` | DAM m=128, 3 seeds |
| `json/results_dam_occs32_K64_1000{,_s1,_s2}.json` | DAM m=32, 3 seeds (`_s1`/`_s2` landed 2026-09-13) |
| `weakness5_verify.json` | S² / St(4,2) CK convergence, `M_violations` |
| `results_weakness5_refaudit.json` | **correct** frame-law audit (refA/refB/refC) |
| `results_frame_law_audit.json` | **superseded** — degenerate reference, do not cite |
| `iasbs/logs/occ_nd_s32.log` | the documented saturation collapse (`loss_h` 315.0476) |
| `MULTISEED_RESULTS.md` | aggregate summary, **stale since 2026-09-12 04:24** |
| `ckpt/stiefel_frame_s5_b1_mcmc.pt`, `ckpt/stiefel_frame600_b1_mcmc.pt` | **byte-identical** sample tensors |

---

## 7. What Tier 1 could not do

This report is **extraction-only**. The following were explicitly requested and are **not** in it,
because each needs GPU time or a source edit (both GPUs are currently saturated by the m=512 queue):

- the (m=128, 1000) × 3-seed **bounded-vs-leaky** ablation → blocked by G1, G2, G3, G7;
- the m=128 **proposal / rollout sensitivity** grid → blocked by G5 (≈675 h serial);
- per-loop **skipped-update rates with denominators** → blocked by G4;
- the **ess_min discard fraction** → blocked by G6.

The corresponding source edits (G1–G4, G6, G11, G12) are all small and CPU-verifiable; doing them
first means the eventual GPU runs produce the ablation table in a single pass rather than two.
