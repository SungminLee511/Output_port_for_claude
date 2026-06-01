# Origami_Gen v2.0 — Per-Case Verification Report

**Pipeline:** P1 parse → P2 topology → P3 fold → P4 mesh → P5 stitch → P6 mapper → P7 bump+cut → P8 dihedral
**Cases:** 5    **Phases reached `done`:** 5/5
**Simple cases passing all gates:** 5/5
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
| hd_mobis_bracket | simple | done | 177415 | 176400 | 0 | 0 | 0 | 1 | 0 | 0 | 1.00 | 0.00e+00 | 0.00 | 10/10 |
| u_bracket | simple | done | 97977 | 97320 | 0 | 0 | 0 | 1 | 0 | 0 | 1.00 | 0.00e+00 | 0.00 | 10/10 |
| u_shape | simple | done | 30227 | 29880 | 0 | 0 | 0 | 1 | 0 | 0 | 1.00 | 0.00e+00 | 0.00 | 10/10 |
| zigzag_4 | simple | done | 10200 | 10000 | 0 | 0 | 0 | 1 | 0 | 0 | 1.00 | 0.00e+00 | 0.00 | 10/10 |
| zigzag_6 | simple | done | 8029 | 7776 | 0 | 0 | 0 | 1 | 0 | 0 | 1.00 | 0.00e+00 | 0.00 | 10/10 |

## Per-case storyboards

### hd_mobis_bracket

![hd_mobis_bracket](hd_mobis_bracket/composite.png)

**All measured gates pass.**

### u_bracket

![u_bracket](u_bracket/composite.png)

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
