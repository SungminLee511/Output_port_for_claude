# GLS-AM Experiment — Return Report

> Honest read. The load-bearing outcome is a **clean kill**: GLS-weighting the Adjoint-Matching loss is **inert against mode collapse** on this target — every weighting variant, the oracle weight, and the proximal baseline all collapse identically to minority occupancy **exactly 0.0**. Caveats about the harshness of the induced collapse are stated plainly in §5/§9.

---

## 0. Run metadata
- **Date / wall-clock total:** 2026-06-30. Calibration (3 ladders) ≈ 3.3 h; main grid (40 runs) ≈ 6.0 h; profiles ≈ 0.2 h.
- **Hardware:** 1× NVIDIA A100 80GB PCIe.
- **Code:** `RESEARCH/temp/gls_am.py` (single-file, phase-driven), plots `RESEARCH/temp/plots.py`.
- **Library versions:** conda env `SML_env`, PyTorch (CUDA 12.6 build), NumPy. float32, device cuda.
- **Random seeds:** grid = {0,1,2,3,4}; calibration = {0,1}.
- **Final calibrated target/sampler settings** (from §3a, after a user-approved deviation — see §1/§6):
  `D=3.0, s=0.5, N=100, sigma=1.5, sigma0=0.5, lr=3e-4, B=512, steps=3000`,
  **prior offset `mu0=(3.0, 0.0)` (one-sided)**. Calibration name `B0_off_sig15`.
- **Total ∇E evaluations per config:** **1,536,000** = B·steps = 512·3000, **EQUAL across all 8 configs** (confirmed in `results.json`, field `nE`). The GLS Σ-estimate and weight construction add **zero** energy/adjoint evaluations (P4 verified operationally). (ORACLE additionally consumed a one-off reference-sampler training of 2000 steps to build its frozen oracle weights; this is reported separately and is not part of the per-config matched budget.)

## 1. Calibration outcome (§3a) — did the baseline collapse?

**Headline: vanilla AM did NOT collapse under the spec as written. Collapse had to be induced by a user-approved deviation (one-sided prior).**

Three calibration ladders were run, each training vanilla AM (A0) for 5000 steps, 2 seeds, with occupancy checkpoints:

1. **Spec ladder (`calib`)** — D∈{3,4,5}, then s→0.35, N→50, σ→2 (the spec's exact hardening order). **No rung collapsed.** Final minority occupancy stayed at 0.34–0.49 (recall=2 throughout); occasional mid-training dips to ~0.28 always *recovered*.
   - C0 D3: 0.45/0.45 · C1 D4: 0.38/0.40 · C2 D5: 0.34/0.48 · C3 D5,s0.35: 0.43/0.34 · C4 +N50: 0.39/0.43 · C5 +σ2: 0.44/0.45.
2. **σ0-shrink ladder (`calib2`, deviation #1)** — σ0∈{0.6,0.4,0.25}, D3/s0.5. **No rung collapsed** (0.48/0.45, 0.48/0.43, …).
3. **Combined offset-prior + σ-reduction ladder (`calib3`, deviation #2, user-approved option C)** — one-sided prior `X0~N((+3,0), σ0²I)`, σ-reduction. **First rung B0 (σ=1.5, σ0=0.5) collapsed TOTALLY:** minority occupancy = **0.0 for both seeds**, recall=1, with collapse complete by **step ~500** and held to step 5000.

- **Did vanilla AM (A0) collapse?** With the spec's symmetric broad prior: **NO** (robustly two-moded). With the user-approved one-sided prior: **YES, totally** (occ = 0.000, recall = 1).
- **What was changed to induce collapse:** the *sampler prior only* — from `N(0,1.5²I)` to `N((3,0),0.5²I)`. The **target stays the balanced 50/50 GMM** (ground-truth minority occupancy = 0.5 unchanged). Mechanistically: a symmetric prior straddling the saddle auto-seeds both wells, so collapse is structurally resisted; a one-sided prior forces the control to actively transport mass *across the barrier* to the minority well — which on-policy AM fails to do.
- **Is the kill-test valid (baseline genuinely fails)?** **Yes** — A0's minority occupancy is *exactly* 0.0 across all 5 grid seeds (not "near 0"). The baseline maximally fails, so any non-zero improvement by a method would be unambiguous. (Limitation: the failure is *total*, see §5/§9.)

## 2. Mechanism confirmation (M5, M6) — is the predicted variance structure present?

Profiles computed for **A0** and **A3-NormB** on the collapsed (chosen) prior, plus a **well-mixed reference sampler** (balanced prior, occ=0.44) as a positive control. Σ_t from 8 averaged rollout batches; G = σ·∂ₓu on a fixed barrier grid (|x₁|,|x₂|<1). Full arrays in `profiles.json`.

### 2a. Variance / expansion profile vs t (M5)

**A0 (collapsed):**
| t | tr Σ̂ₜ | top-eig | angle(top-evec, (1,0)) [deg] |
|---|---|---|---|
| 0.00 | 1.32 | 0.675 | 77.0 |
| 0.42 | 1.86 | 0.945 | 2.7 |
| 0.70 | 2.66 | 1.35 | 51.4 |
| 0.84 | 3.20 | 1.61 | 51.2 |
| 0.99 | 1.85 | 0.946 | 5.0 |

**REF well-mixed (positive control):**
| t | tr Σ̂ₜ | top-eig | angle [deg] | max eig G |
|---|---|---|---|---|
| 0.00 | 5.9e4 | 5.9e4 | 0.5 | +3.79 |
| 0.70 | 1.0e3 | 1.0e3 | 1.5 | +10.0 |
| 0.84 | 6.33 | 4.46 | 1.0 | +17.4 |
| 0.99 | 3.35 | 2.23 | 3.4 | **+20.4** |

- **Does tr Σ̂ₜ / top-eig rise toward t→1?** **A0/A3-NormB: partial then DROPS** — trace rises to ~3.2 at t≈0.84 then falls to 1.85 at t=0.99 (not the predicted monotone terminal rise). **REF well-mixed: the controlled-Jacobian expansion (max eig G) rises monotonically toward t→1 (3.8→20.4), as predicted by P3**, and the top-evec is **consistently aligned with the inter-mode (1,0) axis (angle ~0.5–3.4°)**.
- **Does the top eigenvector align with the inter-mode axis near t→1?** REF: **YES, cleanly** (≤3.4°). A0/A3-NormB: only intermittently (angle wanders 5–77°), consistent with no stable barrier-direction structure.
- **Verdict on mechanism presence:** **PARTIAL / regime-dependent.** The predicted expanding-terminal-barrier structure is **PRESENT in a sampler that bridges both modes** (positive, rising max-eig G; aligned eigenvector) but **ABSENT in the collapsed sampler AM actually trains.**

### 2b. Forced-expansion check (M6)
- `max eig(G)` in the barrier region: **A0 = −0.53 … −2.98 (NEGATIVE for all t)**; **A3-NormB = −0.30 … −1.65 (NEGATIVE)**; **REF = +3.8 … +20.4 (POSITIVE, rising to t=1)**.
- **Consistent with P3?** **Yes, but conditionally.** P3 (barrier ⇒ positive G eigenvalue ⇒ expansion) holds **only where the trained control actually forms a saddle bridging the modes** (the well-mixed sampler). The collapsed control is purely *contractive* (G≺0) at the barrier — it funnels all mass to one well and never creates the inter-mode expansion. **This is the crux of the kill (see §5): GLS is designed to reweight a structure that disappears precisely in the collapse regime it is meant to cure.**

## 3. Main results table (ALL configs × 5 seeds)

Per-seed minority occupancy (M1) is **0.0 for every seed of every config** (see §8). Metrics are seed-means.

| Config | M1 occ_min (per seed) | M1 mean±std | M2 recall (mean) | M3 sliced-W2 (mean) | M4 MMD (mean) | nE | unstable? |
|---|---|---|---|---|---|---|---|
| A0 (vanilla) | [0,0,0,0,0] | **0.0000±0.0000** | 1.00 | 2.6274 | 0.2718 | 1,536,000 | no |
| A3-NormA | [0,0,0,0,0] | 0.0000±0.0000 | 1.00 | 2.6276 | 0.2718 | 1,536,000 | no |
| A3-NormB | [0,0,0,0,0] | 0.0000±0.0000 | 1.00 | 2.6275 | 0.2724 | 1,536,000 | no |
| PROX | [0,0,0,0,0] | 0.0000±0.0000 | 1.00 | 2.6246 | 0.2707 | 1,536,000 | no |
| A1-NormB (diag) | [0,0,0,0,0] | 0.0000±0.0000 | 1.00 | 2.6276 | 0.2724 | 1,536,000 | no |
| A2-NormB (rank1) | [0,0,0,0,0] | 0.0000±0.0000 | 1.00 | 2.6285 | 0.2722 | 1,536,000 | no |
| ORACLE | [0,0,0,0,0] | 0.0000±0.0000 | 1.00 | 2.4929 | 0.2942 | 1,536,000 | no |
| A3-RAW | [0,0,0,0,0] | 0.0000±0.0000 | 1.00 | 2.6283 | 0.2719 | 1,536,000 | no |

**Seed-std noise scale** (std of M1 across seeds for A0, used for kill-conditions): **0.0000** (degenerate — every seed gives identical total collapse). With a zero noise scale the kill-conditions reduce to exact equality tests, all of which the data satisfies trivially.

## 4. Kill-condition verdicts (§8 applied exactly)

Seed-std = 0.0, so "within 1 seed-std of A0" means "exactly equal to A0".

- **K-H1 (primary).** occ(A0)=0.0000±0.0000; occ(A3-NormB)=0.0000; occ(A2-NormB)=0.0000. Both are within 1 seed-std (=0) of A0. → **H1 FALSIFIED.** A3-NormB exceeds A0 by **0.0 seed-std**. GLS-AM is downgraded to "provably-correct-but-inert reweighting."
- **K-MECH (mechanism isolation).** Required for H1 *support*: occ(A3-NormB) > occ(A0) by >2 seed-std → **NO** (0 vs 0).
  - Directional-only (A3-NormA vs A0): helps? **No** (0 vs 0).
  - Temporal adds value (A3-NormB vs A3-NormA): **No** (0 vs 0).
  - Direction matters (A1-NormB ≈ A0 while A3-NormB > A0): **No** — all equal 0.
  - **H3** (A2-NormB ≈ A3-NormB, cheap rank-1 suffices): both 0 → **vacuously equal; H3 cannot be SUPPORTED** because there is no benefit to be cheap about.
  - Scale artifact (A3-RAW vs A3-NormB diverge): **No** — identical (0 vs 0); the result is not a normalization/scale artifact.
  - **Oracle inert (ORACLE ≈ A0): YES (0 vs 0)** → **strongest possible kill: H1 is dead independent of Σ-estimation quality.** Even a Σ_t built from a well-mixed reference (which provably contains the predicted expanding structure) produces zero benefit when applied during collapsed training.
- **K-H2 (early read).** occ(best GLS)=0.0 vs occ(PROX)=0.0, within 1 seed-std. → **"proximal-in-disguise risk" FIRED** — but note this is *moot here*: GLS does not merely fail to beat PROX, **both fully collapse**. Neither local mechanism helps in this regime.

## 5. Overall verdict

**Primary verdict: (V4) — H1 falsified. GLS-AM variance-optimality is inert against mode collapse on this target.** Every W-shape (identity, diagonal, rank-1, full), every normalization (NormA/NormB/RAW), the oracle weight, and the proximal baseline give **identical, total collapse: minority occupancy exactly 0.0 across 5 seeds.** Because the oracle weight is also inert (K-MECH), the kill does not depend on Σ-estimation noise.

**Mechanistic refinement toward (V5):** the M5/M6 profiles show *why* it is inert — the expanding-terminal-barrier variance structure that GLS is derived to exploit is **regime-dependent**: it is present (positive, rising max-eig G; eigenvector aligned to the inter-mode axis) in a sampler that *already bridges both modes*, but **absent (purely contractive control) in the collapsed sampler.** A weight designed to down-weight a barrier direction has no effect when the trained control never forms the barrier-bridging saddle in the first place. GLS is, on this instance, **mis-targeted with respect to the failure mode** — it can only act once coverage already exists.

**The single most decision-relevant number:** occ_min = **0.0000** for **all 8 configs including ORACLE** (seed-std 0).

**Honest limitation (load-bearing for interpretation):** the collapse here is **total and immediate** (occ=0 by step 500), produced by a one-sided-prior deviation because the spec's symmetric setup *would not collapse at all*. In a total-collapse regime, the minority well receives **zero on-policy samples**, hence zero gradient signal — so **no purely local, measure-frozen reweighting (GLS or proximal) can possibly recover it.** This makes the test maximally adversarial: it cleanly **kills H1 and H2 in the total-collapse regime**, but it has **little power to detect a benefit in a milder *partial*-collapse regime** (e.g. occ ~0.02–0.15) where a few minority samples survive and a reweighting could plausibly amplify them. The strongest honest statement is therefore: *GLS-AM provides no escape from collapse once collapse is total, not even with oracle Σ_t; whether it helps in partial collapse is not settled by this experiment and is the obvious next test.*

## 6. Deviations from spec
1. **Collapse could not be induced by the spec's §3a ladder** (D/s/N/σ). Two further deviations were required (the spec anticipates this path and says to report it):
   - **Deviation #1 (tried, failed):** σ0-shrink ladder σ0∈{0.6,0.4,0.25}.
   - **Deviation #2 (used, user-approved "option C"):** one-sided prior `mu0=(3,0)` (+ a σ-reduction ladder that turned out unnecessary — the first offset rung at σ=1.5 already collapsed). **Only the sampler prior changed; the target remained the balanced GMM.**
2. **Steps reduced 15k → 3000** (calibration max 5000). Justified by §10: A0 collapses *totally by step ~500*, so 3000 steps gives every config 6× the collapse-onset horizon to escape if it can. Matched across all configs.
3. **`estimate_Sigma` vectorized** (scatter/`index_add` instead of a Python cell loop) for runtime; numerically equivalent occupancy-weighted within-cell covariance (same estimator, P4 preserved).
4. **ORACLE Σ_t** built from a balanced-prior ("well-mixed") reference sampler trained 2000 steps, then per-slice Σ_t averaged over 8 batches, full-GLS + NormB. (Spec offered "true GMM samples pushed through forward noising, or a long-trained model"; a well-mixed reference is the faithful analogue for a controlled SDE.)
5. Minor harness: conda env `SML_env`, absolute conda path under nohup.
No other tuning, schedules, or extra losses were added. M and W were kept detached throughout (P1).

## 7. Anomalies / instabilities
- **No NaNs, no divergences:** `diverged=False` for all 40 grid runs (and all calibration runs).
- **A2-NormB transient:** in a 200-step smoke, A2 (rank-1) briefly showed occ=0.034 / recall=2 while all others were ~0 — an *early-training* artifact that vanished by full training (final 0.0 all seeds). Listed for completeness; not a real effect.
- **REF early-time Σ trace is huge** (tr ≈ 5.9e4 at t=0): expected — the broad balanced prior makes early adjoint targets m_t very large; it is not an error and does not affect the (data-driven) M5 conclusion, which rests on the late-time aligned, rising max-eig G.
- **ORACLE M3/M4 differ slightly** (sw2 2.49 vs ~2.63; mmd 0.294 vs ~0.272): the oracle weights bias the collapsed cluster's shape marginally, but occupancy is still exactly 0 — cosmetic, not a coverage change.

## 8. Raw appendix (for independent re-derivation)
- `RESEARCH/temp/results.json` — per-seed all metrics, all 8 configs (occ, f0, f1, recall, sliced_w2, mmd, nE, diverged).
- `RESEARCH/temp/profiles.json` — full M5/M6 arrays (t, trace, topeig, angle, maxeig_G) for A0, A3-NormB, REF-wellmixed.
- `RESEARCH/temp/calib.json`, `calib2.json`, `calib3.json` — the three calibration ladders (per-rung histories + finals; `calib3._chosen` = locked settings).
- PNGs: `fig_occupancy_t20260630.png`, `fig_profiles_t20260630.png`, `fig_scatter_t20260630.png`.

**Per-seed M1 occupancy — ALL configs (verbatim):**
```
A0        [0.0, 0.0, 0.0, 0.0, 0.0]
A3-NormA  [0.0, 0.0, 0.0, 0.0, 0.0]
A3-NormB  [0.0, 0.0, 0.0, 0.0, 0.0]
PROX      [0.0, 0.0, 0.0, 0.0, 0.0]
A1-NormB  [0.0, 0.0, 0.0, 0.0, 0.0]
A2-NormB  [0.0, 0.0, 0.0, 0.0, 0.0]
ORACLE    [0.0, 0.0, 0.0, 0.0, 0.0]
A3-RAW    [0.0, 0.0, 0.0, 0.0, 0.0]
```

**M5 variance-profile (verbatim subsample), A0 vs A3-NormB:** `(t, tr, top-eig, angle°, maxeigG)`
```
A0:        t0.00(1.32,0.675,77.0,-0.53) t0.42(1.86,0.945,2.7,-0.83) t0.70(2.66,1.35,51.4,-1.03) t0.84(3.20,1.61,51.2,-2.21) t0.99(1.85,0.946,5.0,-2.98)
A3-NormB:  t0.00(1.34,0.680,82.3,-0.49) t0.42(1.89,0.951,23.7,-0.61) t0.70(2.65,1.35,63.7,-1.07) t0.84(3.14,1.57,61.0,-1.80) t0.99(1.85,0.941,21.0,-1.65)
REF:       t0.00(5.9e4,5.9e4,0.5,+3.79) t0.70(1.0e3,1.0e3,1.5,+10.0) t0.84(6.33,4.46,1.0,+17.4) t0.99(3.35,2.23,3.4,+20.4)
```
- Unexplained-but-noted: the A0/A3-NormB trace *peaks at t≈0.84 then falls* at t=0.99 rather than rising monotonically — the predicted terminal rise is not present in the collapsed sampler (consistent with the absent-mechanism reading).

## 9. What this does and does NOT establish
- **Establishes:**
  - On a balanced 2D GMM driven into **total** collapse, **GLS-weighted Adjoint Matching gives no improvement in mode coverage over vanilla AM** — across diagonal/rank-1/full weights and all normalizations (occ = 0.0, exactly, 5 seeds).
  - The result is **not** a Σ-estimation-quality artifact: the **oracle weight is equally inert** (strongest kill).
  - The result is **not** a normalization/scale artifact: A3-RAW = A3-NormB = A0.
  - **GLS does not beat a proximal-clip baseline** here — both fail identically (K-H2 fired).
  - **P4 confirmed operationally:** GLS adds zero energy/adjoint evaluations (equal nE across configs).
  - **Mechanistic:** the targeted expanding-barrier structure (P3) **exists only in a both-modes-covering sampler** and **vanishes in the collapsed regime**, explaining the inertness.
- **Does NOT establish:**
  - Anything about **partial-collapse** regimes (occ ~0.02–0.15), where a few surviving minority samples could let a reweighting act — **the key untested regime** and the recommended next experiment.
  - The full **H2 heavy-tail vs finite-variance** sweep (only the early read was in scope).
  - Behavior on **symmetric/broad-prior** setups (these did not collapse at all, so H1 was untestable there).
  - Higher-dimensional or real molecular targets (DW-4, LJ-13), Ising bimodal head-to-head.
  - Interaction with a **replay buffer** or Langevin preconditioning (on-policy, no-buffer by design).
  - Whether a *non-local* or coverage-restoring mechanism (annealing, tempering, exploration bonus) combined with GLS would differ — out of scope.

**Bottom line:** an honest negative result. In the total-collapse regime, variance-optimal reweighting — even with the oracle covariance — does nothing to restore the lost mode, because the structure it exploits is itself a casualty of the collapse. The decisive open question is whether GLS helps in *partial* collapse; this experiment does not answer it and is, by construction, unable to.
