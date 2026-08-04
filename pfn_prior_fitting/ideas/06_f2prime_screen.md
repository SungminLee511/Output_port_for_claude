# Step 6 — F2′ screen. Verdict: **DOWNGRADE (do not build).**
Two independent reasons: the branching machinery is occupied, and — more
importantly — **my stated mechanism was partly wrong.** The second reason is the
valuable one, so it is written out in full.

## 6.1 Occupancy
Not a clean kill, but dense:
- **TreePO** — shared-prefix rollout tree, hierarchical advantage at each
  branching depth.
- **Branching Policy Optimization** (2607.14171), **TreeAdv** (2601.03703,
  tree-structured advantage redistribution), **GraphPO** (2606.18954),
  **Tree Search for LLM Agent RL** (2509.21240).
- **TRACE** (2606.11119) — unified *rollout budget allocation*, allocates
  branches to prefixes predicted informative rather than uniformly.
- **Submodular view of tree search for tool-use RL** (2605.05262).
- **VinePPO** — branch from partial states for value estimation.
- Explicitly noted in that literature: prefix branching "can reduce the number
  of effective GRPO groups that provide non-zero learning signal" — i.e. the
  all-zero-group problem is already a discussed object.
What is *not* found: splitting **weights**, unbiasedness of the resulting
gradient, or the rare-event framing. So the delta would be "add importance
weights to TreePO". That is a correctness improvement, not a paper.

## 6.2 The mechanism error (the part worth keeping)

I claimed: *support shrinkage happens because all-zero groups make the estimator
miss rare correct modes, and lower-variance estimation of the same objective
would fix it.* Checking this against the definitions kills it:

Let `p(x) = P_{y~π_θ}(R(x,y)=1)`. Then exactly

    ∇_θ p(x) = p(x) · E_{y ~ π_θ(·|x, R=1)}[ ∇_θ log π_θ(y|x) ].

So for a boundary prompt the **true** gradient of the standard objective is
`O(p)` — vanishingly small **in expectation**, not merely hard to estimate.
Estimating a negligible quantity with lower variance does not make the optimizer
care about it. The standard RLVR objective is *specified* to ignore boundary
prompts; this is not an estimator defect.

Second correction: GRPO zeroes out all-equal groups (std → 0, and such groups
are usually filtered), so all-zero groups contribute **no** negative pressure.
The observed support shrinkage therefore cannot be attributed to them. It comes
from a **global** entropy/diversity contraction driven by the prompts that *do*
produce signal — a different phenomenon with a different fix. My Step-5 story
conflated the two.

**Rule extracted:** before adopting a mechanism, differentiate the relevant
quantity symbolically. The error above is invisible in natural language
("rare successes get lost in the noise") and obvious in one line of algebra.

## 6.3 The one formally correct object recovered from this line

If the goal really is *learn from rare successes*, the objective must be
`log p(x)`, not `p(x)`, because by the identity above

    ∇_θ log p(x) = E_{y ~ π_θ(·|x, R=1)}[ ∇_θ log π_θ(y|x) ],

which is `O(1)` in `p`. This is exactly Fisher's identity, and it says something
sharp: **maximizing log-success is exactly maximum likelihood on samples from
the success-conditioned posterior** — i.e. rejection-sampling fine-tuning
(STaR / RAFT / ReST-EM) *is* the exact gradient of log-success, and advantage-
based RLVR is not.

That is correct, but it is also known (STaR-as-EM is established), and the
remaining hard part — sampling the success-conditioned posterior when success is
rare — is precisely what guided/tree search already attacks. So the line closes.

## 6.4 Status
- F2′: **downgraded**, not built.
- T8: still the only nominal survivor, still weak (Step 5, §T8).
- Net after 6 steps: 0 viable candidates, 3 hard-won rules:
  1. Kill-screen before math.
  2. "Hot area + sharpest gap" is a saturated generator; use structural
     transfer (G2) instead.
  3. Differentiate the mechanism symbolically before believing it.

## 6.5 Strategy correction for Step 7 (the generator is still too narrow)

Six turns of one-idea-at-a-time screening has a bad hit rate because each turn
tests a single point in a space I am sampling from my own priors — the same
priors ~20k other submitters have. Switch to a **coverage-first** procedure:

Step 7 will build a **saturation map**, not another idea:
1. Pull 2026 survey / position / "open challenges" papers for the three biggest
   mainstream areas (LLM post-training & RL; efficient inference; generative
   modelling), plus the RL-environment/task-supply area that is emerging.
2. For each *listed open problem*, search for the count of **method** papers
   attacking it in the last 12 months.
3. Keep only open problems with **≥1 credible statement of importance and ~0
   method papers**. Those are, by construction, either (a) genuinely hard, or
   (b) not yet noticed. Both are what we want; (a) is fine because our
   comparative advantage is patience, not speed.
4. Only then generate ideas, and only inside those cells.

Explicit prior to state now: the strongest emerging structural bottleneck
visible so far is **task/environment supply for verifiable-reward RL** (the "RL
data wall"), where the hard sub-problem — generating tasks that are verifiable,
at the frontier of ability, and not reward-hackable — has an exact foreign
formalism available (minimax-regret unsupervised environment design, Dennis
et al.). This is the first cell to map.
