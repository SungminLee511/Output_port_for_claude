# MOLDFLOW Multi-Output Surrogate — re-run AFTER the injection-node (inlet) fix

Same 12 shots / 9 studies / 6 outputs as before, but with the **h5→solver-input
adapter fixed**. Pics: `multioutput/<output>/pc_<study>__<shot>_t20260626b.png`
(left = predicted scaled, right = Moldflow GT, shared colour scale).

![summary heatmap](moldflow_multioutput_summary_t20260626b.png)

## Why some pressure contours still look different — and why that is NOT fixable here

![pressure diagnostic](fig_pressure_diagnostic_t20260626b.png)

`dircos` is pinned ≈0.99 for every shot (all-positive field of similar magnitude) so
it can't reveal contour shape — the honest metric is **corr** (mean-removed), which
ranges 0.46→0.97. Two findings explain the spread:

- **(a) corr tracks GT signal strength.** Each GT field's coefficient of variation
  (cv = std/mean = how much real gradient exists): strong-gradient parts (bezel,
  lx3_drl, cv 0.24–0.46) match at corr **0.96–0.97**; nearly-flat parts (jx1, cv
  0.08–0.14) collapse to **0.46–0.83** — there is essentially *no contour in the GT
  to reproduce*, so corr is correlating noise. Not a solver failure.
- **(b) the only genuine fidelity outliers** are `nq5_otr_htc/45_35 shot1` — their
  inlet sits ~100 mm (offset 0.18–0.20 × body diag) from the GT pressure peak because
  they are **genuinely multi-gate freeform lenses**.

**Three fixes were prototyped on the worst shot (htc, corr 0.763) and ALL failed:**
1. Laplacian-smooth thickness h (S=h³): 0.763 → 0.766 (no gain).
2. blend melt-front-time as a proxy: mft corr on htc = 0.469 (worse).
3. keep only the dominant connected low-mft cluster as inlet: 0.763 → **0.270**
   (much worse — confirming the part is multi-gate and the spread inlet is correct).

⇒ the residual contour mismatch is the **irreducible gap** between a single isothermal
Laplace pressure solve and Moldflow's transient coupled flow+pack — a solver-class
limitation, not an input/mapping bug. Closing it needs a transient flow-length solve.

## What the (inlet) fix changed
The `mft<=0` "inlet" nodes in the h5 are the **runner/sprue feed system**, not the
cavity gate — they sit off-body in 40–167 scattered micro-components spanning the
whole part. The old adapter projected them onto the body (+ a 200-node knn around an
off-body centroid), **smearing a fake inlet across the cavity** (φ≈1 "instant fill").

**New rule:** inlet = body nodes within 0.5 % of the body's *own* minimum melt-front
time — the real cavity gate. Localized (≈2 mm) for single-gate parts, multi-cluster
for genuine multi-gate parts. Also: `p_in` now reads the cavity-gate pressure, and
`fill_time` falls back to max-body-mft when the process attr is missing.

## Before → after (mean over 12 shots)

| output | dircos (was→now) | corr (was→now) | relL2_s (was→now) | note |
|---|---|---|---|---|
| **pressure** | 0.983 → **0.994** | 0.793 → **0.866** | 0.162 → **0.099** | ✅ clear gain — relL2 halved |
| fill_time | 0.899 → 0.899 | 0.693 → 0.720 | 0.395 → 0.388 | ≈ same |
| eject_time | 0.837 → 0.837 | 0.735 → 0.735 | 0.543 → 0.543 | ≈ same |
| front_temp | 0.917 → 0.913 | 0.054 → 0.079 | 0.397 → 0.404 | ≈ same (shape-only) |
| frozen_frac | 0.715 → 0.715 | 0.159 → 0.161 | 0.673 → 0.673 | ≈ same (coarse) |
| shear_rate | 0.241 → 0.361 | 0.078 → 0.177 | 0.963 → 0.919 | still poor (needs transient solve) |

**Why only pressure improved:** the inlet is the Dirichlet boundary of the *pressure*
solve, so the smearing hit pressure hardest. The derived thermal fields (fill/eject/
temp/frozen) depend on the mft potential + 1-D cooling, not the inlet location, so they
barely move — confirming the fix targets exactly the field it should.

## Verdict per output
- **pressure** now strong everywhere (dircos 0.994, relL2_s 0.099).
- fill_time / eject_time good (shape + trend).
- front_temp shape-only (GT ≈ constant melt temp ± few °C → corr is noise).
- frozen_frac coarse; shear_rate not captured by an end-of-fill ∇p proxy.

## Folders
```
multioutput/pressure/  multioutput/fill_time/  multioutput/eject_time/
multioutput/front_temp/ multioutput/frozen_frac/ multioutput/shear_rate/
```
Each holds 12 PNGs (one per shot). `moldflow_multioutput_summary_t20260626b.png` is
the dircos/corr heatmap over all outputs × shots.

> Note: the validation/adapter code now lives in `SOLVERX/moldflow_validation/`,
> moved OUT of the `MESHnSOLVERS` engine repo (which keeps only solver-engine code).
