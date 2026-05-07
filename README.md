# Output Port

Files Claude moved here are visible on GitHub.

## Step 1 — Read mesh and visualize

Loaded all 40 HD Mobis H5 files via the I0 H5 ingest (solver-ID
remap), rendered each shell with matplotlib's `Poly3DCollection`
(Lambert shading from a single light, gray colormap, light edge
lines).  Per-render time ~9 s × 40 = ~6 min serial.

Geometry repeats within a family (8 geometry families × 5 load-case
variants = 40 files), so the 5 variants of each family render
identically.  The gallery below shows the canonical first variant of
each family; all 40 PNGs are in `step1_visualize/`.

### Family gallery — one canonical variant per family

| family 1 (`_410_*`) | family 2 (`_420_*`) | family 3 (`_430_*`) | family 4 (`_440_*`) |
|---|---|---|---|
| ![f1](step1_visualize/sol103_01_410_08_mesh.png) | ![f2](step1_visualize/sol103_06_420_08_mesh.png) | ![f3](step1_visualize/sol103_11_430_08_mesh.png) | ![f4](step1_visualize/sol103_16_440_08_mesh.png) |

| family 5 (`_450_*`) | family 6 (`_461_*`) | family 7 (`_462_*`) | family 8 (`_463_*`) |
|---|---|---|---|
| ![f5](step1_visualize/sol103_21_450_08_mesh.png) | ![f6](step1_visualize/sol103_26_461_08_mesh.png) | ![f7](step1_visualize/sol103_31_462_08_mesh.png) | ![f8](step1_visualize/sol103_36_463_08_mesh.png) |

### All 40 PNGs

`step1_visualize/sol103_<NN>_<YYY>_<ZZ>_mesh.png` — one per H5 file.

## Step 2 — Main-plane segmentation

Vendored the SML branch of `MOBIS_GEN`'s `region_growing_gpu`
(spherical k-means seeded BFS region growing) into the inverse
package and ran it on all 40 HD Mobis H5 files.

Algorithm: face normals → spherical K-means at fixed K=30 →
adjacency-based BFS from each cluster seed using the **fixed
cluster normal** as target (prevents drift) → fallback BFS with
running mean for any unlabeled faces → tiny-region merge → contiguous
re-index.  Identical math to the SML source — only cosmetic edits
(type hints, docstrings).  Auto-K was bypassed because every file
hit the K=30 cap anyway, wasting ~30× compute.

Angle threshold = **15°**.  (45° was tried and discarded.)

Output naming: `step2_mainplanes/<stem>_planes_15deg.png`.

### Coverage
26 of 40 files complete (52 PNGs).  Families 410 / 420 / 430 / 440
/ 450 fully done at ~30 s per file.  Family 461 (file 26 only) took
~32 min for both angles — region-grow BFS-with-running-mean fallback
explodes on this family.  Killed at user request before 462 / 463.

### Family gallery (one canonical variant per family)

| family 1 (`_410_*`) | family 2 (`_420_*`) | family 3 (`_430_*`) | family 4 (`_440_*`) |
|---|---|---|---|
| ![f1](step2_mainplanes/sol103_01_410_08_planes_15deg.png) | ![f2](step2_mainplanes/sol103_06_420_08_planes_15deg.png) | ![f3](step2_mainplanes/sol103_11_430_08_planes_15deg.png) | ![f4](step2_mainplanes/sol103_16_440_08_planes_15deg.png) |

| family 5 (`_450_*`) | family 7 (`_462_*`) | family 8 (`_463_*`) |
|---|---|---|
| ![f5](step2_mainplanes/sol103_21_450_08_planes_15deg.png) | (462 not run) | (463 not run) |

Family 461 excluded going forward (per user direction).

### All PNGs

`step2_mainplanes/sol103_<NN>_<YYY>_<ZZ>_planes_15deg.png` — files
01–25 + 26 (461) covered.

## Step 3 — Phase 2: main vs bump, flat vs bend (with edge-line demotion)

After phase-1 plane segmentation, each region is classified as
**main** or **bump**.  Bumps are grouped into connected blobs, and
each blob is marked **flat** (sits on one main panel) or **bend**
(bridges two diverging main panels).

Pipeline (vendored from MOBIS_GEN SML, RBE2 logic stripped):

1. `find_boundary_loops` — all boundary edges chained into closed loops.
2. `pick_outer_loop` — outer = largest 3D perimeter (replaces MOBIS
   XY-shoelace; HD Mobis isn't XY-aligned).
3. `classify_main_bump` — region with ≥1 outer-loop node = main; else bump.
4. `reclassify_main_with_parallel_outer_edges` — **new**: a region
   currently classified as main is *demoted to bump* iff:
     - its outer-loop edges form **a single contiguous chain** (multiple
       disjoint chains → keep main, since they bridge far parts of the
       boundary and indicate a real panel), AND
     - all those edges are parallel within **15°**.
   Captures the case where a small feature just clips the panel edge
   along one straight stretch.
5. `build_region_adjacency` — region graph from triangle adjacency.
6. `group_bump_blobs` — connected components in bump-only sub-graph;
   drop blobs with fewer than 3 regions.
7. `classify_blob_flat_or_bend` — adjacent main-region face normals
   coplanar within 30° → flat; diverging → bend.

Color code in PNGs:

| Color | Meaning |
|---|---|
| **HSV-swept hues** (each main region distinct) | main region |
| **Gold** | flat bump blob |
| **Crimson** | bend bump blob |
| **Light yellow** | small / ungrouped bump regions (below `min_blob_size=3`) |
| **Green wireframe** | outer boundary loop |
| **Red wireframe** | hole loops (non-outer boundaries) |

Coverage: **35 / 40 files** (family 461 excluded per user direction).
Per-file ~40 s on CUDA.

Per-case mesh + classification cached as `.npz` in
`data_port/inverse_cache/phase2/<case>.npz` (verts, triangles, region
labels, all loops, outer index, main/bump/demoted IDs, blobs, blob
types) so downstream phases don't have to re-segment.

Stats summary across families (main / bump / demoted / blobs):

| family | main | bump | demoted | blobs |
|---|---|---|---|---|
| 410 | 6–7 | 242–248 | 24–27 | 7 |
| 420 | 10 | 261–269 | 37–40 | 9 |
| 430 | 10–12 | 264–271 | 34–38 | 9 |
| 440 | 9–10 | 256–264 | 31–37 | 9 |
| 450 | 7–10 | 142–148 | 5–6 | 5 |
| 462 | 11–14 | 146–148 | 13–15 | 6 |
| 463 | 10–14 | 135–142 | 7–10 | 5 |

### Family gallery (one canonical variant per family)

| family 1 (`_410_*`) | family 2 (`_420_*`) | family 3 (`_430_*`) | family 4 (`_440_*`) |
|---|---|---|---|
| ![p2-f1](step3_classify_blobs/sol103_01_410_08_blobs.png) | ![p2-f2](step3_classify_blobs/sol103_06_420_08_blobs.png) | ![p2-f3](step3_classify_blobs/sol103_11_430_08_blobs.png) | ![p2-f4](step3_classify_blobs/sol103_16_440_08_blobs.png) |

| family 5 (`_450_*`) | family 7 (`_462_*`) | family 8 (`_463_*`) |
|---|---|---|
| ![p2-f5](step3_classify_blobs/sol103_21_450_08_blobs.png) | ![p2-f7](step3_classify_blobs/sol103_31_462_08_blobs.png) | ![p2-f8](step3_classify_blobs/sol103_36_463_08_blobs.png) |

Family 461 excluded.

### All PNGs

`step3_classify_blobs/sol103_<NN>_<YYY>_<ZZ>_blobs.png` — files
01–25 + 31–40 (35 total).

### `tmp/`
Earlier deliverables, kept for reference.
