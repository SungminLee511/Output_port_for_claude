# Step 9 — Lane L1 screen: amortized Bayesian prediction (PFN / TabPFN)

## 9.1 Occupancy of the lane
Active but **structurally different from every lane screened so far**: the
follow-up work is *extensions* and *scaling*, not competition on the core
formalism.
- Extensions: MultiModalPFN (2602.20223), State-Space PFN backbone (2510.14573),
  TabClustPFN (2601.21656), TabImpute (2510.02625), TabPFN-TS (2501.02945),
  α-PFN for entropy search (2606.07134), PFNs as summary nets for neural
  posterior estimation (2605.07765), graph tabularization (2512.08798).
- Scaling: TabPFN-2.5 (2511.08667) — 50k rows × 2k features, leads TabArena;
  and **Real-TabPFN-2.5**, i.e. *fine-tuned on real data*.
- Context/adaptation: TuneTables (NeurIPS 2024), retrieval-based local context.
- Evaluation: "A Closer Look at TabPFN v2" (2502.17361), "Realistic Evaluation
  in Open Environments" (2505.16226).

**No hit** for: learning/fitting the prior, empirical Bayes over the prior,
bilevel prior optimization, or measuring prior–task alignment. The literature's
own words: *"Performance depends on the alignment between the prior and the
target task, motivating careful prior design"* — i.e. the alignment is
acknowledged as decisive and is handled **by hand**.

## 9.2 The predicted observable (the §8.1 gate)

This is the part that decides viability, so it is stated exactly.

Let the prior be `P` over datasets `D = (x_{1:n}, y_{1:n})`. The PFN pretraining
objective is minimized (over all measurable functions) exactly by the posterior
predictive under `P`:

    q*(y | x, D_{<i}) = p_P(y | x, D_{<i}).

By the chain rule, for any fixed ordering `σ` of a real dataset `D`,

    log p_P(y_{σ(1:n)} | x_{σ(1:n)}) = Σ_{i=1}^{n} log p_P(y_{σ(i)} | x_{σ(i)}, D_{σ(<i)}).

Both sides are **exact** — this is the prequential (Dawid) identity, not an
approximation. Therefore a trained PFN, run once in its ordinary in-context
mode, *already emits* an estimator of the **log marginal likelihood of a real
dataset under its own prior**, at zero additional cost and with no extra
machinery.

Consequences, each of which is an observable that hand-designed-prior practice
cannot produce:

**O1 (failure prediction).** `log p̂_P(D)` should predict, across real datasets,
where the PFN is miscalibrated / beaten by GBDT. Hand-designed priors give no
such score; current practice detects failure only *after* evaluation on labels.

**O2 (prior criticism / attribution).** Because the prior is a composition of
components (SCM depth, activation set, noise model, feature-type mixture), the
same score differences attribute misfit **to specific prior components**,
giving a directed edit to the prior rather than intuition.

**O3 (empirical Bayes).** The natural objective for prior design is
`max_P E_{D~Q_real}[ log p_P(D) ]`, which by the identity above is directly
measurable. So "prior design" stops being taste and becomes an optimization
problem with a computable objective.

**O4 (self-predicted failure mode, required by S4).** Datasets whose score stays
low after prior fitting are exactly those the method should *abstain* on. A
correct method must therefore ship a routing rule that fires on a
label-free statistic — and we can test whether it fires where it should.

## 9.3 Why this lane fits our constraints better than anything screened so far
- **1×A100 is the native scale.** PFN research trains models of ~10–100M
  parameters on synthetic data; this is the standard, not a handicap. For the
  first time, our compute is not a structural disadvantage.
- Baselines are strong, public, and cheap to run honestly (TabPFN v2/2.5,
  CatBoost/XGBoost/LightGBM tuned, AutoGluon). C4 is *satisfiable*, which was
  false in every LLM lane.
- ≥3 seeds over ~300 datasets is affordable ⇒ C6 satisfiable.
- Adoption cost of the score is literally zero (§9.2). C5 satisfied.

## 9.4 Objections to state now, before any enthusiasm

**Ob1 — "Just fine-tune on real data" (Real-TabPFN-2.5 already does this).**
This is the strongest objection and it comes from the incumbent. Answer to be
tested, not asserted: fine-tuning consumes the small finite supply of real
tabular datasets, risks benchmark contamination, and *destroys* the
posterior-predictive interpretation (the model no longer corresponds to any
prior), whereas prior fitting keeps an unlimited synthetic sampler and keeps
the interpretation. If experiments show fine-tuning dominates prior fitting on
held-out real data, the paper is dead; this must be tested **early**.

**Ob2 — the identity holds at the optimum, and PFNs are not optimal.**
`q ≠ p_P` in practice, so `Σ log q` is a biased estimate of `log p_P(D)`.
Worse, real PFNs are **not order-coherent** (the sum depends on `σ`), so the
"marginal likelihood" is not well defined for the actual model. This must be
handled honestly: average over permutations, report the spread, and treat the
order-dependence as a measurable defect rather than hiding it. There is a real
risk that the score is dominated by *model* error rather than *prior* misfit,
which would break O1–O3. **This is the single most likely way the idea dies and
it is cheap to test on 1 GPU.**

**Ob3 — bilevel cost.** Naive empirical Bayes requires re-pretraining the PFN
for every prior update. Candidate escapes: (a) importance-reweighting of prior
samples so a *single* pretraining supports a family of priors; (b) train a
prior-conditional PFN that takes prior hyperparameters as an input token and
amortizes over the prior family. Both need checking for correctness, not just
plausibility.

**Ob4 — prestige.** Tabular is sometimes read as applied. Mitigation: the paper
must lead with the amortized-inference/model-criticism formalism (which applies
to *all* PFNs — Bayesian optimization, neural posterior estimation, time series),
not with tabular benchmark numbers.

## 9.5 Step 10
Focused saturation check on the *specific* claim, not the lane:
prequential/marginal-likelihood scoring of PFNs; "when does TabPFN fail"
predictors; model criticism for amortized inference / simulation-based
inference (the SBI community *does* have model criticism — that is the most
likely pre-emption and must be checked hard); empirical Bayes for PFN priors.
