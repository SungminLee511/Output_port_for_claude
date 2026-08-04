# Step 1 — Lane choice + candidate generation

## Lane decision (defended)

Chosen lane: **inference-time algorithms for masked diffusion language models
(dLLMs)**, with a fallback lane of **optimizer/training-dynamics at 100–500M**.

Why this lane and not the others, stated as elimination:

- **Optimizer lane (d).** Constituency is large (Muon/SOAP/Scion era) but the
  bar is now "show it at ≥1B on a real token budget with equal tuning". On
  1 A100 a 1.3B × 20B-token run is ~2–4 weeks. We would be running exactly one
  such run, with one seed. C4 and C6 both fail. Reject unless the dLLM lane
  dies.
- **Diffusion/flow sampler lane (c).** Exact math is abundant (exponential
  integrators, local truncation error) but the space is saturated
  (DPM-Solver++/UniPC/DEIS/AMED/…) and the remaining gains are ≤1 FID at
  ≥10 NFE. S1 (obvious-in-hindsight) is nearly impossible now. Reject.
- **Post-training lane (b).** RLHF/DPO variants: evaluation is noisy
  (LLM-as-judge), the field is crowded, and equal-compute baselines require
  several 7B runs. C4/C6 marginal. Reject.
- **Test-time RL for reasoning.** Crowded, benchmark-saturated, and gains are
  inside seed noise at our scale. Reject.
- **dLLM inference (a).** (i) Train-free ⇒ we use the *same public checkpoints*
  as any industrial lab, so our evidence is not structurally weaker (this is
  the key point: it neutralizes our compute disadvantage). (ii) The core
  algorithmic question — *how many and which masked positions may be unmasked
  simultaneously* — is currently answered by heuristics (top-k confidence,
  confidence threshold, entropy threshold). (iii) The correct answer has an
  **exact information-theoretic characterization** (below) that is load-bearing,
  not decorative. (iv) The metric (accuracy vs. wall-clock / NFE) is
  unfudgeable. (v) The mechanism predicts its own failure modes.

**Known risk, stated up front:** the dLLM literature routinely compares against
weak autoregressive baselines and reports NFE instead of wall-clock. A single
A100 makes an honest AR baseline (KV-cache, vLLM/flash-attn) *easy* to run, so
we must run it and we will probably show dLLMs are still behind on wall-clock in
some regimes. That honesty is required by C4/S5 and is itself a selling point,
but it constrains the claim we are allowed to make.

## The exact structure that makes this lane worth it

Let `c` be the current partially-unmasked sequence and `S` a set of masked
positions we intend to unmask in one step. A masked diffusion model gives the
marginals `p(x_i | c)` for every `i ∈ S`, and standard parallel decoding samples

    q_S(x_S) = Π_{i∈S} p(x_i | c).

The true model joint is `p(x_S | c)`. Then, exactly (no assumptions):

    KL( p(x_S | c) ‖ q_S ) = TC(S | c)   [total correlation / multi-information]

and, exactly, for any `j ∉ S`:

    TC(S ∪ {j} | c) − TC(S | c) = I(X_j ; X_S | c) ≥ 0.

So TC is monotone non-decreasing in `S`, and the *exact* marginal cost of adding
a position to the parallel set is its multivariate mutual information with the
set. This immediately yields a greedy "unmask while the accumulated dependence
budget is not exhausted" algorithm whose stopping rule is *derived*, not tuned.
Confidence- and entropy-thresholding are exactly the special case that ignores
`I(X_j ; X_S | c)` and uses `H(X_j | c)` instead — and `H` and `I` are
uncorrelated in the cases that matter (two positions can each be 99% confident
and perfectly coupled, e.g. subject–verb agreement, a repeated identifier, or
the two halves of a carried digit).

Everything above is exactly true. The hard part — and the part that will decide
whether this is a paper — is **estimating `I(X_j ; X_S | c)` without paying more
compute than parallel decoding saves.** That is the real research problem.

## Candidate list (to be kill-screened against the literature next step)

| # | One-sentence claim | Main risk |
|---|---|---|
| A1 | Parallel-decoding error in dLLMs *is* the total correlation of the unmasked set; a TC-budgeted greedy selector dominates confidence/entropy thresholds on the accuracy–throughput Pareto. | Estimating TC cheaply; possibly published (entropy-bounded samplers). |
| A2 | **Any-order self-speculation:** because a masked diffusion model defines *all* orderings, a proposed parallel block can be *exactly* verified in **one batched forward pass** (batch = block size), giving lossless parallel decoding with an output distribution provably equal to the model's own sequential any-order distribution. | Wall-clock: batch-k forward costs ~k× FLOPs on a full-sequence bidirectional model. Must beat naive. Possibly published. |
| A3 | Dependence-aware **remasking**: choose the remask set to maximally reduce accumulated TC, converting dLLM self-correction from a heuristic into an error-repair step with a stated objective. | Weak baselines exist; effect may be small. |
| A4 | The confidence heuristic is *systematically* wrong in a predictable direction (high-confidence, high-coupling positions), and a single cheap probe (one extra batched forward with sampled fills) recovers most of the oracle gap. | Probe cost. |
| A5 | Learned dependence head: a small frozen-backbone head predicts `I(X_j;X_S|c)` from existing hidden states at ~0 inference cost. | Adds a training artifact ⇒ adoption cost > 0 (violates C5 partially). |
| A6 | Adaptive AR/diffusion hybrid: derive block size from the same TC budget. | Incremental. |
| B1 | Muon-family: identify the exact invariance the orthogonalized update enforces and derive a corrected preconditioner. | Compute; crowded. |
| B2 | Equal-compute AR-vs-dLLM law. | Analysis paper — excluded by user. |

Front-runners: **A2** (strongest formal content + zero adoption cost) and
**A1/A4** (strongest mechanism story). A2 and A1 compose: A1 selects the block,
A2 certifies it.

## Next step
Literature kill-screen: find whether (i) entropy/confidence-bounded parallel
unmasking with guarantees, (ii) any-order self-speculative verification for
dLLMs, (iii) mutual-information-based unmasking already exist. Kill on sight.
