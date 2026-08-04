# Step 13 — Smoke test S02 (NPMLE, mixture prediction, O1). **Mixed. One result
# is very good, one is quietly damaging, and it is the one the paper is named
# after.**

Script: `smoke/s02_npmle_mixture.py`. **Zero retraining** — the S01 network is
used as-is (deployment mode M1). Protocol: n = 64 rows, score `ℓ_k` on rows
0–47 only, evaluate predictive loss on rows 48–63. No eval-row label is used to
select `k`, so the selection is honest.

## 13.1 T-D — NPMLE. **Does not fire. Clean positive.**
Corpus: 400 datasets drawn with a deliberately uneven `π_true`.
```
π_true = [0.10, 0.15, 0.50, 0.25]      (linear, mlp, tree, rbf)
π*     = [0.096, 0.169, 0.479, 0.255]  TV distance 0.040, entropy 1.227 nats
```
The EM of Corollary 5.1 recovers the mixing distribution to within 4% total
variation, from forward passes alone, and is **not degenerate** (max atom 0.479,
entropy 1.227 vs 1.386 for uniform). Recovery holds despite the linear/mlp
non-identifiability found in S01 — as predicted in §12.2, the soft readout is
robust to what the hard `argmax` gets wrong.

## 13.2 The predictive claim (Remark 5.2(b)). **Real, but small, and the
## decomposition is bad news for the contribution.**

Held-out eval-row loss, nats/row, 400 datasets:

| predictor | loss |
|---|---|
| per-dataset oracle `min_k` (upper bound, not attainable) | 0.4753 |
| **NPMLE mixture `q^{mix,π*}`** | **0.5071** |
| uniform mixture `q^{mix,1/K}` | 0.5081 |
| best single fixed `k` globally (`tree`) | 0.5208 |
| worst fixed `k` | (see json) |

Read this the way a hostile reviewer will:
- Mixing beats the best single prior by **0.0137 nats/row**, i.e. it closes
  **30%** of the oracle gap (0.0455). That part works.
- **Fitting `π` beats uniform `π` by 0.0010 nats/row.** That is ~7% of the
  mixing gain and ~2% of the oracle gap. **With K = 4, the entire empirical-Bayes
  contribution is numerically negligible**; Theorem 4's `log K` slack is 1.39
  nats total, i.e. 0.029 nats/row over 48 score rows, so uniform has almost
  nothing to lose. The NPMLE — the piece the paper is named after — is currently
  decoration on top of a mixture that does the real work.
- Worse for statistics: the NPMLE mixture beats the globally-best fixed `k` on
  only **47.8%** of datasets, while winning **on the mean**. The gain lives in
  the tail (datasets where `tree` is badly wrong). A Wilcoxon signed-rank or
  sign test on per-dataset wins would **not** reject. This is threat T-E arriving
  early and it must be confronted, not hidden: the honest framing is
  "large improvement on the datasets where the default prior is wrong, no change
  elsewhere", and the evaluation must be designed to expose that (per-dataset
  scatter, tail quantiles) rather than a mean.

**Consequence for the research plan.** The NPMLE only earns its place when
`log K` is a real cost, i.e. when `K` is large and `π_true` is peaked. That is
also the realistic regime — real PFN priors are indexed by many continuous
hyperparameters. If the NPMLE-vs-uniform gap does not grow with `K`, the paper
reduces to "Bayesian model averaging over prior hyperparameters", which is
true, useful, cheap — and much less than claimed. **This is now the single most
important open question and it is cheap to test.**

## 13.3 O1 — out-of-family detection. **Works, and is the strongest result so
## far.**
Score = `(1/48) log Σ_k π*_k exp(ℓ_k^{rows 0..47})`, label-free with respect to
every evaluated row.

| family | AUC vs in-family | mean score | eval loss |
|---|---|---|---|
| in-family | — | −0.5642 | 0.5071 |
| periodic (high-freq sinusoid) | **0.929** | −0.7281 | 0.7065 |
| discrete/XOR covariates | **0.870** | −0.7010 | 0.6495 |
| 35% label noise | **0.936** | −0.7303 | 0.7114 |

The score ordering matches the eval-loss ordering exactly across all four
families. This is O1/O4: a model-intrinsic, label-free-at-test statistic that
predicts where the PFN will be bad, which is precisely what 2605.28418 showed
dataset-level meta-features **fail** to do.

Caveat that must be stated in the paper: `discrete_xor` also changes `p(x)`, so
for that family the Theorem-2 partial-likelihood caveat is live and part of the
separation may come from covariate novelty rather than from conditional-model
misfit. The two must be disentangled experimentally (score with `y` shuffled as
a control).

## 13.4 Step 14
**S03 — scale `K`.** Replace the 4 hand-built components with a continuous
hyperparameter vector `θ` (component type × depth/width × noise level ×
feature-relevance sparsity) discretized to `K ∈ {4, 16, 64}`, retrain the
θ-conditional PFN once with continuous θ-conditioning, and measure:
1. NPMLE-vs-uniform gap as a function of `K` — does it grow?
2. Per-dataset win rate vs best fixed `k` as a function of `K`.
3. Whether `π*` stays non-degenerate as `K` grows (NPMLE should sparsify to
   a few atoms — that is the Kiefer–Wolfowitz behaviour and is *good*, unlike
   collapse to one atom).
If (1) is flat, the empirical-Bayes framing must be demoted and the paper
re-centred on O1 + mixture averaging.
