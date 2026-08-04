# Step 5 — Shortlist saturation screen

## T1 — incremental / non-prefix KV reuse with error bounds. **DEAD**
Occupied by a whole systems sub-literature, and CacheBlend is now in ACM TOCS:
- **CacheBlend** (TOCS 2026) — reuses KV "regardless of prefix or not" and
  *selectively recomputes a subset of tokens*; selection = compare recomputed vs
  cached V at layer 2, take top-k discrepancy. That is my selection rule.
- **EPIC**, **KVLink**, **CacheClip** (2510.10129), **ProphetKV** (2602.02579,
  query-driven selective recomputation), **KV Packet** (2604.13226),
  **Leyline** (2606.01065, KV directives for agentic inference),
  **KVEraser** (2606.17034), **Editable/Composable KV** (2606.17107).
Residual gap: none of them has a *bound*, only heuristics (and CacheBlend has a
documented failure band at 30–70% recompute ratio). But "add an error bound to a
crowded systems heuristic" is a workshop paper, not a NeurIPS method paper. Kill.

## T5 — anytime-valid stopping for self-consistency. **DEAD**
- **CITE** (2605.05873) — e-processes, certifies the modal answer under
  *arbitrary data-driven stopping*, no prior knowledge of the answer set.
- **Certified Self-Consistency** (2510.17472) — e-values, finite-sample control
  for all stopping times, SNR-driven compute-adaptive inference.
- **Sequential Information Lift** (2510.06478).
Exactly the claim, three times. Kill.

## T4 — EVT budget allocation. **Deprioritized, not screened**
Adaptive-BoN and reasoning-economy surveys already crowd this; the expected
value of a screening turn is low relative to the survivor below.

## T8 — no-good learning for agents. **Survives, weakly**
No direct hit (searches return agent-memory papers: DeferMem, SSGM, "Where LLM
Agents Fail and How They Can Learn From Failures" 2509.25370, AgentErrorTaxonomy,
Active Context Compression). So the *specific* transfer is not occupied.
But two structural objections, stated against myself:
1. The "monotone pruning guarantee" is only meaningful if the agent's search
   space is a well-defined constraint system. In open-ended agentic tasks it is
   not, so the theorem would be decoration — a direct violation of S2.
2. Agent-benchmark evaluation is a swamp (high variance, harness-sensitive,
   contaminated). C4/C6 are hard to satisfy honestly on 1 GPU.
Keep as fallback only.

## F2 — RLVR support expansion. **The screen produced something better than the
candidate I went in with.**

The *analysis* side is saturated: The Invisible Leash (2507.14843), Pass@k
Inversion (2607.20543), PASS@(k,T) (2604.14877), Breadth–Depth metrics
(2510.08325), Diversity Collapse via Overtraining (2606.15455). So "study
whether RL expands support" is dead — and it was an analysis paper anyway.

But buried in that literature is a **precisely stated, admitted, statistical
failure**:

> "The failure concentrates on **boundary prompts**, where the base model
> contains **rare correct trajectories that are recoverable by sampling but too
> sparse to reliably appear in finite RLVR rollout groups**."

Restated exactly: for a prompt with base success probability `p`, a GRPO group
of size `G` is all-zero with probability `(1−p)^G`. For `p ≲ 1/G` this is the
typical case, so (i) the advantage is degenerate and the gradient is zero, and
(ii) worse, whenever such a prompt *is* mixed with prompts that do produce
signal, the negative-advantage mass on the sampled failures pushes probability
away from the neighbourhood of the rare correct mode. The observed
**support shrinkage** is therefore not mysterious: it is the expected behaviour
of an estimator built on `G` i.i.d. draws applied to a rare event.

This is a **rare-event estimation problem**, and rare-event estimation is a
mature foreign field (G2): Kahn–Harris **importance splitting**, RESTART,
Cérou–Guyader **adaptive multilevel splitting**, subset simulation,
Del Moral's **Feynman–Kac / SMC** unbiasedness theory, Rubinstein's
cross-entropy method. That community routinely estimates probabilities of order
1e−9 with thousands, not billions, of samples — and does so with **exactly
unbiased** estimators.

### New candidate F2′ (promoted to primary)
**Claim (one sentence):** RLVR's failure on boundary prompts is a rare-event
estimation failure, and replacing i.i.d. group sampling with an **adaptive
multilevel splitting** rollout process — branching partial trajectories at
score levels and carrying the exact splitting weights — yields a policy-gradient
estimator that is *unbiased for the same objective* while having exponentially
lower variance on low-`p` prompts, converting all-zero groups into usable
signal at equal token budget.

Why this may survive saturation, stated with the appropriate suspicion:
- Tree/branching rollouts *do* exist in LLM RL (VinePPO, TreePO, prefix-sharing
  in verl). **But their stated motivation is compute sharing or value
  estimation, not rare-event variance reduction, and they do not carry
  splitting weights, so they are biased w.r.t. the on-policy objective.**
  Unbiasedness is the differentiator and it is checkable.
- The target metric is the *documented* failure (pass@k at large k, support
  shrinkage), not pass@1 — so we are not competing on the saturated metric.
- Adoption cost: a change to the rollout sampler only. No new model, no critic.

Why it might still die (to be tested in Step 6):
- Someone may already have done "SMC/splitting rollouts for RLVR" in 2026.
- Unbiasedness of SMC estimators of *normalizing constants* is standard, but
  unbiasedness of the resulting **policy gradient** under adaptive (data-driven)
  level selection is **not automatic** — adaptive levels correlate the
  resampling with the future and can break it. This is the exact point where a
  natural-language proof would be wrong, so it must be done formally.
- Splitting needs a level function (a partial-progress score). If the only
  available score is the model's own confidence, splitting may just amplify a
  miscalibrated signal and produce *correlated* garbage.

## Decision
Survivors: **F2′ (primary)**, **T8 (fallback)**.
Step 6 = saturation screen of F2′ specifically, then formal statement of the
estimator and its unbiasedness/variance claims *before* any code.
