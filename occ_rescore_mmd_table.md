# Occupation re-score: IASBS Dirac / non-Dirac / DAM at m = N = 32, 128, 1000

- samples per seed: **10,000**
- target: independent exact Dirichlet-multinomial, d = 0.5, fresh draw per evaluation
- each checkpoint replayed on its own original inference grid (`steps` read from the checkpoint config)
- kernel: RBF `k(x,y) = exp(-||x-y||^2 / (2 sigma^2))` on the complete, unsorted occupation vector in R^m
- bandwidth: median heuristic, computed once per m on a dedicated exact draw, frozen across every method and seed
- MMD^2: unbiased estimator (diagonal dropped); calibration = 10 independent exact-vs-exact pairs

## Results (mean +- sd over training seeds, ddof = 1)

| m | method | seeds | KS_occ (pooled) | KS_max | MMD^2 | violations |
|---|---|---:|---|---|---|---:|
| 32 | IASBS Dirac | 3 | 0.00660 +- 0.00616 | 0.03797 +- 0.02526 | +1.265e-04 +- 1.57e-04 | 0 |
| 32 | IASBS non-Dirac | 3 | 0.01778 +- 0.00146 | 0.09943 +- 0.00471 | +4.075e-04 +- 7.63e-05 | 0 |
| 32 | DAM | 1 | 0.01160 | 0.03630 | +8.745e-05 | 0 |
| 128 | IASBS Dirac | 3 | 0.00831 +- 0.00058 | 0.08063 +- 0.00076 | +1.485e-04 +- 1.24e-05 | 0 |
| 128 | IASBS non-Dirac | 3 | 0.00984 +- 0.00214 | 0.03513 +- 0.00340 | +1.518e-04 +- 5.94e-05 | 0 |
| 128 | DAM | 3 | 0.17466 +- 0.01266 | 0.89493 +- 0.04231 | +1.803e-02 +- 1.16e-04 | 0 |
| 1000 | IASBS Dirac | 3 | 0.01336 +- 0.00561 | 0.18097 +- 0.02266 | +1.888e-04 +- 9.89e-05 | 0 |
| 1000 | IASBS non-Dirac | 3 | 0.01097 +- 0.00350 | 0.28373 +- 0.18764 | +3.670e-04 +- 3.75e-04 | 0 |
| 1000 | DAM | 0 | - | - | no checkpoint trained | - |

## Per seed

| m | method | seed | ckpt tag | steps | KS_occ | KS_max | MMD^2 |
|---|---|---:|---|---:|---|---|---|
| 32 | IASBS Dirac | 0 | `occ_s32` | 128 | 0.00448 | 0.03520 | +6.493e-05 |
| 32 | IASBS Dirac | 1 | `occ_s32_s1` | 128 | 0.00179 | 0.01420 | +9.101e-06 |
| 32 | IASBS Dirac | 2 | `occ_s32_s2` | 128 | 0.01354 | 0.06450 | +3.055e-04 |
| 32 | IASBS non-Dirac | 0 | `occ_nd_s32_seed0` | 128 | 0.01721 | 0.09400 | +3.820e-04 |
| 32 | IASBS non-Dirac | 1 | `occ_nd_s32_seed1` | 128 | 0.01943 | 0.10230 | +4.933e-04 |
| 32 | IASBS non-Dirac | 2 | `occ_nd_s32_s2` | 128 | 0.01669 | 0.10200 | +3.471e-04 |
| 32 | DAM | 0 | `dam_occs32_K64_1000` | 128 | 0.01160 | 0.03630 | +8.745e-05 |
| 128 | IASBS Dirac | 0 | `occ_s128` | 128 | 0.00862 | 0.08080 | +1.546e-04 |
| 128 | IASBS Dirac | 1 | `occ_s128_s1` | 128 | 0.00763 | 0.08130 | +1.566e-04 |
| 128 | IASBS Dirac | 2 | `occ_s128_s2` | 128 | 0.00866 | 0.07980 | +1.342e-04 |
| 128 | IASBS non-Dirac | 0 | `occ_nd_s128` | 128 | 0.01220 | 0.03420 | +2.189e-04 |
| 128 | IASBS non-Dirac | 1 | `occ_nd_s128_s1` | 128 | 0.00801 | 0.03890 | +1.063e-04 |
| 128 | IASBS non-Dirac | 2 | `occ_nd_s128_s2` | 128 | 0.00931 | 0.03230 | +1.301e-04 |
| 128 | DAM | 0 | `dam_occs128_K64_500` | 128 | 0.17559 | 0.90320 | +1.813e-02 |
| 128 | DAM | 1 | `dam_occs128_K64_500_s1` | 128 | 0.16155 | 0.84910 | +1.790e-02 |
| 128 | DAM | 2 | `dam_occs128_K64_500_s2` | 128 | 0.18683 | 0.93250 | +1.806e-02 |
| 1000 | IASBS Dirac | 0 | `occ_s1000` | 256 | 0.01009 | 0.19410 | +1.492e-04 |
| 1000 | IASBS Dirac | 1 | `occ_s1000_s1` | 256 | 0.01016 | 0.15480 | +1.157e-04 |
| 1000 | IASBS Dirac | 2 | `occ_s1000_s2` | 256 | 0.01984 | 0.19400 | +3.013e-04 |
| 1000 | IASBS non-Dirac | 0 | `occ_nd_s1000` | 256 | 0.01088 | 0.32380 | +1.218e-04 |
| 1000 | IASBS non-Dirac | 1 | `occ_nd_s1000_s1` | 256 | 0.01452 | 0.44810 | +7.992e-04 |
| 1000 | IASBS non-Dirac | 2 | `occ_nd_s1000_s2` | 256 | 0.00752 | 0.07930 | +1.801e-04 |

## Kernel bandwidth and target-vs-target MMD^2 calibration

| m | sigma | sigma^2 | target-vs-target MMD^2 | MMD^2(DAM)/null | MMD^2(IASBS Dirac)/null |
|---|---|---|---|---|---|
| 32 | 12.9615 | 168.0 | +9.721e-06 +- 1.64e-05 | 9x | 13x |
| 128 | 27.1662 | 738.0 | -4.238e-06 +- 4.55e-06 | 4254x | 35x |
| 1000 | 77.2140 | 5962.0 | -1.605e-06 +- 2.49e-06 | - | 118x |

The null straddles zero at every m, as required of the unbiased estimator, so MMD^2 values
are directly comparable against it. Ratios use |mean null| as the scale.

## Notes

- DAM has no m = 1000 checkpoint; that cell is empty, not failed.
- DAM m = 32 currently has 1 seed; seeds 1 and 2 are still training.
- Artifacts: `json/results_occ_rescore_mmd.json`, script `iasbs/analysis/occ_rescore_mmd.py`.
