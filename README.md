# Output Port — Origami_Gen v2.0 Pipeline Gallery

Per-phase per-case pipeline pictures from Origami_Gen v2.0 at the
finest corpus setting: `mesh_resolution = 1.0 px/cell` with
`RENDER_SCALE = 2` (Fix 1 + Fix 3 active). All 16 cases pass
every §3 hard gate (10/10).

Source repo: https://github.com/voltwin-dev/Origami_Gen

![headline gate matrix](pic/headline_t20260512.png)

## Pipeline phases (9 phases visualized; P10 export emits files only)

| Phase | Module | Input → Output |
|---|---|---|
| **P1 Parse** | `parser/` | PNGs → `ParseResult` (panels + folds + masks) |
| **P2 Topology** | `topology/` | `ParseResult` → `FoldTree` + 2D junctions |
| **P3 Fold** | `folder/` | `FoldTree` → `FoldResult` (integer SO(3) poses) |
| **P4 Mesh** | `mesher/` | + `FoldResult` → `MeshResult` (anchor-aware grid) |
| **P5 Stitch** | `stitcher/` | `MeshResult` → `StitchResult` (post-stitch baseline) |
| **P6 Mapper** | `mapper/` | + masks → `MapResult` (yellow / green / purple element labels — pure tagging, no mesh mutation) |
| **P7 Bump+Cut** | `bumper/` | + `MapResult` → `BumpResult` |
| **P8 Dihedral** | `dihedral/` | `BumpResult` → `DihedralResult` (~90 deg edges in red, neighbouring-face shell up to 4 BFS layers in red→orange→yellow, corner vertices (≥3 90 deg edges meet) in red dots with purple→violet→lavender corner-face shell up to 4 BFS layers — pure analysis, no mesh mutation) |
| **P9 Fillet** | `fillet/` | `BumpResult` + `DihedralResult` → `FilletResult` (tris only). Deletes P8 BFS-tagged faces (layers 0..4), replaces them with analytic quarter-cylinder fillets along every 90 deg fold edge (orange) and spherical caps at every ≥3-edge corner (blue), constant radius `r`. v1: cylinders + spheres NOT yet welded to surviving mesh boundary. |
| P10 Export | `export/` | files (no picture) |

P8 was promoted from the old standalone `scripts/dihedral_90.py`
into a real typed phase; the original P8 Export has moved to P9.

## Per-phase mosaics (all cases on one figure)

### P1 — Parse
![P1_parse](pic/phases/P1_parse_t20260512.png)

### P2 — Topology
![P2_topology](pic/phases/P2_topology_t20260512.png)

### P3 — Fold
![P3_fold](pic/phases/P3_fold_t20260512.png)

### P4 — Mesh
![P4_mesh](pic/phases/P4_mesh_t20260512.png)

### P5 — Stitch
![P5_stitch](pic/phases/P5_stitch_t20260512.png)

### P6 — Mapper
![P6_mapper](pic/phases/P6_mapper_t20260512.png)

### P7 — Bump + Cut
![P7_bump_cut](pic/phases/P7_bump_cut_t20260512.png)

### P8 — Dihedral
![P8_dihedral](pic/phases/P8_dihedral_t20260512.png)

### P9 — Fillet
![P9_fillet](pic/phases/P9_fillet_t20260512.png)

## Per-case pipeline pictures

For each case: the **input PNG bundle** (`_main`, `_bump`, `_hole`)
followed by every phase picture (P1 → P2 → P3 → P4 → P5 → P6 → P7 → P8).
P6 colors: gold = yellow-mask quads, green = green-mask quads,
purple = purple-mask (hole) quads, grey = unmapped. P8: red lines
= mesh edges with dihedral angle ∈ [85, 95] deg (the fold seams,
post bump+cut); red→orange→yellow palette (L0..L4) = faces within
4 BFS layers of any 90 deg edge; red dots = corner verts where
≥ 3 90 deg edges converge; purple→violet→lavender palette
(L0..L4) = faces within 4 BFS layers of any corner vert; grey =
faces outside both shells. Title carries `edges`, `corners`, and
the per-layer face counts.

### box_unfolding

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](pic/box_unfolding/box_unfolding_main_t20260512.png) | ![](pic/box_unfolding/box_unfolding_bump_t20260512.png) | ![](pic/box_unfolding/box_unfolding_hole_t20260512.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut | P8 dihedral | P9 fillet |
|---|---|---|---|---|---|---|---|---|
| ![](pic/box_unfolding/parse_t20260512.png) | ![](pic/box_unfolding/topology_t20260512.png) | ![](pic/box_unfolding/fold_t20260512.png) | ![](pic/box_unfolding/mesh_p4_t20260512.png) | ![](pic/box_unfolding/stitch_p5_t20260512.png) | ![](pic/box_unfolding/map_p6_t20260512.png) | ![](pic/box_unfolding/bump_p7_t20260512.png) | ![](pic/box_unfolding/dihedral_p8_t20260512.png) | ![](pic/box_unfolding/fillet_p9_t20260512.png) |

### cascade_5_deep

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](pic/cascade_5_deep/cascade_5_deep_main_t20260512.png) | ![](pic/cascade_5_deep/cascade_5_deep_bump_t20260512.png) | ![](pic/cascade_5_deep/cascade_5_deep_hole_t20260512.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut | P8 dihedral | P9 fillet |
|---|---|---|---|---|---|---|---|---|
| ![](pic/cascade_5_deep/parse_t20260512.png) | ![](pic/cascade_5_deep/topology_t20260512.png) | ![](pic/cascade_5_deep/fold_t20260512.png) | ![](pic/cascade_5_deep/mesh_p4_t20260512.png) | ![](pic/cascade_5_deep/stitch_p5_t20260512.png) | ![](pic/cascade_5_deep/map_p6_t20260512.png) | ![](pic/cascade_5_deep/bump_p7_t20260512.png) | ![](pic/cascade_5_deep/dihedral_p8_t20260512.png) | ![](pic/cascade_5_deep/fillet_p9_t20260512.png) |

### closed_box

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](pic/closed_box/closed_box_main_t20260512.png) | ![](pic/closed_box/closed_box_bump_t20260512.png) | ![](pic/closed_box/closed_box_hole_t20260512.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut | P8 dihedral | P9 fillet |
|---|---|---|---|---|---|---|---|---|
| ![](pic/closed_box/parse_t20260512.png) | ![](pic/closed_box/topology_t20260512.png) | ![](pic/closed_box/fold_t20260512.png) | ![](pic/closed_box/mesh_p4_t20260512.png) | ![](pic/closed_box/stitch_p5_t20260512.png) | ![](pic/closed_box/map_p6_t20260512.png) | ![](pic/closed_box/bump_p7_t20260512.png) | ![](pic/closed_box/dihedral_p8_t20260512.png) | ![](pic/closed_box/fillet_p9_t20260512.png) |

### corner_3panel

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](pic/corner_3panel/corner_3panel_main_t20260512.png) | ![](pic/corner_3panel/corner_3panel_bump_t20260512.png) | ![](pic/corner_3panel/corner_3panel_hole_t20260512.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut | P8 dihedral | P9 fillet |
|---|---|---|---|---|---|---|---|---|
| ![](pic/corner_3panel/parse_t20260512.png) | ![](pic/corner_3panel/topology_t20260512.png) | ![](pic/corner_3panel/fold_t20260512.png) | ![](pic/corner_3panel/mesh_p4_t20260512.png) | ![](pic/corner_3panel/stitch_p5_t20260512.png) | ![](pic/corner_3panel/map_p6_t20260512.png) | ![](pic/corner_3panel/bump_p7_t20260512.png) | ![](pic/corner_3panel/dihedral_p8_t20260512.png) | ![](pic/corner_3panel/fillet_p9_t20260512.png) |

### cross

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](pic/cross/cross_main_t20260512.png) | ![](pic/cross/cross_bump_t20260512.png) | ![](pic/cross/cross_hole_t20260512.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut | P8 dihedral | P9 fillet |
|---|---|---|---|---|---|---|---|---|
| ![](pic/cross/parse_t20260512.png) | ![](pic/cross/topology_t20260512.png) | ![](pic/cross/fold_t20260512.png) | ![](pic/cross/mesh_p4_t20260512.png) | ![](pic/cross/stitch_p5_t20260512.png) | ![](pic/cross/map_p6_t20260512.png) | ![](pic/cross/bump_p7_t20260512.png) | ![](pic/cross/dihedral_p8_t20260512.png) | ![](pic/cross/fillet_p9_t20260512.png) |

### cross_fold_demo

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](pic/cross_fold_demo/cross_fold_demo_main_t20260512.png) | ![](pic/cross_fold_demo/cross_fold_demo_bump_t20260512.png) | ![](pic/cross_fold_demo/cross_fold_demo_hole_t20260512.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut | P8 dihedral | P9 fillet |
|---|---|---|---|---|---|---|---|---|
| ![](pic/cross_fold_demo/parse_t20260512.png) | ![](pic/cross_fold_demo/topology_t20260512.png) | ![](pic/cross_fold_demo/fold_t20260512.png) | ![](pic/cross_fold_demo/mesh_p4_t20260512.png) | ![](pic/cross_fold_demo/stitch_p5_t20260512.png) | ![](pic/cross_fold_demo/map_p6_t20260512.png) | ![](pic/cross_fold_demo/bump_p7_t20260512.png) | ![](pic/cross_fold_demo/dihedral_p8_t20260512.png) | ![](pic/cross_fold_demo/fillet_p9_t20260512.png) |

### l_shape

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](pic/l_shape/l_shape_main_t20260512.png) | ![](pic/l_shape/l_shape_bump_t20260512.png) | ![](pic/l_shape/l_shape_hole_t20260512.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut | P8 dihedral | P9 fillet |
|---|---|---|---|---|---|---|---|---|
| ![](pic/l_shape/parse_t20260512.png) | ![](pic/l_shape/topology_t20260512.png) | ![](pic/l_shape/fold_t20260512.png) | ![](pic/l_shape/mesh_p4_t20260512.png) | ![](pic/l_shape/stitch_p5_t20260512.png) | ![](pic/l_shape/map_p6_t20260512.png) | ![](pic/l_shape/bump_p7_t20260512.png) | ![](pic/l_shape/dihedral_p8_t20260512.png) | ![](pic/l_shape/fillet_p9_t20260512.png) |

### long_thin_panel

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](pic/long_thin_panel/long_thin_panel_main_t20260512.png) | ![](pic/long_thin_panel/long_thin_panel_bump_t20260512.png) | ![](pic/long_thin_panel/long_thin_panel_hole_t20260512.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut | P8 dihedral | P9 fillet |
|---|---|---|---|---|---|---|---|---|
| ![](pic/long_thin_panel/parse_t20260512.png) | ![](pic/long_thin_panel/topology_t20260512.png) | ![](pic/long_thin_panel/fold_t20260512.png) | ![](pic/long_thin_panel/mesh_p4_t20260512.png) | ![](pic/long_thin_panel/stitch_p5_t20260512.png) | ![](pic/long_thin_panel/map_p6_t20260512.png) | ![](pic/long_thin_panel/bump_p7_t20260512.png) | ![](pic/long_thin_panel/dihedral_p8_t20260512.png) | ![](pic/long_thin_panel/fillet_p9_t20260512.png) |

### mismatched_resolution

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](pic/mismatched_resolution/mismatched_resolution_main_t20260512.png) | ![](pic/mismatched_resolution/mismatched_resolution_bump_t20260512.png) | ![](pic/mismatched_resolution/mismatched_resolution_hole_t20260512.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut | P8 dihedral | P9 fillet |
|---|---|---|---|---|---|---|---|---|
| ![](pic/mismatched_resolution/parse_t20260512.png) | ![](pic/mismatched_resolution/topology_t20260512.png) | ![](pic/mismatched_resolution/fold_t20260512.png) | ![](pic/mismatched_resolution/mesh_p4_t20260512.png) | ![](pic/mismatched_resolution/stitch_p5_t20260512.png) | ![](pic/mismatched_resolution/map_p6_t20260512.png) | ![](pic/mismatched_resolution/bump_p7_t20260512.png) | ![](pic/mismatched_resolution/dihedral_p8_t20260512.png) | ![](pic/mismatched_resolution/fillet_p9_t20260512.png) |

### multi_hole_strip

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](pic/multi_hole_strip/multi_hole_strip_main_t20260512.png) | ![](pic/multi_hole_strip/multi_hole_strip_bump_t20260512.png) | ![](pic/multi_hole_strip/multi_hole_strip_hole_t20260512.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut | P8 dihedral | P9 fillet |
|---|---|---|---|---|---|---|---|---|
| ![](pic/multi_hole_strip/parse_t20260512.png) | ![](pic/multi_hole_strip/topology_t20260512.png) | ![](pic/multi_hole_strip/fold_t20260512.png) | ![](pic/multi_hole_strip/mesh_p4_t20260512.png) | ![](pic/multi_hole_strip/stitch_p5_t20260512.png) | ![](pic/multi_hole_strip/map_p6_t20260512.png) | ![](pic/multi_hole_strip/bump_p7_t20260512.png) | ![](pic/multi_hole_strip/dihedral_p8_t20260512.png) | ![](pic/multi_hole_strip/fillet_p9_t20260512.png) |

### single_fold

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](pic/single_fold/single_fold_main_t20260512.png) | ![](pic/single_fold/single_fold_bump_t20260512.png) | ![](pic/single_fold/single_fold_hole_t20260512.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut | P8 dihedral | P9 fillet |
|---|---|---|---|---|---|---|---|---|
| ![](pic/single_fold/parse_t20260512.png) | ![](pic/single_fold/topology_t20260512.png) | ![](pic/single_fold/fold_t20260512.png) | ![](pic/single_fold/mesh_p4_t20260512.png) | ![](pic/single_fold/stitch_p5_t20260512.png) | ![](pic/single_fold/map_p6_t20260512.png) | ![](pic/single_fold/bump_p7_t20260512.png) | ![](pic/single_fold/dihedral_p8_t20260512.png) | ![](pic/single_fold/fillet_p9_t20260512.png) |

### staircase_3

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](pic/staircase_3/staircase_3_main_t20260512.png) | ![](pic/staircase_3/staircase_3_bump_t20260512.png) | ![](pic/staircase_3/staircase_3_hole_t20260512.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut | P8 dihedral | P9 fillet |
|---|---|---|---|---|---|---|---|---|
| ![](pic/staircase_3/parse_t20260512.png) | ![](pic/staircase_3/topology_t20260512.png) | ![](pic/staircase_3/fold_t20260512.png) | ![](pic/staircase_3/mesh_p4_t20260512.png) | ![](pic/staircase_3/stitch_p5_t20260512.png) | ![](pic/staircase_3/map_p6_t20260512.png) | ![](pic/staircase_3/bump_p7_t20260512.png) | ![](pic/staircase_3/dihedral_p8_t20260512.png) | ![](pic/staircase_3/fillet_p9_t20260512.png) |

### tiny_panel

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](pic/tiny_panel/tiny_panel_main_t20260512.png) | ![](pic/tiny_panel/tiny_panel_bump_t20260512.png) | ![](pic/tiny_panel/tiny_panel_hole_t20260512.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut | P8 dihedral | P9 fillet |
|---|---|---|---|---|---|---|---|---|
| ![](pic/tiny_panel/parse_t20260512.png) | ![](pic/tiny_panel/topology_t20260512.png) | ![](pic/tiny_panel/fold_t20260512.png) | ![](pic/tiny_panel/mesh_p4_t20260512.png) | ![](pic/tiny_panel/stitch_p5_t20260512.png) | ![](pic/tiny_panel/map_p6_t20260512.png) | ![](pic/tiny_panel/bump_p7_t20260512.png) | ![](pic/tiny_panel/dihedral_p8_t20260512.png) | ![](pic/tiny_panel/fillet_p9_t20260512.png) |

### u_shape

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](pic/u_shape/u_shape_main_t20260512.png) | ![](pic/u_shape/u_shape_bump_t20260512.png) | ![](pic/u_shape/u_shape_hole_t20260512.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut | P8 dihedral | P9 fillet |
|---|---|---|---|---|---|---|---|---|
| ![](pic/u_shape/parse_t20260512.png) | ![](pic/u_shape/topology_t20260512.png) | ![](pic/u_shape/fold_t20260512.png) | ![](pic/u_shape/mesh_p4_t20260512.png) | ![](pic/u_shape/stitch_p5_t20260512.png) | ![](pic/u_shape/map_p6_t20260512.png) | ![](pic/u_shape/bump_p7_t20260512.png) | ![](pic/u_shape/dihedral_p8_t20260512.png) | ![](pic/u_shape/fillet_p9_t20260512.png) |

### zigzag_4

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](pic/zigzag_4/zigzag_4_main_t20260512.png) | ![](pic/zigzag_4/zigzag_4_bump_t20260512.png) | ![](pic/zigzag_4/zigzag_4_hole_t20260512.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut | P8 dihedral | P9 fillet |
|---|---|---|---|---|---|---|---|---|
| ![](pic/zigzag_4/parse_t20260512.png) | ![](pic/zigzag_4/topology_t20260512.png) | ![](pic/zigzag_4/fold_t20260512.png) | ![](pic/zigzag_4/mesh_p4_t20260512.png) | ![](pic/zigzag_4/stitch_p5_t20260512.png) | ![](pic/zigzag_4/map_p6_t20260512.png) | ![](pic/zigzag_4/bump_p7_t20260512.png) | ![](pic/zigzag_4/dihedral_p8_t20260512.png) | ![](pic/zigzag_4/fillet_p9_t20260512.png) |

### zigzag_6

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](pic/zigzag_6/zigzag_6_main_t20260512.png) | ![](pic/zigzag_6/zigzag_6_bump_t20260512.png) | ![](pic/zigzag_6/zigzag_6_hole_t20260512.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut | P8 dihedral | P9 fillet |
|---|---|---|---|---|---|---|---|---|
| ![](pic/zigzag_6/parse_t20260512.png) | ![](pic/zigzag_6/topology_t20260512.png) | ![](pic/zigzag_6/fold_t20260512.png) | ![](pic/zigzag_6/mesh_p4_t20260512.png) | ![](pic/zigzag_6/stitch_p5_t20260512.png) | ![](pic/zigzag_6/map_p6_t20260512.png) | ![](pic/zigzag_6/bump_p7_t20260512.png) | ![](pic/zigzag_6/dihedral_p8_t20260512.png) | ![](pic/zigzag_6/fillet_p9_t20260512.png) |
