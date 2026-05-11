# Origami_Gen v2.0 — Per-Case Verification Report

**Pipeline:** P1 parse → P2 topology → P3 fold → P4 mesh → P5 stitch → P6 mapper → P7 bump+cut → P8 dihedral
**Cases:** 16    **Phases reached `done`:** 16/16
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

### P7 bump cut

![P7_bump_cut](phases/P7_bump_cut.png)

### P8 dihedral

![P8_dihedral](phases/P8_dihedral.png)

## Per-case results

| Case | Class | Phase | Verts | Quads | Tris | nm | orph | comp | inv | sliver | asp_p95 | plan_p95 | edge_cv | Gates |
|------|-------|-------|-------|-------|------|----|------|------|-----|--------|---------|----------|---------|-------|
| box_unfolding | simple | done | 72241 | 72000 | 0 | 0 | 0 | 1 | 0 | 0 | 1.00 | 0.00e+00 | 0.00 | 10/10 |
| cascade_5_deep | simple | done | 32481 | 32000 | 0 | 0 | 0 | 1 | 0 | 0 | 1.00 | 0.00e+00 | 0.00 | 10/10 |
| closed_box | simple | done | 60002 | 60000 | 0 | 0 | 0 | 1 | 0 | 0 | 1.00 | 0.00e+00 | 0.00 | 10/10 |
| corner_3panel | simple | done | 59221 | 58800 | 0 | 0 | 0 | 1 | 0 | 0 | 1.00 | 0.00e+00 | 0.00 | 10/10 |
| cross | simple | done | 72241 | 72000 | 0 | 0 | 0 | 1 | 0 | 0 | 1.00 | 0.00e+00 | 0.00 | 10/10 |
| cross_fold_demo | simple | done | 59361 | 58800 | 0 | 0 | 0 | 1 | 0 | 0 | 1.00 | 0.00e+00 | 0.00 | 10/10 |
| l_shape | simple | done | 98553 | 97920 | 0 | 0 | 0 | 1 | 0 | 0 | 1.00 | 0.00e+00 | 0.00 | 10/10 |
| long_thin_panel | simple | done | 61341 | 60800 | 0 | 0 | 0 | 1 | 0 | 0 | 1.00 | 0.00e+00 | 0.00 | 10/10 |
| mismatched_resolution | simple | done | 66553 | 65920 | 0 | 0 | 0 | 1 | 0 | 0 | 1.00 | 0.00e+00 | 0.00 | 10/10 |
| multi_hole_strip | simple | done | 59361 | 58800 | 0 | 0 | 0 | 1 | 0 | 0 | 1.00 | 0.00e+00 | 0.00 | 10/10 |
| single_fold | simple | done | 61953 | 61440 | 0 | 0 | 0 | 1 | 0 | 0 | 1.00 | 0.00e+00 | 0.00 | 10/10 |
| staircase_3 | simple | done | 43681 | 43200 | 0 | 0 | 0 | 1 | 0 | 0 | 1.00 | 0.00e+00 | 0.00 | 10/10 |
| tiny_panel | simple | done | 18285 | 17984 | 0 | 0 | 0 | 1 | 0 | 0 | 1.00 | 0.00e+00 | 0.00 | 10/10 |
| u_shape | simple | done | 120213 | 119520 | 0 | 0 | 0 | 1 | 0 | 0 | 1.00 | 0.00e+00 | 0.00 | 10/10 |
| zigzag_4 | simple | done | 40400 | 40000 | 0 | 0 | 0 | 1 | 0 | 0 | 1.00 | 0.00e+00 | 0.00 | 10/10 |
| zigzag_6 | simple | done | 31609 | 31104 | 0 | 0 | 0 | 1 | 0 | 0 | 1.00 | 0.00e+00 | 0.00 | 10/10 |

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
