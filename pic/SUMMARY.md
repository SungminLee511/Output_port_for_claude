# Origami_Gen v2.0 — Per-Case Verification Report

**Pipeline:** P1 parse → P2 topology → P3 fold → P4 mesh → P5 stitch → P6 mapper → P7 bump+cut → P8 dihedral
**Cases:** 16    **Phases reached `done`:** 15/16
**Simple cases passing all gates:** 16/16
**Junction-case (WIP) total:** 0 (soft-gate acceptance only)

![gate matrix](headline.png)

## Per-phase pipeline (all cases on one figure)

### P1 parse

![P1_parse](phases/P1_parse.png)

### P2 topology

![P2_topology](phases/P2_topology.png)

### P3 fold

![P3_fold](phases/P3_fold.png)

### P4 mesh

![P4_mesh](phases/P4_mesh.png)

### P5 stitch

![P5_stitch](phases/P5_stitch.png)

### P6 mapper

![P6_mapper](phases/P6_mapper.png)

### P7 dihedral

![P7_dihedral](phases/P7_dihedral.png)

### P8 fillet

![P8_fillet](phases/P8_fillet.png)

### P9 mapper

![P9_mapper](phases/P9_mapper.png)

### P10 bumpcut

![P10_bumpcut](phases/P10_bumpcut.png)

## Per-case results

| Case | Class | Phase | Verts | Quads | Tris | nm | orph | comp | inv | sliver | asp_p95 | plan_p95 | edge_cv | Gates |
|------|-------|-------|-------|-------|------|----|------|------|-----|--------|---------|----------|---------|-------|
| box_unfolding | simple | done | 18121 | 18000 | 0 | 0 | 0 | 1 | 0 | 0 | 1.00 | 0.00e+00 | 0.00 | 10/10 |
| cascade_5_deep | simple | done | 8241 | 8000 | 0 | 0 | 0 | 1 | 0 | 0 | 1.00 | 0.00e+00 | 0.00 | 10/10 |
| closed_box | simple | done | 15002 | 15000 | 0 | 0 | 0 | 1 | 0 | 0 | 1.00 | 0.00e+00 | 0.00 | 10/10 |
| corner_3panel | simple | done | 14911 | 14700 | 0 | 0 | 0 | 1 | 0 | 0 | 1.00 | 0.00e+00 | 0.00 | 10/10 |
| cross | simple | done | 18121 | 18000 | 0 | 0 | 0 | 1 | 0 | 0 | 1.00 | 0.00e+00 | 0.00 | 10/10 |
| cross_fold_demo | simple | P10.bumpcut | 14981 | 14700 | 0 | 0 | 0 | 1 | 0 | 0 | 1.00 | 0.00e+00 | 0.00 | 10/10 |
| l_shape | simple | done | 24797 | 24480 | 0 | 0 | 0 | 1 | 0 | 0 | 1.00 | 0.00e+00 | 0.00 | 10/10 |
| long_thin_panel | simple | done | 15471 | 15200 | 0 | 0 | 0 | 1 | 0 | 0 | 1.00 | 0.00e+00 | 0.00 | 10/10 |
| mismatched_resolution | simple | done | 16797 | 16480 | 0 | 0 | 0 | 1 | 0 | 0 | 1.00 | 0.00e+00 | 0.00 | 10/10 |
| multi_hole_strip | simple | done | 14981 | 14700 | 0 | 0 | 0 | 1 | 0 | 0 | 1.00 | 0.00e+00 | 0.00 | 10/10 |
| single_fold | simple | done | 15617 | 15360 | 0 | 0 | 0 | 1 | 0 | 0 | 1.00 | 0.00e+00 | 0.00 | 10/10 |
| staircase_3 | simple | done | 11041 | 10800 | 0 | 0 | 0 | 1 | 0 | 0 | 1.00 | 0.00e+00 | 0.00 | 10/10 |
| tiny_panel | simple | done | 4647 | 4496 | 0 | 0 | 0 | 1 | 0 | 0 | 1.00 | 0.00e+00 | 0.00 | 10/10 |
| u_shape | simple | done | 30227 | 29880 | 0 | 0 | 0 | 1 | 0 | 0 | 1.00 | 0.00e+00 | 0.00 | 10/10 |
| zigzag_4 | simple | done | 10200 | 10000 | 0 | 0 | 0 | 1 | 0 | 0 | 1.00 | 0.00e+00 | 0.00 | 10/10 |
| zigzag_6 | simple | done | 8029 | 7776 | 0 | 0 | 0 | 1 | 0 | 0 | 1.00 | 0.00e+00 | 0.00 | 10/10 |

## Per-case storyboards

### box_unfolding

![box_unfolding](box_unfolding/composite.png)

**All measured gates pass.**

### cascade_5_deep

![cascade_5_deep](cascade_5_deep/composite.png)

**All measured gates pass.**

### closed_box

![closed_box](closed_box/composite.png)

**All measured gates pass.**

### corner_3panel

![corner_3panel](corner_3panel/composite.png)

**All measured gates pass.**

### cross

![cross](cross/composite.png)

**All measured gates pass.**

### cross_fold_demo

![cross_fold_demo](cross_fold_demo/composite.png)

**Error:** `PYTHON_EXC: IndexError: index 27456 is out of bounds for axis 0 with size 27456`
**All measured gates pass.**

### l_shape

![l_shape](l_shape/composite.png)

**All measured gates pass.**

### long_thin_panel

![long_thin_panel](long_thin_panel/composite.png)

**All measured gates pass.**

### mismatched_resolution

![mismatched_resolution](mismatched_resolution/composite.png)

**All measured gates pass.**

### multi_hole_strip

![multi_hole_strip](multi_hole_strip/composite.png)

**All measured gates pass.**

### single_fold

![single_fold](single_fold/composite.png)

**All measured gates pass.**

### staircase_3

![staircase_3](staircase_3/composite.png)

**All measured gates pass.**

### tiny_panel

![tiny_panel](tiny_panel/composite.png)

**All measured gates pass.**

### u_shape

![u_shape](u_shape/composite.png)

**All measured gates pass.**

### zigzag_4

![zigzag_4](zigzag_4/composite.png)

**All measured gates pass.**

### zigzag_6

![zigzag_6](zigzag_6/composite.png)

**All measured gates pass.**
