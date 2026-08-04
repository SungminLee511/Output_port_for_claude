# Step 7 — Saturation map (coverage-first)

## 7.1 Map

| Cell | Stated importance | Method-paper density (last 12 mo) | Verdict |
|---|---|---|---|
| dLLM parallel decoding | high | ~10+ | saturated (Step 2) |
| Optimizer / HP transfer / muP | high | ~5+ incl. closed-form laws | saturated (Step 3) |
| Diffusion guidance (CFG) | high | ~4 incl. exact path-integral | saturated (Step 3) |
| RLVR estimators (variance, coupling, normalization) | high | ~8+ | saturated (Step 3) |
| Credit assignment, multi-turn/long-horizon | **explicitly admitted open** | ~6 + curated list | saturated (Step 4) |
| Non-prefix KV reuse / selective recompute | high | ~8, one in ACM TOCS | saturated (Step 5) |
| Anytime-valid test-time stopping | med | 3 exact hits | saturated (Step 5) |
| Tree / branching rollouts for RLVR | high | ~7 | saturated (Step 6) |
| Low-precision (FP8/FP4) training | very high | ~8 incl. NVIDIA NVFP4 pretraining; 2026 papers already solve shrinkage bias (2606.20381), transposition-invariant blocks (2607.24953), flash-attention low-precision failure (2510.04212) | saturated |
| Video diffusion / world models efficiency | very high | ~84 video accel. papers in 2025 alone | saturated **and** compute-prohibitive |
| **RL task / environment supply** | **explicitly admitted: "improving the training environment is largely manual"; "gains from dynamically generated synthetic tasks plateau due to limited teacher models"** | med (~3–4: Self-Evolving Curriculum, LLM-designed envs 2606.17682, code-RL curricula 2603.24202) | **open-ish** |
| **UED / minimax-regret autocurricula** | med-high, and it is the *formal* backbone of the cell above | low for LLMs; the RL-side literature admits a structural failure: *"once the agent reaches the regret bound on all levels, the adversary will only sample levels where regret cannot be further reduced, and learning stagnates"* | **open, with a named formal defect** |

## 7.2 The conclusion I have to draw after 7 turns

Every cell reachable by (mainstream) × (methodology) × (1 GPU) is occupied.
That is not a failure of search; it is the true state of the field in 2026.
Continuing to hunt for *unoccupied territory* is therefore a losing strategy and
I am stopping it.

**Strategy change:** stop looking for empty cells. Look instead for a **crowded
cell whose occupants all share a formalism that is provably about the wrong
object.** Crowding then becomes an asset — the constituency is pre-verified, the
baselines exist and are strong, and the delta is qualitative rather than
incremental. This is how the actually-cited method papers get written; it is
also the only route compatible with our compute.

Screening criterion for a formalism replacement (all four required):
1. The quantity everyone optimizes, `Q`, is **not** the quantity they claim to
   care about, `Q*`, and `Q ≠ Q*` is provable, not rhetorical.
2. `Q*` is **computable** in the same pipeline at ~no extra cost.
3. Optimizing `Q*` changes behaviour *qualitatively* (predicts a phenomenon that
   optimizing `Q` cannot produce).
4. The replacement predicts its own failure mode.

## 7.3 Three formalism-replacement candidates for Step 8

**R1 — RLVR diversity is regularized on the wrong measure.**
Everyone controls token-level entropy `H(π(·|s))` (entropy bonus, clip-higher,
KL-to-ref) and reports "entropy collapse". But the property actually wanted is
diversity of the **pushforward** measure on solution outcomes,
`ν = f_# π` where `f` maps a trajectory to its verified answer / solution class.
`H(π)` and `H(f_#π)` are not monotonically related in either direction
(counterexample: uniform paraphrase noise ⇒ high `H(π)`, `H(f_#π)=0`). Since
RLVR already runs a verifier and an answer extractor, `f` is available for free,
so `H(f_#π)` is estimable from the same rollout group at zero extra cost.
Claim shape: *entropy control acts on the wrong measure; controlling the
pushforward measure preserves pass@k at large k without the pass@1 cost that
entropy bonuses incur.*

**R2 — UED/autocurriculum regret is the wrong potential.**
Minimax-regret UED provably stagnates once regret is equalized across levels
(admitted in the literature). Regret is a property of the *current* policy's
suboptimality, not of the *learning gradient* the level supplies. Replacement:
a potential that is an explicit functional of expected parameter movement /
information gain about the policy, which is nonzero exactly when the level is
still teaching. Needs care: "learning progress" heuristics exist since Oudeyer,
so the delta must be the exact functional plus its non-stagnation property.

**R3 — verifier-as-scalar vs verifier-as-program.**
RLVR compresses a verifier (a program with structure: which test failed, where,
with what error) into a scalar in {0,1}. The information discarded is large and
free. Claim shape: the discarded structure identifies *which* sub-goal failed
and therefore supplies credit assignment without a critic. Risk: adjacent to
process-reward-model and unit-test-feedback literature; must screen hard.

## 7.4 Step 8 plan
Screen R1, R2, R3 against literature under the four-point criterion above.
Do **not** proceed to math on any of them until the `Q ≠ Q*` separation is
written as a counterexample, not as a sentence.
