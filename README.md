# Output Port for Claude

This repo is used to share result images from Claude Code.

**Timezone: KST (UTC+9)** — Server time is 9 hours behind KST.

## Results

### Moldflow Solver — Gmsh Test Cases (Element-based Viz) (2026-03-19 23:34 KST)

#### Cell 4: Boundary Classification (All 4 Geometries)
![cell4_boundary_classification](cell4_boundary_classification.png)

#### Cell 5: Plate with Rib — Isothermal, Constant Viscosity
![cell5_plate_rib](cell5_plate_rib.png)

#### Cell 6: Center-Gated Disc — Isothermal, Constant Viscosity
![cell6_disc](cell6_disc.png)

#### Cell 7: L-Bracket — Isothermal, Constant Viscosity
![cell7_l_bracket](cell7_l_bracket.png)

#### Cell 8: Stepped Plate — Isothermal, Constant Viscosity
![cell8_stepped_plate](cell8_stepped_plate.png)

#### Cell 9: Cross-WLF on Plate with Rib
![cell9_cross_wlf](cell9_cross_wlf.png)

---

### H5 Analysis Results — contact_test_jsp (2026-03-22 20:01 KST)

Full output of all 16 processed H5 files (attributes, shapes, dtypes):

[h5_analysis_results.txt](h5_analysis_results.txt)

---

### Shape Visualizations — Fixed BC & Contact (2026-03-22 20:09 KST)

Each figure shows 6 panels: Fixed BC category, Fixed DOF 1 (ux), Fixed DOF 2 (uy), Contact Master, Contact Slave, Contact One-Hot.

#### shape_1
![viz_shape_1](viz_shape_1.png)

#### shape_1-1MN
![viz_shape_1-1MN](viz_shape_1-1MN.png)

#### shape_2
![viz_shape_2](viz_shape_2.png)

#### shape_2-1MN
![viz_shape_2-1MN](viz_shape_2-1MN.png)

#### shape_3
![viz_shape_3](viz_shape_3.png)

#### shape_3-1MN
![viz_shape_3-1MN](viz_shape_3-1MN.png)

#### shape_4
![viz_shape_4](viz_shape_4.png)

#### shape_4-1MN
![viz_shape_4-1MN](viz_shape_4-1MN.png)

#### shape_5
![viz_shape_5](viz_shape_5.png)

#### shape_6
![viz_shape_6](viz_shape_6.png)

#### shape_7
![viz_shape_7](viz_shape_7.png)

#### shape_8
![viz_shape_8](viz_shape_8.png)

#### shape_9
![viz_shape_9](viz_shape_9.png)

#### shape_10
![viz_shape_10](viz_shape_10.png)

#### shape_11
![viz_shape_11](viz_shape_11.png)

#### shape_16
![viz_shape_16](viz_shape_16.png)

---

### Stein_ASBS — Grid25 NeurIPS Evaluation (2026-04-07 14:50 KST)

ASBS vs SDR-ASBS on 25-mode GMM. Both cover all 25 modes; SDR-ASBS is ~2× better on W₂ and Sinkhorn.

#### Terminal Distribution (Ground Truth / ASBS / SDR-ASBS)
![grid25_terminal](grid25_terminal_neurips.png)

#### Marginal Evolution: ASBS
![grid25_marginal_asbs](grid25_marginal_asbs_neurips.png)

#### Marginal Evolution: SDR-ASBS
![grid25_marginal_sdr](grid25_marginal_sdr_neurips.png)

---

### Stein_ASBS — Grid25 ASBS Seed 5 (Diverged) (2026-04-08 23:14 KST)

Seed 5 diverged at ~epoch 867 (loss exploded to 1e15 then NaN). This is the marginal evolution from **checkpoint_800.pt** — the last valid checkpoint before divergence.

#### Marginal Evolution: ASBS Seed 5 (ckpt 800)
![grid25_seed5_marginal](grid25_seed5_marginal_ckpt800.png)
