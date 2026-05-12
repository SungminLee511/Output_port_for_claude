# Output Port — Origami_Gen v2.0 Pipeline Gallery

Per-phase per-case pipeline pictures from Origami_Gen v2.0 at the
finest corpus setting: `mesh_resolution = 1.0 px/cell` with
`RENDER_SCALE = 2` (Fix 1 + Fix 3 active). All 16 cases pass
every §3 hard gate (10/10).

Source repo: https://github.com/voltwin-dev/Origami_Gen

![headline gate matrix](Origami_Gen_p6_mapper_verification/headline.png)

## Pipeline phases (8 phases visualized; P9 export emits files only)

| Phase | Module | Input → Output |
|---|---|---|
| **P1 Parse** | `parser/` | PNGs → `ParseResult` (panels + folds + masks) |
| **P2 Topology** | `topology/` | `ParseResult` → `FoldTree` + 2D junctions |
| **P3 Fold** | `folder/` | `FoldTree` → `FoldResult` (integer SO(3) poses) |
| **P4 Mesh** | `mesher/` | + `FoldResult` → `MeshResult` (anchor-aware grid) |
| **P5 Stitch** | `stitcher/` | `MeshResult` → `StitchResult` (post-stitch baseline) |
| **P6 Mapper** | `mapper/` | + masks → `MapResult` (yellow / green / purple element labels — pure tagging, no mesh mutation) |
| **P7 Bump+Cut** | `bumper/` | + `MapResult` → `BumpResult` |
| **P8 Dihedral** | `dihedral/` | `BumpResult` → `DihedralResult` (~90 deg edges in red, neighbouring-face shell up to 2 BFS layers in orange, corner vertices (≥3 90 deg edges meet) in red dots with blue corner-face shell up to 2 BFS layers — pure analysis, no mesh mutation) |
| P9 Export | `export/` | files (no picture) |

P8 was promoted from the old standalone `scripts/dihedral_90.py`
into a real typed phase; the original P8 Export has moved to P9.

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

### P8 — Dihedral
![P8_dihedral](Origami_Gen_p6_mapper_verification/phases/P8_dihedral.png)

## Per-case pipeline pictures

For each case: the **input PNG bundle** (`_main`, `_bump`, `_hole`)
followed by every phase picture (P1 → P2 → P3 → P4 → P5 → P6 → P7 → P8).
P6 colors: gold = yellow-mask quads, green = green-mask quads,
purple = purple-mask (hole) quads, grey = unmapped. P8: red lines
= mesh edges with dihedral angle ∈ [85, 95] deg (the fold seams,
post bump+cut); orange palette (L0/L1/L2) = faces within 2 BFS
layers of any 90 deg edge; red dots = corner verts where ≥ 3
90 deg edges converge; blue palette (L0/L1/L2) = faces within 2
BFS layers of any corner vert; grey = faces outside both shells.
Title carries `edges`, `corners`, and the per-layer face counts.

### box_unfolding

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/box_unfolding/box_unfolding_main.png) | ![](Origami_Gen_p6_mapper_verification/box_unfolding/box_unfolding_bump.png) | ![](Origami_Gen_p6_mapper_verification/box_unfolding/box_unfolding_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut | P8 dihedral |
|---|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/box_unfolding/parse.png) | ![](Origami_Gen_p6_mapper_verification/box_unfolding/topology.png) | ![](Origami_Gen_p6_mapper_verification/box_unfolding/fold.png) | ![](Origami_Gen_p6_mapper_verification/box_unfolding/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/box_unfolding/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/box_unfolding/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/box_unfolding/bump_p7.png) | ![](Origami_Gen_p6_mapper_verification/box_unfolding/dihedral_p8.png) |

### cascade_5_deep

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/cascade_5_deep/cascade_5_deep_main.png) | ![](Origami_Gen_p6_mapper_verification/cascade_5_deep/cascade_5_deep_bump.png) | ![](Origami_Gen_p6_mapper_verification/cascade_5_deep/cascade_5_deep_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut | P8 dihedral |
|---|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/cascade_5_deep/parse.png) | ![](Origami_Gen_p6_mapper_verification/cascade_5_deep/topology.png) | ![](Origami_Gen_p6_mapper_verification/cascade_5_deep/fold.png) | ![](Origami_Gen_p6_mapper_verification/cascade_5_deep/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/cascade_5_deep/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/cascade_5_deep/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/cascade_5_deep/bump_p7.png) | ![](Origami_Gen_p6_mapper_verification/cascade_5_deep/dihedral_p8.png) |

### closed_box

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/closed_box/closed_box_main.png) | ![](Origami_Gen_p6_mapper_verification/closed_box/closed_box_bump.png) | ![](Origami_Gen_p6_mapper_verification/closed_box/closed_box_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut | P8 dihedral |
|---|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/closed_box/parse.png) | ![](Origami_Gen_p6_mapper_verification/closed_box/topology.png) | ![](Origami_Gen_p6_mapper_verification/closed_box/fold.png) | ![](Origami_Gen_p6_mapper_verification/closed_box/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/closed_box/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/closed_box/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/closed_box/bump_p7.png) | ![](Origami_Gen_p6_mapper_verification/closed_box/dihedral_p8.png) |

### corner_3panel

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/corner_3panel/corner_3panel_main.png) | ![](Origami_Gen_p6_mapper_verification/corner_3panel/corner_3panel_bump.png) | ![](Origami_Gen_p6_mapper_verification/corner_3panel/corner_3panel_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut | P8 dihedral |
|---|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/corner_3panel/parse.png) | ![](Origami_Gen_p6_mapper_verification/corner_3panel/topology.png) | ![](Origami_Gen_p6_mapper_verification/corner_3panel/fold.png) | ![](Origami_Gen_p6_mapper_verification/corner_3panel/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/corner_3panel/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/corner_3panel/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/corner_3panel/bump_p7.png) | ![](Origami_Gen_p6_mapper_verification/corner_3panel/dihedral_p8.png) |

### cross

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/cross/cross_main.png) | ![](Origami_Gen_p6_mapper_verification/cross/cross_bump.png) | ![](Origami_Gen_p6_mapper_verification/cross/cross_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut | P8 dihedral |
|---|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/cross/parse.png) | ![](Origami_Gen_p6_mapper_verification/cross/topology.png) | ![](Origami_Gen_p6_mapper_verification/cross/fold.png) | ![](Origami_Gen_p6_mapper_verification/cross/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/cross/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/cross/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/cross/bump_p7.png) | ![](Origami_Gen_p6_mapper_verification/cross/dihedral_p8.png) |

### cross_fold_demo

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/cross_fold_demo/cross_fold_demo_main.png) | ![](Origami_Gen_p6_mapper_verification/cross_fold_demo/cross_fold_demo_bump.png) | ![](Origami_Gen_p6_mapper_verification/cross_fold_demo/cross_fold_demo_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut | P8 dihedral |
|---|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/cross_fold_demo/parse.png) | ![](Origami_Gen_p6_mapper_verification/cross_fold_demo/topology.png) | ![](Origami_Gen_p6_mapper_verification/cross_fold_demo/fold.png) | ![](Origami_Gen_p6_mapper_verification/cross_fold_demo/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/cross_fold_demo/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/cross_fold_demo/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/cross_fold_demo/bump_p7.png) | ![](Origami_Gen_p6_mapper_verification/cross_fold_demo/dihedral_p8.png) |

### l_shape

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/l_shape/l_shape_main.png) | ![](Origami_Gen_p6_mapper_verification/l_shape/l_shape_bump.png) | ![](Origami_Gen_p6_mapper_verification/l_shape/l_shape_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut | P8 dihedral |
|---|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/l_shape/parse.png) | ![](Origami_Gen_p6_mapper_verification/l_shape/topology.png) | ![](Origami_Gen_p6_mapper_verification/l_shape/fold.png) | ![](Origami_Gen_p6_mapper_verification/l_shape/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/l_shape/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/l_shape/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/l_shape/bump_p7.png) | ![](Origami_Gen_p6_mapper_verification/l_shape/dihedral_p8.png) |

### long_thin_panel

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/long_thin_panel/long_thin_panel_main.png) | ![](Origami_Gen_p6_mapper_verification/long_thin_panel/long_thin_panel_bump.png) | ![](Origami_Gen_p6_mapper_verification/long_thin_panel/long_thin_panel_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut | P8 dihedral |
|---|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/long_thin_panel/parse.png) | ![](Origami_Gen_p6_mapper_verification/long_thin_panel/topology.png) | ![](Origami_Gen_p6_mapper_verification/long_thin_panel/fold.png) | ![](Origami_Gen_p6_mapper_verification/long_thin_panel/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/long_thin_panel/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/long_thin_panel/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/long_thin_panel/bump_p7.png) | ![](Origami_Gen_p6_mapper_verification/long_thin_panel/dihedral_p8.png) |

### mismatched_resolution

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/mismatched_resolution/mismatched_resolution_main.png) | ![](Origami_Gen_p6_mapper_verification/mismatched_resolution/mismatched_resolution_bump.png) | ![](Origami_Gen_p6_mapper_verification/mismatched_resolution/mismatched_resolution_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut | P8 dihedral |
|---|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/mismatched_resolution/parse.png) | ![](Origami_Gen_p6_mapper_verification/mismatched_resolution/topology.png) | ![](Origami_Gen_p6_mapper_verification/mismatched_resolution/fold.png) | ![](Origami_Gen_p6_mapper_verification/mismatched_resolution/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/mismatched_resolution/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/mismatched_resolution/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/mismatched_resolution/bump_p7.png) | ![](Origami_Gen_p6_mapper_verification/mismatched_resolution/dihedral_p8.png) |

### multi_hole_strip

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/multi_hole_strip/multi_hole_strip_main.png) | ![](Origami_Gen_p6_mapper_verification/multi_hole_strip/multi_hole_strip_bump.png) | ![](Origami_Gen_p6_mapper_verification/multi_hole_strip/multi_hole_strip_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut | P8 dihedral |
|---|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/multi_hole_strip/parse.png) | ![](Origami_Gen_p6_mapper_verification/multi_hole_strip/topology.png) | ![](Origami_Gen_p6_mapper_verification/multi_hole_strip/fold.png) | ![](Origami_Gen_p6_mapper_verification/multi_hole_strip/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/multi_hole_strip/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/multi_hole_strip/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/multi_hole_strip/bump_p7.png) | ![](Origami_Gen_p6_mapper_verification/multi_hole_strip/dihedral_p8.png) |

### single_fold

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/single_fold/single_fold_main.png) | ![](Origami_Gen_p6_mapper_verification/single_fold/single_fold_bump.png) | ![](Origami_Gen_p6_mapper_verification/single_fold/single_fold_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut | P8 dihedral |
|---|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/single_fold/parse.png) | ![](Origami_Gen_p6_mapper_verification/single_fold/topology.png) | ![](Origami_Gen_p6_mapper_verification/single_fold/fold.png) | ![](Origami_Gen_p6_mapper_verification/single_fold/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/single_fold/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/single_fold/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/single_fold/bump_p7.png) | ![](Origami_Gen_p6_mapper_verification/single_fold/dihedral_p8.png) |

### staircase_3

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/staircase_3/staircase_3_main.png) | ![](Origami_Gen_p6_mapper_verification/staircase_3/staircase_3_bump.png) | ![](Origami_Gen_p6_mapper_verification/staircase_3/staircase_3_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut | P8 dihedral |
|---|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/staircase_3/parse.png) | ![](Origami_Gen_p6_mapper_verification/staircase_3/topology.png) | ![](Origami_Gen_p6_mapper_verification/staircase_3/fold.png) | ![](Origami_Gen_p6_mapper_verification/staircase_3/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/staircase_3/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/staircase_3/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/staircase_3/bump_p7.png) | ![](Origami_Gen_p6_mapper_verification/staircase_3/dihedral_p8.png) |

### tiny_panel

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/tiny_panel/tiny_panel_main.png) | ![](Origami_Gen_p6_mapper_verification/tiny_panel/tiny_panel_bump.png) | ![](Origami_Gen_p6_mapper_verification/tiny_panel/tiny_panel_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut | P8 dihedral |
|---|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/tiny_panel/parse.png) | ![](Origami_Gen_p6_mapper_verification/tiny_panel/topology.png) | ![](Origami_Gen_p6_mapper_verification/tiny_panel/fold.png) | ![](Origami_Gen_p6_mapper_verification/tiny_panel/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/tiny_panel/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/tiny_panel/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/tiny_panel/bump_p7.png) | ![](Origami_Gen_p6_mapper_verification/tiny_panel/dihedral_p8.png) |

### u_shape

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/u_shape/u_shape_main.png) | ![](Origami_Gen_p6_mapper_verification/u_shape/u_shape_bump.png) | ![](Origami_Gen_p6_mapper_verification/u_shape/u_shape_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut | P8 dihedral |
|---|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/u_shape/parse.png) | ![](Origami_Gen_p6_mapper_verification/u_shape/topology.png) | ![](Origami_Gen_p6_mapper_verification/u_shape/fold.png) | ![](Origami_Gen_p6_mapper_verification/u_shape/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/u_shape/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/u_shape/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/u_shape/bump_p7.png) | ![](Origami_Gen_p6_mapper_verification/u_shape/dihedral_p8.png) |

### zigzag_4

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/zigzag_4/zigzag_4_main.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_4/zigzag_4_bump.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_4/zigzag_4_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut | P8 dihedral |
|---|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/zigzag_4/parse.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_4/topology.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_4/fold.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_4/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_4/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_4/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_4/bump_p7.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_4/dihedral_p8.png) |

### zigzag_6

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/zigzag_6/zigzag_6_main.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_6/zigzag_6_bump.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_6/zigzag_6_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut | P8 dihedral |
|---|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/zigzag_6/parse.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_6/topology.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_6/fold.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_6/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_6/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_6/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_6/bump_p7.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_6/dihedral_p8.png) |
