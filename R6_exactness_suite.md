# R#6 — T1–T6 exactness suite, DoF table, majorant conservatism

**Date:** 2026-08-07 · **Block I complete (S1.8 – S1.14c)** · commits `e193e40 … 52e5374`

This is the pre-registered gate for **all** G1/G2 training (docs/20 §5). Nothing below
was tuned to pass: every tolerance is the one written in docs/20 §5 before the code
existed, and the two places where a *test's own* metric had to change are called out
explicitly with the reason.

---

## 1. Single command

```bash
cd /home/sky/home/RESEARCH/ConvFS && \
  /home/sky/miniconda3/bin/conda run -n convfs_env python -m pytest tests/ -v
```

```
153 passed in 148.42s (0:02:28)
```

**0 failed, 0 skipped, 0 xfail.** The 4 previously-skipped CORR-001 acceptance tests
went live in S1.14c, so the suite now has no escape hatches left.

---

## 2. Green/red per test

All **65 test functions / 153 parameterizations green**. Grouped by gate, with the
worst measured number for each (tolerance in parentheses).

### T1 — DST operator match (S1.8) · 5 tests
| test | params | worst measured | tol | status |
| --- | --- | --- | --- | --- |
| `test_T1_dst_operator_match` | 2 (upstream, skew) | **1.66e−15** rel. Frobenius | 1e−5 | PASS |
| `test_T1_conventions_are_similar` | 1 | < 1e−12, identical entrywise magnitudes | 1e−12 | PASS |
| `test_T1_matches_the_R2_symbol_module` | 1 | — | 1e−5 | PASS |
| `test_T1_stability_of_the_drawn_symbols` | 1 | 200 draws, 0 unstable | — | PASS |

### T2 — flow (circulant) operator match (S1.9) · 4 tests
| test | params | worst measured | tol | status |
| --- | --- | --- | --- | --- |
| `test_T2_flow_operator_match` | 2 (R3, R4) | **2.678e−16 / 2.749e−16** | 1e−5 | PASS |
| `test_T2_matches_the_flow_symbol_module` | 1 | {R3,R4}×{majorant,grid} | 1e−5 | PASS |
| `test_T2_operator_really_wraps_around` | 1 | `|A[0,(7,0)]| = 1`, `AᴴA = I` | — | PASS |
| `test_T2_stability_of_the_drawn_symbols` | 1 | 200 chan × 4 configs, 0 unstable | — | PASS |

### T3 — parallel scan vs sequential (S1.10) · 4 tests
| test | params | worst measured | tol | status |
| --- | --- | --- | --- | --- |
| `test_T3_scan_vs_sequential` | 5 (plain, with_state, time_varying, odd_length, length_1) | **2.9e−16** | 1e−5 | PASS |
| `test_T3_fused_equals_split_scan` | 1 | < 1e−14 | 1e−14 | PASS |
| `test_T3_chunked_state_carry_equals_full_scan` | 1 | cuts (1,7,16,31) | 1e−14 | PASS |
| `test_T3_layer_both_channel_groups` | 4 (R2, R2p, R3, R4) | perturbed off exact init | 1e−5 | PASS |
| `test_T3_forward_rnn_matches_forward` | 1 | upstream inference path | 1e−5 | PASS |

### T4 — exact-init chain (S1.11) · 4 tests
| test | params | worst measured | tol | status |
| --- | --- | --- | --- | --- |
| `test_T4_exact_init_chain` | 10 (5 rungs × 2 dtypes) | **1.2e−15** (c128) / **2.96e−07** (c64) output rel; `max|z−λ|` ≤ 1e−12 / 1e−5 | 1e−6 | PASS |
| `test_T4_the_4eps_absorption_is_load_bearing` | 1 | counterfactual **4.000e−04** = 400× the gate | — | PASS |
| `test_T4_R3_center_tap_carries_the_imaginary_part` | 1 | — | 1e−6 | PASS |
| `test_T4_flowsin_init_is_identical_to_R2` | 1 | `torch.equal` on all params | exact | PASS |

> **Margin warning, stated up front:** at **complex64** (the production dtype) T4 clears
> the 1e−6 gate by only **3.4×**. Exactness is therefore *demonstrated* in float64 and
> only *gated* in float32. Any future claim of "exact nesting" must name the precision.

### T5 — real I/O (S1.12) · 4 tests
| test | params | worst measured | tol | status |
| --- | --- | --- | --- | --- |
| `test_T5_real_io_under_conjugate_pairing` | 10 (5 rungs × 2 DST conventions) | **≤ 1.2e−15** `max|Im y|` | 1e−6 | PASS |
| `test_T5_is_not_vacuous_without_pairing` | 2 (R2, R3) | ratio **0.7107 / 0.7167** | > 1e−3 | PASS |
| `test_T5_conjugation_rule_at_the_symbol_level` | 2 (upstream, skew) | — | 1e−6 | PASS |
| `test_T5_production_output_dtype_is_real` | 1 | dtype check | — | PASS |

> **Finding worth carrying forward:** with channels **unpaired** — which is the actual
> V4 production situation, since upstream imposes no pairing and just takes `Re(C∗x)` —
> `‖Im‖/‖C∗x‖` is **0.7107 (R2) / 0.7167 (R3)**. The `.real` discards ~71 % of the
> complex state's norm. That is a legitimate real projection, not a bug, but it must be
> on the table before any capacity/DoF argument is made.

### T6 — stability sampling (S1.13) · 4 tests
| test | params | worst measured | tol | status |
| --- | --- | --- | --- | --- |
| `test_T6_stability_sampling` | 21 (7 configs × 3 scales) | **0 violations / 10⁴ channels × 64 grid pts each** | — | PASS |
| `test_T6_discretized_A_is_contracting` | 7 | worst `|Ā|` over Δ∈[1e−4,10] = **0.9999672 … 0.9999986** | < 1 | PASS |
| `test_T6_no_nan_in_forward_backward_at_exact_init` | 12 (6 rungs × 2 modes) | all grads finite, `k_off` grad **non-zero** | — | PASS |
| `test_T6_unsmoothed_majorant_would_nan` | 1 | see D-014 | — | PASS |

### Module-local (S1.14) · 9 tests · and CORR-001 §8 (S1.14b/c) · 13 tests
See §3 and §4 below for the numbers; all 22 green.

### Data generators (Block H) · 15 tests
All green (`test_generators.py`): exact integer translation, energy conservation,
dispersion, Péclet monotonicity, ink conservation, split disjointness, determinism.

---

## 3. DoF table — **verified against the code, not transcribed**

Per-channel state DoF. `effective` excludes Δ and the softmax redundancy; `raw` includes
both. The `counted` column is `sum(numel)/P` over the symbol module's actual
`nn.Parameter`s, i.e. `raw − 1` (Δ lives in the layer as `log_step`).

| rung | class | basis | declared eff / raw | counted params/chan | parameter tensors |
| --- | --- | --- | --- | --- | --- |
| R0 | `ConstSymbol` | DST | 2 / 3 | **2.000** | `lambda_re`, `lambda_im` |
| R1 | `T3Symbol` (upstream) | DST | 5 / 7 | **6.000** | `lambda_re`, `lambda_im`, `values(4)` |
| R2 | `CDSTSymbol` | DST | 8 / 9 | **8.000** | `w(4)`, `y(4)` |
| R2p | `FlowSinSymbol` | DFT | 8 / 9 | **8.000** | `w(4)`, `y(4)` |
| R3 | `FlowSymbol(complex_taps=False)` | DFT | 10 / 11 | **10.000** | `k_off_re(8)`, `w`, `kappa_im` |
| R4 | `FlowSymbol(complex_taps=True)` | DFT | 18 / 19 | **18.000** | `k_off_re(8)`, `k_off_im(8)`, `w`, `kappa_im` |

Every declared number checks out. R1 is the only rung where `counted ≠ effective`
(6 vs 5): its four `values` logits go through a softmax, so one is redundant — exactly
the redundancy docs/30 §9 says `raw` keeps and `effective` removes.

### Layer-level totals at the ablation config (P = 256, 8 blocks, ρ = ½ where applicable)

| rung | ρ | P_dst / P_flow | symbol params (×8 blocks) | Δ vs R1 (**raw**, counted) | Δ vs R1 (**effective**, docs/30 §9) |
| --- | --- | --- | --- | --- | --- |
| R0 | 0 | 256 / 0 | 4 096 | −8 192 | — |
| R1 | 0 | 256 / 0 | 12 288 | 0 | 0 |
| R2 | 0 | 256 / 0 | 16 384 | **+4 096** | **+6 144** |
| R2p | ½ | 128 / 128 | 16 384 | **+4 096** | **+6 144** (param-matched to R2 by construction) |
| R3 | ½ | 128 / 128 | 18 432 | **+6 144** | **+8 192** |
| R4 | ½ | 128 / 128 | 26 624 | **+14 336** | **+16 384** |

Both columns reproduce docs/30 §9 exactly (including its explicit "+2 raw/chan ⟹
+4,096 raw" for R2). The whole-layer parameter count moves from **4 732 928 (R1)** to
**4 739 072 (R3)** / **4 747 264 (R4)** — i.e. **+0.13 % / +0.30 %**, MiniT3-grade, so
"more parameters" is visibly excluded as an explanation for any G1 gain (risk
register #2 / Table 12's 5×5 backfire precedent).

---

## 4. Majorant conservatism gap

The flow rungs pin `Re k₀₀ = −softplus(w) − M` with `M = Σ_pairs m_ε(pair)`, giving
`sup_θ Re z ≤ −softplus(w) < 0`. `M` bounds the *whole torus*; `flow_grid_max` is the
exact max over the H·W grid points. The gap is what docs/30 §8 asked us to report.

**Validity: 0 violations, ever.** Across S1.14 (24 000 draws) and S1.14c (40 000 draws,
independent RNG stream) the gap was non-negative in **64 000 / 64 000** cases.

### Gap vs parameter scale (S1.14, 4 000 draws per cell, 8×8 grid)

| | scale 0.1 | scale 0.5 | scale 2.0 |
| --- | --- | --- | --- |
| R3 median gap | 0.0726 | 0.3813 | 1.4690 |
| R3 max gap | 0.5478 | 2.6228 | 10.6883 |
| R3 **relative** median | 0.199 | 0.211 | 0.203 |
| R4 median gap | 0.1431 | 0.7099 | 2.8569 |
| R4 max gap | 0.7008 | 2.9742 | 11.4579 |
| R4 **relative** median | 0.213 | 0.212 | 0.212 |

### High-sample confirmation (S1.14c, 20 000 draws per tap kind, `scale = 1`)

| | violations | median | mean | min | max | relative median |
| --- | --- | --- | --- | --- | --- | --- |
| R3 (real taps) | **0 / 20 000** | 0.7548 | 0.9285 | 6.178e−09 | 6.7651 | **0.2026** |
| R4 (complex taps) | **0 / 20 000** | 1.4078 | 1.5726 | 1.130e−02 | 7.2963 | **0.2134** |

**Headline:** the absolute gap grows linearly in the tap scale, but the *relative* gap
`gap / |M|` is **scale-invariant at 0.20 (R3) / 0.21 (R4)**. So the reportable statement
is "**the majorant is ~20 % conservative, ~21 % with complex taps**", independent of
where training takes the parameters. R4's larger gap is consistent with complex taps
having twice the phase freedom the pairing bound must cover.

### Where the conservatism comes from — it is *not* `m_ε`

Put all the mass on one pair (`k_{1,0} = k_{−1,0} = 0.7`), so `Re z_off = 2a cos θ_H`
peaks at a grid point:

| quantity | value |
| --- | --- |
| exact grid max | 1.400000 |
| majorant | 1.400300 |
| **gap** | **3.000e−04 = 3ε**, + 3.57e−09 |

The 3ε is the three **idle** pairs' `m_ε(0)` floor; the 3.57e−09 is the active pair's
`ε²/4a`. So the bound is *attained* up to the ε floor, and the ~20 % figure above is
entirely **phase misalignment across pairs**, not looseness in the smoothing.

### The exact alternative is available and free

`stability="grid"` uses `flow_grid_max` directly. Measured slack (`bound − max_grid Re z`)
on a live `FlowSymbol(64)` perturbed by 0.6:

| config | max Re z | slack median | slack min |
| --- | --- | --- | --- |
| R3 majorant | −0.3172 | 0.5615 | 1.878e−08 |
| R3 **grid** | −0.2950 | **0.0000** | −3.331e−16 |
| R4 majorant | −0.4538 | 0.9271 | 4.908e−02 |
| R4 **grid** | −0.1845 | **0.0000** | −4.441e−16 |

Both modes are stability-correct; `grid` is tight to round-off. G1 will run `majorant`
(smooth, grid-size independent) with `grid` available as a sensitivity check.

---

## 5. CORR-001 §8 named acceptance criteria (S1.14b + S1.14c) — 13/13

| criterion | measured | status |
| --- | --- | --- |
| **T-CE** (reviewer counterexample) | DST operator `tridiag(c/2,−γ,−c/2)` magnitude-reciprocal to 1e−12 **and** transports by +ct | PASS |
| **T-upwind** | `A(16) > 0.9` | PASS |
| **T-centered** (negative control) | `A(τ) < 1e−4` ∀τ ≤ 64 | PASS |
| B2 reference group velocities, quadrature deficiency | — | PASS |
| **T-R3-nest** | chain R0→R1 **3.149e−16**, R1→R2 **0**, R2→R3 **1.188e−15**; `max|z−λ| = 0` and `|k_off| = 0` exactly; `Im k₀₀ == kappa_im` exactly | PASS (tol 1e−6) |
| **T-R3-real** | paired `max|Im y| = 2.665e−15`; un-negating **only** `kappa_im` → ratio **0.6061** | PASS (tol 1e−6) |
| **T-flowsin-corner** | `|grid_max − corner_max| = 4.441e−16` on 8×8 (contains sin θ = ±1); one-sided bound holds on 6×6 (slack 0.5403); `exact_init_` **bit-identical** to R2's, `max|z−λ| = 5.551e−17` | PASS (tol 1e−12) |
| **T-majorant** | see §4 | PASS |

---

## 6. Deviations logged in this block

| id | what | why it matters |
| --- | --- | --- |
| **D-014** | `m_ε`'s NaN justification is *framework convention*, not necessity — PyTorch defines `sgn(0) = 0`, so a `torch.abs` majorant would **not** have NaN-ed. Only the hand-written `sqrt(Σ x²)` NaNs (24/24 entries). | The writeup must not claim "without `m_ε` R3/R4 NaN on the first backward". Defensible version: `m_ε` buys framework-independence + smoothness at a measured cost of `4ε`, absorbed exactly by init. |
| **D-015** | `PHI1_EPS = 1e−4` is **precision-blind**. Seam error is 2.006e−10 in c128 but **5.046e−04 in c64**, and lives **entirely on the exp side** (`exp(x)−1` cancels to ~\|x\|). Optimal seam is 4.8e−3 (f64) / 1.1e−1 (f32). | Do not claim the φ₁ branch makes ZOH accurate "independently of precision". Kept at 1e−4 because all exactness claims are float64, production `|Δz| ∈ [1e−3,1e−1]` is 1–3 decades above the seam, and raising it would break the `eps=0 ⟹ upstream verbatim` property T1/T2's bit-match uses. |

Two test-side metric changes, both recorded in PROGRESS with the reason:
1. **Corner round-trip** switched from elementwise- to **norm-relative** error. The
   elementwise version failed at scale 5 (2.856e−07) because at that scale corners span
   1e−9 … 81 and recovering the 1e−9 one as a difference of 80-sized numbers is at the
   float64 noise floor *by construction*. Not a code bug.
2. **`test_T6_no_nan…`** originally asserted `k_off.grad == 0`; corrected to
   **non-zero**, because `k_off` reaches the loss by two routes — the majorant (derivative
   0 at 0) *and* `flow_offcenter_symbol`, which is **linear** in `k_off`. A zero there
   would mean R3/R4 could never leave ConvS5.

---

## 7. Gate verdict

**GREEN — G1 training is unblocked by the exactness suite.** 153/153, no skips, every
tolerance the pre-registered one, both DoF columns reproduce docs/30 §9, and the
stability construction has 0 violations in 64 000 draws with a quantified ~20 %
conservatism and an exact alternative available at no cost.

The two things a reader should carry forward: **T4 at complex64 has only 3.4× margin**,
and **`.real` discards ~71 % of the unpaired complex state's norm**.
