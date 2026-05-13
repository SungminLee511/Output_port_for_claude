# Output Port — Origami_Gen Pipeline Gallery

Per-phase per-case pipeline pictures at `mesh_resolution = 2.0 px/cell`.
Run timestamp: **2026-05-13 14:57 KST** (P10 refine pass: subdivide cut-boundary edges on fillet tris with mid-edge verts projected onto cylinder/sphere — boundary tessellation 2× finer, snap smooths cleanly).

Pipeline order (cut moved BEFORE bump; snap preserves panel-local z):

**P1 parse → P2 topology → P3 fold → P4 mesh → P5 stitch → P6 mapper (on stitch) → P7 dihedral → P8 fillet → P9 mapper (propagated onto fillet tris) → P10 cut → bump → snap**

Source repo: https://github.com/voltwin-dev/Origami_Gen

This batch fixes the `cross_fold_demo` "disconnected cut boundary"
bug. Previously bump ran before cut, so the bump-purple seam was
treated as a region boundary (weight=0); cut-edge nodes inside a
bump dome were pinned at z=0 and snap flattened any residual
displacement, creating a visible cliff. Now cut runs first, so
bump rolls smoothly to the cut edge, and snap preserves each
boundary vert's panel-local z so the bump elevation survives the
contour pull.

![headline](pic/headline_t20260513j.png)

## Pipeline phases (10 visualized)

| Phase | Module | Input → Output |
|---|---|---|
| **P1 Parse** | `parser/` | PNGs → `ParseResult` |
| **P2 Topology** | `topology/` | `ParseResult` → `FoldTree` |
| **P3 Fold** | `folder/` | `FoldTree` → `FoldResult` |
| **P4 Mesh** | `mesher/` | + `FoldResult` → `MeshResult` |
| **P5 Stitch** | `stitcher/` | `MeshResult` → `StitchResult` |
| **P6 Mapper (stitch)** | `mapper.compute_mapping` | `StitchResult` → `MapResult` (per-stitch-face labels via inverse-pose 2D projection) |
| **P7 Dihedral** | `dihedral/` | `StitchResult` → `DihedralResult` |
| **P8 Fillet** | `fillet/` | `StitchResult` + `DihedralResult` → `FilletResult` (boundary-grown, tri-only) |
| **P9 Mapper (propagated)** | `mapper.propagate_mapping` | `MapResult(stitch)` + `FilletResult` → `MapResult(fillet)` (each fillet tri inherits its parent stitch face's label) |
| **P10 Cut → Bump → Snap** | `bumper/` | `FilletResult` + propagated `MapResult` → `BumpResult` (drop purple tris, then yellow → +z / green → −z displacement, then snap new boundary onto purple contour) |

## Per-phase mosaics

### P1 parse
![P1_parse](pic/phases/P1_parse_t20260513j.png)

### P2 topology
![P2_topology](pic/phases/P2_topology_t20260513j.png)

### P3 fold
![P3_fold](pic/phases/P3_fold_t20260513j.png)

### P4 mesh
![P4_mesh](pic/phases/P4_mesh_t20260513j.png)

### P5 stitch
![P5_stitch](pic/phases/P5_stitch_t20260513j.png)

### P6 mapper (stitch, pre-fillet)
![P6_mapper](pic/phases/P6_mapper_t20260513j.png)

### P7 dihedral
![P7_dihedral](pic/phases/P7_dihedral_t20260513j.png)

### P8 fillet
![P8_fillet](pic/phases/P8_fillet_t20260513j.png)

### P9 mapper (propagated, post-fillet)
![P9_mapper](pic/phases/P9_mapper_t20260513j.png)

### P10 cut → bump → snap
![P10_bumpcut](pic/phases/P10_bumpcut_t20260513j.png)

## Per-case pipeline pictures

### box_unfolding

**Inputs:**

| `_main.png` | `_bump.png` | `_hole.png` |
|---|---|---|
| ![](pic/box_unfolding/box_unfolding_main_t20260513j.png) | ![](pic/box_unfolding/box_unfolding_bump_t20260513j.png) | ![](pic/box_unfolding/box_unfolding_hole_t20260513j.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper (stitch) | P7 dihedral | P8 fillet | P9 mapper (fillet) | P10 bump+cut |
|---|---|---|---|---|---|---|---|---|---|
| ![](pic/box_unfolding/parse_t20260513j.png) | ![](pic/box_unfolding/topology_t20260513j.png) | ![](pic/box_unfolding/fold_t20260513j.png) | ![](pic/box_unfolding/mesh_p4_t20260513j.png) | ![](pic/box_unfolding/stitch_p5_t20260513j.png) | ![](pic/box_unfolding/mapper_p6_t20260513j.png) | ![](pic/box_unfolding/dihedral_p7_t20260513j.png) | ![](pic/box_unfolding/fillet_p8_t20260513j.png) | ![](pic/box_unfolding/mapper_p9_t20260513j.png) | ![](pic/box_unfolding/bump_p10_t20260513j.png) |

**Composite:** ![](pic/box_unfolding/composite_t20260513j.png)

### cascade_5_deep

**Inputs:**

| `_main.png` | `_bump.png` | `_hole.png` |
|---|---|---|
| ![](pic/cascade_5_deep/cascade_5_deep_main_t20260513j.png) | ![](pic/cascade_5_deep/cascade_5_deep_bump_t20260513j.png) | ![](pic/cascade_5_deep/cascade_5_deep_hole_t20260513j.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper (stitch) | P7 dihedral | P8 fillet | P9 mapper (fillet) | P10 bump+cut |
|---|---|---|---|---|---|---|---|---|---|
| ![](pic/cascade_5_deep/parse_t20260513j.png) | ![](pic/cascade_5_deep/topology_t20260513j.png) | ![](pic/cascade_5_deep/fold_t20260513j.png) | ![](pic/cascade_5_deep/mesh_p4_t20260513j.png) | ![](pic/cascade_5_deep/stitch_p5_t20260513j.png) | ![](pic/cascade_5_deep/mapper_p6_t20260513j.png) | ![](pic/cascade_5_deep/dihedral_p7_t20260513j.png) | ![](pic/cascade_5_deep/fillet_p8_t20260513j.png) | ![](pic/cascade_5_deep/mapper_p9_t20260513j.png) | ![](pic/cascade_5_deep/bump_p10_t20260513j.png) |

**Composite:** ![](pic/cascade_5_deep/composite_t20260513j.png)

### closed_box

**Inputs:**

| `_main.png` | `_bump.png` | `_hole.png` |
|---|---|---|
| ![](pic/closed_box/closed_box_main_t20260513j.png) | ![](pic/closed_box/closed_box_bump_t20260513j.png) | ![](pic/closed_box/closed_box_hole_t20260513j.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper (stitch) | P7 dihedral | P8 fillet | P9 mapper (fillet) | P10 bump+cut |
|---|---|---|---|---|---|---|---|---|---|
| ![](pic/closed_box/parse_t20260513j.png) | ![](pic/closed_box/topology_t20260513j.png) | ![](pic/closed_box/fold_t20260513j.png) | ![](pic/closed_box/mesh_p4_t20260513j.png) | ![](pic/closed_box/stitch_p5_t20260513j.png) | ![](pic/closed_box/mapper_p6_t20260513j.png) | ![](pic/closed_box/dihedral_p7_t20260513j.png) | ![](pic/closed_box/fillet_p8_t20260513j.png) | ![](pic/closed_box/mapper_p9_t20260513j.png) | ![](pic/closed_box/bump_p10_t20260513j.png) |

**Composite:** ![](pic/closed_box/composite_t20260513j.png)

### corner_3panel

**Inputs:**

| `_main.png` | `_bump.png` | `_hole.png` |
|---|---|---|
| ![](pic/corner_3panel/corner_3panel_main_t20260513j.png) | ![](pic/corner_3panel/corner_3panel_bump_t20260513j.png) | ![](pic/corner_3panel/corner_3panel_hole_t20260513j.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper (stitch) | P7 dihedral | P8 fillet | P9 mapper (fillet) | P10 bump+cut |
|---|---|---|---|---|---|---|---|---|---|
| ![](pic/corner_3panel/parse_t20260513j.png) | ![](pic/corner_3panel/topology_t20260513j.png) | ![](pic/corner_3panel/fold_t20260513j.png) | ![](pic/corner_3panel/mesh_p4_t20260513j.png) | ![](pic/corner_3panel/stitch_p5_t20260513j.png) | ![](pic/corner_3panel/mapper_p6_t20260513j.png) | ![](pic/corner_3panel/dihedral_p7_t20260513j.png) | ![](pic/corner_3panel/fillet_p8_t20260513j.png) | ![](pic/corner_3panel/mapper_p9_t20260513j.png) | ![](pic/corner_3panel/bump_p10_t20260513j.png) |

**Composite:** ![](pic/corner_3panel/composite_t20260513j.png)

### cross

**Inputs:**

| `_main.png` | `_bump.png` | `_hole.png` |
|---|---|---|
| ![](pic/cross/cross_main_t20260513j.png) | ![](pic/cross/cross_bump_t20260513j.png) | ![](pic/cross/cross_hole_t20260513j.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper (stitch) | P7 dihedral | P8 fillet | P9 mapper (fillet) | P10 bump+cut |
|---|---|---|---|---|---|---|---|---|---|
| ![](pic/cross/parse_t20260513j.png) | ![](pic/cross/topology_t20260513j.png) | ![](pic/cross/fold_t20260513j.png) | ![](pic/cross/mesh_p4_t20260513j.png) | ![](pic/cross/stitch_p5_t20260513j.png) | ![](pic/cross/mapper_p6_t20260513j.png) | ![](pic/cross/dihedral_p7_t20260513j.png) | ![](pic/cross/fillet_p8_t20260513j.png) | ![](pic/cross/mapper_p9_t20260513j.png) | ![](pic/cross/bump_p10_t20260513j.png) |

**Composite:** ![](pic/cross/composite_t20260513j.png)

### cross_fold_demo

**Inputs:**

| `_main.png` | `_bump.png` | `_hole.png` |
|---|---|---|
| ![](pic/cross_fold_demo/cross_fold_demo_main_t20260513j.png) | ![](pic/cross_fold_demo/cross_fold_demo_bump_t20260513j.png) | ![](pic/cross_fold_demo/cross_fold_demo_hole_t20260513j.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper (stitch) | P7 dihedral | P8 fillet | P9 mapper (fillet) | P10 bump+cut |
|---|---|---|---|---|---|---|---|---|---|
| ![](pic/cross_fold_demo/parse_t20260513j.png) | ![](pic/cross_fold_demo/topology_t20260513j.png) | ![](pic/cross_fold_demo/fold_t20260513j.png) | ![](pic/cross_fold_demo/mesh_p4_t20260513j.png) | ![](pic/cross_fold_demo/stitch_p5_t20260513j.png) | ![](pic/cross_fold_demo/mapper_p6_t20260513j.png) | ![](pic/cross_fold_demo/dihedral_p7_t20260513j.png) | ![](pic/cross_fold_demo/fillet_p8_t20260513j.png) | ![](pic/cross_fold_demo/mapper_p9_t20260513j.png) | ![](pic/cross_fold_demo/bump_p10_t20260513j.png) |

**Composite:** ![](pic/cross_fold_demo/composite_t20260513j.png)

### l_shape

**Inputs:**

| `_main.png` | `_bump.png` | `_hole.png` |
|---|---|---|
| ![](pic/l_shape/l_shape_main_t20260513j.png) | ![](pic/l_shape/l_shape_bump_t20260513j.png) | ![](pic/l_shape/l_shape_hole_t20260513j.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper (stitch) | P7 dihedral | P8 fillet | P9 mapper (fillet) | P10 bump+cut |
|---|---|---|---|---|---|---|---|---|---|
| ![](pic/l_shape/parse_t20260513j.png) | ![](pic/l_shape/topology_t20260513j.png) | ![](pic/l_shape/fold_t20260513j.png) | ![](pic/l_shape/mesh_p4_t20260513j.png) | ![](pic/l_shape/stitch_p5_t20260513j.png) | ![](pic/l_shape/mapper_p6_t20260513j.png) | ![](pic/l_shape/dihedral_p7_t20260513j.png) | ![](pic/l_shape/fillet_p8_t20260513j.png) | ![](pic/l_shape/mapper_p9_t20260513j.png) | ![](pic/l_shape/bump_p10_t20260513j.png) |

**Composite:** ![](pic/l_shape/composite_t20260513j.png)

### long_thin_panel

**Inputs:**

| `_main.png` | `_bump.png` | `_hole.png` |
|---|---|---|
| ![](pic/long_thin_panel/long_thin_panel_main_t20260513j.png) | ![](pic/long_thin_panel/long_thin_panel_bump_t20260513j.png) | ![](pic/long_thin_panel/long_thin_panel_hole_t20260513j.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper (stitch) | P7 dihedral | P8 fillet | P9 mapper (fillet) | P10 bump+cut |
|---|---|---|---|---|---|---|---|---|---|
| ![](pic/long_thin_panel/parse_t20260513j.png) | ![](pic/long_thin_panel/topology_t20260513j.png) | ![](pic/long_thin_panel/fold_t20260513j.png) | ![](pic/long_thin_panel/mesh_p4_t20260513j.png) | ![](pic/long_thin_panel/stitch_p5_t20260513j.png) | ![](pic/long_thin_panel/mapper_p6_t20260513j.png) | ![](pic/long_thin_panel/dihedral_p7_t20260513j.png) | ![](pic/long_thin_panel/fillet_p8_t20260513j.png) | ![](pic/long_thin_panel/mapper_p9_t20260513j.png) | ![](pic/long_thin_panel/bump_p10_t20260513j.png) |

**Composite:** ![](pic/long_thin_panel/composite_t20260513j.png)

### mismatched_resolution

**Inputs:**

| `_main.png` | `_bump.png` | `_hole.png` |
|---|---|---|
| ![](pic/mismatched_resolution/mismatched_resolution_main_t20260513j.png) | ![](pic/mismatched_resolution/mismatched_resolution_bump_t20260513j.png) | ![](pic/mismatched_resolution/mismatched_resolution_hole_t20260513j.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper (stitch) | P7 dihedral | P8 fillet | P9 mapper (fillet) | P10 bump+cut |
|---|---|---|---|---|---|---|---|---|---|
| ![](pic/mismatched_resolution/parse_t20260513j.png) | ![](pic/mismatched_resolution/topology_t20260513j.png) | ![](pic/mismatched_resolution/fold_t20260513j.png) | ![](pic/mismatched_resolution/mesh_p4_t20260513j.png) | ![](pic/mismatched_resolution/stitch_p5_t20260513j.png) | ![](pic/mismatched_resolution/mapper_p6_t20260513j.png) | ![](pic/mismatched_resolution/dihedral_p7_t20260513j.png) | ![](pic/mismatched_resolution/fillet_p8_t20260513j.png) | ![](pic/mismatched_resolution/mapper_p9_t20260513j.png) | ![](pic/mismatched_resolution/bump_p10_t20260513j.png) |

**Composite:** ![](pic/mismatched_resolution/composite_t20260513j.png)

### multi_hole_strip

**Inputs:**

| `_main.png` | `_bump.png` | `_hole.png` |
|---|---|---|
| ![](pic/multi_hole_strip/multi_hole_strip_main_t20260513j.png) | ![](pic/multi_hole_strip/multi_hole_strip_bump_t20260513j.png) | ![](pic/multi_hole_strip/multi_hole_strip_hole_t20260513j.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper (stitch) | P7 dihedral | P8 fillet | P9 mapper (fillet) | P10 bump+cut |
|---|---|---|---|---|---|---|---|---|---|
| ![](pic/multi_hole_strip/parse_t20260513j.png) | ![](pic/multi_hole_strip/topology_t20260513j.png) | ![](pic/multi_hole_strip/fold_t20260513j.png) | ![](pic/multi_hole_strip/mesh_p4_t20260513j.png) | ![](pic/multi_hole_strip/stitch_p5_t20260513j.png) | ![](pic/multi_hole_strip/mapper_p6_t20260513j.png) | ![](pic/multi_hole_strip/dihedral_p7_t20260513j.png) | ![](pic/multi_hole_strip/fillet_p8_t20260513j.png) | ![](pic/multi_hole_strip/mapper_p9_t20260513j.png) | ![](pic/multi_hole_strip/bump_p10_t20260513j.png) |

**Composite:** ![](pic/multi_hole_strip/composite_t20260513j.png)

### single_fold

**Inputs:**

| `_main.png` | `_bump.png` | `_hole.png` |
|---|---|---|
| ![](pic/single_fold/single_fold_main_t20260513j.png) | ![](pic/single_fold/single_fold_bump_t20260513j.png) | ![](pic/single_fold/single_fold_hole_t20260513j.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper (stitch) | P7 dihedral | P8 fillet | P9 mapper (fillet) | P10 bump+cut |
|---|---|---|---|---|---|---|---|---|---|
| ![](pic/single_fold/parse_t20260513j.png) | ![](pic/single_fold/topology_t20260513j.png) | ![](pic/single_fold/fold_t20260513j.png) | ![](pic/single_fold/mesh_p4_t20260513j.png) | ![](pic/single_fold/stitch_p5_t20260513j.png) | ![](pic/single_fold/mapper_p6_t20260513j.png) | ![](pic/single_fold/dihedral_p7_t20260513j.png) | ![](pic/single_fold/fillet_p8_t20260513j.png) | ![](pic/single_fold/mapper_p9_t20260513j.png) | ![](pic/single_fold/bump_p10_t20260513j.png) |

**Composite:** ![](pic/single_fold/composite_t20260513j.png)

### staircase_3

**Inputs:**

| `_main.png` | `_bump.png` | `_hole.png` |
|---|---|---|
| ![](pic/staircase_3/staircase_3_main_t20260513j.png) | ![](pic/staircase_3/staircase_3_bump_t20260513j.png) | ![](pic/staircase_3/staircase_3_hole_t20260513j.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper (stitch) | P7 dihedral | P8 fillet | P9 mapper (fillet) | P10 bump+cut |
|---|---|---|---|---|---|---|---|---|---|
| ![](pic/staircase_3/parse_t20260513j.png) | ![](pic/staircase_3/topology_t20260513j.png) | ![](pic/staircase_3/fold_t20260513j.png) | ![](pic/staircase_3/mesh_p4_t20260513j.png) | ![](pic/staircase_3/stitch_p5_t20260513j.png) | ![](pic/staircase_3/mapper_p6_t20260513j.png) | ![](pic/staircase_3/dihedral_p7_t20260513j.png) | ![](pic/staircase_3/fillet_p8_t20260513j.png) | ![](pic/staircase_3/mapper_p9_t20260513j.png) | ![](pic/staircase_3/bump_p10_t20260513j.png) |

**Composite:** ![](pic/staircase_3/composite_t20260513j.png)

### tiny_panel

**Inputs:**

| `_main.png` | `_bump.png` | `_hole.png` |
|---|---|---|
| ![](pic/tiny_panel/tiny_panel_main_t20260513j.png) | ![](pic/tiny_panel/tiny_panel_bump_t20260513j.png) | ![](pic/tiny_panel/tiny_panel_hole_t20260513j.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper (stitch) | P7 dihedral | P8 fillet | P9 mapper (fillet) | P10 bump+cut |
|---|---|---|---|---|---|---|---|---|---|
| ![](pic/tiny_panel/parse_t20260513j.png) | ![](pic/tiny_panel/topology_t20260513j.png) | ![](pic/tiny_panel/fold_t20260513j.png) | ![](pic/tiny_panel/mesh_p4_t20260513j.png) | ![](pic/tiny_panel/stitch_p5_t20260513j.png) | ![](pic/tiny_panel/mapper_p6_t20260513j.png) | ![](pic/tiny_panel/dihedral_p7_t20260513j.png) | ![](pic/tiny_panel/fillet_p8_t20260513j.png) | ![](pic/tiny_panel/mapper_p9_t20260513j.png) | ![](pic/tiny_panel/bump_p10_t20260513j.png) |

**Composite:** ![](pic/tiny_panel/composite_t20260513j.png)

### u_shape

**Inputs:**

| `_main.png` | `_bump.png` | `_hole.png` |
|---|---|---|
| ![](pic/u_shape/u_shape_main_t20260513j.png) | ![](pic/u_shape/u_shape_bump_t20260513j.png) | ![](pic/u_shape/u_shape_hole_t20260513j.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper (stitch) | P7 dihedral | P8 fillet | P9 mapper (fillet) | P10 bump+cut |
|---|---|---|---|---|---|---|---|---|---|
| ![](pic/u_shape/parse_t20260513j.png) | ![](pic/u_shape/topology_t20260513j.png) | ![](pic/u_shape/fold_t20260513j.png) | ![](pic/u_shape/mesh_p4_t20260513j.png) | ![](pic/u_shape/stitch_p5_t20260513j.png) | ![](pic/u_shape/mapper_p6_t20260513j.png) | ![](pic/u_shape/dihedral_p7_t20260513j.png) | ![](pic/u_shape/fillet_p8_t20260513j.png) | ![](pic/u_shape/mapper_p9_t20260513j.png) | ![](pic/u_shape/bump_p10_t20260513j.png) |

**Composite:** ![](pic/u_shape/composite_t20260513j.png)

### zigzag_4

**Inputs:**

| `_main.png` | `_bump.png` | `_hole.png` |
|---|---|---|
| ![](pic/zigzag_4/zigzag_4_main_t20260513j.png) | ![](pic/zigzag_4/zigzag_4_bump_t20260513j.png) | ![](pic/zigzag_4/zigzag_4_hole_t20260513j.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper (stitch) | P7 dihedral | P8 fillet | P9 mapper (fillet) | P10 bump+cut |
|---|---|---|---|---|---|---|---|---|---|
| ![](pic/zigzag_4/parse_t20260513j.png) | ![](pic/zigzag_4/topology_t20260513j.png) | ![](pic/zigzag_4/fold_t20260513j.png) | ![](pic/zigzag_4/mesh_p4_t20260513j.png) | ![](pic/zigzag_4/stitch_p5_t20260513j.png) | ![](pic/zigzag_4/mapper_p6_t20260513j.png) | ![](pic/zigzag_4/dihedral_p7_t20260513j.png) | ![](pic/zigzag_4/fillet_p8_t20260513j.png) | ![](pic/zigzag_4/mapper_p9_t20260513j.png) | ![](pic/zigzag_4/bump_p10_t20260513j.png) |

**Composite:** ![](pic/zigzag_4/composite_t20260513j.png)

### zigzag_6

**Inputs:**

| `_main.png` | `_bump.png` | `_hole.png` |
|---|---|---|
| ![](pic/zigzag_6/zigzag_6_main_t20260513j.png) | ![](pic/zigzag_6/zigzag_6_bump_t20260513j.png) | ![](pic/zigzag_6/zigzag_6_hole_t20260513j.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper (stitch) | P7 dihedral | P8 fillet | P9 mapper (fillet) | P10 bump+cut |
|---|---|---|---|---|---|---|---|---|---|
| ![](pic/zigzag_6/parse_t20260513j.png) | ![](pic/zigzag_6/topology_t20260513j.png) | ![](pic/zigzag_6/fold_t20260513j.png) | ![](pic/zigzag_6/mesh_p4_t20260513j.png) | ![](pic/zigzag_6/stitch_p5_t20260513j.png) | ![](pic/zigzag_6/mapper_p6_t20260513j.png) | ![](pic/zigzag_6/dihedral_p7_t20260513j.png) | ![](pic/zigzag_6/fillet_p8_t20260513j.png) | ![](pic/zigzag_6/mapper_p9_t20260513j.png) | ![](pic/zigzag_6/bump_p10_t20260513j.png) |

**Composite:** ![](pic/zigzag_6/composite_t20260513j.png)
