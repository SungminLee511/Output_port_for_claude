# MOLDFLOW pressure validation — root cause of "nothing works" = h5→solver input mapping

Not the solver. The inlet/gate boundary condition was wired wrong.

## Bug
Cavity tetra mesh is **not one connected body** (nq5_sub_bezel: 66 components;
otr_lens overmolding: 236). The gate / injection (`F_MeltFrontTime≈0`) nodes are
**isolated single-node islands**, NOT in the main cavity component. The old script
applied gate pressure to `/runner` beam node IDs, which use a **separate numbering**
(only 1/66 coincides, and it isn't even the true gate). Result: pressure injected
into DOFs disconnected from the cavity → never propagates → near-zero field
(the single red gate dot), corr≈0.

## Fix
1. Keep the **largest connected component** as the cavity.
2. Map inlet by **spatial proximity** of the gate footprint (mft≈0 coords) onto
   main-body nodes (KD-tree), not by shared node IDs.
3. Flow front = high-`F_MeltFrontTime` main nodes (p≈0).
4. FE P1-tet Laplace pressure solve, compare on non-NaN `F_PressureAtEndOfFill`.

## Result (corr vs Moldflow F_PressureAtEndOfFill)
| case | old | NEW |
|---|---|---|
| jx1_sublowref1 | 0.84 | 0.79 |
| jx1_sublowref2 | 0.38 | 0.33 |
| **nq5_sub_bezel_rev1** | **0.11** | **0.72** |
| **nq5_sub_bezel_50_45** | **0.11** | **0.72** |
| nq5_otr_lens_45_35 (OM) | nan | nan* |
| nq5_otr_lens_htc (OM) | nan | nan* |

\* overmolding: 2 shots, mesh fragments into 236 comps (main=55%); needs per-shot
input construction (separate body + mft/pressure field per shot) — same input-mapping
theme, deeper refinement, still not a solver bug.

![nq5](moldflow_inlet_fix_nq5_t20260625.png)

## Overmolding (otr_lens) — per-shot fix
OM studies are **two shots = two separate connected bodies** (comp0=124811 nodes
shot1, comp1=150236 shot2). Old single-domain solve → nan. Fix: solve **per shot** —
pick each shot's body (component where its `F_MeltFrontTime[_OM]` is defined), map
that shot's gate footprint by proximity, use that shot's `F_PressureAtEndOfFill[_OM]`
as target. Also dropped degenerate (zero-volume) tets in assembly.

| case | shot | old | NEW |
|---|---|---|---|
| otr_lens_htc | shot1 | nan | 0.90 |
| otr_lens_htc | shot2 (OM) | nan | 0.81 |
| otr_lens_45_35 | shot1 | nan | 0.81 |
| otr_lens_45_35 | shot2 (OM) | nan | 0.90 |

![overmolding](moldflow_overmolding_fix_t20260625.png)
