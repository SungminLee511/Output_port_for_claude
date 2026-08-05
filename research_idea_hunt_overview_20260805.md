# Research Idea Hunt — Overview (as of 2026-08-05 23:30 KST)

Goal: find ONE unique, mainstream, **methodology-type** research idea meeting
top-tier NeurIPS/ICLR criteria, stress-tested mathematically BEFORE heavy
experiments. Constraint: 1×A100 80GB (shared), theory-first positioning.

---

## 1. Acceptance criteria used (gatekeeping framework)

**Hard gates**: (1) technical soundness, (2) claims == evidence,
(3) conceptual delta vs 3 nearest papers, (4) reproducibility.

**Oral-tier**: (5) one-sentence crisp idea, (6) generality, (7) mainstream
significance, (8) simplicity, (9) explanatory insight.

**Death modes**: D1 untuned baselines, D2 wins vanish at scale, D3 toy
theory, D4 reparametrization of known method, D5 per-task tuning,
D6 analysis-only, D7 dishonest compute accounting.

---

## 2. Kill log (15+ candidates eliminated via novelty scans + skeptical agents)

| ID | Idea | Verdict / killer prior art |
|----|------|---------------------------|
| C4 | Martingale/optional-stopping adaptive compute + calibration | KILL — conformal risk control + Confident Adaptive Transformers already cover it (D4) |
| C6 | Rate-distortion KV-cache theory | KILL — 2607.01520 minimax bounds already sharper |
| C3 | RMT trust-region optimizer (Muon successor) | KILL — TrasMuon etc.; "Muon is Not That Special" closes lane (D1/D2) |
| C5 | Noether / backward-error-analysis training | KILL — IGR flow 2021, collapses into optimizer lane |
| C1 | Symplectic/port-Hamiltonian training | KILL — same optimizer-lane closure |
| C9 | Multilevel splitting for inference scaling | KILL — particle-filter inference scaling = same family (D4) |
| C8 | MLMC gradients for pretraining | KILL (fallback HOLD) — 2501.12739 / 2505.12940 did the transplant |
| C2 | Rough-path signatures | KILL — niche, fails significance gate |
| C7 | Thermo/OT fine-tune schedules | KILL — thin delta |
| C10 | Stable-matching MoE routing | KILL — routing space mined, gains small |
| P10 | PE length-extrapolation theory | KILL — Huang/Hahn ICLR'25 + 3 groups camped |
| P1/P3 | dLLM sampler exactness / joint dependence | KILL — ASSD solved exact joint sampling; 8+ concurrent fixes |
| P4 | Async-RL staleness theory | KILL — "zero theory" claim false (GAC, SAT, TIC-GRPO; 1 paper/3wks) |
| P2 | dLLM train-time revision | HOLD — least crowded but negative empirics headwind |

**Meta-lessons**: (1) hot areas absorb imported proof techniques within
~6 months; (2) tool-first generation lands on already-transplanted
structures → inverted to **problem-first** search over 2026 pain points.

---

## 3. SURVIVOR — P5: Martingale credit + Neyman rollout allocation for RLVR

**Working title**: *Credit Where Credit Is Due: Variance-Optimal Rollout
Allocation for Token-Level Credit Assignment in RLVR.*

**One-sentence pitch**: token credit in RLVR is the quadratic variation of a
Doob martingale — a conserved resource concentrated at a few forks — and the
variance-optimal way to spend rollout budget is Neyman allocation on fork
variance, not uniform branching or entropy heuristics.

### Math core (verified)
- Prefix value `V_t = E[R | F_t]` is a Doob martingale, `V_T = R`.
- **Conservation law (Thm 1)**: `Σ_t E[A_{t+1}² | x] = V₀(1−V₀)` — total
  squared token credit per prompt is conserved and bounded.
- Two-object structure: fork variance `σ_t² = Var(V_{t+1}|F_t)` (SIGNAL,
  conserved) vs `ν_t = V_t(1−V_t)` (estimation NOISE); linked by
  `ν_t = E[Σ_{u≥t} σ_u² | F_t]`.
- **Neyman-KKT (Thm 2)**: minimize `Σ a_t/m_t` s.t. `Σ c_t m_t ≤ B` with
  `a_t = ‖d_t‖² ν_t` → `m_t* ∝ √(a_t/c_t)`; efficiency ratio ≥ 1, equality
  iff `a_t/c_t` constant; auto-truncates decided tails (`ν_t = 0`).
- Shared value estimates strictly dominate split branches (parallelogram law).
- Cost-aware: suffix cost `c_t ≈ E[T−t]` decays with position — cleanest
  unclaimed piece in the literature.

### Positioning (v2 reframe = unification)
One variance-optimal budget-allocation theory over the full rollout grid
(prompts × positions, with costs). DAPO/DynaMO (prompt-level Neyman) and
BPO/TreeRL (entropy position heuristics) drop out as special cases; entropy
is provably the wrong signal when lexical ≠ outcome uncertainty.
Must beat: BPO, DynaMO, VinePPO, P2T, GRPO — all at matched TOKEN budget.

### Method sketch (VOLTA)
1. GRPO group = free pilot → `V₀`, coarse prefix values, candidate forks.
2. Neyman allocation of branch budget over token blocks (Thm 2).
3. Per-block MC advantages, shared estimates; PG update.
4. Matched token budget vs all baselines (D7 honesty).

---

## 4. Kill-test status

| Test | Content | Status |
|------|---------|--------|
| K1 (math) | KKT closed form, variance decomposition, conservation law — numerical verification `k1_check.py` | **PASSED** (KKT 200/200 trials, MC relerr 6e-4, conservation exact 1e-10) + 5 skeleton corrections logged |
| K2 (smoke) | Decorrelation test on Qwen2.5-0.5B / GSM8K: 48 prompts × 8 boundaries × 48 branches. KILL if corr(ν,H) > 0.9 (collapses into BPO) or efficiency ratio < 1.3× | **READY, NOT RUN** — `k2_smoke.py` written, vLLM env installed (INSTALL_OK) |
| K3 (smoke) | Suffix-cost profile c_t (cost-aware vs cost-blind gap) | Folded into K2 script |
| K4 | Full experiment plan (only if K1–K3 pass) | Pending |

### Remaining risks (open)
- F4: ν–entropy correlation may be high → K2 is decisive.
- F2: flat GRPO credit may be "good enough" at matched compute.
- F7: 1.5B max scale — mitigate with 3 model families + scaling trend.
- Theory is textbook-level (Neyman 1934, Carpentier-Munos) — must be sold
  as structure transplant + conservation identity + method, not deep theory.

---

## 5. Artifacts (in `RESEARCH/test/idea_forge/`)
- `00_criteria_and_candidates.md` — criteria + first candidate queue
- `01_verdicts.md` — kill log with cited prior art
- `02_pain_points.md` — problem-first pivot, P1–P11 audits
- `03_p5_math_skeleton.md` — formal skeleton, theorems, corrections (canonical)
- `k1_check.py` — math verification (all passed)
- `k2_smoke.py` — decorrelation smoke test (ready to run)

**Current state**: relay halted by user. Next action when resumed: run K2,
evaluate kill metrics, then K4 full experiment plan.
