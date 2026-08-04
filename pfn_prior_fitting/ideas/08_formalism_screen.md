# Step 8 — Formalism-replacement screen

## R1 — token entropy vs. pushforward (solution-level) diversity. **DEAD**
The counterexample I was going to build (paraphrase noise ⇒ `H(π)` large,
`H(f_#π)=0`) is correct but it is already the stated premise of published work:
- **DARLING** — learns a *semantic partition of answers* and feeds quality **and**
  diversity into online RL.
- **UCPO** (2605.00365, "Breaking RLVR's Indifference to Diversity") — preserves
  GRPO's total advantage mass but reallocates it toward under-represented
  **correct** responses. That is exactly "regularize the pushforward, not the
  token distribution".
- **Rewarding the Rare** (2601.08763), **Anchored Policy Optimization**
  (2602.05717, support-constrained rectification), **Diversity Collapse via
  Overtraining** (2606.15455), Pass@k-training line.
Criterion 1 satisfied; criteria 3/novelty fail. Kill.

## R3 — verifier-as-program vs. verifier-as-scalar. **DEAD**
- **Execution-Grounded Credit Assignment for GRPO in Code Generation**
  (2603.16158, ICLR 2026 SPOT workshop) — states the exact premise: "a single
  outcome signal is spread uniformly across long programs even when failure
  stems from a localized issue".
- **Murphy** (2511.07833) feedback-aware GRPO with retrospective credit,
  **RLTF** (execution feedback beyond binary), **Process-Verified RL via Lean**
  (2606.20068) with per-tactic → token-level advantage mapping,
  **Self-Conditioned Credit Assignment** (2606.18810),
  **Path-Conditioned Self-Distillation** (2606.15576).
Kill.

## R2 — regret vs. learning-progress potential in UED. **Alive but wrong venue-fit**
The formal defect is real and admitted (stagnation once regret equalizes).
But: (i) UED is a modest RL sub-community, not a NeurIPS-mainstream cell, and
the LLM-side curriculum work does not use minimax regret, so fixing it does not
serve the large constituency; (ii) "learning progress" potentials have existed
since Oudeyer et al., so the delta would have to be entirely in the
non-stagnation proof — i.e. a theory paper, which the user excluded. Park it.

## 8.1 The pattern across 8 steps (this is the actionable finding)

Across every kill, the same residue keeps appearing:

| Cell | What was occupied | What was **not** occupied |
|---|---|---|
| dLLM parallel decoding | dependence-aware selection heuristics | — (even the bound was taken) |
| non-prefix KV reuse | selective-recompute heuristics | **any error bound** |
| branching RLVR rollouts | tree construction, budget allocation | **splitting weights / unbiasedness of the resulting gradient** |
| diversity in RLVR | semantic partitions, advantage reallocation | — |
| structured verifiers | per-test/per-tactic credit | — |

The field reliably ships the *heuristic* and reliably skips the *correctness
argument*. That is a real, repeatable gap and it matches our comparative
advantage (patience, not compute, not speed). **But** a paper of the form "we
add a bound to a known heuristic" is a poster. It becomes top-tier only if the
correctness analysis **reveals a phenomenon the heuristic community has not
seen** — i.e. if the exact treatment *changes what you do*, not merely what you
can prove.

Standing requirement from here on: any candidate must come with a **predicted
observable that the incumbent methods cannot produce**. If I cannot name that
observable before writing code, the candidate is not viable.

## 8.2 Lane not yet examined at all — and it fits our constraints better

Every lane examined so far sits inside frontier-LLM research, i.e. inside the
most compute-rich, most crowded part of the field, where we are structurally
disadvantaged on both speed and scale. There is a mainstream NeurIPS cell that
is *not* in that regime:

**L1 — Amortized / in-context Bayesian prediction (PFNs, TabPFN-style tabular
foundation models).**
- Mainstream at NeurIPS/ICLR; large applied constituency; TabPFN-v2-era work is
  visible and growing, but nowhere near LLM-level crowding.
- **1 A100 is the native scale of this literature**, so for the first time our
  compute is not a handicap — it is the standard.
- The mathematics is exact and load-bearing: a PFN trained on samples from a
  prior `p(D)` has, at its optimum, output equal to the **posterior predictive**
  under that prior. This is an exact statement, not an asymptotic one.
- **The admitted state of practice is manual prior engineering**: the synthetic
  prior (SCM/BNN generators, feature counts, noise models) *is* the entire
  inductive bias, and it is hand-designed by intuition. There is no principled
  procedure for choosing it, and no way to say what a given prior is good for.
- The formalism replacement writes itself: prior design should be **empirical
  Bayes / bilevel optimization over a meta-distribution of real tasks**, and the
  hypergradient is computable because the inner problem's optimum is
  characterized in closed form.

**L2 — Test-time training / adaptation** (cheap, mainstream again post-ARC).
Secondary.

## 8.3 Step 9
Screen **L1** hard: (a) is prior-learning / prior-fitting for PFNs already done;
(b) is the tabular-FM cell prestigious enough for the user's bar; (c) what is
the *predicted observable* (per §8.1) that hand-designed priors cannot produce.
Screen **L2** only if L1 fails.
