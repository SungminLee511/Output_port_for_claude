# Output Port — Origami_Gen v2.0 Pipeline Gallery

Per-phase per-case pipeline pictures from Origami_Gen v2.0
verification runs. 16 cases, all 10/10 §3 gates passing.

Source repo: https://github.com/voltwin-dev/Origami_Gen

![headline gate matrix](Origami_Gen_no_heightmap_verification/headline.png)

## Pipeline phases

| Phase | Module | Input → Output |
|---|---|---|
| **P1 Parse** | `parser/` | PNGs → `ParseResult` (panels + folds + masks) |
| **P2 Topology** | `topology/` | `ParseResult` → `FoldTree` + 2D junctions |
| **P3 Fold** | `folder/` | `FoldTree` → `FoldResult` (integer SO(3) poses) |
| **P4 Mesh** | `mesher/` | + `FoldResult` → `MeshResult` (anchor-aware grid) |
| **P5 Stitch** | `stitcher/` | `MeshResult` → `StitchResult` (post-stitch baseline) |
| P6 Heightmap | `heightmap/` | (skipped in this run) |
| **P7 Bump+Cut** | `bumper/` | + masks → `BumpResult` |
| P8 Export | `export/` | files (no picture) |

## Per-phase mosaics (all cases on one figure)

### P1 — Parse
![P1_parse](Origami_Gen_no_heightmap_verification/phases/P1_parse.png)

### P2 — Topology
![P2_topology](Origami_Gen_no_heightmap_verification/phases/P2_topology.png)

### P3 — Fold
![P3_fold](Origami_Gen_no_heightmap_verification/phases/P3_fold.png)

### P4 — Mesh
![P4_mesh](Origami_Gen_no_heightmap_verification/phases/P4_mesh.png)

### P5 — Stitch
![P5_stitch](Origami_Gen_no_heightmap_verification/phases/P5_stitch.png)

### P7 — Bump + Cut
![P7_bump_cut](Origami_Gen_no_heightmap_verification/phases/P7_bump_cut.png)

## Per-case pipeline pictures

For each case: the **input PNG bundle** (`_main`, `_bump`, `_hole`;
heightmap layer was not used in this run) followed by every phase
picture (P1 → P2 → P3 → P4 → P5 → P7).

### box_unfolding

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_no_heightmap_verification/box_unfolding/box_unfolding_main.png) | ![](Origami_Gen_no_heightmap_verification/box_unfolding/box_unfolding_bump.png) | ![](Origami_Gen_no_heightmap_verification/box_unfolding/box_unfolding_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P7 bump+cut |
|---|---|---|---|---|---|
| ![](Origami_Gen_no_heightmap_verification/box_unfolding/parse.png) | ![](Origami_Gen_no_heightmap_verification/box_unfolding/topology.png) | ![](Origami_Gen_no_heightmap_verification/box_unfolding/fold.png) | ![](Origami_Gen_no_heightmap_verification/box_unfolding/mesh_p4.png) | ![](Origami_Gen_no_heightmap_verification/box_unfolding/stitch_p5.png) | ![](Origami_Gen_no_heightmap_verification/box_unfolding/bump_p7.png) |

### cascade_5_deep

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_no_heightmap_verification/cascade_5_deep/cascade_5_deep_main.png) | ![](Origami_Gen_no_heightmap_verification/cascade_5_deep/cascade_5_deep_bump.png) | ![](Origami_Gen_no_heightmap_verification/cascade_5_deep/cascade_5_deep_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P7 bump+cut |
|---|---|---|---|---|---|
| ![](Origami_Gen_no_heightmap_verification/cascade_5_deep/parse.png) | ![](Origami_Gen_no_heightmap_verification/cascade_5_deep/topology.png) | ![](Origami_Gen_no_heightmap_verification/cascade_5_deep/fold.png) | ![](Origami_Gen_no_heightmap_verification/cascade_5_deep/mesh_p4.png) | ![](Origami_Gen_no_heightmap_verification/cascade_5_deep/stitch_p5.png) | ![](Origami_Gen_no_heightmap_verification/cascade_5_deep/bump_p7.png) |

### closed_box

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_no_heightmap_verification/closed_box/closed_box_main.png) | ![](Origami_Gen_no_heightmap_verification/closed_box/closed_box_bump.png) | ![](Origami_Gen_no_heightmap_verification/closed_box/closed_box_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P7 bump+cut |
|---|---|---|---|---|---|
| ![](Origami_Gen_no_heightmap_verification/closed_box/parse.png) | ![](Origami_Gen_no_heightmap_verification/closed_box/topology.png) | ![](Origami_Gen_no_heightmap_verification/closed_box/fold.png) | ![](Origami_Gen_no_heightmap_verification/closed_box/mesh_p4.png) | ![](Origami_Gen_no_heightmap_verification/closed_box/stitch_p5.png) | ![](Origami_Gen_no_heightmap_verification/closed_box/bump_p7.png) |

### corner_3panel

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_no_heightmap_verification/corner_3panel/corner_3panel_main.png) | ![](Origami_Gen_no_heightmap_verification/corner_3panel/corner_3panel_bump.png) | ![](Origami_Gen_no_heightmap_verification/corner_3panel/corner_3panel_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P7 bump+cut |
|---|---|---|---|---|---|
| ![](Origami_Gen_no_heightmap_verification/corner_3panel/parse.png) | ![](Origami_Gen_no_heightmap_verification/corner_3panel/topology.png) | ![](Origami_Gen_no_heightmap_verification/corner_3panel/fold.png) | ![](Origami_Gen_no_heightmap_verification/corner_3panel/mesh_p4.png) | ![](Origami_Gen_no_heightmap_verification/corner_3panel/stitch_p5.png) | ![](Origami_Gen_no_heightmap_verification/corner_3panel/bump_p7.png) |

### cross

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_no_heightmap_verification/cross/cross_main.png) | ![](Origami_Gen_no_heightmap_verification/cross/cross_bump.png) | ![](Origami_Gen_no_heightmap_verification/cross/cross_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P7 bump+cut |
|---|---|---|---|---|---|
| ![](Origami_Gen_no_heightmap_verification/cross/parse.png) | ![](Origami_Gen_no_heightmap_verification/cross/topology.png) | ![](Origami_Gen_no_heightmap_verification/cross/fold.png) | ![](Origami_Gen_no_heightmap_verification/cross/mesh_p4.png) | ![](Origami_Gen_no_heightmap_verification/cross/stitch_p5.png) | ![](Origami_Gen_no_heightmap_verification/cross/bump_p7.png) |

### cross_fold_demo

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_no_heightmap_verification/cross_fold_demo/cross_fold_demo_main.png) | ![](Origami_Gen_no_heightmap_verification/cross_fold_demo/cross_fold_demo_bump.png) | ![](Origami_Gen_no_heightmap_verification/cross_fold_demo/cross_fold_demo_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P7 bump+cut |
|---|---|---|---|---|---|
| ![](Origami_Gen_no_heightmap_verification/cross_fold_demo/parse.png) | ![](Origami_Gen_no_heightmap_verification/cross_fold_demo/topology.png) | ![](Origami_Gen_no_heightmap_verification/cross_fold_demo/fold.png) | ![](Origami_Gen_no_heightmap_verification/cross_fold_demo/mesh_p4.png) | ![](Origami_Gen_no_heightmap_verification/cross_fold_demo/stitch_p5.png) | ![](Origami_Gen_no_heightmap_verification/cross_fold_demo/bump_p7.png) |

### l_shape

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_no_heightmap_verification/l_shape/l_shape_main.png) | ![](Origami_Gen_no_heightmap_verification/l_shape/l_shape_bump.png) | ![](Origami_Gen_no_heightmap_verification/l_shape/l_shape_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P7 bump+cut |
|---|---|---|---|---|---|
| ![](Origami_Gen_no_heightmap_verification/l_shape/parse.png) | ![](Origami_Gen_no_heightmap_verification/l_shape/topology.png) | ![](Origami_Gen_no_heightmap_verification/l_shape/fold.png) | ![](Origami_Gen_no_heightmap_verification/l_shape/mesh_p4.png) | ![](Origami_Gen_no_heightmap_verification/l_shape/stitch_p5.png) | ![](Origami_Gen_no_heightmap_verification/l_shape/bump_p7.png) |

### long_thin_panel

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_no_heightmap_verification/long_thin_panel/long_thin_panel_main.png) | ![](Origami_Gen_no_heightmap_verification/long_thin_panel/long_thin_panel_bump.png) | ![](Origami_Gen_no_heightmap_verification/long_thin_panel/long_thin_panel_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P7 bump+cut |
|---|---|---|---|---|---|
| ![](Origami_Gen_no_heightmap_verification/long_thin_panel/parse.png) | ![](Origami_Gen_no_heightmap_verification/long_thin_panel/topology.png) | ![](Origami_Gen_no_heightmap_verification/long_thin_panel/fold.png) | ![](Origami_Gen_no_heightmap_verification/long_thin_panel/mesh_p4.png) | ![](Origami_Gen_no_heightmap_verification/long_thin_panel/stitch_p5.png) | ![](Origami_Gen_no_heightmap_verification/long_thin_panel/bump_p7.png) |

### mismatched_resolution

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_no_heightmap_verification/mismatched_resolution/mismatched_resolution_main.png) | ![](Origami_Gen_no_heightmap_verification/mismatched_resolution/mismatched_resolution_bump.png) | ![](Origami_Gen_no_heightmap_verification/mismatched_resolution/mismatched_resolution_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P7 bump+cut |
|---|---|---|---|---|---|
| ![](Origami_Gen_no_heightmap_verification/mismatched_resolution/parse.png) | ![](Origami_Gen_no_heightmap_verification/mismatched_resolution/topology.png) | ![](Origami_Gen_no_heightmap_verification/mismatched_resolution/fold.png) | ![](Origami_Gen_no_heightmap_verification/mismatched_resolution/mesh_p4.png) | ![](Origami_Gen_no_heightmap_verification/mismatched_resolution/stitch_p5.png) | ![](Origami_Gen_no_heightmap_verification/mismatched_resolution/bump_p7.png) |

### multi_hole_strip

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_no_heightmap_verification/multi_hole_strip/multi_hole_strip_main.png) | ![](Origami_Gen_no_heightmap_verification/multi_hole_strip/multi_hole_strip_bump.png) | ![](Origami_Gen_no_heightmap_verification/multi_hole_strip/multi_hole_strip_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P7 bump+cut |
|---|---|---|---|---|---|
| ![](Origami_Gen_no_heightmap_verification/multi_hole_strip/parse.png) | ![](Origami_Gen_no_heightmap_verification/multi_hole_strip/topology.png) | ![](Origami_Gen_no_heightmap_verification/multi_hole_strip/fold.png) | ![](Origami_Gen_no_heightmap_verification/multi_hole_strip/mesh_p4.png) | ![](Origami_Gen_no_heightmap_verification/multi_hole_strip/stitch_p5.png) | ![](Origami_Gen_no_heightmap_verification/multi_hole_strip/bump_p7.png) |

### single_fold

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_no_heightmap_verification/single_fold/single_fold_main.png) | ![](Origami_Gen_no_heightmap_verification/single_fold/single_fold_bump.png) | ![](Origami_Gen_no_heightmap_verification/single_fold/single_fold_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P7 bump+cut |
|---|---|---|---|---|---|
| ![](Origami_Gen_no_heightmap_verification/single_fold/parse.png) | ![](Origami_Gen_no_heightmap_verification/single_fold/topology.png) | ![](Origami_Gen_no_heightmap_verification/single_fold/fold.png) | ![](Origami_Gen_no_heightmap_verification/single_fold/mesh_p4.png) | ![](Origami_Gen_no_heightmap_verification/single_fold/stitch_p5.png) | ![](Origami_Gen_no_heightmap_verification/single_fold/bump_p7.png) |

### staircase_3

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_no_heightmap_verification/staircase_3/staircase_3_main.png) | ![](Origami_Gen_no_heightmap_verification/staircase_3/staircase_3_bump.png) | ![](Origami_Gen_no_heightmap_verification/staircase_3/staircase_3_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P7 bump+cut |
|---|---|---|---|---|---|
| ![](Origami_Gen_no_heightmap_verification/staircase_3/parse.png) | ![](Origami_Gen_no_heightmap_verification/staircase_3/topology.png) | ![](Origami_Gen_no_heightmap_verification/staircase_3/fold.png) | ![](Origami_Gen_no_heightmap_verification/staircase_3/mesh_p4.png) | ![](Origami_Gen_no_heightmap_verification/staircase_3/stitch_p5.png) | ![](Origami_Gen_no_heightmap_verification/staircase_3/bump_p7.png) |

### tiny_panel

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_no_heightmap_verification/tiny_panel/tiny_panel_main.png) | ![](Origami_Gen_no_heightmap_verification/tiny_panel/tiny_panel_bump.png) | ![](Origami_Gen_no_heightmap_verification/tiny_panel/tiny_panel_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P7 bump+cut |
|---|---|---|---|---|---|
| ![](Origami_Gen_no_heightmap_verification/tiny_panel/parse.png) | ![](Origami_Gen_no_heightmap_verification/tiny_panel/topology.png) | ![](Origami_Gen_no_heightmap_verification/tiny_panel/fold.png) | ![](Origami_Gen_no_heightmap_verification/tiny_panel/mesh_p4.png) | ![](Origami_Gen_no_heightmap_verification/tiny_panel/stitch_p5.png) | ![](Origami_Gen_no_heightmap_verification/tiny_panel/bump_p7.png) |

### u_shape

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_no_heightmap_verification/u_shape/u_shape_main.png) | ![](Origami_Gen_no_heightmap_verification/u_shape/u_shape_bump.png) | ![](Origami_Gen_no_heightmap_verification/u_shape/u_shape_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P7 bump+cut |
|---|---|---|---|---|---|
| ![](Origami_Gen_no_heightmap_verification/u_shape/parse.png) | ![](Origami_Gen_no_heightmap_verification/u_shape/topology.png) | ![](Origami_Gen_no_heightmap_verification/u_shape/fold.png) | ![](Origami_Gen_no_heightmap_verification/u_shape/mesh_p4.png) | ![](Origami_Gen_no_heightmap_verification/u_shape/stitch_p5.png) | ![](Origami_Gen_no_heightmap_verification/u_shape/bump_p7.png) |

### zigzag_4

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_no_heightmap_verification/zigzag_4/zigzag_4_main.png) | ![](Origami_Gen_no_heightmap_verification/zigzag_4/zigzag_4_bump.png) | ![](Origami_Gen_no_heightmap_verification/zigzag_4/zigzag_4_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P7 bump+cut |
|---|---|---|---|---|---|
| ![](Origami_Gen_no_heightmap_verification/zigzag_4/parse.png) | ![](Origami_Gen_no_heightmap_verification/zigzag_4/topology.png) | ![](Origami_Gen_no_heightmap_verification/zigzag_4/fold.png) | ![](Origami_Gen_no_heightmap_verification/zigzag_4/mesh_p4.png) | ![](Origami_Gen_no_heightmap_verification/zigzag_4/stitch_p5.png) | ![](Origami_Gen_no_heightmap_verification/zigzag_4/bump_p7.png) |

### zigzag_6

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_no_heightmap_verification/zigzag_6/zigzag_6_main.png) | ![](Origami_Gen_no_heightmap_verification/zigzag_6/zigzag_6_bump.png) | ![](Origami_Gen_no_heightmap_verification/zigzag_6/zigzag_6_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P7 bump+cut |
|---|---|---|---|---|---|
| ![](Origami_Gen_no_heightmap_verification/zigzag_6/parse.png) | ![](Origami_Gen_no_heightmap_verification/zigzag_6/topology.png) | ![](Origami_Gen_no_heightmap_verification/zigzag_6/fold.png) | ![](Origami_Gen_no_heightmap_verification/zigzag_6/mesh_p4.png) | ![](Origami_Gen_no_heightmap_verification/zigzag_6/stitch_p5.png) | ![](Origami_Gen_no_heightmap_verification/zigzag_6/bump_p7.png) |

## Other Origami_Gen verification folders

- `Origami_Gen_dihedral_90/` — dihedral-angle verification renders
  (every fold ≡ 90°) per case.
- `Origami_Gen_P7_6_compare/` — P7.6 quad-split fallback comparison
  (default vs. stress).
- `Origami_Gen_no_heightmap_verification/SUMMARY.md` — per-case gate counts + composite storyboards.

## Legacy MOBIS_GEN inverse-pipeline folders

Phase-1..5 inverse-design output from prior MOBIS_GEN work, kept
for reference only:

- `step1_visualize/` — H5 mesh renders (40 files).
- `step2_mainplanes/` — region-growing plane segmentation.
- `step3_classify_blobs/` — main / flat-bump / bend-bump classify.
- `step4_blob_graph/` — blob-topology graph.
- `step5_collapse_smalls/` — small-region collapse.
