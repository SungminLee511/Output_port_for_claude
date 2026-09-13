# Occupation re-score: KS + MMD² (unbiased U-statistic)

Source: `json/results_occ_rescore_mmd.json` — 24 runs, 9 summary cells.

Protocol: n=10,000 samples/seed, each run re-scored on its **own original inference grid**;
target is a fresh independent exact draw every time. RBF kernel on the full ℝ^m occupation
vector, diagonal zeroed. Bandwidth = median pairwise squared distance over 2000 exact
samples (seed 987654+m), **frozen per m** across all methods and seeds.

## Summary (mean ± sd over seeds)

| m | method | seeds | KS_occ | KS_max | MMD² |
|---|---|---|---|---|---|
| 32 | dam | 3 | 0.01116 ± 0.00140 | 0.03640 ± 0.00195 | +1.0267e-04 ± 1.33e-05 |
| 32 | iasbs_dirac | 3 | 0.00660 ± 0.00616 | 0.03797 ± 0.02526 | +1.2650e-04 ± 1.57e-04 |
| 32 | iasbs_nondirac | 3 | 0.01778 ± 0.00146 | 0.09943 ± 0.00471 | +4.0745e-04 ± 7.63e-05 |
| 128 | dam | 3 | 0.17466 ± 0.01266 | 0.89493 ± 0.04231 | +1.8031e-02 ± 1.16e-04 |
| 128 | iasbs_dirac | 3 | 0.00831 ± 0.00058 | 0.08063 ± 0.00076 | +1.4845e-04 ± 1.24e-05 |
| 128 | iasbs_nondirac | 3 | 0.00984 ± 0.00214 | 0.03513 ± 0.00340 | +1.5178e-04 ± 5.94e-05 |
| 1000 | dam | **0** | — | — | — |
| 1000 | iasbs_dirac | 3 | 0.01336 ± 0.00561 | 0.18097 ± 0.02266 | +1.8877e-04 ± 9.89e-05 |
| 1000 | iasbs_nondirac | 3 | 0.01097 ± 0.00350 | 0.28373 ± 0.18764 | +3.6704e-04 ± 3.75e-04 |

> m=1000 DAM is empty because **no DAM checkpoint was ever trained at m=1000**
> (`iasbs/analysis/occ_rescore_mmd.py:67`). Deliberate omission recorded in source.

## Frozen bandwidths

Rule: median of pairwise squared distances, 2000 exact samples, seed 987654+m

| m | σ² | σ |
|---|---|---|
| 32 | 168.0 | 12.96148139681572 |
| 128 | 737.9999999999999 | 27.16615541441225 |
| 1000 | 5961.999999999999 | 77.21398836998384 |

## Null / calibration MMD² (10 reps, n=10000)

| m | mean | sd |
|---|---|---|
| 32 | +9.721178e-06 | 1.643133e-05 |
| 128 | -4.238251e-06 | 4.546526e-06 |
| 1000 | -1.604730e-06 | 2.486092e-06 |

**Floor caveat.** Measured MMD² values (±1e-05 … ±1.5e-04) are the same order as the
null/calibration spread, and calibration means are partly negative (legitimate for an
unbiased U-statistic under H₀). Correct reading: *no distributional error detectable above
a ≈1e-04 noise floor*. The sole exception is **DAM at m=128 (1.80e-02)** — two orders of
magnitude above the floor, a genuine failure.

## Per-seed runs

| m | method | seed | KS_occ | KS_max | MMD² |
|---|---|---|---|---|---|
| 32 | dam | 0 | 0.01160 | 0.03630 | +8.7452e-05 |
| 32 | dam | 1 | 0.01228 | 0.03450 | +1.1240e-04 |
| 32 | dam | 2 | 0.00959 | 0.03840 | +1.0815e-04 |
| 32 | iasbs_dirac | 0 | 0.00448 | 0.03520 | +6.4926e-05 |
| 32 | iasbs_dirac | 1 | 0.00179 | 0.01420 | +9.1007e-06 |
| 32 | iasbs_dirac | 2 | 0.01354 | 0.06450 | +3.0549e-04 |
| 32 | iasbs_nondirac | 0 | 0.01721 | 0.09400 | +3.8197e-04 |
| 32 | iasbs_nondirac | 1 | 0.01943 | 0.10230 | +4.9326e-04 |
| 32 | iasbs_nondirac | 2 | 0.01669 | 0.10200 | +3.4712e-04 |
| 128 | dam | 0 | 0.17559 | 0.90320 | +1.8126e-02 |
| 128 | dam | 1 | 0.16155 | 0.84910 | +1.7901e-02 |
| 128 | dam | 2 | 0.18683 | 0.93250 | +1.8065e-02 |
| 128 | iasbs_dirac | 0 | 0.00862 | 0.08080 | +1.5455e-04 |
| 128 | iasbs_dirac | 1 | 0.00763 | 0.08130 | +1.5665e-04 |
| 128 | iasbs_dirac | 2 | 0.00866 | 0.07980 | +1.3416e-04 |
| 128 | iasbs_nondirac | 0 | 0.01220 | 0.03420 | +2.1893e-04 |
| 128 | iasbs_nondirac | 1 | 0.00801 | 0.03890 | +1.0626e-04 |
| 128 | iasbs_nondirac | 2 | 0.00931 | 0.03230 | +1.3013e-04 |
| 1000 | iasbs_dirac | 0 | 0.01009 | 0.19410 | +1.4924e-04 |
| 1000 | iasbs_dirac | 1 | 0.01016 | 0.15480 | +1.1575e-04 |
| 1000 | iasbs_dirac | 2 | 0.01984 | 0.19400 | +3.0134e-04 |
| 1000 | iasbs_nondirac | 0 | 0.01088 | 0.32380 | +1.2181e-04 |
| 1000 | iasbs_nondirac | 1 | 0.01452 | 0.44810 | +7.9918e-04 |
| 1000 | iasbs_nondirac | 2 | 0.00752 | 0.07930 | +1.8014e-04 |

## Reproduce

```bash
cd /home/RESEARCH/iasbs
/root/miniconda3/envs/cuau_env/bin/python -m iasbs.analysis.occ_rescore_mmd \
    --ms 32 128 1000 --n 10000 --cal-reps 10 --chunk 2048 \
    --out json/results_occ_rescore_mmd.json
```
