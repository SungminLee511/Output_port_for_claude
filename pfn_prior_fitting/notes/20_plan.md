# Step 16 — The paper, and the implementation plan. Written to be attacked.

## 0. The one-sentence claim (C1)

> **The synthetic prior of a prior-data fitted network can be *fitted* to real
> data — by scoring a θ-conditional PFN prequentially and solving a convex NPMLE
> for the mixing distribution over prior hyperparameters — and retraining on the
> fitted prior yields a strictly better tabular foundation model, together with a
> label-free statistic that predicts where that model will fail.**

Title candidate: *Fitting the Prior of a Prior-Data Fitted Network.*

Everything about the paper follows from the fact that this sentence is
falsifiable in two independent places (the model gets better / it does not; the
statistic predicts failure / it does not).

## 1. Why this is a method paper and not an analysis paper

Deliverables are artefacts, not observations:
- **M2** — a retrained PFN checkpoint that is better than the same PFN trained
  on the hand-designed prior at *identical* compute. Drop-in.
- **M1** — a zero-training inference-time mixture over prior hyperparameters,
  plus `s(D) = (1/n) log Σ_k π*_k exp(ℓ_k(D))`, a label-free-at-test-rows
  abstention/failure statistic.
The analysis (Theorems 1–5) exists to justify the artefacts, not vice versa.

## 2. What the smoke tests already established, and did not

Established on synthetic data (Steps 12–15, `smoke/s01..s04`):
- θ-recovery works (0.703 vs 0.25 chance), order-incoherence is 3.7× below the
  signal, θ-conditioning is used, NPMLE recovers a known mixing law to TV 0.04
  and does not collapse.
- **M2: B recovers 96% of the oracle's gain, 60–120× seed noise, 59.8% paired
  win rate over 800 datasets.**
- **M1 is an `O(1/n)` effect and is demoted.** Documented in
  `ideas/13_smoke_S03.md` §14.2(ii). Not hidden; it becomes a *remark* in the
  paper, because the reason is exact and worth stating.
- Specialization cost is real: −0.0030 nats/row off-corpus.

Not established, and these are what the main experiment is for:
1. Real tabular data is **outside** any synthetic family; the NPMLE then fits a
   projection, not a recovery. Unknown whether the projection is useful.
2. Scale (n=64,d≤8 → n≈1–10k, d≈50–500).
3. **Ob1: fine-tuning on real data (Real-TabPFN-2.5) may dominate.**
4. Kernel bandwidth of the π*-resampler is an unjustified hyperparameter.
5. O1's AUC in the continuous-θ regime, with the y-shuffle control.

## 3. Prior parameterization θ

Reimplement a TabPFN-v2-style SCM/BNN prior with its hyperparameters **exposed**
rather than fixed. Target `d_θ ≈ 12`, all in `[0,1]` after monotone reparam:

| group | hyperparameters |
|---|---|
| structure | SCM depth, width, edge density, DAG vs tree topology mix |
| functional | activation-set mixture weights (identity / relu / tanh / sin / step), weight-scale |
| noise | additive noise scale, noise family mixture (Gaussian / Student-t / uniform), label-noise rate |
| features | categorical fraction, cardinality scale, missing-value rate, quantile-warp strength |
| task | class-count law, class-imbalance, feature-count law, informative-feature fraction |

Two things must be true and must be checked, not assumed:
(a) `θ ↦ P_θ` is smooth enough that a network can condition on it;
(b) at `θ ~ π₀` the family **contains** something close to the shipped TabPFN
prior, so that arm A is a fair stand-in for the incumbent. Verify by matching
arm A against the released TabPFN v2 at matched compute; if arm A is far worse,
the whole comparison is against a straw man and the paper is invalid.

## 4. Data, and the contamination rule that decides the paper's credibility

Three **disjoint** real-dataset pools, split **before** anything is run:
- `R_fit` (≈150–250 datasets): used *only* to compute `L[m,k]` and fit `π*`.
  Sources: OpenML-CC18 / AMLB / TabZilla / TALENT, minus everything in `R_eval`.
- `R_eval` (TabArena, 51 datasets + held-out remainder): used *only* for final
  numbers. Never touched during prior fitting, architecture choice, or
  hyperparameter selection.
- `R_dev` (≈30 datasets): all development decisions.

Deduplicate `R_fit` against `R_eval` by dataset id **and** by content hash of
`(n, d, class counts, column-name multiset)` — OpenML has near-duplicates under
different ids and a reviewer will check. Report the dedup procedure and the
number of datasets it removed. This is the single easiest way for the paper to
be destroyed, and the only defence is doing it in public.

## 5. Method, exactly

1. **Train one θ-conditional PFN** on `θ ~ π₀` (broad). One run.
2. **Choose the atom set** `{θ_k}_{k<K}`, `K ≈ 512`, by scrambled Sobol in
   `[0,1]^{d_θ}` (not a factorial grid — `4^12` is absurd).
3. **Score**: `ℓ_k(D_m) = Σ_i log q(y_{σ(i)}|x_{σ(i)}, D_{σ(<i)}, θ_k)` for all
   `m ∈ R_fit`, `k < K`. Cost = `K` forward passes per dataset via the causal
   row mask (`math/01_setup.md` §7). Average over `P = 8` orderings `σ` and
   **report the σ-spread** as a coherence diagnostic (Warning 2.3).
4. **NPMLE**: `π* = argmax_{π ∈ Δ_K} Σ_m log Σ_k π_k e^{ℓ_k(D_m)}`, concave
   (Theorem 5), solved by the EM of Corollary 5.1 in log space.
   State the classical fact that the NPMLE has **at most `|R_fit|` support
   points**; with `K = 512 > M ≈ 200` sparsity is guaranteed a priori, and
   `e^{H(π*)}` is the honest report of effective support.
5. **M1**: `p(y|x,D) = Σ_k w_k(D) p(y|x,D,θ_k)`, `w_k(D) ∝ π*_k e^{ℓ_k(D)}`.
   Free. Report it, and report the `O(1/n)` remark alongside it.
6. **M2**: resample the pretraining corpus from `π*` smoothed by a kernel of
   bandwidth `h`, retrain one unconditional PFN. `h` selected on `R_dev` only,
   with the full sensitivity curve reported.

## 6. Experiments, with the controls that matter more than the main number

**E1 — controlled A/B (the paper's core).** Identical architecture, steps,
optimizer, seeds; only the pretraining θ-law differs.
`A: π₀` | `B: π*` | `B-rand: π ~ Dirichlet(1)` renormalized to the same entropy
as `π*` | `B-single: δ_{argmax_k}` (the T-D collapse baseline) |
`C: π` fitted on `R_eval` (oracle, **reported as an upper bound and never as a
result**).
`B-rand` is the control that decides whether the gain comes from *fitting* or
merely from *reshaping* the prior. If `B-rand ≈ B`, the paper is dead. This
control did not exist in the smoke tests and must exist here.

**E2 — vs. the incumbent.** TabPFN v2, TabPFN-2.5, **Real-TabPFN-2.5**, tuned
CatBoost / XGBoost / LightGBM (Optuna, ≥100 trials, time-matched), AutoGluon
best-quality. Plus: continued pretraining of the *released* TabPFN checkpoint on
`π*`-resampled data, which is the cheap route to a headline number against a
real model rather than against our own arm A.

**E3 — Ob1 head-to-head (the objection that can kill us).** At matched real-data
budget `|R_fit|`: (i) fine-tune arm A on `R_fit`; (ii) our `π*` refit; (iii) both.
Report `R_eval` results *and* an out-of-distribution slice. Prediction to be
tested, not asserted: fine-tuning wins on datasets similar to `R_fit` and loses
off-distribution, while prior fitting is flatter. If fine-tuning dominates
everywhere, say so in the abstract.

**E4 — O1 / abstention.** AUC of `s(D)` for predicting (a) PFN-beaten-by-GBDT,
(b) top-quartile NLL. Baselines: the meta-feature predictor of 2605.28418 (a
published *failure*, so beating it is necessary but not sufficient), dataset
size/dimension heuristics, and a **y-shuffled control** that isolates covariate
novelty from conditional-model misfit. Deliver a routing rule with a
selective-risk / coverage curve.

**E5 — ablations.** `K ∈ {64,128,512}`; `|R_fit| ∈ {25,50,100,200}` (the
sample-complexity curve of prior fitting — this is a genuinely interesting plot
and nobody has it); kernel bandwidth `h`; number of orderings `P`; NPMLE vs
plain argmax vs uniform.

**Statistics, fixed in advance.** ≥3 seeds per arm. Per-dataset paired
differences, Wilcoxon signed-rank and sign tests, Holm correction across the
metric family, critical-difference diagrams, and **per-dataset scatter plots**
— because both M1 results were mean-positive and median-neutral, and the same
shape is likely here. If the headline is mean-only, the paper reports it as
mean-only and says why.

## 7. Compute

1×A100 80GB. Estimated: θ-conditional PFN ≈ 12–20 h; scoring `R_fit` ≈ 2–4 h;
NPMLE seconds; each unconditional arm ≈ 12–20 h × (5 arms × 3 seeds) ≈ 200–300
GPU-h; baselines (GBDT/AutoGluon) are CPU-bound and fit the 96-core box.
Total ≈ **300–400 GPU-hours ≈ 2 weeks on one A100**, which is affordable.
More GPUs would buy: more seeds, a scale ladder (n ∈ {1k, 5k, 10k}), and E2's
continued-pretraining arm in parallel — **useful, not necessary**. This lane was
chosen precisely because 1 GPU is its native scale.

## 8. Pre-registered kill conditions

The paper is **abandoned or radically rescoped** if any of these hold:
1. `B-rand ≈ B` on `R_eval` (gain is from reshaping, not fitting).
2. `B ≈ A` within seed noise on `R_eval`.
3. Arm A is far below the released TabPFN v2 at matched compute (straw-man
   baseline ⇒ the A/B is meaningless).
4. Fine-tuning (E3) dominates `π*` fitting both on- and off-distribution.
5. `s(D)` fails to beat the published meta-feature failure baseline in E4 **and**
   E1 shows no gain — i.e. neither deliverable stands.
6. σ-spread of `ℓ_k` exceeds the k-spread at realistic `n` (Warning 2.3 at scale).

Conditions 1 and 3 are new relative to the smoke tests and are the two I most
expect to bite.

## 9. Honest assessment of the paper's ceiling

Best case: a clean, cheap, general method (it applies to *every* PFN — Bayesian
optimization, neural posterior estimation, time series — not just tabular), with
exact math, an artefact people can download, a free diagnostic, and a published
negative result to beat. That is a strong NeurIPS/ICLR paper, plausibly a
spotlight if the real-data gain is large.

Realistic case: gains of 1–3% relative NLL on `R_eval`, mean-positive and
median-neutral, with a strong O1 result carrying the paper. That is an accept,
not a spotlight.

Worst case: kill condition 1 or 4 fires and the contribution collapses to
"Bayesian model averaging over prior hyperparameters helps a little", which is
a workshop paper. **The probability of this is not small — I estimate 30–40%**,
driven mostly by Ob1 and by the real-data-outside-the-family gap (§2 item 1).

## 10. HALT

Cheap validation is complete. The next action is the real-data main experiment
in §6, which is a multi-week commitment of the GPU. **Halting the relay for
approval before starting it.**
