# Output Port — Origami_Gen Pipeline Gallery

Per-phase per-case pipeline pictures at `mesh_resolution = 1.0 px/cell`. Pipeline order:

**P1 parse → P2 topology → P3 fold → P4 mesh → P5 stitch → mapper (on stitch) → dihedral → fillet → propagate_mapping (carries stitch labels onto fillet tris)**

Source repo: https://github.com/voltwin-dev/Origami_Gen

![headline](pic/headline_t20260513b.png)

## Pipeline phases (8 phases visualized)

| Phase | Module | Input → Output |
|---|---|---|
| **P1 Parse** | `parser/` | PNGs → `ParseResult` |
| **P2 Topology** | `topology/` | `ParseResult` → `FoldTree` |
| **P3 Fold** | `folder/` | `FoldTree` → `FoldResult` |
| **P4 Mesh** | `mesher/` | + `FoldResult` → `MeshResult` |
| **P5 Stitch** | `stitcher/` | `MeshResult` → `StitchResult` |
| **Dihedral** | `dihedral/` | `StitchResult` → `DihedralResult` (~90 deg edges + BFS-layer shells + corners) |
| **Fillet** | `fillet/` | `StitchResult` + `DihedralResult` → `FilletResult` (tri-only; boundary-grown, watertight) |
| **Mapper** | `mapper/` | `compute_mapping(stitch, fold, parse)` → labels per stitch face; `propagate_mapping(stitch_map, fillet)` → labels per fillet tri |

**Option A** wiring: mapper runs BEFORE dihedral/fillet on the flat stitch geometry; fillet tracks which stitch face each new tri replaced, and `propagate_mapping` carries yellow / green / purple labels through. Labels stay accurate on curved fillet tris.

## Per-phase mosaics

### P1 parse
![P1_parse](pic/phases/P1_parse_t20260513b.png)

### P2 topology
![P2_topology](pic/phases/P2_topology_t20260513b.png)

### P3 fold
![P3_fold](pic/phases/P3_fold_t20260513b.png)

### P4 mesh
![P4_mesh](pic/phases/P4_mesh_t20260513b.png)

### P5 stitch
![P5_stitch](pic/phases/P5_stitch_t20260513b.png)

### Dihedral
![dihedral](pic/phases/dihedral_t20260513b.png)

### Fillet
![fillet](pic/phases/fillet_t20260513b.png)

### Mapper
![mapper](pic/phases/mapper_t20260513b.png)

## Per-case pipeline pictures

### box_unfolding

**Inputs:**

| `_main.png` | `_bump.png` | `_hole.png` |
|---|---|---|
| ![](pic/box_unfolding/box_unfolding_main_t20260513b.png) | ![](pic/box_unfolding/box_unfolding_bump_t20260513b.png) | ![](pic/box_unfolding/box_unfolding_hole_t20260513b.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | dihedral | fillet | mapper |
|---|---|---|---|---|---|---|---|
| ![](pic/box_unfolding/parse_t20260513b.png) | ![](pic/box_unfolding/topology_t20260513b.png) | ![](pic/box_unfolding/fold_t20260513b.png) | ![](pic/box_unfolding/mesh_p4_t20260513b.png) | ![](pic/box_unfolding/stitch_p5_t20260513b.png) | ![](pic/box_unfolding/dihedral_t20260513b.png) | ![](pic/box_unfolding/fillet_t20260513b.png) | ![](pic/box_unfolding/mapper_t20260513b.png) |

### cascade_5_deep

**Inputs:**

| `_main.png` | `_bump.png` | `_hole.png` |
|---|---|---|
| ![](pic/cascade_5_deep/cascade_5_deep_main_t20260513b.png) | ![](pic/cascade_5_deep/cascade_5_deep_bump_t20260513b.png) | ![](pic/cascade_5_deep/cascade_5_deep_hole_t20260513b.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | dihedral | fillet | mapper |
|---|---|---|---|---|---|---|---|
| ![](pic/cascade_5_deep/parse_t20260513b.png) | ![](pic/cascade_5_deep/topology_t20260513b.png) | ![](pic/cascade_5_deep/fold_t20260513b.png) | ![](pic/cascade_5_deep/mesh_p4_t20260513b.png) | ![](pic/cascade_5_deep/stitch_p5_t20260513b.png) | ![](pic/cascade_5_deep/dihedral_t20260513b.png) | ![](pic/cascade_5_deep/fillet_t20260513b.png) | ![](pic/cascade_5_deep/mapper_t20260513b.png) |

### closed_box

**Inputs:**

| `_main.png` | `_bump.png` | `_hole.png` |
|---|---|---|
| ![](pic/closed_box/closed_box_main_t20260513b.png) | ![](pic/closed_box/closed_box_bump_t20260513b.png) | ![](pic/closed_box/closed_box_hole_t20260513b.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | dihedral | fillet | mapper |
|---|---|---|---|---|---|---|---|
| ![](pic/closed_box/parse_t20260513b.png) | ![](pic/closed_box/topology_t20260513b.png) | ![](pic/closed_box/fold_t20260513b.png) | ![](pic/closed_box/mesh_p4_t20260513b.png) | ![](pic/closed_box/stitch_p5_t20260513b.png) | ![](pic/closed_box/dihedral_t20260513b.png) | ![](pic/closed_box/fillet_t20260513b.png) | ![](pic/closed_box/mapper_t20260513b.png) |

### corner_3panel

**Inputs:**

| `_main.png` | `_bump.png` | `_hole.png` |
|---|---|---|
| ![](pic/corner_3panel/corner_3panel_main_t20260513b.png) | ![](pic/corner_3panel/corner_3panel_bump_t20260513b.png) | ![](pic/corner_3panel/corner_3panel_hole_t20260513b.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | dihedral | fillet | mapper |
|---|---|---|---|---|---|---|---|
| ![](pic/corner_3panel/parse_t20260513b.png) | ![](pic/corner_3panel/topology_t20260513b.png) | ![](pic/corner_3panel/fold_t20260513b.png) | ![](pic/corner_3panel/mesh_p4_t20260513b.png) | ![](pic/corner_3panel/stitch_p5_t20260513b.png) | ![](pic/corner_3panel/dihedral_t20260513b.png) | ![](pic/corner_3panel/fillet_t20260513b.png) | ![](pic/corner_3panel/mapper_t20260513b.png) |

### cross

**Inputs:**

| `_main.png` | `_bump.png` | `_hole.png` |
|---|---|---|
| ![](pic/cross/cross_main_t20260513b.png) | ![](pic/cross/cross_bump_t20260513b.png) | ![](pic/cross/cross_hole_t20260513b.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | dihedral | fillet | mapper |
|---|---|---|---|---|---|---|---|
| ![](pic/cross/parse_t20260513b.png) | ![](pic/cross/topology_t20260513b.png) | ![](pic/cross/fold_t20260513b.png) | ![](pic/cross/mesh_p4_t20260513b.png) | ![](pic/cross/stitch_p5_t20260513b.png) | ![](pic/cross/dihedral_t20260513b.png) | ![](pic/cross/fillet_t20260513b.png) | ![](pic/cross/mapper_t20260513b.png) |

### cross_fold_demo

**Inputs:**

| `_main.png` | `_bump.png` | `_hole.png` |
|---|---|---|
| ![](pic/cross_fold_demo/cross_fold_demo_main_t20260513b.png) | ![](pic/cross_fold_demo/cross_fold_demo_bump_t20260513b.png) | ![](pic/cross_fold_demo/cross_fold_demo_hole_t20260513b.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | dihedral | fillet | mapper |
|---|---|---|---|---|---|---|---|
| ![](pic/cross_fold_demo/parse_t20260513b.png) | ![](pic/cross_fold_demo/topology_t20260513b.png) | ![](pic/cross_fold_demo/fold_t20260513b.png) | ![](pic/cross_fold_demo/mesh_p4_t20260513b.png) | ![](pic/cross_fold_demo/stitch_p5_t20260513b.png) | ![](pic/cross_fold_demo/dihedral_t20260513b.png) | ![](pic/cross_fold_demo/fillet_t20260513b.png) | ![](pic/cross_fold_demo/mapper_t20260513b.png) |

### l_shape

**Inputs:**

| `_main.png` | `_bump.png` | `_hole.png` |
|---|---|---|
| ![](pic/l_shape/l_shape_main_t20260513b.png) | ![](pic/l_shape/l_shape_bump_t20260513b.png) | ![](pic/l_shape/l_shape_hole_t20260513b.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | dihedral | fillet | mapper |
|---|---|---|---|---|---|---|---|
| ![](pic/l_shape/parse_t20260513b.png) | ![](pic/l_shape/topology_t20260513b.png) | ![](pic/l_shape/fold_t20260513b.png) | ![](pic/l_shape/mesh_p4_t20260513b.png) | ![](pic/l_shape/stitch_p5_t20260513b.png) | ![](pic/l_shape/dihedral_t20260513b.png) | ![](pic/l_shape/fillet_t20260513b.png) | ![](pic/l_shape/mapper_t20260513b.png) |

### long_thin_panel

**Inputs:**

| `_main.png` | `_bump.png` | `_hole.png` |
|---|---|---|
| ![](pic/long_thin_panel/long_thin_panel_main_t20260513b.png) | ![](pic/long_thin_panel/long_thin_panel_bump_t20260513b.png) | ![](pic/long_thin_panel/long_thin_panel_hole_t20260513b.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | dihedral | fillet | mapper |
|---|---|---|---|---|---|---|---|
| ![](pic/long_thin_panel/parse_t20260513b.png) | ![](pic/long_thin_panel/topology_t20260513b.png) | ![](pic/long_thin_panel/fold_t20260513b.png) | ![](pic/long_thin_panel/mesh_p4_t20260513b.png) | ![](pic/long_thin_panel/stitch_p5_t20260513b.png) | ![](pic/long_thin_panel/dihedral_t20260513b.png) | ![](pic/long_thin_panel/fillet_t20260513b.png) | ![](pic/long_thin_panel/mapper_t20260513b.png) |

### mismatched_resolution

**Inputs:**

| `_main.png` | `_bump.png` | `_hole.png` |
|---|---|---|
| ![](pic/mismatched_resolution/mismatched_resolution_main_t20260513b.png) | ![](pic/mismatched_resolution/mismatched_resolution_bump_t20260513b.png) | ![](pic/mismatched_resolution/mismatched_resolution_hole_t20260513b.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | dihedral | fillet | mapper |
|---|---|---|---|---|---|---|---|
| ![](pic/mismatched_resolution/parse_t20260513b.png) | ![](pic/mismatched_resolution/topology_t20260513b.png) | ![](pic/mismatched_resolution/fold_t20260513b.png) | ![](pic/mismatched_resolution/mesh_p4_t20260513b.png) | ![](pic/mismatched_resolution/stitch_p5_t20260513b.png) | ![](pic/mismatched_resolution/dihedral_t20260513b.png) | ![](pic/mismatched_resolution/fillet_t20260513b.png) | ![](pic/mismatched_resolution/mapper_t20260513b.png) |

### multi_hole_strip

**Inputs:**

| `_main.png` | `_bump.png` | `_hole.png` |
|---|---|---|
| ![](pic/multi_hole_strip/multi_hole_strip_main_t20260513b.png) | ![](pic/multi_hole_strip/multi_hole_strip_bump_t20260513b.png) | ![](pic/multi_hole_strip/multi_hole_strip_hole_t20260513b.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | dihedral | fillet | mapper |
|---|---|---|---|---|---|---|---|
| ![](pic/multi_hole_strip/parse_t20260513b.png) | ![](pic/multi_hole_strip/topology_t20260513b.png) | ![](pic/multi_hole_strip/fold_t20260513b.png) | ![](pic/multi_hole_strip/mesh_p4_t20260513b.png) | ![](pic/multi_hole_strip/stitch_p5_t20260513b.png) | ![](pic/multi_hole_strip/dihedral_t20260513b.png) | ![](pic/multi_hole_strip/fillet_t20260513b.png) | ![](pic/multi_hole_strip/mapper_t20260513b.png) |

### single_fold

**Inputs:**

| `_main.png` | `_bump.png` | `_hole.png` |
|---|---|---|
| ![](pic/single_fold/single_fold_main_t20260513b.png) | ![](pic/single_fold/single_fold_bump_t20260513b.png) | ![](pic/single_fold/single_fold_hole_t20260513b.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | dihedral | fillet | mapper |
|---|---|---|---|---|---|---|---|
| ![](pic/single_fold/parse_t20260513b.png) | ![](pic/single_fold/topology_t20260513b.png) | ![](pic/single_fold/fold_t20260513b.png) | ![](pic/single_fold/mesh_p4_t20260513b.png) | ![](pic/single_fold/stitch_p5_t20260513b.png) | ![](pic/single_fold/dihedral_t20260513b.png) | ![](pic/single_fold/fillet_t20260513b.png) | ![](pic/single_fold/mapper_t20260513b.png) |

### staircase_3

**Inputs:**

| `_main.png` | `_bump.png` | `_hole.png` |
|---|---|---|
| ![](pic/staircase_3/staircase_3_main_t20260513b.png) | ![](pic/staircase_3/staircase_3_bump_t20260513b.png) | ![](pic/staircase_3/staircase_3_hole_t20260513b.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | dihedral | fillet | mapper |
|---|---|---|---|---|---|---|---|
| ![](pic/staircase_3/parse_t20260513b.png) | ![](pic/staircase_3/topology_t20260513b.png) | ![](pic/staircase_3/fold_t20260513b.png) | ![](pic/staircase_3/mesh_p4_t20260513b.png) | ![](pic/staircase_3/stitch_p5_t20260513b.png) | ![](pic/staircase_3/dihedral_t20260513b.png) | ![](pic/staircase_3/fillet_t20260513b.png) | ![](pic/staircase_3/mapper_t20260513b.png) |

### tiny_panel

**Inputs:**

| `_main.png` | `_bump.png` | `_hole.png` |
|---|---|---|
| ![](pic/tiny_panel/tiny_panel_main_t20260513b.png) | ![](pic/tiny_panel/tiny_panel_bump_t20260513b.png) | ![](pic/tiny_panel/tiny_panel_hole_t20260513b.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | dihedral | fillet | mapper |
|---|---|---|---|---|---|---|---|
| ![](pic/tiny_panel/parse_t20260513b.png) | ![](pic/tiny_panel/topology_t20260513b.png) | ![](pic/tiny_panel/fold_t20260513b.png) | ![](pic/tiny_panel/mesh_p4_t20260513b.png) | ![](pic/tiny_panel/stitch_p5_t20260513b.png) | ![](pic/tiny_panel/dihedral_t20260513b.png) | ![](pic/tiny_panel/fillet_t20260513b.png) | ![](pic/tiny_panel/mapper_t20260513b.png) |

### u_shape

**Inputs:**

| `_main.png` | `_bump.png` | `_hole.png` |
|---|---|---|
| ![](pic/u_shape/u_shape_main_t20260513b.png) | ![](pic/u_shape/u_shape_bump_t20260513b.png) | ![](pic/u_shape/u_shape_hole_t20260513b.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | dihedral | fillet | mapper |
|---|---|---|---|---|---|---|---|
| ![](pic/u_shape/parse_t20260513b.png) | ![](pic/u_shape/topology_t20260513b.png) | ![](pic/u_shape/fold_t20260513b.png) | ![](pic/u_shape/mesh_p4_t20260513b.png) | ![](pic/u_shape/stitch_p5_t20260513b.png) | ![](pic/u_shape/dihedral_t20260513b.png) | ![](pic/u_shape/fillet_t20260513b.png) | ![](pic/u_shape/mapper_t20260513b.png) |

### zigzag_4

**Inputs:**

| `_main.png` | `_bump.png` | `_hole.png` |
|---|---|---|
| ![](pic/zigzag_4/zigzag_4_main_t20260513b.png) | ![](pic/zigzag_4/zigzag_4_bump_t20260513b.png) | ![](pic/zigzag_4/zigzag_4_hole_t20260513b.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | dihedral | fillet | mapper |
|---|---|---|---|---|---|---|---|
| ![](pic/zigzag_4/parse_t20260513b.png) | ![](pic/zigzag_4/topology_t20260513b.png) | ![](pic/zigzag_4/fold_t20260513b.png) | ![](pic/zigzag_4/mesh_p4_t20260513b.png) | ![](pic/zigzag_4/stitch_p5_t20260513b.png) | ![](pic/zigzag_4/dihedral_t20260513b.png) | ![](pic/zigzag_4/fillet_t20260513b.png) | ![](pic/zigzag_4/mapper_t20260513b.png) |

### zigzag_6

**Inputs:**

| `_main.png` | `_bump.png` | `_hole.png` |
|---|---|---|
| ![](pic/zigzag_6/zigzag_6_main_t20260513b.png) | ![](pic/zigzag_6/zigzag_6_bump_t20260513b.png) | ![](pic/zigzag_6/zigzag_6_hole_t20260513b.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | dihedral | fillet | mapper |
|---|---|---|---|---|---|---|---|
| ![](pic/zigzag_6/parse_t20260513b.png) | ![](pic/zigzag_6/topology_t20260513b.png) | ![](pic/zigzag_6/fold_t20260513b.png) | ![](pic/zigzag_6/mesh_p4_t20260513b.png) | ![](pic/zigzag_6/stitch_p5_t20260513b.png) | ![](pic/zigzag_6/dihedral_t20260513b.png) | ![](pic/zigzag_6/fillet_t20260513b.png) | ![](pic/zigzag_6/mapper_t20260513b.png) |
