# Step 14 — Smoke test S03 (scale K). **The demotion condition I pre-registered
# in §13.4 has FIRED. The empirical-Bayes framing of M1 is dead, and I now know
# why, at theorem level.**

Script: `smoke/s03_scale_K.py`. Continuous 7-dim `θ = [onehot4(type), c, ν, s]`
(type × complexity × noise × feature-sparsity), one θ-conditional PFN
(d_model 192, 8 layers, 40k steps, 21 min on 1×A100), evaluated on grids
`K ∈ {4,16,64}` **without retraining**. Corpus deliberately peaked:
70% tree / 30% mlp, `c~Beta(5,2)`, `ν~Beta(2,5)`, `s~Beta(5,2)`.
600 fit datasets, 600 held-out, `N_SCORE = 48`, eval on 16 rows.

## 14.1 The table

| K | uniform mix | NPMLE mix | **gap** | `(log K − H(π*))/48` | eff. support `e^H` | vs best fixed atom | win% vs best fixed |
|---|---|---|---|---|---|---|---|
| 4 | 0.5327 | 0.5276 | **0.0051** | 0.0150 | 1.94 | −0.0044 | 42.5% |
| 16 | 0.5223 | 0.5164 | **0.0060** | 0.0292 | 3.94 | −0.0087 | 49.5% |
| 64 | 0.5225 | 0.5161 | **0.0063** | 0.0534 | 4.93 | −0.0081 | 52.0% |

Per-dataset oracle: 0.5042 / 0.4724 / 0.4647.

## 14.2 Reading

**(i) The pre-registered kill fired.** §13.4 item 1 asked: does the
NPMLE-vs-uniform gap grow with `K`? It goes 0.0051 → 0.0060 → 0.0063, a factor
**1.24** while `K` grows **16×** and the naive `log K` term grows **3.6×**. The
gap is flat. The condition I wrote in advance — *"If (1) is flat, the
empirical-Bayes framing must be demoted"* — is met. I am demoting it.

**(ii) I now know the mechanism, and it is not fixable.** The measured gap is
also far *below* `(log K − H(π*))/N_SCORE`, and the reason is exact:

> In the sequential mixture (Theorem 3), the log-weight of atom `k` after `n_s`
> score rows is `log π_k + ℓ_k^{(n_s)}`. The data term `ℓ_k` differs across `k`
> by `Θ(n_s)`; the prior term differs by `O(1)`. Hence the influence of `π` on
> the eval-row predictive decays as `O(1/n_s)` and vanishes for large datasets.

So **deployment mode M1's dependence on `π` is intrinsically an `O(1/n)`
effect**. This is not an experimental shortfall to be engineered away; it is
what the identity says. Any paper claiming "we fit the prior and inference-time
prediction improves" is claiming a `1/n` term. On TabPFN's own advertised
regime (small `n`) it is nonzero — 0.006 nats/row here — but it is not a
headline and a reviewer who understands Theorem 3 will say so in one line.

**(iii) What survived in M1, restated honestly.** Averaging over a *grid* of
prior hyperparameters is worth real money and it is not the `π` that buys it:
- best fixed atom → NPMLE mixture: **−0.0081 nats/row** at K=64,
- coarse grid → fine grid (K=4 → 64): **−0.0115 nats/row**,
- but the win rate against the best fixed atom is **52%**, i.e. the mean gain is
  again tail-driven (threat T-E, seen for the second time). The correct claim is
  *"no loss on datasets the default prior already suits, large gain on the
  minority it does not"*, and the evaluation must be built around that shape.
- the mixture still captures only ~30% of the per-dataset oracle gap (0.0081 of
  0.0596 at K=64). Most of the achievable gain is *not* captured by mixing.

**(iv) `π*` is sparse but not collapsed** (`e^H` = 4.9 atoms out of 64, top atom
0.45). Kiefer–Wolfowitz behaviour as expected; T-D remains dead.

## 14.3 Where the claim must move: M2

M1 and M2 are different mechanisms and §6 of `math/01_setup.md` already said
they must not be conflated. The `O(1/n)` argument in 14.2(ii) applies **only to
M1**, because there `π` enters solely as an additive `log π_k` in a weight.

In M2 the fitted `π*` is used to **resample the synthetic pretraining corpus**
and a standard unconditional PFN is retrained. There `π*` changes *what function
the network learns* — the allocation of a finite network's capacity across the
prior family. That is an `O(1)` effect in `n`, not `O(1/n)`, and nothing in
Theorems 3–5 bounds it. It is also the deliverable practitioners want ("a
drop-in better TabPFN") and the one that costs exactly one retraining.

**M2 is now the paper's headline candidate and it is completely untested.**

## 14.4 Step 15 — S04, the decisive M2 test

Three *unconditional* PFNs, identical architecture/steps/seeds, differing only
in the distribution over `θ` used to generate pretraining data:

| arm | pretraining θ-distribution | meaning |
|---|---|---|
| **A** | `π₀` = broad/uniform (`t` uniform, `c,ν,s ~ U[0,1]`) | "TabPFN as shipped" |
| **B** | `π*` fitted by NPMLE on the fit corpus (S03, K=64) | the proposal |
| **C** | the true corpus θ-law (70/30 tree/mlp, Beta knobs) | oracle upper bound |

Evaluate all three on the **held-out** corpus. Report per-dataset paired
differences and win rates, not just means. Decision rule, fixed in advance:
- if `B ≈ A` → M2 fails, the whole empirical-Bayes contribution is dead, and
  what remains is O1 (failure prediction) plus grid averaging — a weaker paper
  that must be re-scoped or abandoned;
- if `A > B ≈ C` (B recovers most of the oracle) → M2 works, and the paper is
  "fit the PFN prior by NPMLE on real data, retrain once, get a strictly better
  PFN, plus a free label-free failure detector". That is the paper worth running
  at full scale.
Cost: 3 × 21 min on 1 GPU. There is no excuse for not running it.
