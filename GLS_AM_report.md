# GLS-AM Experiment — Return Report (template to FILL IN)

> Claude Code: fill every section. Report raw per-seed numbers, not just means — the reader will re-derive verdicts independently and will not trust summary adjectives. If a result is ambiguous, say "inconclusive," do not round toward success. The most valuable outcome is an honest kill.

---

## 0. Run metadata
- Date / wall-clock total:
- Hardware (GPU, mem):
- Code commit / file hash of the run script:
- Library versions (torch, numpy):
- Random seeds used:
- **Final calibrated target/sampler settings** (from §3a): `D=`, `s=`, `N=`, `sigma=`, `sigma0=`, `lr=`, `B=`, `steps=`
- Total $\nabla E$ evaluations per config (must be EQUAL across configs — confirm or explain):

## 1. Calibration outcome (§3a) — did the baseline collapse?
- A0 minority-mode occupancy (M1), per seed: `[ , , , , ]`, mean ± std:
- **Did vanilla AM (A0) collapse?** (minority occupancy < 0.2 reliably) → YES / NO
- If NO: what was changed to induce collapse, or did it prove uninducible? (If uninducible, the kill-test cannot run — say so and stop.)
- One sentence: is the kill-test valid (baseline genuinely fails)?

## 2. Mechanism confirmation (M5, M6) — is the predicted variance structure actually present?
This decides whether the method even targets a real phenomenon (Threat B). Report for A0 and A3-NormB.

### 2a. Variance profile vs $t$ (M5) — give the actual numbers, not just "yes it rose"
Table (≈8 rows spanning $t\in[0,1]$):

| $t$ | $\mathrm{tr}\,\hat\Sigma_t$ | top-eig $\hat\Sigma_t$ | angle(top-evec, inter-mode axis) [deg] |
|---|---|---|---|
| 0.0 | | | |
| ... | | | |
| 1.0 | | | |

- Does $\mathrm{tr}\,\hat\Sigma_t$ / top-eig **rise toward $t\to1$** as predicted? YES / NO / partial:
- Does the top eigenvector **align with the inter-mode $(1,0)$ axis** near $t\to1$ (angle → 0/180°)? YES / NO:
- **Verdict on mechanism presence:** the predicted expanding-terminal-barrier variance structure is PRESENT / ABSENT / PARTIAL. (If ABSENT, the method is mis-targeted — flag loudly; the rest is likely moot.)

### 2b. Forced-expansion check (M6)
- $\max\mathrm{eig}(G_k)$ in the barrier region vs $t$ — is it $>0$ on a terminal interval? YES / NO, with the interval:
- Consistent with P3? YES / NO:

## 3. Main results table (ALL configs × per-seed)
Report per-seed M1 (minority occupancy), and mean ± std for every metric.

| Config | M1 occ_min (per seed) | M1 mean±std | M2 recall (mean) | M3 sliced-W2 (mean±std) | M4 MMD (mean±std) | unstable runs? |
|---|---|---|---|---|---|---|
| A0 (vanilla) | | | | | | |
| A3-NormA | | | | | | |
| A3-NormB | | | | | | |
| PROX | | | | | | |
| A1-NormB (diag) | | | | | | |
| A2-NormB (rank1) | | | | | | |
| ORACLE | | | | | | |
| A3-RAW | | | | | | |

Define the **seed-std noise scale** used for the kill-conditions (e.g. std of M1 across seeds for A0): `____`.

## 4. Kill-condition verdicts (apply §8 of the spec EXACTLY; show the arithmetic)
For each, state the numbers compared, the threshold, and FIRED / NOT-FIRED.

- **K-H1 (primary).** Compare occ(A3-NormB) and occ(A2-NormB) vs occ(A0), threshold = 1 seed-std.
  - Numbers: occ(A0)=`__±__`, occ(A3-NormB)=`__`, occ(A2-NormB)=`__`.
  - Verdict: **H1 FALSIFIED** / **H1 not falsified** (and by how many seed-std A3-NormB exceeds A0):
- **K-MECH (mechanism isolation).** Required for H1 *support*: occ(A3-NormB) > occ(A0) by > 2 seed-std?  YES / NO. Then:
  - Directional-only (A3-NormA vs A0): helps? by how much:
  - Temporal adds value (A3-NormB vs A3-NormA): YES / NO:
  - Direction matters (A1-NormB ≈ A0 while A3-NormB > A0): YES / NO:
  - **H3** (A2-NormB ≈ A3-NormB, cheap rank-1 suffices): SUPPORTED / NOT:
  - Scale artifact (A3-RAW vs A3-NormB diverge): YES / NO → discount?:
  - Oracle inert (ORACLE ≈ A0): YES / NO → if YES, H1 dead independent of estimation:
- **K-H2 (early read).** occ(best GLS) vs occ(PROX), threshold 1 seed-std.
  - Numbers:
  - Verdict: **proximal-in-disguise risk FIRED** / **GLS beats PROX here** (by how much):

## 5. Overall verdict (one short paragraph, honest)
Pick exactly one and justify with the numbers above:
- **(V1) H1 supported, mechanism isolated, cheap (rank-1) works, beats PROX** → proceed to harder targets (Ising bimodal head-to-head, then DW-4/LJ-13) and the H2 noise-regime sweep.
- **(V2) H1 supported but only via full $\Sigma$ (rank-1 inert)** → method works but is more expensive; H3 dead; proceed but reframe cost claim.
- **(V3) H1 supported but does NOT beat PROX** → proximal-in-disguise; not a distinct contribution on this target; needs the H2 regime split to find where GLS strictly wins, else likely dead as a paper.
- **(V4) H1 falsified (GLS ≈ vanilla)** → variance-optimality is inert against collapse; method downgraded to "provably-correct-but-inert reweighting." Report as a negative result.
- **(V5) mechanism absent (M5 profile not as predicted)** → method mis-targeted on this instance; the derived variance structure does not appear in the trained sampler; investigate before any further claim.

State which V, and the single most decision-relevant number behind it.

## 6. Deviations from spec
List every deviation from `GLS_AM_experiment.md` (numerical fixes, LR changes, anything). If none, write "none."

## 7. Anomalies / instabilities
NaNs, divergences, configs dropped, seeds that behaved differently, suspicious metric values. Be specific.

## 8. Raw appendix (for independent re-derivation)
- Path to `results.json` (per-seed all metrics), `profiles.json` (M5/M6 arrays), and PNGs.
- Paste the per-seed M1 occupancy arrays for ALL configs here verbatim.
- Paste the M5 variance-profile arrays (t, tr, top-eig, angle) for A0 and A3-NormB here verbatim.
- Anything that looked off but you couldn't explain — list it; do not omit it.

## 9. What this does and does NOT establish (fill in honestly)
- Establishes:
- Does NOT establish (e.g. higher-d, real molecular targets, heavy-tail regime, the full H2 sweep, interaction with replay buffer / Langevin preconditioning):
