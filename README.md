# Origami-Gemini-Gen — Full Pipeline Results
Updated: 2026-04-24 14:03 KST

ALL 11 CASES PASSED — Phase 0 through Phase 7, zero degenerate elements.

## Features Tested
- Non-rectangular blobs (circle, ellipse, polygon, organic)
- Clean hole boundary snapping
- Heightmap z-displacement (curved planes)
- Full pipeline regression (stitch, bump, cut, export)

## Overview — Flat vs Heightmap (all cases)
![Overview](all_phases_overview.png)

## Per-Case Detail

### l_shape
![l_shape](detail_l_shape.png)

### t_shape
![t_shape](detail_t_shape.png)

### cross
![cross](detail_cross.png)

### u_shape
![u_shape](detail_u_shape.png)

### box_unfolding
![box_unfolding](detail_box_unfolding.png)

### branching_tree
![branching_tree](detail_branching_tree.png)

### h_shape
![h_shape](detail_h_shape.png)

### staircase
![staircase](detail_staircase.png)

### l_shape_nonrect
![l_shape_nonrect](detail_l_shape_nonrect.png)

### cross_nonrect
![cross_nonrect](detail_cross_nonrect.png)

### t_shape_nonrect
![t_shape_nonrect](detail_t_shape_nonrect.png)

## Non-Rectangular Blobs Close-Up
![nonrect](nonrect_blobs_detail.png)

## Summary Table

| Case | Status | Degen | Elems | HM verts |
|------|--------|-------|-------|----------|
| l_shape | PASS | 0 | 3838 | 3788 |
| t_shape | PASS | 0 | 7659 | 6104 |
| cross | PASS | 0 | 26148 | 25765 |
| u_shape | PASS | 0 | 6981 | 178 |
| box_unfolding | PASS | 0 | 17352 | 15847 |
| branching_tree | PASS | 0 | 27682 | 21540 |
| h_shape | PASS | 0 | 15223 | 15203 |
| staircase | PASS | 0 | 21528 | 21507 |
| l_shape_nonrect | PASS | 0 | 5709 | 159 |
| cross_nonrect | PASS | 0 | 20295 | 18402 |
| t_shape_nonrect | PASS | 0 | 9520 | 7505 |
