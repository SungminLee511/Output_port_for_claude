# Origami_Gen v2.0 — Full Pipeline Test + Visualization

**Run date:** 2026-05-31 KST
**Pipeline:** P1 parse → P2 topology → P3 fold → P4 mesh → P5 stitch →
P6 mapper → P7 dihedral → P8 fillet → P9 mapper (propagate) →
P10 bump+cut → Export.

**Audit** (`scripts/audit.py --full`):
- 42 cases × 3 resolutions (2.0, 4.0, 8.0) = **126 runs**
- **0 errors**, all gates pass
- Wall: **16 min 27 s**, summary CSV in `output/summary.csv`

**Visualization** (`scripts/verify_visualize.py --resolution 2.0 --workers 4`):
- 42 cases, 12 PNGs per case (3 input + 9 per-phase + 1 dihedral + 1 composite)
- Wall: **39 min 03 s** (with `--workers 4`)
- Single composite per case shows P1→P10 in one figure

**Per-case PNG legend:**
| File | Phase |
|------|-------|
| `<case>_main.png` | input — panels + fold lines |
| `<case>_bump.png` | input — yellow / green bump overlay |
| `<case>_hole.png` | input — purple hole overlay |
| `parse.png` | P1 — parsed panel + fold layout |
| `topology.png` | P2 — BFS panel tree + 2D junctions |
| `fold.png` | P3 — 3D pose corners |
| `mesh_p4.png` | P4 — per-panel quad mesh |
| `stitch_p5.png` | P5 — post-stitch (free / non-manifold overlays) |
| `mapper_p6.png` | P6 — per-element yellow/green/purple labels |
| `dihedral_p7.png` | P7 — ~90° fold-seam edges + BFS shells |
| `fillet_p8.png` | P8 — cylinder + sphere fillet patches |
| `mapper_p9.png` | P9 — propagated labels on fillet tris |
| `bump_p10.png` | P10 — post-bump-cut-snap |
| `composite.png` | All 10 phases in one row |

## Cross-case gate-pass matrix

![headline](headline_t20260531.png)


## Per-case storyboards


### accessory_l_bracket


**input — panels + fold lines**

![accessory_l_bracket main](accessory_l_bracket_main_t20260531.png)


**input — yellow/green bump overlay**

![accessory_l_bracket bump](accessory_l_bracket_bump_t20260531.png)


**input — purple hole overlay**

![accessory_l_bracket hole](accessory_l_bracket_hole_t20260531.png)


**P1 parse**

![accessory_l_bracket parse](accessory_l_bracket_parse_t20260531.png)


**P2 topology**

![accessory_l_bracket topology](accessory_l_bracket_topology_t20260531.png)


**P3 fold**

![accessory_l_bracket fold](accessory_l_bracket_fold_t20260531.png)


**P4 mesh**

![accessory_l_bracket mesh_p4](accessory_l_bracket_mesh_p4_t20260531.png)


**P5 stitch**

![accessory_l_bracket stitch_p5](accessory_l_bracket_stitch_p5_t20260531.png)


**P6 mapper**

![accessory_l_bracket mapper_p6](accessory_l_bracket_mapper_p6_t20260531.png)


**P7 dihedral**

![accessory_l_bracket dihedral_p7](accessory_l_bracket_dihedral_p7_t20260531.png)


**P8 fillet**

![accessory_l_bracket fillet_p8](accessory_l_bracket_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![accessory_l_bracket mapper_p9](accessory_l_bracket_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![accessory_l_bracket bump_p10](accessory_l_bracket_bump_p10_t20260531.png)


**All phases composite**

![accessory_l_bracket composite](accessory_l_bracket_composite_t20260531.png)


---


### box_unfolding


**input — panels + fold lines**

![box_unfolding main](box_unfolding_main_t20260531.png)


**input — yellow/green bump overlay**

![box_unfolding bump](box_unfolding_bump_t20260531.png)


**input — purple hole overlay**

![box_unfolding hole](box_unfolding_hole_t20260531.png)


**P1 parse**

![box_unfolding parse](box_unfolding_parse_t20260531.png)


**P2 topology**

![box_unfolding topology](box_unfolding_topology_t20260531.png)


**P3 fold**

![box_unfolding fold](box_unfolding_fold_t20260531.png)


**P4 mesh**

![box_unfolding mesh_p4](box_unfolding_mesh_p4_t20260531.png)


**P5 stitch**

![box_unfolding stitch_p5](box_unfolding_stitch_p5_t20260531.png)


**P6 mapper**

![box_unfolding mapper_p6](box_unfolding_mapper_p6_t20260531.png)


**P7 dihedral**

![box_unfolding dihedral_p7](box_unfolding_dihedral_p7_t20260531.png)


**P8 fillet**

![box_unfolding fillet_p8](box_unfolding_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![box_unfolding mapper_p9](box_unfolding_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![box_unfolding bump_p10](box_unfolding_bump_p10_t20260531.png)


**All phases composite**

![box_unfolding composite](box_unfolding_composite_t20260531.png)


---


### bracket_v01


**input — panels + fold lines**

![bracket_v01 main](bracket_v01_main_t20260531.png)


**input — yellow/green bump overlay**

![bracket_v01 bump](bracket_v01_bump_t20260531.png)


**input — purple hole overlay**

![bracket_v01 hole](bracket_v01_hole_t20260531.png)


**P1 parse**

![bracket_v01 parse](bracket_v01_parse_t20260531.png)


**P2 topology**

![bracket_v01 topology](bracket_v01_topology_t20260531.png)


**P3 fold**

![bracket_v01 fold](bracket_v01_fold_t20260531.png)


**P4 mesh**

![bracket_v01 mesh_p4](bracket_v01_mesh_p4_t20260531.png)


**P5 stitch**

![bracket_v01 stitch_p5](bracket_v01_stitch_p5_t20260531.png)


**P6 mapper**

![bracket_v01 mapper_p6](bracket_v01_mapper_p6_t20260531.png)


**P7 dihedral**

![bracket_v01 dihedral_p7](bracket_v01_dihedral_p7_t20260531.png)


**P8 fillet**

![bracket_v01 fillet_p8](bracket_v01_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![bracket_v01 mapper_p9](bracket_v01_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![bracket_v01 bump_p10](bracket_v01_bump_p10_t20260531.png)


**All phases composite**

![bracket_v01 composite](bracket_v01_composite_t20260531.png)


---


### bracket_v02


**input — panels + fold lines**

![bracket_v02 main](bracket_v02_main_t20260531.png)


**input — yellow/green bump overlay**

![bracket_v02 bump](bracket_v02_bump_t20260531.png)


**input — purple hole overlay**

![bracket_v02 hole](bracket_v02_hole_t20260531.png)


**P1 parse**

![bracket_v02 parse](bracket_v02_parse_t20260531.png)


**P2 topology**

![bracket_v02 topology](bracket_v02_topology_t20260531.png)


**P3 fold**

![bracket_v02 fold](bracket_v02_fold_t20260531.png)


**P4 mesh**

![bracket_v02 mesh_p4](bracket_v02_mesh_p4_t20260531.png)


**P5 stitch**

![bracket_v02 stitch_p5](bracket_v02_stitch_p5_t20260531.png)


**P6 mapper**

![bracket_v02 mapper_p6](bracket_v02_mapper_p6_t20260531.png)


**P7 dihedral**

![bracket_v02 dihedral_p7](bracket_v02_dihedral_p7_t20260531.png)


**P8 fillet**

![bracket_v02 fillet_p8](bracket_v02_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![bracket_v02 mapper_p9](bracket_v02_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![bracket_v02 bump_p10](bracket_v02_bump_p10_t20260531.png)


**All phases composite**

![bracket_v02 composite](bracket_v02_composite_t20260531.png)


---


### bracket_v03


**input — panels + fold lines**

![bracket_v03 main](bracket_v03_main_t20260531.png)


**input — yellow/green bump overlay**

![bracket_v03 bump](bracket_v03_bump_t20260531.png)


**input — purple hole overlay**

![bracket_v03 hole](bracket_v03_hole_t20260531.png)


**P1 parse**

![bracket_v03 parse](bracket_v03_parse_t20260531.png)


**P2 topology**

![bracket_v03 topology](bracket_v03_topology_t20260531.png)


**P3 fold**

![bracket_v03 fold](bracket_v03_fold_t20260531.png)


**P4 mesh**

![bracket_v03 mesh_p4](bracket_v03_mesh_p4_t20260531.png)


**P5 stitch**

![bracket_v03 stitch_p5](bracket_v03_stitch_p5_t20260531.png)


**P6 mapper**

![bracket_v03 mapper_p6](bracket_v03_mapper_p6_t20260531.png)


**P7 dihedral**

![bracket_v03 dihedral_p7](bracket_v03_dihedral_p7_t20260531.png)


**P8 fillet**

![bracket_v03 fillet_p8](bracket_v03_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![bracket_v03 mapper_p9](bracket_v03_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![bracket_v03 bump_p10](bracket_v03_bump_p10_t20260531.png)


**All phases composite**

![bracket_v03 composite](bracket_v03_composite_t20260531.png)


---


### bracket_v04


**input — panels + fold lines**

![bracket_v04 main](bracket_v04_main_t20260531.png)


**input — yellow/green bump overlay**

![bracket_v04 bump](bracket_v04_bump_t20260531.png)


**input — purple hole overlay**

![bracket_v04 hole](bracket_v04_hole_t20260531.png)


**P1 parse**

![bracket_v04 parse](bracket_v04_parse_t20260531.png)


**P2 topology**

![bracket_v04 topology](bracket_v04_topology_t20260531.png)


**P3 fold**

![bracket_v04 fold](bracket_v04_fold_t20260531.png)


**P4 mesh**

![bracket_v04 mesh_p4](bracket_v04_mesh_p4_t20260531.png)


**P5 stitch**

![bracket_v04 stitch_p5](bracket_v04_stitch_p5_t20260531.png)


**P6 mapper**

![bracket_v04 mapper_p6](bracket_v04_mapper_p6_t20260531.png)


**P7 dihedral**

![bracket_v04 dihedral_p7](bracket_v04_dihedral_p7_t20260531.png)


**P8 fillet**

![bracket_v04 fillet_p8](bracket_v04_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![bracket_v04 mapper_p9](bracket_v04_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![bracket_v04 bump_p10](bracket_v04_bump_p10_t20260531.png)


**All phases composite**

![bracket_v04 composite](bracket_v04_composite_t20260531.png)


---


### bracket_v05


**input — panels + fold lines**

![bracket_v05 main](bracket_v05_main_t20260531.png)


**input — yellow/green bump overlay**

![bracket_v05 bump](bracket_v05_bump_t20260531.png)


**input — purple hole overlay**

![bracket_v05 hole](bracket_v05_hole_t20260531.png)


**P1 parse**

![bracket_v05 parse](bracket_v05_parse_t20260531.png)


**P2 topology**

![bracket_v05 topology](bracket_v05_topology_t20260531.png)


**P3 fold**

![bracket_v05 fold](bracket_v05_fold_t20260531.png)


**P4 mesh**

![bracket_v05 mesh_p4](bracket_v05_mesh_p4_t20260531.png)


**P5 stitch**

![bracket_v05 stitch_p5](bracket_v05_stitch_p5_t20260531.png)


**P6 mapper**

![bracket_v05 mapper_p6](bracket_v05_mapper_p6_t20260531.png)


**P7 dihedral**

![bracket_v05 dihedral_p7](bracket_v05_dihedral_p7_t20260531.png)


**P8 fillet**

![bracket_v05 fillet_p8](bracket_v05_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![bracket_v05 mapper_p9](bracket_v05_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![bracket_v05 bump_p10](bracket_v05_bump_p10_t20260531.png)


**All phases composite**

![bracket_v05 composite](bracket_v05_composite_t20260531.png)


---


### bracket_v06


**input — panels + fold lines**

![bracket_v06 main](bracket_v06_main_t20260531.png)


**input — yellow/green bump overlay**

![bracket_v06 bump](bracket_v06_bump_t20260531.png)


**input — purple hole overlay**

![bracket_v06 hole](bracket_v06_hole_t20260531.png)


**P1 parse**

![bracket_v06 parse](bracket_v06_parse_t20260531.png)


**P2 topology**

![bracket_v06 topology](bracket_v06_topology_t20260531.png)


**P3 fold**

![bracket_v06 fold](bracket_v06_fold_t20260531.png)


**P4 mesh**

![bracket_v06 mesh_p4](bracket_v06_mesh_p4_t20260531.png)


**P5 stitch**

![bracket_v06 stitch_p5](bracket_v06_stitch_p5_t20260531.png)


**P6 mapper**

![bracket_v06 mapper_p6](bracket_v06_mapper_p6_t20260531.png)


**P7 dihedral**

![bracket_v06 dihedral_p7](bracket_v06_dihedral_p7_t20260531.png)


**P8 fillet**

![bracket_v06 fillet_p8](bracket_v06_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![bracket_v06 mapper_p9](bracket_v06_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![bracket_v06 bump_p10](bracket_v06_bump_p10_t20260531.png)


**All phases composite**

![bracket_v06 composite](bracket_v06_composite_t20260531.png)


---


### bracket_v07


**input — panels + fold lines**

![bracket_v07 main](bracket_v07_main_t20260531.png)


**input — yellow/green bump overlay**

![bracket_v07 bump](bracket_v07_bump_t20260531.png)


**input — purple hole overlay**

![bracket_v07 hole](bracket_v07_hole_t20260531.png)


**P1 parse**

![bracket_v07 parse](bracket_v07_parse_t20260531.png)


**P2 topology**

![bracket_v07 topology](bracket_v07_topology_t20260531.png)


**P3 fold**

![bracket_v07 fold](bracket_v07_fold_t20260531.png)


**P4 mesh**

![bracket_v07 mesh_p4](bracket_v07_mesh_p4_t20260531.png)


**P5 stitch**

![bracket_v07 stitch_p5](bracket_v07_stitch_p5_t20260531.png)


**P6 mapper**

![bracket_v07 mapper_p6](bracket_v07_mapper_p6_t20260531.png)


**P7 dihedral**

![bracket_v07 dihedral_p7](bracket_v07_dihedral_p7_t20260531.png)


**P8 fillet**

![bracket_v07 fillet_p8](bracket_v07_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![bracket_v07 mapper_p9](bracket_v07_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![bracket_v07 bump_p10](bracket_v07_bump_p10_t20260531.png)


**All phases composite**

![bracket_v07 composite](bracket_v07_composite_t20260531.png)


---


### bracket_v08


**input — panels + fold lines**

![bracket_v08 main](bracket_v08_main_t20260531.png)


**input — yellow/green bump overlay**

![bracket_v08 bump](bracket_v08_bump_t20260531.png)


**input — purple hole overlay**

![bracket_v08 hole](bracket_v08_hole_t20260531.png)


**P1 parse**

![bracket_v08 parse](bracket_v08_parse_t20260531.png)


**P2 topology**

![bracket_v08 topology](bracket_v08_topology_t20260531.png)


**P3 fold**

![bracket_v08 fold](bracket_v08_fold_t20260531.png)


**P4 mesh**

![bracket_v08 mesh_p4](bracket_v08_mesh_p4_t20260531.png)


**P5 stitch**

![bracket_v08 stitch_p5](bracket_v08_stitch_p5_t20260531.png)


**P6 mapper**

![bracket_v08 mapper_p6](bracket_v08_mapper_p6_t20260531.png)


**P7 dihedral**

![bracket_v08 dihedral_p7](bracket_v08_dihedral_p7_t20260531.png)


**P8 fillet**

![bracket_v08 fillet_p8](bracket_v08_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![bracket_v08 mapper_p9](bracket_v08_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![bracket_v08 bump_p10](bracket_v08_bump_p10_t20260531.png)


**All phases composite**

![bracket_v08 composite](bracket_v08_composite_t20260531.png)


---


### bracket_v09


**input — panels + fold lines**

![bracket_v09 main](bracket_v09_main_t20260531.png)


**input — yellow/green bump overlay**

![bracket_v09 bump](bracket_v09_bump_t20260531.png)


**input — purple hole overlay**

![bracket_v09 hole](bracket_v09_hole_t20260531.png)


**P1 parse**

![bracket_v09 parse](bracket_v09_parse_t20260531.png)


**P2 topology**

![bracket_v09 topology](bracket_v09_topology_t20260531.png)


**P3 fold**

![bracket_v09 fold](bracket_v09_fold_t20260531.png)


**P4 mesh**

![bracket_v09 mesh_p4](bracket_v09_mesh_p4_t20260531.png)


**P5 stitch**

![bracket_v09 stitch_p5](bracket_v09_stitch_p5_t20260531.png)


**P6 mapper**

![bracket_v09 mapper_p6](bracket_v09_mapper_p6_t20260531.png)


**P7 dihedral**

![bracket_v09 dihedral_p7](bracket_v09_dihedral_p7_t20260531.png)


**P8 fillet**

![bracket_v09 fillet_p8](bracket_v09_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![bracket_v09 mapper_p9](bracket_v09_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![bracket_v09 bump_p10](bracket_v09_bump_p10_t20260531.png)


**All phases composite**

![bracket_v09 composite](bracket_v09_composite_t20260531.png)


---


### bracket_v10


**input — panels + fold lines**

![bracket_v10 main](bracket_v10_main_t20260531.png)


**input — yellow/green bump overlay**

![bracket_v10 bump](bracket_v10_bump_t20260531.png)


**input — purple hole overlay**

![bracket_v10 hole](bracket_v10_hole_t20260531.png)


**P1 parse**

![bracket_v10 parse](bracket_v10_parse_t20260531.png)


**P2 topology**

![bracket_v10 topology](bracket_v10_topology_t20260531.png)


**P3 fold**

![bracket_v10 fold](bracket_v10_fold_t20260531.png)


**P4 mesh**

![bracket_v10 mesh_p4](bracket_v10_mesh_p4_t20260531.png)


**P5 stitch**

![bracket_v10 stitch_p5](bracket_v10_stitch_p5_t20260531.png)


**P6 mapper**

![bracket_v10 mapper_p6](bracket_v10_mapper_p6_t20260531.png)


**P7 dihedral**

![bracket_v10 dihedral_p7](bracket_v10_dihedral_p7_t20260531.png)


**P8 fillet**

![bracket_v10 fillet_p8](bracket_v10_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![bracket_v10 mapper_p9](bracket_v10_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![bracket_v10 bump_p10](bracket_v10_bump_p10_t20260531.png)


**All phases composite**

![bracket_v10 composite](bracket_v10_composite_t20260531.png)


---


### bracket_v11


**input — panels + fold lines**

![bracket_v11 main](bracket_v11_main_t20260531.png)


**input — yellow/green bump overlay**

![bracket_v11 bump](bracket_v11_bump_t20260531.png)


**input — purple hole overlay**

![bracket_v11 hole](bracket_v11_hole_t20260531.png)


**P1 parse**

![bracket_v11 parse](bracket_v11_parse_t20260531.png)


**P2 topology**

![bracket_v11 topology](bracket_v11_topology_t20260531.png)


**P3 fold**

![bracket_v11 fold](bracket_v11_fold_t20260531.png)


**P4 mesh**

![bracket_v11 mesh_p4](bracket_v11_mesh_p4_t20260531.png)


**P5 stitch**

![bracket_v11 stitch_p5](bracket_v11_stitch_p5_t20260531.png)


**P6 mapper**

![bracket_v11 mapper_p6](bracket_v11_mapper_p6_t20260531.png)


**P7 dihedral**

![bracket_v11 dihedral_p7](bracket_v11_dihedral_p7_t20260531.png)


**P8 fillet**

![bracket_v11 fillet_p8](bracket_v11_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![bracket_v11 mapper_p9](bracket_v11_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![bracket_v11 bump_p10](bracket_v11_bump_p10_t20260531.png)


**All phases composite**

![bracket_v11 composite](bracket_v11_composite_t20260531.png)


---


### bracket_v12


**input — panels + fold lines**

![bracket_v12 main](bracket_v12_main_t20260531.png)


**input — yellow/green bump overlay**

![bracket_v12 bump](bracket_v12_bump_t20260531.png)


**input — purple hole overlay**

![bracket_v12 hole](bracket_v12_hole_t20260531.png)


**P1 parse**

![bracket_v12 parse](bracket_v12_parse_t20260531.png)


**P2 topology**

![bracket_v12 topology](bracket_v12_topology_t20260531.png)


**P3 fold**

![bracket_v12 fold](bracket_v12_fold_t20260531.png)


**P4 mesh**

![bracket_v12 mesh_p4](bracket_v12_mesh_p4_t20260531.png)


**P5 stitch**

![bracket_v12 stitch_p5](bracket_v12_stitch_p5_t20260531.png)


**P6 mapper**

![bracket_v12 mapper_p6](bracket_v12_mapper_p6_t20260531.png)


**P7 dihedral**

![bracket_v12 dihedral_p7](bracket_v12_dihedral_p7_t20260531.png)


**P8 fillet**

![bracket_v12 fillet_p8](bracket_v12_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![bracket_v12 mapper_p9](bracket_v12_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![bracket_v12 bump_p10](bracket_v12_bump_p10_t20260531.png)


**All phases composite**

![bracket_v12 composite](bracket_v12_composite_t20260531.png)


---


### bracket_v13


**input — panels + fold lines**

![bracket_v13 main](bracket_v13_main_t20260531.png)


**input — yellow/green bump overlay**

![bracket_v13 bump](bracket_v13_bump_t20260531.png)


**input — purple hole overlay**

![bracket_v13 hole](bracket_v13_hole_t20260531.png)


**P1 parse**

![bracket_v13 parse](bracket_v13_parse_t20260531.png)


**P2 topology**

![bracket_v13 topology](bracket_v13_topology_t20260531.png)


**P3 fold**

![bracket_v13 fold](bracket_v13_fold_t20260531.png)


**P4 mesh**

![bracket_v13 mesh_p4](bracket_v13_mesh_p4_t20260531.png)


**P5 stitch**

![bracket_v13 stitch_p5](bracket_v13_stitch_p5_t20260531.png)


**P6 mapper**

![bracket_v13 mapper_p6](bracket_v13_mapper_p6_t20260531.png)


**P7 dihedral**

![bracket_v13 dihedral_p7](bracket_v13_dihedral_p7_t20260531.png)


**P8 fillet**

![bracket_v13 fillet_p8](bracket_v13_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![bracket_v13 mapper_p9](bracket_v13_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![bracket_v13 bump_p10](bracket_v13_bump_p10_t20260531.png)


**All phases composite**

![bracket_v13 composite](bracket_v13_composite_t20260531.png)


---


### bracket_v14


**input — panels + fold lines**

![bracket_v14 main](bracket_v14_main_t20260531.png)


**input — yellow/green bump overlay**

![bracket_v14 bump](bracket_v14_bump_t20260531.png)


**input — purple hole overlay**

![bracket_v14 hole](bracket_v14_hole_t20260531.png)


**P1 parse**

![bracket_v14 parse](bracket_v14_parse_t20260531.png)


**P2 topology**

![bracket_v14 topology](bracket_v14_topology_t20260531.png)


**P3 fold**

![bracket_v14 fold](bracket_v14_fold_t20260531.png)


**P4 mesh**

![bracket_v14 mesh_p4](bracket_v14_mesh_p4_t20260531.png)


**P5 stitch**

![bracket_v14 stitch_p5](bracket_v14_stitch_p5_t20260531.png)


**P6 mapper**

![bracket_v14 mapper_p6](bracket_v14_mapper_p6_t20260531.png)


**P7 dihedral**

![bracket_v14 dihedral_p7](bracket_v14_dihedral_p7_t20260531.png)


**P8 fillet**

![bracket_v14 fillet_p8](bracket_v14_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![bracket_v14 mapper_p9](bracket_v14_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![bracket_v14 bump_p10](bracket_v14_bump_p10_t20260531.png)


**All phases composite**

![bracket_v14 composite](bracket_v14_composite_t20260531.png)


---


### bracket_v15


**input — panels + fold lines**

![bracket_v15 main](bracket_v15_main_t20260531.png)


**input — yellow/green bump overlay**

![bracket_v15 bump](bracket_v15_bump_t20260531.png)


**input — purple hole overlay**

![bracket_v15 hole](bracket_v15_hole_t20260531.png)


**P1 parse**

![bracket_v15 parse](bracket_v15_parse_t20260531.png)


**P2 topology**

![bracket_v15 topology](bracket_v15_topology_t20260531.png)


**P3 fold**

![bracket_v15 fold](bracket_v15_fold_t20260531.png)


**P4 mesh**

![bracket_v15 mesh_p4](bracket_v15_mesh_p4_t20260531.png)


**P5 stitch**

![bracket_v15 stitch_p5](bracket_v15_stitch_p5_t20260531.png)


**P6 mapper**

![bracket_v15 mapper_p6](bracket_v15_mapper_p6_t20260531.png)


**P7 dihedral**

![bracket_v15 dihedral_p7](bracket_v15_dihedral_p7_t20260531.png)


**P8 fillet**

![bracket_v15 fillet_p8](bracket_v15_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![bracket_v15 mapper_p9](bracket_v15_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![bracket_v15 bump_p10](bracket_v15_bump_p10_t20260531.png)


**All phases composite**

![bracket_v15 composite](bracket_v15_composite_t20260531.png)


---


### bracket_v16


**input — panels + fold lines**

![bracket_v16 main](bracket_v16_main_t20260531.png)


**input — yellow/green bump overlay**

![bracket_v16 bump](bracket_v16_bump_t20260531.png)


**input — purple hole overlay**

![bracket_v16 hole](bracket_v16_hole_t20260531.png)


**P1 parse**

![bracket_v16 parse](bracket_v16_parse_t20260531.png)


**P2 topology**

![bracket_v16 topology](bracket_v16_topology_t20260531.png)


**P3 fold**

![bracket_v16 fold](bracket_v16_fold_t20260531.png)


**P4 mesh**

![bracket_v16 mesh_p4](bracket_v16_mesh_p4_t20260531.png)


**P5 stitch**

![bracket_v16 stitch_p5](bracket_v16_stitch_p5_t20260531.png)


**P6 mapper**

![bracket_v16 mapper_p6](bracket_v16_mapper_p6_t20260531.png)


**P7 dihedral**

![bracket_v16 dihedral_p7](bracket_v16_dihedral_p7_t20260531.png)


**P8 fillet**

![bracket_v16 fillet_p8](bracket_v16_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![bracket_v16 mapper_p9](bracket_v16_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![bracket_v16 bump_p10](bracket_v16_bump_p10_t20260531.png)


**All phases composite**

![bracket_v16 composite](bracket_v16_composite_t20260531.png)


---


### bracket_v17


**input — panels + fold lines**

![bracket_v17 main](bracket_v17_main_t20260531.png)


**input — yellow/green bump overlay**

![bracket_v17 bump](bracket_v17_bump_t20260531.png)


**input — purple hole overlay**

![bracket_v17 hole](bracket_v17_hole_t20260531.png)


**P1 parse**

![bracket_v17 parse](bracket_v17_parse_t20260531.png)


**P2 topology**

![bracket_v17 topology](bracket_v17_topology_t20260531.png)


**P3 fold**

![bracket_v17 fold](bracket_v17_fold_t20260531.png)


**P4 mesh**

![bracket_v17 mesh_p4](bracket_v17_mesh_p4_t20260531.png)


**P5 stitch**

![bracket_v17 stitch_p5](bracket_v17_stitch_p5_t20260531.png)


**P6 mapper**

![bracket_v17 mapper_p6](bracket_v17_mapper_p6_t20260531.png)


**P7 dihedral**

![bracket_v17 dihedral_p7](bracket_v17_dihedral_p7_t20260531.png)


**P8 fillet**

![bracket_v17 fillet_p8](bracket_v17_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![bracket_v17 mapper_p9](bracket_v17_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![bracket_v17 bump_p10](bracket_v17_bump_p10_t20260531.png)


**All phases composite**

![bracket_v17 composite](bracket_v17_composite_t20260531.png)


---


### bracket_v18


**input — panels + fold lines**

![bracket_v18 main](bracket_v18_main_t20260531.png)


**input — yellow/green bump overlay**

![bracket_v18 bump](bracket_v18_bump_t20260531.png)


**input — purple hole overlay**

![bracket_v18 hole](bracket_v18_hole_t20260531.png)


**P1 parse**

![bracket_v18 parse](bracket_v18_parse_t20260531.png)


**P2 topology**

![bracket_v18 topology](bracket_v18_topology_t20260531.png)


**P3 fold**

![bracket_v18 fold](bracket_v18_fold_t20260531.png)


**P4 mesh**

![bracket_v18 mesh_p4](bracket_v18_mesh_p4_t20260531.png)


**P5 stitch**

![bracket_v18 stitch_p5](bracket_v18_stitch_p5_t20260531.png)


**P6 mapper**

![bracket_v18 mapper_p6](bracket_v18_mapper_p6_t20260531.png)


**P7 dihedral**

![bracket_v18 dihedral_p7](bracket_v18_dihedral_p7_t20260531.png)


**P8 fillet**

![bracket_v18 fillet_p8](bracket_v18_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![bracket_v18 mapper_p9](bracket_v18_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![bracket_v18 bump_p10](bracket_v18_bump_p10_t20260531.png)


**All phases composite**

![bracket_v18 composite](bracket_v18_composite_t20260531.png)


---


### bracket_v19


**input — panels + fold lines**

![bracket_v19 main](bracket_v19_main_t20260531.png)


**input — yellow/green bump overlay**

![bracket_v19 bump](bracket_v19_bump_t20260531.png)


**input — purple hole overlay**

![bracket_v19 hole](bracket_v19_hole_t20260531.png)


**P1 parse**

![bracket_v19 parse](bracket_v19_parse_t20260531.png)


**P2 topology**

![bracket_v19 topology](bracket_v19_topology_t20260531.png)


**P3 fold**

![bracket_v19 fold](bracket_v19_fold_t20260531.png)


**P4 mesh**

![bracket_v19 mesh_p4](bracket_v19_mesh_p4_t20260531.png)


**P5 stitch**

![bracket_v19 stitch_p5](bracket_v19_stitch_p5_t20260531.png)


**P6 mapper**

![bracket_v19 mapper_p6](bracket_v19_mapper_p6_t20260531.png)


**P7 dihedral**

![bracket_v19 dihedral_p7](bracket_v19_dihedral_p7_t20260531.png)


**P8 fillet**

![bracket_v19 fillet_p8](bracket_v19_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![bracket_v19 mapper_p9](bracket_v19_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![bracket_v19 bump_p10](bracket_v19_bump_p10_t20260531.png)


**All phases composite**

![bracket_v19 composite](bracket_v19_composite_t20260531.png)


---


### bracket_v20


**input — panels + fold lines**

![bracket_v20 main](bracket_v20_main_t20260531.png)


**input — yellow/green bump overlay**

![bracket_v20 bump](bracket_v20_bump_t20260531.png)


**input — purple hole overlay**

![bracket_v20 hole](bracket_v20_hole_t20260531.png)


**P1 parse**

![bracket_v20 parse](bracket_v20_parse_t20260531.png)


**P2 topology**

![bracket_v20 topology](bracket_v20_topology_t20260531.png)


**P3 fold**

![bracket_v20 fold](bracket_v20_fold_t20260531.png)


**P4 mesh**

![bracket_v20 mesh_p4](bracket_v20_mesh_p4_t20260531.png)


**P5 stitch**

![bracket_v20 stitch_p5](bracket_v20_stitch_p5_t20260531.png)


**P6 mapper**

![bracket_v20 mapper_p6](bracket_v20_mapper_p6_t20260531.png)


**P7 dihedral**

![bracket_v20 dihedral_p7](bracket_v20_dihedral_p7_t20260531.png)


**P8 fillet**

![bracket_v20 fillet_p8](bracket_v20_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![bracket_v20 mapper_p9](bracket_v20_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![bracket_v20 bump_p10](bracket_v20_bump_p10_t20260531.png)


**All phases composite**

![bracket_v20 composite](bracket_v20_composite_t20260531.png)


---


### cascade_5_deep


**input — panels + fold lines**

![cascade_5_deep main](cascade_5_deep_main_t20260531.png)


**input — yellow/green bump overlay**

![cascade_5_deep bump](cascade_5_deep_bump_t20260531.png)


**input — purple hole overlay**

![cascade_5_deep hole](cascade_5_deep_hole_t20260531.png)


**P1 parse**

![cascade_5_deep parse](cascade_5_deep_parse_t20260531.png)


**P2 topology**

![cascade_5_deep topology](cascade_5_deep_topology_t20260531.png)


**P3 fold**

![cascade_5_deep fold](cascade_5_deep_fold_t20260531.png)


**P4 mesh**

![cascade_5_deep mesh_p4](cascade_5_deep_mesh_p4_t20260531.png)


**P5 stitch**

![cascade_5_deep stitch_p5](cascade_5_deep_stitch_p5_t20260531.png)


**P6 mapper**

![cascade_5_deep mapper_p6](cascade_5_deep_mapper_p6_t20260531.png)


**P7 dihedral**

![cascade_5_deep dihedral_p7](cascade_5_deep_dihedral_p7_t20260531.png)


**P8 fillet**

![cascade_5_deep fillet_p8](cascade_5_deep_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![cascade_5_deep mapper_p9](cascade_5_deep_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![cascade_5_deep bump_p10](cascade_5_deep_bump_p10_t20260531.png)


**All phases composite**

![cascade_5_deep composite](cascade_5_deep_composite_t20260531.png)


---


### channel_bracket


**input — panels + fold lines**

![channel_bracket main](channel_bracket_main_t20260531.png)


**input — yellow/green bump overlay**

![channel_bracket bump](channel_bracket_bump_t20260531.png)


**input — purple hole overlay**

![channel_bracket hole](channel_bracket_hole_t20260531.png)


**P1 parse**

![channel_bracket parse](channel_bracket_parse_t20260531.png)


**P2 topology**

![channel_bracket topology](channel_bracket_topology_t20260531.png)


**P3 fold**

![channel_bracket fold](channel_bracket_fold_t20260531.png)


**P4 mesh**

![channel_bracket mesh_p4](channel_bracket_mesh_p4_t20260531.png)


**P5 stitch**

![channel_bracket stitch_p5](channel_bracket_stitch_p5_t20260531.png)


**P6 mapper**

![channel_bracket mapper_p6](channel_bracket_mapper_p6_t20260531.png)


**P7 dihedral**

![channel_bracket dihedral_p7](channel_bracket_dihedral_p7_t20260531.png)


**P8 fillet**

![channel_bracket fillet_p8](channel_bracket_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![channel_bracket mapper_p9](channel_bracket_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![channel_bracket bump_p10](channel_bracket_bump_p10_t20260531.png)


**All phases composite**

![channel_bracket composite](channel_bracket_composite_t20260531.png)


---


### closed_box


**input — panels + fold lines**

![closed_box main](closed_box_main_t20260531.png)


**input — yellow/green bump overlay**

![closed_box bump](closed_box_bump_t20260531.png)


**input — purple hole overlay**

![closed_box hole](closed_box_hole_t20260531.png)


**P1 parse**

![closed_box parse](closed_box_parse_t20260531.png)


**P2 topology**

![closed_box topology](closed_box_topology_t20260531.png)


**P3 fold**

![closed_box fold](closed_box_fold_t20260531.png)


**P4 mesh**

![closed_box mesh_p4](closed_box_mesh_p4_t20260531.png)


**P5 stitch**

![closed_box stitch_p5](closed_box_stitch_p5_t20260531.png)


**P6 mapper**

![closed_box mapper_p6](closed_box_mapper_p6_t20260531.png)


**P7 dihedral**

![closed_box dihedral_p7](closed_box_dihedral_p7_t20260531.png)


**P8 fillet**

![closed_box fillet_p8](closed_box_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![closed_box mapper_p9](closed_box_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![closed_box bump_p10](closed_box_bump_p10_t20260531.png)


**All phases composite**

![closed_box composite](closed_box_composite_t20260531.png)


---


### corner_3panel


**input — panels + fold lines**

![corner_3panel main](corner_3panel_main_t20260531.png)


**input — yellow/green bump overlay**

![corner_3panel bump](corner_3panel_bump_t20260531.png)


**input — purple hole overlay**

![corner_3panel hole](corner_3panel_hole_t20260531.png)


**P1 parse**

![corner_3panel parse](corner_3panel_parse_t20260531.png)


**P2 topology**

![corner_3panel topology](corner_3panel_topology_t20260531.png)


**P3 fold**

![corner_3panel fold](corner_3panel_fold_t20260531.png)


**P4 mesh**

![corner_3panel mesh_p4](corner_3panel_mesh_p4_t20260531.png)


**P5 stitch**

![corner_3panel stitch_p5](corner_3panel_stitch_p5_t20260531.png)


**P6 mapper**

![corner_3panel mapper_p6](corner_3panel_mapper_p6_t20260531.png)


**P7 dihedral**

![corner_3panel dihedral_p7](corner_3panel_dihedral_p7_t20260531.png)


**P8 fillet**

![corner_3panel fillet_p8](corner_3panel_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![corner_3panel mapper_p9](corner_3panel_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![corner_3panel bump_p10](corner_3panel_bump_p10_t20260531.png)


**All phases composite**

![corner_3panel composite](corner_3panel_composite_t20260531.png)


---


### cross


**input — panels + fold lines**

![cross main](cross_main_t20260531.png)


**input — yellow/green bump overlay**

![cross bump](cross_bump_t20260531.png)


**input — purple hole overlay**

![cross hole](cross_hole_t20260531.png)


**P1 parse**

![cross parse](cross_parse_t20260531.png)


**P2 topology**

![cross topology](cross_topology_t20260531.png)


**P3 fold**

![cross fold](cross_fold_t20260531.png)


**P4 mesh**

![cross mesh_p4](cross_mesh_p4_t20260531.png)


**P5 stitch**

![cross stitch_p5](cross_stitch_p5_t20260531.png)


**P6 mapper**

![cross mapper_p6](cross_mapper_p6_t20260531.png)


**P7 dihedral**

![cross dihedral_p7](cross_dihedral_p7_t20260531.png)


**P8 fillet**

![cross fillet_p8](cross_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![cross mapper_p9](cross_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![cross bump_p10](cross_bump_p10_t20260531.png)


**All phases composite**

![cross composite](cross_composite_t20260531.png)


---


### cross_fold_demo


**input — panels + fold lines**

![cross_fold_demo main](cross_fold_demo_main_t20260531.png)


**input — yellow/green bump overlay**

![cross_fold_demo bump](cross_fold_demo_bump_t20260531.png)


**input — purple hole overlay**

![cross_fold_demo hole](cross_fold_demo_hole_t20260531.png)


**P1 parse**

![cross_fold_demo parse](cross_fold_demo_parse_t20260531.png)


**P2 topology**

![cross_fold_demo topology](cross_fold_demo_topology_t20260531.png)


**P3 fold**

![cross_fold_demo fold](cross_fold_demo_fold_t20260531.png)


**P4 mesh**

![cross_fold_demo mesh_p4](cross_fold_demo_mesh_p4_t20260531.png)


**P5 stitch**

![cross_fold_demo stitch_p5](cross_fold_demo_stitch_p5_t20260531.png)


**P6 mapper**

![cross_fold_demo mapper_p6](cross_fold_demo_mapper_p6_t20260531.png)


**P7 dihedral**

![cross_fold_demo dihedral_p7](cross_fold_demo_dihedral_p7_t20260531.png)


**P8 fillet**

![cross_fold_demo fillet_p8](cross_fold_demo_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![cross_fold_demo mapper_p9](cross_fold_demo_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![cross_fold_demo bump_p10](cross_fold_demo_bump_p10_t20260531.png)


**All phases composite**

![cross_fold_demo composite](cross_fold_demo_composite_t20260531.png)


---


### hd_mobis_bracket


**input — panels + fold lines**

![hd_mobis_bracket main](hd_mobis_bracket_main_t20260531.png)


**input — yellow/green bump overlay**

![hd_mobis_bracket bump](hd_mobis_bracket_bump_t20260531.png)


**input — purple hole overlay**

![hd_mobis_bracket hole](hd_mobis_bracket_hole_t20260531.png)


**P1 parse**

![hd_mobis_bracket parse](hd_mobis_bracket_parse_t20260531.png)


**P2 topology**

![hd_mobis_bracket topology](hd_mobis_bracket_topology_t20260531.png)


**P3 fold**

![hd_mobis_bracket fold](hd_mobis_bracket_fold_t20260531.png)


**P4 mesh**

![hd_mobis_bracket mesh_p4](hd_mobis_bracket_mesh_p4_t20260531.png)


**P5 stitch**

![hd_mobis_bracket stitch_p5](hd_mobis_bracket_stitch_p5_t20260531.png)


**P6 mapper**

![hd_mobis_bracket mapper_p6](hd_mobis_bracket_mapper_p6_t20260531.png)


**P7 dihedral**

![hd_mobis_bracket dihedral_p7](hd_mobis_bracket_dihedral_p7_t20260531.png)


**P8 fillet**

![hd_mobis_bracket fillet_p8](hd_mobis_bracket_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![hd_mobis_bracket mapper_p9](hd_mobis_bracket_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![hd_mobis_bracket bump_p10](hd_mobis_bracket_bump_p10_t20260531.png)


---


### l_shape


**input — panels + fold lines**

![l_shape main](l_shape_main_t20260531.png)


**input — yellow/green bump overlay**

![l_shape bump](l_shape_bump_t20260531.png)


**input — purple hole overlay**

![l_shape hole](l_shape_hole_t20260531.png)


**P1 parse**

![l_shape parse](l_shape_parse_t20260531.png)


**P2 topology**

![l_shape topology](l_shape_topology_t20260531.png)


**P3 fold**

![l_shape fold](l_shape_fold_t20260531.png)


**P4 mesh**

![l_shape mesh_p4](l_shape_mesh_p4_t20260531.png)


**P5 stitch**

![l_shape stitch_p5](l_shape_stitch_p5_t20260531.png)


**P6 mapper**

![l_shape mapper_p6](l_shape_mapper_p6_t20260531.png)


**P7 dihedral**

![l_shape dihedral_p7](l_shape_dihedral_p7_t20260531.png)


**P8 fillet**

![l_shape fillet_p8](l_shape_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![l_shape mapper_p9](l_shape_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![l_shape bump_p10](l_shape_bump_p10_t20260531.png)


**All phases composite**

![l_shape composite](l_shape_composite_t20260531.png)


---


### long_thin_panel


**input — panels + fold lines**

![long_thin_panel main](long_thin_panel_main_t20260531.png)


**input — yellow/green bump overlay**

![long_thin_panel bump](long_thin_panel_bump_t20260531.png)


**input — purple hole overlay**

![long_thin_panel hole](long_thin_panel_hole_t20260531.png)


**P1 parse**

![long_thin_panel parse](long_thin_panel_parse_t20260531.png)


**P2 topology**

![long_thin_panel topology](long_thin_panel_topology_t20260531.png)


**P3 fold**

![long_thin_panel fold](long_thin_panel_fold_t20260531.png)


**P4 mesh**

![long_thin_panel mesh_p4](long_thin_panel_mesh_p4_t20260531.png)


**P5 stitch**

![long_thin_panel stitch_p5](long_thin_panel_stitch_p5_t20260531.png)


**P6 mapper**

![long_thin_panel mapper_p6](long_thin_panel_mapper_p6_t20260531.png)


**P7 dihedral**

![long_thin_panel dihedral_p7](long_thin_panel_dihedral_p7_t20260531.png)


**P8 fillet**

![long_thin_panel fillet_p8](long_thin_panel_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![long_thin_panel mapper_p9](long_thin_panel_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![long_thin_panel bump_p10](long_thin_panel_bump_p10_t20260531.png)


**All phases composite**

![long_thin_panel composite](long_thin_panel_composite_t20260531.png)


---


### mismatched_resolution


**input — panels + fold lines**

![mismatched_resolution main](mismatched_resolution_main_t20260531.png)


**input — yellow/green bump overlay**

![mismatched_resolution bump](mismatched_resolution_bump_t20260531.png)


**input — purple hole overlay**

![mismatched_resolution hole](mismatched_resolution_hole_t20260531.png)


**P1 parse**

![mismatched_resolution parse](mismatched_resolution_parse_t20260531.png)


**P2 topology**

![mismatched_resolution topology](mismatched_resolution_topology_t20260531.png)


**P3 fold**

![mismatched_resolution fold](mismatched_resolution_fold_t20260531.png)


**P4 mesh**

![mismatched_resolution mesh_p4](mismatched_resolution_mesh_p4_t20260531.png)


**P5 stitch**

![mismatched_resolution stitch_p5](mismatched_resolution_stitch_p5_t20260531.png)


**P6 mapper**

![mismatched_resolution mapper_p6](mismatched_resolution_mapper_p6_t20260531.png)


**P7 dihedral**

![mismatched_resolution dihedral_p7](mismatched_resolution_dihedral_p7_t20260531.png)


**P8 fillet**

![mismatched_resolution fillet_p8](mismatched_resolution_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![mismatched_resolution mapper_p9](mismatched_resolution_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![mismatched_resolution bump_p10](mismatched_resolution_bump_p10_t20260531.png)


**All phases composite**

![mismatched_resolution composite](mismatched_resolution_composite_t20260531.png)


---


### multi_hole_strip


**input — panels + fold lines**

![multi_hole_strip main](multi_hole_strip_main_t20260531.png)


**input — yellow/green bump overlay**

![multi_hole_strip bump](multi_hole_strip_bump_t20260531.png)


**input — purple hole overlay**

![multi_hole_strip hole](multi_hole_strip_hole_t20260531.png)


**P1 parse**

![multi_hole_strip parse](multi_hole_strip_parse_t20260531.png)


**P2 topology**

![multi_hole_strip topology](multi_hole_strip_topology_t20260531.png)


**P3 fold**

![multi_hole_strip fold](multi_hole_strip_fold_t20260531.png)


**P4 mesh**

![multi_hole_strip mesh_p4](multi_hole_strip_mesh_p4_t20260531.png)


**P5 stitch**

![multi_hole_strip stitch_p5](multi_hole_strip_stitch_p5_t20260531.png)


**P6 mapper**

![multi_hole_strip mapper_p6](multi_hole_strip_mapper_p6_t20260531.png)


**P7 dihedral**

![multi_hole_strip dihedral_p7](multi_hole_strip_dihedral_p7_t20260531.png)


**P8 fillet**

![multi_hole_strip fillet_p8](multi_hole_strip_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![multi_hole_strip mapper_p9](multi_hole_strip_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![multi_hole_strip bump_p10](multi_hole_strip_bump_p10_t20260531.png)


**All phases composite**

![multi_hole_strip composite](multi_hole_strip_composite_t20260531.png)


---


### simple_l_bracket


**input — panels + fold lines**

![simple_l_bracket main](simple_l_bracket_main_t20260531.png)


**input — yellow/green bump overlay**

![simple_l_bracket bump](simple_l_bracket_bump_t20260531.png)


**input — purple hole overlay**

![simple_l_bracket hole](simple_l_bracket_hole_t20260531.png)


**P1 parse**

![simple_l_bracket parse](simple_l_bracket_parse_t20260531.png)


**P2 topology**

![simple_l_bracket topology](simple_l_bracket_topology_t20260531.png)


**P3 fold**

![simple_l_bracket fold](simple_l_bracket_fold_t20260531.png)


**P4 mesh**

![simple_l_bracket mesh_p4](simple_l_bracket_mesh_p4_t20260531.png)


**P5 stitch**

![simple_l_bracket stitch_p5](simple_l_bracket_stitch_p5_t20260531.png)


**P6 mapper**

![simple_l_bracket mapper_p6](simple_l_bracket_mapper_p6_t20260531.png)


**P7 dihedral**

![simple_l_bracket dihedral_p7](simple_l_bracket_dihedral_p7_t20260531.png)


**P8 fillet**

![simple_l_bracket fillet_p8](simple_l_bracket_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![simple_l_bracket mapper_p9](simple_l_bracket_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![simple_l_bracket bump_p10](simple_l_bracket_bump_p10_t20260531.png)


**All phases composite**

![simple_l_bracket composite](simple_l_bracket_composite_t20260531.png)


---


### single_fold


**input — panels + fold lines**

![single_fold main](single_fold_main_t20260531.png)


**input — yellow/green bump overlay**

![single_fold bump](single_fold_bump_t20260531.png)


**input — purple hole overlay**

![single_fold hole](single_fold_hole_t20260531.png)


**P1 parse**

![single_fold parse](single_fold_parse_t20260531.png)


**P2 topology**

![single_fold topology](single_fold_topology_t20260531.png)


**P3 fold**

![single_fold fold](single_fold_fold_t20260531.png)


**P4 mesh**

![single_fold mesh_p4](single_fold_mesh_p4_t20260531.png)


**P5 stitch**

![single_fold stitch_p5](single_fold_stitch_p5_t20260531.png)


**P6 mapper**

![single_fold mapper_p6](single_fold_mapper_p6_t20260531.png)


**P7 dihedral**

![single_fold dihedral_p7](single_fold_dihedral_p7_t20260531.png)


**P8 fillet**

![single_fold fillet_p8](single_fold_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![single_fold mapper_p9](single_fold_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![single_fold bump_p10](single_fold_bump_p10_t20260531.png)


**All phases composite**

![single_fold composite](single_fold_composite_t20260531.png)


---


### staircase_3


**input — panels + fold lines**

![staircase_3 main](staircase_3_main_t20260531.png)


**input — yellow/green bump overlay**

![staircase_3 bump](staircase_3_bump_t20260531.png)


**input — purple hole overlay**

![staircase_3 hole](staircase_3_hole_t20260531.png)


**P1 parse**

![staircase_3 parse](staircase_3_parse_t20260531.png)


**P2 topology**

![staircase_3 topology](staircase_3_topology_t20260531.png)


**P3 fold**

![staircase_3 fold](staircase_3_fold_t20260531.png)


**P4 mesh**

![staircase_3 mesh_p4](staircase_3_mesh_p4_t20260531.png)


**P5 stitch**

![staircase_3 stitch_p5](staircase_3_stitch_p5_t20260531.png)


**P6 mapper**

![staircase_3 mapper_p6](staircase_3_mapper_p6_t20260531.png)


**P7 dihedral**

![staircase_3 dihedral_p7](staircase_3_dihedral_p7_t20260531.png)


**P8 fillet**

![staircase_3 fillet_p8](staircase_3_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![staircase_3 mapper_p9](staircase_3_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![staircase_3 bump_p10](staircase_3_bump_p10_t20260531.png)


**All phases composite**

![staircase_3 composite](staircase_3_composite_t20260531.png)


---


### tab_plate_4


**input — panels + fold lines**

![tab_plate_4 main](tab_plate_4_main_t20260531.png)


**input — yellow/green bump overlay**

![tab_plate_4 bump](tab_plate_4_bump_t20260531.png)


**input — purple hole overlay**

![tab_plate_4 hole](tab_plate_4_hole_t20260531.png)


**P1 parse**

![tab_plate_4 parse](tab_plate_4_parse_t20260531.png)


**P2 topology**

![tab_plate_4 topology](tab_plate_4_topology_t20260531.png)


**P3 fold**

![tab_plate_4 fold](tab_plate_4_fold_t20260531.png)


**P4 mesh**

![tab_plate_4 mesh_p4](tab_plate_4_mesh_p4_t20260531.png)


**P5 stitch**

![tab_plate_4 stitch_p5](tab_plate_4_stitch_p5_t20260531.png)


**P6 mapper**

![tab_plate_4 mapper_p6](tab_plate_4_mapper_p6_t20260531.png)


**P7 dihedral**

![tab_plate_4 dihedral_p7](tab_plate_4_dihedral_p7_t20260531.png)


**P8 fillet**

![tab_plate_4 fillet_p8](tab_plate_4_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![tab_plate_4 mapper_p9](tab_plate_4_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![tab_plate_4 bump_p10](tab_plate_4_bump_p10_t20260531.png)


---


### tiny_panel


**input — panels + fold lines**

![tiny_panel main](tiny_panel_main_t20260531.png)


**input — yellow/green bump overlay**

![tiny_panel bump](tiny_panel_bump_t20260531.png)


**input — purple hole overlay**

![tiny_panel hole](tiny_panel_hole_t20260531.png)


**P1 parse**

![tiny_panel parse](tiny_panel_parse_t20260531.png)


**P2 topology**

![tiny_panel topology](tiny_panel_topology_t20260531.png)


**P3 fold**

![tiny_panel fold](tiny_panel_fold_t20260531.png)


**P4 mesh**

![tiny_panel mesh_p4](tiny_panel_mesh_p4_t20260531.png)


**P5 stitch**

![tiny_panel stitch_p5](tiny_panel_stitch_p5_t20260531.png)


**P6 mapper**

![tiny_panel mapper_p6](tiny_panel_mapper_p6_t20260531.png)


**P7 dihedral**

![tiny_panel dihedral_p7](tiny_panel_dihedral_p7_t20260531.png)


**P8 fillet**

![tiny_panel fillet_p8](tiny_panel_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![tiny_panel mapper_p9](tiny_panel_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![tiny_panel bump_p10](tiny_panel_bump_p10_t20260531.png)


**All phases composite**

![tiny_panel composite](tiny_panel_composite_t20260531.png)


---


### u_bracket


**input — panels + fold lines**

![u_bracket main](u_bracket_main_t20260531.png)


**input — yellow/green bump overlay**

![u_bracket bump](u_bracket_bump_t20260531.png)


**input — purple hole overlay**

![u_bracket hole](u_bracket_hole_t20260531.png)


**P1 parse**

![u_bracket parse](u_bracket_parse_t20260531.png)


**P2 topology**

![u_bracket topology](u_bracket_topology_t20260531.png)


**P3 fold**

![u_bracket fold](u_bracket_fold_t20260531.png)


**P4 mesh**

![u_bracket mesh_p4](u_bracket_mesh_p4_t20260531.png)


**P5 stitch**

![u_bracket stitch_p5](u_bracket_stitch_p5_t20260531.png)


**P6 mapper**

![u_bracket mapper_p6](u_bracket_mapper_p6_t20260531.png)


**P7 dihedral**

![u_bracket dihedral_p7](u_bracket_dihedral_p7_t20260531.png)


**P8 fillet**

![u_bracket fillet_p8](u_bracket_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![u_bracket mapper_p9](u_bracket_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![u_bracket bump_p10](u_bracket_bump_p10_t20260531.png)


---


### u_shape


**input — panels + fold lines**

![u_shape main](u_shape_main_t20260531.png)


**input — yellow/green bump overlay**

![u_shape bump](u_shape_bump_t20260531.png)


**input — purple hole overlay**

![u_shape hole](u_shape_hole_t20260531.png)


**P1 parse**

![u_shape parse](u_shape_parse_t20260531.png)


**P2 topology**

![u_shape topology](u_shape_topology_t20260531.png)


**P3 fold**

![u_shape fold](u_shape_fold_t20260531.png)


**P4 mesh**

![u_shape mesh_p4](u_shape_mesh_p4_t20260531.png)


**P5 stitch**

![u_shape stitch_p5](u_shape_stitch_p5_t20260531.png)


**P6 mapper**

![u_shape mapper_p6](u_shape_mapper_p6_t20260531.png)


**P7 dihedral**

![u_shape dihedral_p7](u_shape_dihedral_p7_t20260531.png)


**P8 fillet**

![u_shape fillet_p8](u_shape_fillet_p8_t20260531.png)


**P9 mapper (propagated)**

![u_shape mapper_p9](u_shape_mapper_p9_t20260531.png)


**P10 bump+cut+snap**

![u_shape bump_p10](u_shape_bump_p10_t20260531.png)


**All phases composite**

![u_shape composite](u_shape_composite_t20260531.png)


---


### zigzag_4


**input — panels + fold lines**

![zigzag_4 main](zigzag_4_main_t20260531.png)


**input — yellow/green bump overlay**

![zigzag_4 bump](zigzag_4_bump_t20260531.png)


**input — purple hole overlay**

![zigzag_4 hole](zigzag_4_hole_t20260531.png)


---


### zigzag_6


**input — panels + fold lines**

![zigzag_6 main](zigzag_6_main_t20260531.png)


**input — yellow/green bump overlay**

![zigzag_6 bump](zigzag_6_bump_t20260531.png)


**input — purple hole overlay**

![zigzag_6 hole](zigzag_6_hole_t20260531.png)


---
