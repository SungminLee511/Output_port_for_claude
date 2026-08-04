# Step 3 — Re-screen of 4 lanes. Result: 4/4 dead. Generator itself is broken.

## Lane 1 — Optimizer / hyperparameter transfer. **DEAD**
- *Deriving Hyperparameter Scaling Laws via Modern Optimization Theory*
  (2603.15958): closed-form power-law schedules for lr/momentum/batch from LMO
  convergence bounds, covering normalized SGD, signSGD, Muon. This is exactly
  the "exact math that derives the tuning rule" slot.
- *Spectral Scaling Laws of Muon* (2606.04058).
- *On the Width Scaling of Neural Optimizers Under Matrix Operator Norms I*
  (2603.09952) — row/column normalization + hyperparameter transfer.
- *Hyperparameter Transfer Enables Consistent Gains of Matrix-Preconditioned
  Optimizers Across Scales* (2512.05620) — Shampoo/SOAP/Muon, finite-width
  deviations from muP already characterized.
- *GQA-µP* (2605.15290).
Nothing left except a delta on finite-width corrections, which also costs the
most compute of any lane. Reject on both novelty and C4/C6.

## Lane 2 — Diffusion guidance. **DEAD**
- *Analytic Distribution of Classifier-Free Guidance for Schedule Design*
  (2607.19725): explicitly states that the CFG-sampled distribution is **not**
  the product-distribution heuristic, and gives **exact analytic path-integral
  representations** of the induced distribution for constant and time-dependent
  guidance. That is precisely the "shared wrong assumption" I intended to
  attack, already attacked, already exactly.
- *Improving CFG in Masked Diffusion* (2507.08965); *Information-Theoretic CFG*
  (2606.24025).

## Lane 3 — RL-for-reasoning estimators. **DEAD (multiple hits)**
- Deployed-decoder / distribution mismatch: *Analysis of On-policy Policy
  Gradient Methods under Distribution Mismatch* (2503.22244); *Revisiting
  On-Policy Distillation* (2603.25562) already uses truncated top-K support
  matching + top-p rollouts; *Self-Distilled Policy Gradient* (2606.04036).
- Variance reduction by coupling: **Coupled-GRPO** already applies antithetic
  variates with complementary masks and proves unbiased variance reduction;
  **Dropout-GRPO** (2606.10184) already uses common-random-numbers mask replay;
  **VRPO** already shares batches between current and reference model as
  antithetic sampling; **BASIS** (2605.27293) shares information across
  rollouts for advantage estimation.
- Curvature/normalization: *Why GRPO Needs Normalization* (2601.23135).

## Lane 4 — Rotation/quantization. Not searched. Deprioritized:
even without a search, the QuaRot/SpinQuant/Hadamard line has ~2 years of dense
follow-up and the remaining deltas are ≤0.2 ppl at 4-bit. Prior probability of
an unoccupied, load-bearing gap is low enough that spending a turn is
-EV relative to fixing the generator.

## The real finding of Steps 2–3

Six independent, carefully-chosen "hot area + non-obvious gap" ideas were each
pre-empted, usually within the preceding 6 months, usually by 2–10 papers.
This is not bad luck. The mechanism:

> The set of ideas reachable by "take a hot area, find the sharpest gap a
> competent person would find" is exactly the set of ideas that ~20k submitters
> — most now using the same LLM-assisted ideation — also reach. Saturation of
> that set is structural, not incidental.

So the generator must be changed, not retried. Retrying it is the definition of
insanity and would burn the relay budget.

## New generation procedure for Step 4 (three independent generators)

**G1 — Mine admitted failure.** Do not search for gaps; search for *explicit
statements of failure* by strong groups: limitations sections, "we were unable
to", negative-result papers, workshop position papers, and reproducibility
reports from mid-2026. A problem that a strong group publicly failed at is
(a) real, (b) has a constituency, (c) is by construction not easy, so it is not
in the saturated set.

**G2 — Cross-community primitive transfer.** Enumerate mature primitives from
fields that do not co-attend with ML (numerical analysis, coding theory,
survey sampling / experimental design, queueing, formal verification,
compilers, computational geometry) and ask which mainstream ML bottleneck has
the *exact structural signature* that primitive solves. Transfers survive
saturation because they are not reachable from inside the ML literature.

**G3 — Universal implementation details that are wrong.** The highest-impact
2025–26 papers of this genre (e.g. training/inference numerical mismatch making
"on-policy" RL secretly off-policy; loss-normalization across variable-length
sequences) share a signature: a detail every implementation gets wrong the same
way, invisible because it is in the framework, not the algorithm. Enumerate
candidate details and check which are still unexamined.

**Constraint carried forward:** whatever survives must still be runnable on
1×A100 (more GPUs obtainable only if *absolutely necessary*), must be a
methodology paper, and must not be an analysis/probing paper.

## Also recorded: an unusual resource we have
96 CPU cores and 866 GB RAM alongside one A100. This is a *lopsided* machine.
Methods that trade GPU work for large-memory CPU-side exact computation
(exact retrieval/attribution over a full corpus, huge replay buffers, exact
combinatorial selection) are cheap for us and expensive for a typical 8×GPU
lab node with 200 GB RAM. Any candidate that exploits this asymmetry gets a
bonus, because it is annoying for others to reproduce and natural for us.
