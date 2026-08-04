# Step 12 — Smoke test S01. **T-A survives. Warning 2.3 survives. T-B survives.**

Script: `smoke/s01_theta_recovery.py`. Model: θ-conditional dual-token causal
PFN (d_model 128, 6 layers, 4 heads, 4.8 MB), 30k steps, ~13 min on 1×A100.
K = 4 prior components {linear, mlp, tree, rbf}, n = 64 rows, d ∈ [3,8],
**shared covariate law** `x ~ N(0,I)` so the Theorem-2 partial-likelihood caveat
is inert and any failure is attributable to the network alone.

## 12.1 Numbers (64 held-out datasets per component, 8 orderings each)

| quantity | value | required |
|---|---|---|
| T-A: `argmax_k ℓ_k = k*` accuracy | **0.703** | ≫ 0.25 (chance) |
| Warning 2.3: σ-spread / k-spread | **0.134** | ≪ 1 |
| T-B: k-spread (nats/row) | **0.0453** | ≫ 0 |
| top-2 gap (nats/row) | 0.0224 | > σ-spread 0.0061 |
| argmax agreement across σ | 0.85–0.94 | high |

Confusion (row = true k, col = argmax):
```
          linear  mlp  tree  rbf
linear      57     4     ?    ?
mlp         23    25     7    9
tree         1     5    49    9
rbf          1     2    12   49
```

## 12.2 Reading, stated negatively first

- The one bad row is **mlp**: 23/64 datasets are assigned to `linear`. This is
  *not* a defect of the statistic. A random 2-layer tanh MLP with small
  pre-activations **is** approximately linear, so `P_linear` and `P_mlp` overlap
  substantially as measures on datasets. The prequential score is reporting a
  true fact about the prior family: **the components are not identifiable.**
  Two consequences, one bad and one good:
  - bad: any claim of the form "the score attributes misfit to a *specific*
    prior component" (O2) is only as strong as the identifiability of the
    component decomposition, and must be reported with the confusion structure,
    not as a clean attribution.
  - good: non-identifiability is exactly the situation the NPMLE mixture
    (Theorems 3–5) is designed for. A hard `argmax_k` is the wrong readout; the
    soft posterior `w_k(D) ∝ π*_k L_k(D)` is the right one, and Theorem 4's
    bound never referred to identifiability.
- σ-spread is **0.0061 nats/row** against a top-2 gap of **0.0224 nats/row**, a
  factor 3.7. Order-incoherence is real and measurable but is *not* dominant.
  The §8 item-2 kill condition ("σ-spread ≫ k-spread ⇒ dead") **did not fire**;
  the observed ratio is 0.134.
- k-spread 0.045 nats/row over a base loss of ~0.6 nats is ~7%. The network
  genuinely uses θ. T-B does not fire.

## 12.3 What this does *not* establish

1. n = 64 only. σ-spread and k-spread scale differently in n (σ-spread should
   shrink like the per-row variance of an average; k-spread is a per-row bias
   and should not). The ratio is therefore expected to *improve* with n, but
   that is a prediction, not a measurement, and must be measured.
2. K = 4 hand-separated components. Real TabPFN priors are parameterized by
   continuous hyperparameters with far more overlap. Expect worse recovery.
3. All test datasets are **in-family**. The interesting case (O1/O4) is
   out-of-family data, untested here.
4. Nothing has been shown about **predictive gain**. Recovering θ is necessary,
   not sufficient. The paper's claim is about held-out log-loss / accuracy of
   the mixture, which is Remark 5.2(b) and is still entirely unproven.

## 12.4 Step 13 (next smoke test, S02)

Test, in this order, all on the *same* trained network (zero extra training):
1. **T-D / NPMLE.** Build a synthetic "real corpus" as a mixture with known,
   deliberately uneven weights `π_true` plus out-of-family datasets. Fit `π*`
   by the EM of Corollary 5.1. Does `π*` recover `π_true`? Is it degenerate?
2. **Theorem 3/4 empirically.** Held-out log-loss of `q^{mix,π*}` vs each fixed
   `q^{(k)}` vs uniform mixture vs the oracle best-`k`-in-hindsight. The bound
   guarantees `≥ ℓ_k + log π_k`; the *claim* is that it is better than the best
   fixed `k`, which the bound does **not** give and which can fail.
3. **O1.** Does `max_k ℓ_k` (label-free at test rows? — no, it is not; state
   this honestly) separate in-family from out-of-family datasets?
