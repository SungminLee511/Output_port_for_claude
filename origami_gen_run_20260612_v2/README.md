# Origami_Gen v2.0 — Full Corpus Run v2 (2026-06-12, post-fillet-orientation-fix)

End-to-end pipeline run over all 42 corpus cases AFTER fixing two
P8 fillet bugs that caused fillet patches to face the wrong
direction in cap-stack brackets.

## What changed since `origami_gen_run_20260612` (prior run)

Two `src/origami_gen/fillet/` bugs identified and fixed:

### Fix #1 — `_panel_outward_normals` now uses pose, not mesh winding
**File**: `src/origami_gen/fillet/primitives.py`

The old code derived each panel's "outward" normal from the
Newell-formula normal of the FIRST face in stitch order
(`stacked[0]`), then sign-locked the rest of that panel's faces
to it. Whenever a single P5-emitted face had inverted winding AND
landed at slot 0, the whole panel's outward direction silently
flipped. Downstream, `axis_offset = r·(n_a + n_b)` then placed the
cylinder fillet on the concave side of the bend.

Replaced with the authoritative pose-derived normal:
`pose.transform[:3,:3] @ (0, 0, 1)` — exact ±x̂/±ŷ/±ẑ in the
24-element integer cube-rotation group (§3.0a), independent of
mesh face order.

### Fix #2 — `_assign_owners_batch` uses segment distance + panel mask
**File**: `src/origami_gen/fillet/grow.py`

The old code routed each deleted face to the cylinder with the
smallest perpendicular distance to the **infinite axis line**. In
cap-stack brackets (`hd_mobis_bracket`, `accessory_l_bracket`,
`bracket_v*`) where B↔C, C↔D, D↔E folds are mutually parallel, the
perp-distance metric tied between cylinders. `np.argmin` then
picked the wrong cylinder. The mis-routed face also failed the
`panel_id ∈ {panel_a, panel_b}` check inside `_map_to_cylinder`,
hit a silent `theta=π/4` fallback, and got displaced by the
**wrong cylinder's axis offset** — visible as a fillet patch
oriented toward the wrong bracket corner.

Two changes:
1. **Segment distance**: clamp `t` to `[0, L]` before computing
   distance so a face past the end of a fold polyline can't win
   against a genuinely-incident parallel fold.
2. **Panel-id mask**: a face on panel `P` is only eligible for
   cylinders whose `(panel_a, panel_b)` pair contains `P`
   (analogous mask for spheres). With a small graceful fallback
   (logged warning) for very-coarse-resolution edge cases.

Plus new error code `E_FILLET_OWNER_UNASSIGNED` /
`E_FILLET_OWNER_PANEL_MISMATCH` in `errors.py` so any future
regression surfaces loudly per §4.1.

## New `write_vtp` exporter

`src/origami_gen/export/vtp.py` — XML PolyData (ParaView /
PyVista). Wired into `scripts/audit.py` so every (case × res)
row now writes `mesh.obj` + `mesh.vtk` + **`mesh.vtp`**.

## Layout

```
origami_gen_run_20260612_v2/
├── mesh_output/<case>/res_{2.0,4.0,8.0}/
│   ├── mesh.vtk          # legacy VTK ASCII (UnstructuredGrid)
│   ├── mesh.vtp          # XML PolyData (NEW)
│   ├── metrics.json      # all §3 gates + diagnostics
│   └── log.txt
└── verification/
    ├── SUMMARY.md        # per-case gate table + headline
    ├── headline.png      # gate-pass matrix
    └── <case>/
        ├── <case>_main.png   # source PNG
        ├── <case>_bump.png
        ├── <case>_hole.png
        ├── parse.png         # P1
        ├── topology.png      # P2
        ├── fold.png          # P3
        ├── mesh_p4.png       # P4
        ├── stitch_p5.png     # P5
        ├── mapper_p6.png     # P6 (per-element labels)
        ├── dihedral_p7.png   # P7 (~90° fold seams)
        ├── fillet_p8.png     # P8 (NOW WITH CORRECT ORIENTATION)
        ├── mapper_p9.png     # P9 (propagated labels on fillet)
        ├── bump_p10.png      # P10 (bump + cut)
        ├── composite.png     # all phases as one row
        ├── metrics.json
        └── verdict.txt
```

OBJ files dropped from this push to keep total repo growth under
1 GB; meshes are equally readable via `mesh.vtk` (any ParaView /
meshio / VTK reader) and `mesh.vtp` (preferred for PyVista).

## Run stats

| | |
|---|---|
| Cases | 42 |
| Resolutions | 2.0, 4.0, 8.0 px/cell |
| Rows (case × res) | 126 |
| Audit errors | **0 / 126** (was 1/126 pre-fallback) |
| Audit wall-time | 164 s |
| Verify wall-time | 1335 s (22 min, all 42 cases at res 2.0) |
| Per-resolution PNGs | 269 total |

## How to view a result

```python
import pyvista as pv
m = pv.read("mesh_output/hd_mobis_bracket/res_2.0/mesh.vtp")
m.plot(show_edges=True, color="lightsteelblue")
```

Or in ParaView: File → Open → `mesh.vtk` or `mesh.vtp`.

The orientation-fix payoff is clearest on the cap-stack brackets
(`hd_mobis_bracket`, `accessory_l_bracket`, every `bracket_v*`):
inspect the P8 fillet PNG / VTP and the fillet patches on the
B↔C / C↔D / D↔E parallel folds now consistently round the
**outside** of each bend rather than leaking toward the wrong
corner.
