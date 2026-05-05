# Plan 07 — Mesh Quality Verification Visualizations
Side-by-side comparison of the mesh pipeline before and
after Plan 07 (phases A → E). Pre-plan_07 snapshot was
taken from git commit `34730f9`; post-plan_07 from current
`HEAD`. The pre-plan_07 corpus has 14 cases × 3 res = 42
rows; post-plan_07 has 23 cases × 3 res = 69 rows. The 9
cases added by Phase 0 (`quad_junction`, `closed_box`, and
7 others) appear only in the AFTER snapshot.

## Headline (one-page summary)
<img src="compare/03_one_page_summary.png" width="800"/>

### Headline bars (worst-case 7 metrics)
<img src="compare/01_headline_bars.png" width="800"/>

### Per-case heatmap (6 metrics, before vs after)
<img src="compare/02_metric_heatmap.png" width="800"/>

## Per-metric corpus-wide views
For each metric, two panels: per-case bar chart
(before/after × 3 resolutions), and a corpus-wide
distribution histogram.

### `free_a`
<img src="compare/11_free_a_per_case.png" width="700"/>  <img src="compare/12_free_a_distribution.png" width="460"/>

### `tj_a`
<img src="compare/11_tj_a_per_case.png" width="700"/>  <img src="compare/12_tj_a_distribution.png" width="460"/>

### `nm_a`
<img src="compare/11_nm_a_per_case.png" width="700"/>  <img src="compare/12_nm_a_distribution.png" width="460"/>

### `orphan_a`
<img src="compare/11_orphan_a_per_case.png" width="700"/>  <img src="compare/12_orphan_a_distribution.png" width="460"/>

### `dup_a`
<img src="compare/11_dup_a_per_case.png" width="700"/>  <img src="compare/12_dup_a_distribution.png" width="460"/>

### `inverted_q_a`
<img src="compare/11_inverted_q_a_per_case.png" width="700"/>  <img src="compare/12_inverted_q_a_distribution.png" width="460"/>

### `nonplanar_q_a`
<img src="compare/11_nonplanar_q_a_per_case.png" width="700"/>  <img src="compare/12_nonplanar_q_a_distribution.png" width="460"/>

### `aspect_p95_a`
<img src="compare/11_aspect_p95_a_per_case.png" width="700"/>  <img src="compare/12_aspect_p95_a_distribution.png" width="460"/>

### `edge_cv_a`
<img src="compare/11_edge_cv_a_per_case.png" width="700"/>  <img src="compare/12_edge_cv_a_distribution.png" width="460"/>

### `planarity_p95_a`
<img src="compare/11_planarity_p95_a_per_case.png" width="700"/>  <img src="compare/12_planarity_p95_a_distribution.png" width="460"/>

### `mean_edge_a`
<img src="compare/11_mean_edge_a_per_case.png" width="700"/>  <img src="compare/12_mean_edge_a_distribution.png" width="460"/>

### `min_angle_p05_a`
<img src="compare/11_min_angle_p05_a_per_case.png" width="700"/>  <img src="compare/12_min_angle_p05_a_distribution.png" width="460"/>

## Per-case storyboards
For every (case, resolution) row that appears in BOTH
snapshots, a 4-panel composite showing 3D mesh colored by
aspect ratio (top) and free-edge overlay (bottom), before
vs after.

### `box_unfolding`
**res_2.0** — <img src="compare/per_case/box_unfolding/res_2.0/before_vs_after.png" width="700"/>

**res_4.0** — <img src="compare/per_case/box_unfolding/res_4.0/before_vs_after.png" width="700"/>

**res_8.0** — <img src="compare/per_case/box_unfolding/res_8.0/before_vs_after.png" width="700"/>

### `branching_tree`
**res_2.0** — <img src="compare/per_case/branching_tree/res_2.0/before_vs_after.png" width="700"/>

**res_4.0** — <img src="compare/per_case/branching_tree/res_4.0/before_vs_after.png" width="700"/>

**res_8.0** — <img src="compare/per_case/branching_tree/res_8.0/before_vs_after.png" width="700"/>

### `cross`
**res_2.0** — <img src="compare/per_case/cross/res_2.0/before_vs_after.png" width="700"/>

**res_4.0** — <img src="compare/per_case/cross/res_4.0/before_vs_after.png" width="700"/>

**res_8.0** — <img src="compare/per_case/cross/res_8.0/before_vs_after.png" width="700"/>

### `cross_nonrect`
**res_2.0** — <img src="compare/per_case/cross_nonrect/res_2.0/before_vs_after.png" width="700"/>

**res_4.0** — <img src="compare/per_case/cross_nonrect/res_4.0/before_vs_after.png" width="700"/>

**res_8.0** — <img src="compare/per_case/cross_nonrect/res_8.0/before_vs_after.png" width="700"/>

### `h_shape`
**res_2.0** — <img src="compare/per_case/h_shape/res_2.0/before_vs_after.png" width="700"/>

**res_4.0** — <img src="compare/per_case/h_shape/res_4.0/before_vs_after.png" width="700"/>

**res_8.0** — <img src="compare/per_case/h_shape/res_8.0/before_vs_after.png" width="700"/>

### `l_shape`
**res_2.0** — <img src="compare/per_case/l_shape/res_2.0/before_vs_after.png" width="700"/>

**res_4.0** — <img src="compare/per_case/l_shape/res_4.0/before_vs_after.png" width="700"/>

**res_8.0** — <img src="compare/per_case/l_shape/res_8.0/before_vs_after.png" width="700"/>

### `l_shape_nonrect`
**res_2.0** — <img src="compare/per_case/l_shape_nonrect/res_2.0/before_vs_after.png" width="700"/>

**res_4.0** — <img src="compare/per_case/l_shape_nonrect/res_4.0/before_vs_after.png" width="700"/>

**res_8.0** — <img src="compare/per_case/l_shape_nonrect/res_8.0/before_vs_after.png" width="700"/>

### `staircase`
**res_2.0** — <img src="compare/per_case/staircase/res_2.0/before_vs_after.png" width="700"/>

**res_4.0** — <img src="compare/per_case/staircase/res_4.0/before_vs_after.png" width="700"/>

**res_8.0** — <img src="compare/per_case/staircase/res_8.0/before_vs_after.png" width="700"/>

### `t_shape`
**res_2.0** — <img src="compare/per_case/t_shape/res_2.0/before_vs_after.png" width="700"/>

**res_4.0** — <img src="compare/per_case/t_shape/res_4.0/before_vs_after.png" width="700"/>

**res_8.0** — <img src="compare/per_case/t_shape/res_8.0/before_vs_after.png" width="700"/>

### `t_shape_nonrect`
**res_2.0** — <img src="compare/per_case/t_shape_nonrect/res_2.0/before_vs_after.png" width="700"/>

**res_4.0** — <img src="compare/per_case/t_shape_nonrect/res_4.0/before_vs_after.png" width="700"/>

**res_8.0** — <img src="compare/per_case/t_shape_nonrect/res_8.0/before_vs_after.png" width="700"/>

### `u_shape`
**res_2.0** — <img src="compare/per_case/u_shape/res_2.0/before_vs_after.png" width="700"/>

**res_4.0** — <img src="compare/per_case/u_shape/res_4.0/before_vs_after.png" width="700"/>

**res_8.0** — <img src="compare/per_case/u_shape/res_8.0/before_vs_after.png" width="700"/>

### `wide_t`
**res_2.0** — <img src="compare/per_case/wide_t/res_2.0/before_vs_after.png" width="700"/>

**res_4.0** — <img src="compare/per_case/wide_t/res_4.0/before_vs_after.png" width="700"/>

**res_8.0** — <img src="compare/per_case/wide_t/res_8.0/before_vs_after.png" width="700"/>

### `zigzag_4`
**res_2.0** — <img src="compare/per_case/zigzag_4/res_2.0/before_vs_after.png" width="700"/>

**res_4.0** — <img src="compare/per_case/zigzag_4/res_4.0/before_vs_after.png" width="700"/>

**res_8.0** — <img src="compare/per_case/zigzag_4/res_8.0/before_vs_after.png" width="700"/>

### `zigzag_6`
**res_2.0** — <img src="compare/per_case/zigzag_6/res_2.0/before_vs_after.png" width="700"/>

**res_4.0** — <img src="compare/per_case/zigzag_6/res_4.0/before_vs_after.png" width="700"/>

**res_8.0** — <img src="compare/per_case/zigzag_6/res_8.0/before_vs_after.png" width="700"/>

## Pipeline-stage evolution (`branching_tree`)
<img src="compare/pipeline/branching_tree/after_p3_p4_p5.png" width="900"/>

P3 (Folder) → P4 (Mesher) → P5 (Stitcher) for the
post-plan_07 pipeline. For the pre-plan_07 P5 view,
see `per_case/branching_tree/res_2.0/before_vs_after.png`
(top-left and bottom-left panels — the audit harness
only saved P5 OBJs, not P3/P4 separately).

## Cascade-depth study
<img src="compare/cascade/depth_vs_metrics.png" width="800"/>

## Resolution-sensitivity study
<img src="compare/resolution/aspect_p95_a_per_res.png" width="700"/>

<img src="compare/resolution/free_a_per_res.png" width="700"/>

<img src="compare/resolution/inverted_q_a_per_res.png" width="700"/>

## Topology zoom-ins
### `junction_box_unfolding`
<img src="compare/topology/junction_box_unfolding.png" width="700"/>

### `junction_cross`
<img src="compare/topology/junction_cross.png" width="700"/>

## Numerical-hygiene distributions
<img src="compare/numerical/aspect_distribution.png" width="700"/>

<img src="compare/numerical/planarity_distribution.png" width="700"/>

<img src="compare/numerical/jacobian_distribution.png" width="700"/>

## Test-suite growth
<img src="compare/tests/test_count_growth.png" width="800"/>

## Source data
- `before/` — pre-plan_07 audit artifacts (14 cases × 3 res).
- `after/`  — post-plan_07 audit artifacts (23 cases × 3 res).
- `data/compare_summary.csv` — joined wide-form metrics.
- `data/delta_summary.csv` — long-form per-row deltas.
- `data/agg_summary.csv` — corpus-aggregate per metric.
