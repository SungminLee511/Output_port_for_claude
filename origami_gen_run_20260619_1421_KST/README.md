# Origami_Gen v2.0 — Full Corpus Run

**Timestamp**: 2026-06-19 14:21 KST (server UTC 05:21).
**Pipeline source**: [voltwin-dev/Origami_Gen@e565817](https://github.com/voltwin-dev/Origami_Gen/commit/e565817)
— this commit fixes two user-reported bugs:

1. **Reverse fillets at valley folds.** P8 placed the cylinder axis at
   `+r*(n_a + n_b)`, which only lands on the concave side for mountain
   folds. For valley folds the pose-derived sum lands on the
   convex/sharp side and the fillet curves backwards. Fix: detect
   mountain/valley geometrically per cylinder and apply a sign flip
   to `axis_offset`, `u`, `v` in both scalar and batch mappers.
2. **Bumps + holes missing from exported .obj/.vtk/.vtp.** `audit.py`
   exported the post-P8 fillet mesh instead of the post-P10 bump+cut
   mesh, so the storyboard PNGs showed bumps/holes but downstream
   viewers (ParaView, PyVista) loaded only the post-fillet quads+tris.
   Fix: hook `apply_bump_and_cut` in `audit.py` between
   `propagate_mapping` and the writers.

## Contents

```
mesh_output/<case>/res_{2.0,4.0,8.0}/
  mesh.obj                 post-P10 bumped + cut mesh (was post-P8 before fix)
  mesh.vtk                 legacy VTK ASCII (ParaView)
  mesh.vtp                 VTK XML PolyData (ParaView, PyVista)
  metrics.json             gate vector + counts + wall time
  log.txt                  per-case run log

verification/<case>/
  parse.png                P1: panels + fold lines
  topology.png             P2: panel-tree graph
  fold.png                 P3: 3D pose corners
  mesh_p4.png              P4: per-panel quad mesh
  stitch_p5.png            P5: post-stitch overlay
  mapper_p6.png            P6: yellow/green/purple element labels (flat)
  dihedral_p7.png          P7: 90° fold-seam edges
  fillet_p8.png            P8: cylinder/sphere fillet patches
  mapper_p9.png            P9: propagated labels on fillet tris
  bump_p10.png             P10: post-bump-cut shaded geometry
  composite.png            all phases as one strip (use this to compare cases)
  <case>_main.png          P10 main view (composite supplement)
  <case>_bump.png          P10 bump-only overlay
  <case>_hole.png          P10 cut-only overlay
  metrics.json             per-phase pass/fail + wall time
  verdict.txt              plain-language summary

verification/SUMMARY.md    full corpus table + headline link
verification/headline.png  gate-pass matrix mosaic
```

## Cases (42)

`accessory_l_bracket`, `box_unfolding`, `bracket_v01..v20`,
`cascade_5_deep`, `channel_bracket`, `closed_box`, `corner_3panel`,
`cross`, `cross_fold_demo`, `hd_mobis_bracket`, `l_shape`,
`long_thin_panel`, `mismatched_resolution`, `multi_hole_strip`,
`simple_l_bracket`, `single_fold`, `staircase_3`, `tab_plate_4`,
`tiny_panel`, `u_bracket`, `u_shape`, `zigzag_4`, `zigzag_6`.

## How to inspect

* **Validate Bug 1 fix (reverse fillets)** — open
  `verification/<case>/composite.png` for any case containing valley
  folds (e.g. `bracket_v01..v20`, `cascade_5_deep`, `simple_l_bracket`).
  The post-P8 fillet patches should curve into the concave side of the
  bend, not the convex/sharp side. Compare against the previous
  `origami_gen_run_20260612/` run to see the difference.
* **Validate Bug 2 fix (bumps + holes in geometry)** — load
  `mesh_output/<case>/res_2.0/mesh.vtp` into ParaView. The displaced
  yellow/green bumps and the carved purple holes should be present in
  the geometry itself, not just in the storyboard PNGs.

## Run command

```bash
PYTHONHASHSEED=0 conda run -n SML_env python scripts/audit.py \
  --full --resolutions 2.0,4.0,8.0 --workers 8 \
  --output-dir <run_dir>/mesh_output

PYTHONHASHSEED=0 conda run -n SML_env python scripts/verify_visualize.py \
  --resolution 2.0 --workers 8 --save-pool 0 \
  --output-dir <run_dir>/verification
```

Audit step: ~190 s wall-time.
Verify_visualize: ~17 min wall-time at workers=8.
