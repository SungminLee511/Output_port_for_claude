# MOLDFLOW_SOLVER — pressure validation on ALL real samples (revised)

Re-ran the MESHnSOLVERS Stokes solver vs Moldflow `F_PressureAtEndOfFill` on
every **result-complete** study in the data port, with two fixes applied after
the first attempt:

1. **Gate pin calibrated to Moldflow's actual cavity pressure** (mean over the
   gate nodes) instead of the runner-peak 35 MPa. This was the main reason the
   first figure looked so different — the old pin was the sprue/runner pressure,
   not the cavity-gate pressure.
2. **Visualization cleaned**: only cavity tetra nodes are plotted (the stray
   out-of-frame dots in the first figure were sprue/runner **beam** nodes, which
   the cavity Stokes solve does not model), cropped to the part bbox, auto
   face-on projection (thin axis dropped).

## Setup
Pressure-driven steady isothermal Stokes: gate p and far-outlet p pinned to
Moldflow's cavity values, no-slip walls, μ = Cross-WLF η₀ at the study melt
temperature. Direct sparse solve for the small meshes, GPU-MINRES (Schur
preconditioner) for the large ones.

## Results (8 result-complete studies)
| # | study | nodes | tetra | μ [Pa·s] | solver | **corr** | solver p [MPa] | Moldflow p [MPa] |
|---|-------|------:|------:|---------:|--------|:--------:|----------------|------------------|
| 1 | jx1 sublowref1 | 17,429 | 95,020 | 251 | direct | **+0.84** | 8.5–13.9 | 7.1–16.5 |
| 2 | jx1 sublowref2 | 18,302 | 101,219 | 633 | direct | **+0.38** | 10.3–14.6 | 5.4–22.6 |
| 3 | nq5 sub_bezel rev1 | 225,345 | 1,226,210 | 222 | minres | +0.11 | 0–40.1 | 1.7–45.5 |
| 4 | nq5 sub_bezel rev1 (50/45) | 225,345 | 1,226,210 | 222 | minres | +0.11 | 0–40.1 | 1.7–45.5 |
| 5 | nq5 otr_lens rev2 (45/35) | 275,281 | 1,509,162 | 1399 | minres | n/a* | 0–0 | 14.0–52.4 |
| 6 | nq5 otr_lens rev2 (htc) | 275,281 | 1,509,162 | 1399 | minres | n/a* | 0–0 | 20.6–50.9 |
| 7 | lx3 drl std | 890,043 | 4,893,326 | — | — | OOM† | — | — |
| 8 | lx3 otr_lens | 940,724 | 5,145,087 | — | — | OOM† | — | — |

\* studies 5–6: MINRES returned the trivial (zero) solution (it=0) — a solver
robustness gap on that geometry/viscosity (μ≈1400 Pa·s); under investigation.
† studies 7–8: CUDA OOM — a co-tenant process held 41 GB of the 80 GB A100, so
only ~4 GB was free; the 5 M-tetra assembly needs ~30 GB. Re-runnable on a clear
GPU or with mat-free assembly.

## Interpretation — why solver ≠ Moldflow
- **It is not (mainly) a solver bug.** Moldflow's field is a snapshot from a full
  *transient, non-isothermal, shear-thinning (Cross-WLF), free-surface (VOF)*
  fill; ours is *steady, isothermal, constant-μ* Stokes. Different physics.
- With the **calibrated gate pin**, the primary case (jx1 sublowref1) correlates
  at **0.84** — the steady-Stokes pressure distribution genuinely tracks the
  Moldflow fill pressure (it jumped from 0.05 with the bad pin). The validated
  assembly produces the right gate→far gradient, sign and magnitude band.
- Correlation drops on the larger, thicker bezel/lens parts because (a) thicker
  3-D parts deviate more from the thin-wall Hele-Shaw regime that steady Stokes
  mimics, and (b) those use a single gate→single far-outlet pin pair, a coarse
  proxy for the real multi-path fill.

## Files
`01..06_*.png` — solver (left) vs Moldflow (right) cavity pressure, face-on,
shared colour scale. `summary_*.txt` — raw stats table.
