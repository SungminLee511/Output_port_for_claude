# Origami-Gemini-Gen — Full Pipeline Results
Updated: 2026-04-24 14:09 KST

ALL 11 CASES PASSED — Phase 0 through Phase 7, zero degenerate elements.
Heightmap DEACTIVATED pending redesign.

## Features Tested
- Non-rectangular blobs (circle, ellipse, polygon, organic)
- Clean hole boundary snapping
- Full pipeline regression (stitch, bump, cut, export)

## Overview — All Cases
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

| Case | Status | Degen | Elems | MinArea |
|------|--------|-------|-------|---------|
| l_shape | PASS | 0 | 3838 | 0.002004 |
| t_shape | PASS | 0 | 7659 | 0.010469 |
| cross | PASS | 0 | 26148 | 0.242367 |
| u_shape | PASS | 0 | 6981 | 0.041435 |
| box_unfolding | PASS | 0 | 17352 | 0.000434 |
| branching_tree | PASS | 0 | 27682 | 0.000143 |
| h_shape | PASS | 0 | 15223 | 0.004020 |
| staircase | PASS | 0 | 21528 | 0.001642 |
| l_shape_nonrect | PASS | 0 | 5709 | 0.009836 |
| cross_nonrect | PASS | 0 | 20295 | 0.000343 |
| t_shape_nonrect | PASS | 0 | 9520 | 0.028825 |
