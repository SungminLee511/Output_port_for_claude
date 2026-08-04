# Step 4 — Three generators, 14 candidates

## G1 results (mine admitted failure) — mostly already colonized

- **Long-horizon / multi-turn RL instability** is an *explicitly admitted*
  bottleneck ("increasing horizon length alone induces severe training
  instability driven by exploration difficulty and credit assignment",
  2605.02572). But the fix-space is already dense: TRACE (2607.13988),
  Turn-PPO (2512.17008), HCAPO, SORL, ECHO (2606.31650), plus a curated
  `Awesome-Credit-Assignment-in-LLM-RL` list. **Occupied.**
- **Framework-level silent bugs** genre is live (2604.23747 found a CPU-offload
  gradient-accumulation bug that silently drops all but the first micro-batch).
  Genre works, but finding a *new* such bug is luck, not a plan. Keep as a
  side-channel, not a thesis.
- **Data wall / storage-IO as the real pretraining bottleneck** (2602.17288):
  real, but not a methodology paper for NeurIPS.
- **Evaluation irreproducibility** (69 papers evaluating OpenAI models: 5 ran,
  0 reproduced): real and damning, but analysis ⇒ excluded by user.
- **dLLM open challenges** (2601.14041, "Top 10 Open Challenges"): lane already
  killed in Step 2, but this document is worth reading once as a source of
  *admitted* failures if we ever return.

## G2 results (cross-community primitive transfer) — the productive generator

Method: enumerate mature primitives from communities that do not co-attend with
NeurIPS/ICLR, and match on *structural signature*, not on topic.

| # | Foreign primitive | Structural signature | ML bottleneck with that signature | One-sentence claim | Sat. risk |
|---|---|---|---|---|---|
| T1 | **Self-adjusting computation / incremental recomputation** (PL community, Acar et al.) | recompute only the part of a dataflow graph affected by a small input edit, with exact change propagation | agentic long-context inference re-runs 50k-token contexts that differ by a *mid-sequence* edit; prefix KV caching salvages nothing after the edit point | Given a small edit to a long context, one can select a provably sufficient recomputation set so that the attention output error is bounded by ε, at cost proportional to the *influence* of the edit rather than to the suffix length. | med (CacheBlend/Prompt-Cache adjacent, but those are heuristic and systems-venue) |
| T2 | **Learned Belady / reuse-distance prediction** (computer architecture: Hawkeye, Glider) | evict the line whose *next* use is farthest, predicted from history | KV-cache eviction (H2O/SnapKV/StreamingLLM use *past* attention as the score) | Past-attention scores are a biased estimator of future reuse; a reuse-distance predictor trained offline dominates them at equal cache budget. | med-high (crowded) |
| T3 | **Balanced / cube-method sampling** (survey statistics, Deville–Tillé) | draw a sample that *exactly* balances chosen auxiliary totals while staying unbiased | minibatch construction (uniform iid) | Minibatches balanced on cheap gradient features give an unbiased gradient with strictly lower variance, at negligible CPU cost. | med, but strong prior of *practical failure* (importance-sampled SGD has repeatedly failed at LLM scale) |
| T4 | **Extreme value theory** | distribution of the max of n draws is governed by a tail index | test-time compute: best-of-n / self-consistency budget allocation | The per-prompt tail index of the reward distribution is estimable from ~8 samples and predicts the marginal value of further samples, enabling budget allocation that dominates uniform-n at equal total compute. | med-high (adaptive BoN exists) |
| T5 | **Anytime-valid sequential testing / e-values** (Wald, Ramdas) | stop as early as possible with a guarantee that holds under optional stopping | when to stop sampling in self-consistency; when to let an agent commit to an irreversible action | Self-consistency stopping rules in use today are not anytime-valid and their empirical error rates exceed their nominal ones; an e-value rule attains the nominal rate at lower mean cost. | med |
| T6 | **Rateless / fountain codes** | any sufficiently large *subset* of symbols decodes; no rate chosen in advance | quantization & KV compression where the budget is not known until serving time | A single rateless encoding of weights/KV supports any bitrate at decode time with no re-encoding and no accuracy loss vs. rate-specific codecs. | med (Matryoshka/any-precision adjacent) |
| T7 | **Perfect simulation / coupling-from-the-past; quasi-rejection sampling** | exact draws from a target with no asymptotic bias | inference-time alignment: sample exactly from π* ∝ π_ref·exp(r/β) | Exact sampling from the tilted policy is achievable at bounded expected cost using a sequential rejection scheme with a certified soft-value upper bound. | high (controlled decoding / twisted SMC / VAS) |
| T8 | **CDCL no-good learning** (SAT solvers) | on failure, derive a *constraint* that prunes an exponential region of the search space | agent self-improvement, which currently converts failures into gradient signal or into unstructured "reflections" | Failures in agentic rollouts can be compiled into reusable no-goods that prune future search, giving improvement without weight updates and with a monotone-pruning guarantee. | med (Reflexion-adjacent but the *guarantee* is not) |
| T9 | **Scheduling with unknown service times (SRPT / learning-augmented)** | minimize latency when job sizes are unknown but predictable | LLM serving: output length unknown at admission | — | high, and MLSys-venue |
| T10 | **FDR control / multiple testing** | control the expected fraction of false discoveries over many decisions | hallucination gating over many agent claims | — | med, but reviewers read it as niche |

## G3 results (universal wrong implementation details)
- D1 length-normalization of loss/advantage — occupied (DAPO et al.).
- D2 rollout/train numerical mismatch — occupied (2025 "secretly off-policy").
- D3 non-canonical tokenization robustness — occupied (2607.26831).
- D4 **position-id and attention-mask correctness under cache reuse / packing**
  — *not* obviously occupied, and it is the same object as T1. Merge into T1.

## Shortlist to saturation-screen in Step 5 (max 5)

1. **T1** — incremental exact-error-bounded recomputation for edited long
   contexts. Best fit to our lopsided machine (866 GB RAM holds many full KV
   caches), zero training, exact linear-algebra error control, and the
   constituency (agent loops, tool outputs inserted mid-context, KV reuse in
   RAG) is the dominant 2026 deployment pattern.
2. **T8** — no-good learning for agents, with a monotone pruning guarantee.
3. **T5** — anytime-valid stopping for test-time compute.
4. **T4** — EVT-based budget allocation.
5. **F2** — RLVR support expansion via structured proposals + exact IS
   correction (the "RL sharpens but does not teach" problem).

Kill any of these on sight if a 2025–26 paper already states the same claim.

## Standing risk to keep visible
Three of the five (T1, T5, T4) are *inference-time* methods, which reviewers at
NeurIPS/ICLR sometimes bounce as "systems". Mitigation: the paper must lead with
the mathematical object (error bound / validity guarantee), not the speedup, and
must report accuracy-vs-cost Pareto curves rather than raw latency.
