# Output Port — Origami_Gen v2.0 Pipeline Gallery

Per-phase per-case pipeline pictures from Origami_Gen v2.0
verification runs at the **finest** corpus setting:
`mesh_resolution = 1.0 px/cell` with `RENDER_SCALE = 2`
(Fix 1 + Fix 3 active). All 16 cases pass every §3 hard gate
(10/10) — see `Origami_Gen_p6_mapper_verification/SUMMARY.md`.

Source repo: https://github.com/voltwin-dev/Origami_Gen

![headline gate matrix](Origami_Gen_p6_mapper_verification/headline.png)

## Pipeline phases

| Phase | Module | Input → Output |
|---|---|---|
| **P1 Parse** | `parser/` | PNGs → `ParseResult` (panels + folds + masks) |
| **P2 Topology** | `topology/` | `ParseResult` → `FoldTree` + 2D junctions |
| **P3 Fold** | `folder/` | `FoldTree` → `FoldResult` (integer SO(3) poses) |
| **P4 Mesh** | `mesher/` | + `FoldResult` → `MeshResult` (anchor-aware grid) |
| **P5 Stitch** | `stitcher/` | `MeshResult` → `StitchResult` (post-stitch baseline) |
| **P6 Mapper** | `mapper/` | + masks → `MapResult` (yellow / green / purple element labels — pure tagging, no mesh mutation) |
| **P7 Bump+Cut** | `bumper/` | + `MapResult` → `BumpResult` |
| P8 Export | `export/` | files (no picture) |

## Per-phase performance (16-case corpus, this run)

`mesh_resolution = 1.0` + `RENDER_SCALE = 2` →
**950 288 quads / 957 496 verts corpus-wide**.

| Phase | Aggregate (ms) | Aggregate (s) |
|---|---:|---:|
| P1 Parse | 535 | 0.5 |
| P2 Topology | 1 | 0.0 |
| P3 Fold | 14 | 0.0 |
| P4 Mesh | 2 654 | 2.7 |
| **P5 Stitch** | **46 357** | **46.4** |
| P6 Mapper | 311 | 0.3 |
| **P7 Bump + Cut** | **63 085** | **63.1** |
| **Total (P1..P7)** | **112 958** | **113.0** |
| Avg peak RSS | — | **153 MB / case** |

Per-quad rate: **0.119 ms/quad** — near-linear across 950 k quads
thanks to scipy.sparse.csgraph + vectorized numpy in P5 / P7.

Per-case breakdown is in [`perf_res1.md`](perf_res1.md).

### Per-case totals (this run)

| Case | quads | total (ms) | total (s) | peak RSS (MB) |
|---|---:|---:|---:|---:|
| tiny_panel | 17 984 | 1 779 | 1.8 | 145 |
| zigzag_6 | 31 104 | 3 498 | 3.5 | 141 |
| cascade_5_deep | 32 000 | 3 757 | 3.8 | 140 |
| zigzag_4 | 40 000 | 5 049 | 5.0 | 141 |
| staircase_3 | 43 200 | 5 071 | 5.1 | 145 |
| cross_fold_demo | 58 800 | 6 393 | 6.4 | 138 |
| long_thin_panel | 60 800 | 6 405 | 6.4 | 144 |
| multi_hole_strip | 58 800 | 6 575 | 6.6 | 145 |
| single_fold | 61 440 | 6 569 | 6.6 | 145 |
| closed_box | 60 000 | 7 049 | 7.0 | 137 |
| mismatched_resolution | 65 920 | 7 537 | 7.5 | 145 |
| corner_3panel | 58 800 | 8 261 | 8.3 | 137 |
| cross | 72 000 | 10 308 | 10.3 | 142 |
| box_unfolding | 72 000 | 10 469 | 10.5 | 142 |
| l_shape | 97 920 | 10 690 | 10.7 | 152 |
| u_shape | 119 520 | 13 549 | 13.5 | 159 |

(Hardware: `SML_env` CPU only — see `Origami_Gen.git` README for
the optimization story; GPU intentionally not used at this graph
scale.)

## Per-phase mosaics (all cases on one figure)

### P1 — Parse
![P1_parse](Origami_Gen_p6_mapper_verification/phases/P1_parse.png)

### P2 — Topology
![P2_topology](Origami_Gen_p6_mapper_verification/phases/P2_topology.png)

### P3 — Fold
![P3_fold](Origami_Gen_p6_mapper_verification/phases/P3_fold.png)

### P4 — Mesh
![P4_mesh](Origami_Gen_p6_mapper_verification/phases/P4_mesh.png)

### P5 — Stitch
![P5_stitch](Origami_Gen_p6_mapper_verification/phases/P5_stitch.png)

### P6 — Mapper
![P6_mapper](Origami_Gen_p6_mapper_verification/phases/P6_mapper.png)

### P7 — Bump + Cut
![P7_bump_cut](Origami_Gen_p6_mapper_verification/phases/P7_bump_cut.png)

## Per-case pipeline pictures

For each case: the **input PNG bundle** (`_main`, `_bump`, `_hole`)
followed by every phase picture (P1 → P2 → P3 → P4 → P5 → P6 → P7).
P6 colors: gold = yellow-mask quads, green = green-mask quads,
purple = purple-mask (hole) quads, grey = unmapped.

### box_unfolding

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/box_unfolding/box_unfolding_main.png) | ![](Origami_Gen_p6_mapper_verification/box_unfolding/box_unfolding_bump.png) | ![](Origami_Gen_p6_mapper_verification/box_unfolding/box_unfolding_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut |
|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/box_unfolding/parse.png) | ![](Origami_Gen_p6_mapper_verification/box_unfolding/topology.png) | ![](Origami_Gen_p6_mapper_verification/box_unfolding/fold.png) | ![](Origami_Gen_p6_mapper_verification/box_unfolding/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/box_unfolding/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/box_unfolding/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/box_unfolding/bump_p7.png) |

### cascade_5_deep

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/cascade_5_deep/cascade_5_deep_main.png) | ![](Origami_Gen_p6_mapper_verification/cascade_5_deep/cascade_5_deep_bump.png) | ![](Origami_Gen_p6_mapper_verification/cascade_5_deep/cascade_5_deep_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut |
|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/cascade_5_deep/parse.png) | ![](Origami_Gen_p6_mapper_verification/cascade_5_deep/topology.png) | ![](Origami_Gen_p6_mapper_verification/cascade_5_deep/fold.png) | ![](Origami_Gen_p6_mapper_verification/cascade_5_deep/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/cascade_5_deep/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/cascade_5_deep/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/cascade_5_deep/bump_p7.png) |

### closed_box

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/closed_box/closed_box_main.png) | ![](Origami_Gen_p6_mapper_verification/closed_box/closed_box_bump.png) | ![](Origami_Gen_p6_mapper_verification/closed_box/closed_box_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut |
|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/closed_box/parse.png) | ![](Origami_Gen_p6_mapper_verification/closed_box/topology.png) | ![](Origami_Gen_p6_mapper_verification/closed_box/fold.png) | ![](Origami_Gen_p6_mapper_verification/closed_box/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/closed_box/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/closed_box/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/closed_box/bump_p7.png) |

### corner_3panel

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/corner_3panel/corner_3panel_main.png) | ![](Origami_Gen_p6_mapper_verification/corner_3panel/corner_3panel_bump.png) | ![](Origami_Gen_p6_mapper_verification/corner_3panel/corner_3panel_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut |
|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/corner_3panel/parse.png) | ![](Origami_Gen_p6_mapper_verification/corner_3panel/topology.png) | ![](Origami_Gen_p6_mapper_verification/corner_3panel/fold.png) | ![](Origami_Gen_p6_mapper_verification/corner_3panel/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/corner_3panel/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/corner_3panel/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/corner_3panel/bump_p7.png) |

### cross

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/cross/cross_main.png) | ![](Origami_Gen_p6_mapper_verification/cross/cross_bump.png) | ![](Origami_Gen_p6_mapper_verification/cross/cross_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut |
|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/cross/parse.png) | ![](Origami_Gen_p6_mapper_verification/cross/topology.png) | ![](Origami_Gen_p6_mapper_verification/cross/fold.png) | ![](Origami_Gen_p6_mapper_verification/cross/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/cross/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/cross/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/cross/bump_p7.png) |

### cross_fold_demo

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/cross_fold_demo/cross_fold_demo_main.png) | ![](Origami_Gen_p6_mapper_verification/cross_fold_demo/cross_fold_demo_bump.png) | ![](Origami_Gen_p6_mapper_verification/cross_fold_demo/cross_fold_demo_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut |
|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/cross_fold_demo/parse.png) | ![](Origami_Gen_p6_mapper_verification/cross_fold_demo/topology.png) | ![](Origami_Gen_p6_mapper_verification/cross_fold_demo/fold.png) | ![](Origami_Gen_p6_mapper_verification/cross_fold_demo/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/cross_fold_demo/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/cross_fold_demo/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/cross_fold_demo/bump_p7.png) |

### l_shape

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/l_shape/l_shape_main.png) | ![](Origami_Gen_p6_mapper_verification/l_shape/l_shape_bump.png) | ![](Origami_Gen_p6_mapper_verification/l_shape/l_shape_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut |
|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/l_shape/parse.png) | ![](Origami_Gen_p6_mapper_verification/l_shape/topology.png) | ![](Origami_Gen_p6_mapper_verification/l_shape/fold.png) | ![](Origami_Gen_p6_mapper_verification/l_shape/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/l_shape/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/l_shape/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/l_shape/bump_p7.png) |

### long_thin_panel

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/long_thin_panel/long_thin_panel_main.png) | ![](Origami_Gen_p6_mapper_verification/long_thin_panel/long_thin_panel_bump.png) | ![](Origami_Gen_p6_mapper_verification/long_thin_panel/long_thin_panel_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut |
|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/long_thin_panel/parse.png) | ![](Origami_Gen_p6_mapper_verification/long_thin_panel/topology.png) | ![](Origami_Gen_p6_mapper_verification/long_thin_panel/fold.png) | ![](Origami_Gen_p6_mapper_verification/long_thin_panel/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/long_thin_panel/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/long_thin_panel/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/long_thin_panel/bump_p7.png) |

### mismatched_resolution

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/mismatched_resolution/mismatched_resolution_main.png) | ![](Origami_Gen_p6_mapper_verification/mismatched_resolution/mismatched_resolution_bump.png) | ![](Origami_Gen_p6_mapper_verification/mismatched_resolution/mismatched_resolution_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut |
|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/mismatched_resolution/parse.png) | ![](Origami_Gen_p6_mapper_verification/mismatched_resolution/topology.png) | ![](Origami_Gen_p6_mapper_verification/mismatched_resolution/fold.png) | ![](Origami_Gen_p6_mapper_verification/mismatched_resolution/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/mismatched_resolution/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/mismatched_resolution/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/mismatched_resolution/bump_p7.png) |

### multi_hole_strip

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/multi_hole_strip/multi_hole_strip_main.png) | ![](Origami_Gen_p6_mapper_verification/multi_hole_strip/multi_hole_strip_bump.png) | ![](Origami_Gen_p6_mapper_verification/multi_hole_strip/multi_hole_strip_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut |
|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/multi_hole_strip/parse.png) | ![](Origami_Gen_p6_mapper_verification/multi_hole_strip/topology.png) | ![](Origami_Gen_p6_mapper_verification/multi_hole_strip/fold.png) | ![](Origami_Gen_p6_mapper_verification/multi_hole_strip/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/multi_hole_strip/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/multi_hole_strip/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/multi_hole_strip/bump_p7.png) |

### single_fold

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/single_fold/single_fold_main.png) | ![](Origami_Gen_p6_mapper_verification/single_fold/single_fold_bump.png) | ![](Origami_Gen_p6_mapper_verification/single_fold/single_fold_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut |
|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/single_fold/parse.png) | ![](Origami_Gen_p6_mapper_verification/single_fold/topology.png) | ![](Origami_Gen_p6_mapper_verification/single_fold/fold.png) | ![](Origami_Gen_p6_mapper_verification/single_fold/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/single_fold/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/single_fold/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/single_fold/bump_p7.png) |

### staircase_3

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/staircase_3/staircase_3_main.png) | ![](Origami_Gen_p6_mapper_verification/staircase_3/staircase_3_bump.png) | ![](Origami_Gen_p6_mapper_verification/staircase_3/staircase_3_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut |
|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/staircase_3/parse.png) | ![](Origami_Gen_p6_mapper_verification/staircase_3/topology.png) | ![](Origami_Gen_p6_mapper_verification/staircase_3/fold.png) | ![](Origami_Gen_p6_mapper_verification/staircase_3/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/staircase_3/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/staircase_3/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/staircase_3/bump_p7.png) |

### tiny_panel

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/tiny_panel/tiny_panel_main.png) | ![](Origami_Gen_p6_mapper_verification/tiny_panel/tiny_panel_bump.png) | ![](Origami_Gen_p6_mapper_verification/tiny_panel/tiny_panel_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut |
|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/tiny_panel/parse.png) | ![](Origami_Gen_p6_mapper_verification/tiny_panel/topology.png) | ![](Origami_Gen_p6_mapper_verification/tiny_panel/fold.png) | ![](Origami_Gen_p6_mapper_verification/tiny_panel/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/tiny_panel/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/tiny_panel/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/tiny_panel/bump_p7.png) |

### u_shape

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/u_shape/u_shape_main.png) | ![](Origami_Gen_p6_mapper_verification/u_shape/u_shape_bump.png) | ![](Origami_Gen_p6_mapper_verification/u_shape/u_shape_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut |
|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/u_shape/parse.png) | ![](Origami_Gen_p6_mapper_verification/u_shape/topology.png) | ![](Origami_Gen_p6_mapper_verification/u_shape/fold.png) | ![](Origami_Gen_p6_mapper_verification/u_shape/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/u_shape/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/u_shape/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/u_shape/bump_p7.png) |

### zigzag_4

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/zigzag_4/zigzag_4_main.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_4/zigzag_4_bump.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_4/zigzag_4_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut |
|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/zigzag_4/parse.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_4/topology.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_4/fold.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_4/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_4/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_4/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_4/bump_p7.png) |

### zigzag_6

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/zigzag_6/zigzag_6_main.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_6/zigzag_6_bump.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_6/zigzag_6_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut |
|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/zigzag_6/parse.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_6/topology.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_6/fold.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_6/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_6/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_6/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_6/bump_p7.png) |
