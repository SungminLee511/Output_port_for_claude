# Step 2 — Literature kill-screen: dLLM parallel decoding lane

## Verdict: **LANE KILLED.** All front-runners are already published.

### A1 / A4 (TC- or dependence-budgeted parallel unmasking) — DEAD
Directly pre-empted, multiple times, by mid-2026:

- **EB-Sampler** (arXiv:2505.24857, Ben-Hamu et al.) — "Accelerated Sampling
  from Masked Diffusion Models via Entropy Bounded Unmasking": adaptive parallel
  unmasking with an *explicit approximate error tolerance* and an error analysis
  motivating the algorithm. This is my A1 with entropy in place of TC.
- **DEMASK** — lightweight predictor of *pairwise conditional influence* between
  masked positions + **greedy selection under a bounded cumulative dependency
  budget**, with a TV-distance bound under a sub-additivity assumption. This is
  my A1 **and** A5, including the greedy-budget algorithm and the (correctly
  flagged) sub-additivity caveat I had identified as the honest weak point.
- **DAPD** (arXiv:2603.12996) — attention-induced dependency graph, selects
  approximately independent token subsets.
- **DAWN**, **DOS**, **Attn-Sampler**, **Attention-Discounted Adaptive Sampler**
  (arXiv:2606.10829), **Cluster-Level Attention-Guided Parallel Decoding**
  (2605.29607), **Mean-Field Parallel Decoding** (2606.15805), **TACG**
  (2607.03236), **Adaptive Multi-Step Lookahead Decoding** (2607.15655),
  **Improving Sampling for MDMs via Information Gain** (2602.18176).

Note the arXiv numbers: 2602–2607 = Feb–Jul 2026. The idea I generated in one
hour has ~10 competitors published in the last six months. There is no version
of A1/A4 left that is not incremental.

### A2 (any-order self-speculation, lossless parallel decoding) — DEAD
- **"Self-speculative decoding accelerates lossless inference in any-order and
  any-subset autoregressive models"** — ICLR 2026. This is exactly A2.
- **FreeDave** (arXiv:2510.00294) — "Free Draft-and-Verification: Toward
  Lossless Parallel Decoding for Diffusion LLMs", no model modification, no
  extra modules.
- **SimSD** (arXiv:2606.02544), **Dystruct** (2605.09820).

### A3 (dependence-aware remasking) — mortally wounded
Self-correcting masked diffusion (2602.11590) plus the DAPD/DAWN family cover
the selection machinery; a remasking variant is a delta on a delta.

### A6 (adaptive block size) — DEAD
Block Diffusion + HERALD (2606.21633) + d²Cache (2509.23094) occupy this.

## Second-order finding (useful, keep)
The honest-throughput problem is real and acknowledged: early dLLMs use full
bidirectional attention per step and cannot KV-cache; the fair metric is total
output tokens / total wall time, and dLLMs still lag AR on reasoning, long-form
coherence and format adherence. So even a *winning* dLLM decoding paper would be
fighting for the Pareto frontier of a modality that is currently behind. Bad
risk-adjusted bet even before the saturation finding.

## Meta-lesson — this must govern all further idea generation
With ~20–25k submissions/venue, **the obvious next step in a hot area is
already on arXiv within ~3 months.** Idea generation by "find a hot area, find
its obvious gap" is structurally guaranteed to fail. Two survivable strategies
remain:

1. **Attack a shared assumption** that the whole hot area is built on (the
   assumption is invisible precisely because everyone shares it).
2. **Pick a problem whose obvious solution requires doing something annoying**
   (an exact derivation nobody wants to do, or infrastructure nobody wants to
   build). Our comparative advantage is patience, not compute or speed.

Corollary: **do the kill-screen before the math, not after.** Cost of this
lesson: one relay turn. Cheap.

## Next step (Step 3)
Re-screen candidate lanes under the new rule. Priority order to screen:
1. Optimizer / training-dynamics + hyperparameter-transfer geometry (muP-era
   math, modern optimizer stack). Small-proxy evidence is *accepted practice* in
   this subfield ⇒ C4/C6 pass on 1–2 GPUs. Constituency = everyone who trains.
2. Quantization / rotation-based outlier suppression (exact linear-algebra
   content, 1-GPU feasible, but crowded).
3. RL-for-reasoning estimator/credit-assignment math (huge constituency,
   extremely crowded, noisy eval).
4. Guidance in diffusion (CFG is not sampling from any well-defined tempered
   distribution — a genuinely shared, load-bearing wrong assumption).

Screen each for saturation FIRST, then keep at most two for math stress-testing.
