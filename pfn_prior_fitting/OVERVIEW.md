# Fitting the Prior of a Prior-Data Fitted Network — overview

Everything below was produced in a 16-step relay: literature screening → idea
generation → formal setup → four smoke tests on 1×A100. **No real-data
experiment has been run yet.** This document exists so the plan can be attacked
before ~300 GPU-hours are spent on it.

Read order: `notes/00_criteria.md` → `ideas/*.md` (chronological) →
`math/01_setup.md` → `notes/20_plan.md`.

---

## 1. The claim

> The synthetic prior of a prior-data fitted network (PFN / TabPFN) can be
> **fitted** to real data — by scoring a θ-conditional PFN prequentially and
> solving a convex NPMLE for the mixing distribution over prior hyperparameters
> — and retraining on the fitted prior yields a strictly better tabular
> foundation model, together with a label-free statistic that predicts where
> that model will fail.

### Why anyone should care
A PFN's entire inductive bias **is** its synthetic prior. Today that prior is
hand-designed by intuition; the literature says so in its own words
(*"performance depends on the alignment between the prior and the target task,
motivating careful prior design"*). There is no procedure for choosing it and no
way to say what a given prior is good for. This turns prior design from taste
into a convex optimization problem with a computable objective.

### The two deliverables
- **M2 (training-time)** — refit the prior, retrain once, ship a strictly better
  checkpoint. Drop-in.
- **M1 (inference-time)** — a zero-cost Bayesian mixture over prior
  hyperparameters, plus `s(D) = (1/n) log Σ_k π*_k exp(ℓ_k(D))`, a statistic that
  uses **no test-row label** and predicts failure.

---

## 2. How the idea was found (and 10 that were killed first)

| step | lane | verdict |
|---|---|---|
| 2 | dLLM parallel decoding | dead — pre-empted, incl. the bound |
| 3 | optimizer/µP transfer, CFG guidance, RLVR estimators | dead ×3 |
| 5 | non-prefix KV reuse, anytime-valid stopping | dead |
| 6 | adaptive multilevel splitting for RLVR | dead — **by my own algebra**, see below |
| 8 | RLVR diversity on the pushforward; verifier-as-program | dead ×2 |
| 8 | UED regret potential | parked (wrong constituency) |
| 9–10 | **amortized Bayesian prediction (PFN)** | **survives** |

Step 7 records the honest conclusion after 7 turns: *every* cell reachable by
(mainstream) × (methodology) × (1 GPU) is occupied, so hunting empty territory
is a losing strategy. The strategy switched to finding a **crowded cell whose
occupants share a formalism about the wrong object**.

**A mistake I made and caught** (`ideas/06_f2prime_screen.md`): I claimed RLVR
support-shrinkage was a rare-event *estimation* failure. Differentiating
symbolically, `∇_θ p(x) = p(x)·E_{y~π(·|x,R=1)}[∇_θ log π]` is `O(p)` — negligible
*in expectation* — so lower-variance estimation cannot help. Rule adopted:
**differentiate the mechanism before believing it.**

---

## 3. The math (`math/01_setup.md`) — every claim tagged EXACT or APPROX

Prequential score, for an ordering σ of a dataset `D`:

```
ℓ_σ(q; D) := Σ_{i=1..n} log q( y_{σ(i)} | x_{σ(i)}, D_{σ(<i)} )
```

- **Thm 1** — the PFN pretraining objective is minimized exactly by the
  posterior predictive under the prior.
- **Thm 2 + Warning 2.2** — a correction to my own earlier phrasing:
  `exp(ℓ_id) = P(D)/Π_i P(x_i|D_{<i})`, a **partial likelihood**. *"The PFN gives
  you the marginal likelihood of the dataset under its prior" is **false as
  stated***, because the prior also generates the covariates.
- **Warning 2.3** — real PFNs are not order-coherent; the σ-spread is a
  measurable defect and must be reported, not hidden.
- **Thm 3 (EXACT, no assumptions)** —
  `ℓ_σ(q^{mix,π}; D) = log Σ_k π_k exp(ℓ_k(D))`.
- **Thm 4 (assumption-free)** — `ℓ_σ(q^{mix,π};D) ≥ ℓ_k(D) + log π_k`; with
  uniform π, within `log K` of the best hyperparameter in hindsight, with **no
  assumption on the data-generating process and no assumption that the networks
  are Bayes-optimal.**
- **Thm 5 + Cor 5.1** — `F(π) = Σ_m log Σ_k π_k L_{mk}` is concave on the
  simplex (Kiefer–Wolfowitz NPMLE); EM update given. No bilevel loop, no
  hypergradients, no retraining inside the loop.
- **§7** — naive prequential scoring is `Θ(n³)`; a causal row mask gives all `n`
  terms in one forward pass, `Θ(n²)`.

---

## 4. Smoke tests (4 experiments, ~2 GPU-hours, all on synthetic data)

### S01 — does the score recover the prior? (`smoke/s01_theta_recovery.py`)
K=4 components, n=64 rows, covariate law held identical across components so
Warning 2.2 is inert and any failure is the network's fault.

| quantity | value | required |
|---|---|---|
| θ-recovery accuracy `argmax_k ℓ_k = k*` | **0.703** | ≫ 0.25 chance |
| σ-spread / k-spread | **0.134** | ≪ 1 |
| k-spread (nats/row) | **0.045** (~7% of base loss) | ≫ 0 |

Negative finding: `mlp` datasets are assigned to `linear` 23/64 times. The
components are genuinely **non-identifiable** (a small-weight tanh MLP *is*
approximately linear). Hard-argmax attribution is therefore weak; the soft NPMLE
readout is the right one, and Thm 4 never needed identifiability.

### S02 — NPMLE, prediction, failure detection (`smoke/s02_npmle_mixture.py`)
Zero retraining. Score on rows 0–47, evaluate on rows 48–63; no eval-row label
is ever used to pick `k`.

```
π_true = [0.10, 0.15, 0.50, 0.25]
π*     = [0.096, 0.169, 0.479, 0.255]      TV = 0.040, not degenerate
```

Out-of-family detection by the label-free score:

| family | AUC | eval loss |
|---|---|---|
| in-family | — | 0.507 |
| high-frequency periodic | **0.929** | 0.706 |
| discrete/XOR covariates | **0.870** | 0.649 |
| 35% label noise | **0.936** | 0.711 |

Score ordering matches eval-loss ordering exactly. This is the thing
dataset-level meta-features were *published as failing to do*
(arXiv 2605.28418, leave-one-dataset-out on TabArena).

**But**: mixing beat the best single prior by 0.0137 nats/row while *fitting* π
beat *uniform* π by only **0.0010**. At K=4 the empirical-Bayes piece is
decoration.

### S03 — scale K: the pre-registered kill test (`smoke/s03_scale_K.py`)
Continuous 7-dim θ, one network, grids K = 4/16/64 evaluated without retraining.

| K | uniform mix | NPMLE mix | **gap** | theory `(log K − H)/48` |
|---|---|---|---|---|
| 4 | 0.5327 | 0.5276 | 0.0051 | 0.0150 |
| 16 | 0.5223 | 0.5164 | 0.0060 | 0.0292 |
| 64 | 0.5225 | 0.5161 | **0.0063** | 0.0534 |

The gap grows **1.24×** while K grows **16×**. Flat. The kill condition I wrote
down in advance fired, and I demoted the claim. The mechanism is exact:

> In the sequential mixture the log-weight of atom `k` is `log π_k + ℓ_k`. Atoms
> differ by `Θ(n)` in the data term and only `O(1)` in the prior term. **So
> inference-time (M1) dependence on the fitted prior is intrinsically an
> `O(1/n)` effect.**

Not an engineering shortfall — it is what the identity says. A reviewer who
reads Thm 3 kills that claim in one line, so the paper says it first.

### S04 — the decisive M2 test (`smoke/s04_m2_retrain.py`)
3 arms × 2 seeds = 6 *unconditional* PFNs, identical architecture / steps /
optimizer / seeds; **only** the pretraining θ-law differs.

| arm | pretraining prior | corpus NLL | ±seed | corpus ACC | broad NLL |
|---|---|---|---|---|---|
| A | π₀ broad — "TabPFN as shipped" | 0.5304 | 0.0001 | 0.7252 | **0.5322** |
| **B** | **π\* NPMLE fit — ours** | **0.5185** | 0.0001 | **0.7331** | 0.5352 |
| C | true corpus law — oracle | 0.5180 | 0.0002 | 0.7352 | 0.5364 |

- **B recovers 96% of the oracle's gain** having never seen the true law — only
  600 datasets and forward passes.
- Effect is **60–120× the seed SD**; paired win rate **59.8%** over 800 datasets
  (sign test z ≈ 5.5). **The first result in the project that survives a paired
  per-dataset test** — M1 never did (47.8%, 52%).
- **No free lunch, and the data says so**: off-corpus, B is *worse* by 0.0030.
  Honest statement — *π\* buys 96% of the oracle's on-corpus gain at 73% of its
  off-corpus cost*, a ~4:1 trade, and π\* sits on a better point of the
  trade-off curve than the true law does.

### Threat register
| threat | result |
|---|---|
| T-A score dominated by network error | survived |
| T-B θ-conditioning ignored | survived |
| T-D NPMLE collapses to one atom | survived (`e^H` ≈ 5 of 64) |
| T-E gains inside seed noise | **fires for M1** (demoted), does **not** fire for M2 |
| Warning 2.3 order incoherence | measurable, 3.7× below the signal |
| **T-C / Ob1 fine-tuning dominates** | **untested — still the strongest objection** |

---

## 5. The main experiment (`notes/20_plan.md`) — not yet run

- **θ**: ~12 exposed hyperparameters of a TabPFN-v2-style SCM/BNN prior
  (structure, activations, noise families, categorical fraction, missing rate,
  class law…). K ≈ 512 atoms by scrambled Sobol.
- **Data discipline** (the thing that decides credibility): three *disjoint*
  pools — `R_fit` (~200 datasets, prior fitting only), `R_dev` (~30, all
  development decisions), `R_eval` (TabArena, final numbers only). Dedup by
  OpenML id **and** content hash; report how many datasets dedup removed.
- **E1 controlled A/B**: `π₀` vs `π*` vs **`π`-random at matched entropy** vs
  single-best-atom vs oracle. The random-π control decides whether the gain is
  from *fitting* or merely *reshaping*; it did not exist in the smoke tests.
- **E2**: TabPFN v2 / 2.5 / Real-TabPFN-2.5, tuned CatBoost/XGBoost/LightGBM,
  AutoGluon; plus continued pretraining of the *released* checkpoint on π*.
- **E3**: head-to-head vs fine-tuning at matched real-data budget, on- and
  off-distribution.
- **E4**: abstention/routing, vs the published meta-feature baseline, with a
  y-shuffled control separating covariate novelty from conditional misfit.
- **E5**: sample-complexity of prior fitting (`|R_fit|` ∈ 25…200) — a plot
  nobody currently has.
- ≥3 seeds, Wilcoxon + sign tests, Holm correction, CD diagrams, **per-dataset
  scatter** (because both M1 results were mean-positive / median-neutral).

**Compute**: ≈300–400 GPU-hours ≈ 2 weeks on one A100. This lane was chosen
*because* 1 GPU is its native scale. More GPUs buy more seeds and a scale
ladder — useful, not necessary.

### Pre-registered kill conditions
1. random-π ≈ fitted-π → gain is reshaping, not fitting.
2. B ≈ A within seed noise on `R_eval`.
3. Arm A far below released TabPFN v2 at matched compute → straw-man baseline.
4. Fine-tuning dominates both on- and off-distribution.
5. `s(D)` fails to beat the meta-feature baseline **and** E1 shows no gain.
6. σ-spread exceeds k-spread at realistic `n`.

(1) and (3) are the two most likely to bite.

---

## 6. Self-assessment

- **Best case** — a cheap, general method (applies to *every* PFN: Bayesian
  optimization, neural posterior estimation, time series), exact math, a
  downloadable artefact, a free diagnostic, a published negative result to beat.
  Strong NeurIPS/ICLR paper; spotlight if the real-data gain is large.
- **Realistic** — 1–3% relative NLL on `R_eval`, mean-positive/median-neutral,
  with the failure-prediction result carrying the paper. Accept, not spotlight.
- **Worst** — kill condition 1 or 4 fires and it collapses to "model averaging
  over prior hyperparameters helps a little". Workshop paper.
  **I put this at 30–40%.**

The two things most likely to break it: real tabular data lies **outside** any
synthetic family, so the NPMLE fits a projection rather than recovering
anything; and fine-tuning on real data may simply dominate.
