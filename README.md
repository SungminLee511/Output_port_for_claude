# Output Port — Origami_Gen v2.0 Pipeline Gallery

Per-phase per-case pipeline pictures from Origami_Gen v2.0
verification runs. 16 cases, all 10/10 §3 gates passing.

Source repo: https://github.com/voltwin-dev/Origami_Gen

![headline gate matrix](Origami_Gen_p6_mapper_verification/headline.png)

## Pipeline phases

| Phase | Module | Input → Output |
|---|---|---|
| **P1 Parse** | `parser/` | PNGs → `ParseResult` (panels + folds + masks) |
| **P2 Topology** | `topology/` | `ParseResult` → `FoldTree` + 2D junctions |
| **P3 Fold** | `folder/` | `FoldTree` → `FoldResult` (integer SO(3) poses) |
| **P4 Mesh** | `mesher/` | + `FoldResult` → `MeshResult` (anchor-aware grid) |
| **P5 Stitch** | `stitcher/` | `MeshResult` → `StitchResult` (post-stitch baseline) |
| **P6 Mapper** | `mapper/` | + masks → `MapResult` (yellow / green / purple element labels — pure tagging, no mesh mutation) |
| **P7 Bump+Cut** | `bumper/` | + `MapResult` → `BumpResult` |
| P8 Export | `export/` | files (no picture) |

P6 was originally the "Heightmap" phase. v2.0 dropped viridis
heightmap input as out of scope and repurposed P6 as the **Mapper**:
the prelim step that tags every post-stitch quad / tri with the
yellow / green / purple overlay channels P7 will consume. P7 no
longer re-derives its labels from masks; the mapping is now an
inspectable artifact.

## Per-phase mosaics (all cases on one figure)

### P1 — Parse
![P1_parse](Origami_Gen_p6_mapper_verification/phases/P1_parse.png)

### P2 — Topology
![P2_topology](Origami_Gen_p6_mapper_verification/phases/P2_topology.png)

### P3 — Fold
![P3_fold](Origami_Gen_p6_mapper_verification/phases/P3_fold.png)

### P4 — Mesh
![P4_mesh](Origami_Gen_p6_mapper_verification/phases/P4_mesh.png)

### P5 — Stitch
![P5_stitch](Origami_Gen_p6_mapper_verification/phases/P5_stitch.png)

### P6 — Mapper
![P6_mapper](Origami_Gen_p6_mapper_verification/phases/P6_mapper.png)

### P7 — Bump + Cut
![P7_bump_cut](Origami_Gen_p6_mapper_verification/phases/P7_bump_cut.png)

## Per-phase performance (16-case corpus)

Per-case wall-time + peak RSS measured by `scripts/perf_measure.py`
on `SML_env` (CPU — numpy / scipy.sparse.csgraph vectorization;
GPU explored, see "GPU?" below). Render pass (matplotlib)
excluded; numbers reflect the pure pipeline P1..P7.

Two improvements landed in this revision:
- **Fix 1**: optional **`mesh_resolution = 1.0`** (was 2.0 px/cell)
  — 4× finer mesh per panel, smoother bump ramp, sharper purple-cut
  contour snap.
- **Fix 3**: **`RENDER_SCALE = 2`** in `corpus/_primitives.py` — every
  generated PNG is rendered at 2× pixel density (panel positions
  scaled, fold thickness held at 4 px so parser morphology budgets
  stay valid). 4× the pixel real-estate per panel, 4× more cells at
  the same `mesh_resolution`.

### Default audit (Fix 3 active, `resolution = 2.0` px/cell, 237 k quads)

| Phase | Aggregate (ms) | Notes |
|---|---|---|
| P1 Parse | 537 | PNG decode + per-axis morphological fold detect |
| P2 Topology | 2 | BFS over panel-fold graph |
| P3 Fold | 17 | Integer cube-rotation pose composition |
| P4 Mesh | 685 | Anchor-aware grid + junction routing |
| P5 Stitch | **11 366** | Fixpoint: weld → split → dedup → compact (cKDTree + scipy sparse) |
| P6 Mapper | 84 | Per-element 3D centroid → 2D pixel → mask lookup |
| P7 Bump+Cut | **15 571** | scipy.sparse.csgraph multi-source Dijkstra geodesic + hole-snap |
| **Total** | **28 260** | ~1.77 s / case, **237 572 quads / 241 184 verts** corpus-wide |
| Avg peak RSS | 109 MB | per case |

### Fix 1 + Fix 3 (`resolution = 1.0` px/cell, 950 k quads — finest)

| Phase | Aggregate (ms) | × vs default |
|---|---|---|
| P1 Parse | 536 | 1.0× |
| P2 Topology | 1 | 1.0× |
| P3 Fold | 16 | 1.0× |
| P4 Mesh | 2 669 | 3.9× |
| P5 Stitch | **45 807** | 4.0× |
| P6 Mapper | 317 | 3.8× |
| P7 Bump+Cut | **62 692** | 4.0× |
| **Total** | **112 037** | 4.0× |
| Avg peak RSS | 150 MB | +38 % |

Quad counts: **950 288** corpus-wide at res 1.0 + Fix 3. Wall-time
scales **near-linearly** with quad count (~4× quads → ~4× time)
thanks to the scipy / numpy vectorization layer — no super-linear
Python overhead spikes left.

### Optimization history (the speedup work that landed alongside Fix 3)

| Hot path | Before | After | Change |
|---|---|---|---|
| `apply_bump` geodesic | `heapq` Dijkstra in pure Python over per-vertex `dict` adjacency | scipy.sparse.csgraph multi-source Dijkstra on CSR adjacency | C-vectorized, ~10× faster on labeled-region size |
| `_mean_edge_length` | Python `set` over every quad/tri edge, then `np.linalg.norm` per pair | `np.unique(np.sort(edges,axis=1))` + batched `np.linalg.norm` | ~50× on 60 k-quad corpus |
| `collect_fold_edge_verts` | Python `dict[v] = set(pids)` over every element | `np.bincount` on the unique `(v, pid)` pair array | ~30× |
| `split_t_junctions` | `np.linalg.norm(vertices[r]-vertices[p])` × 4 × Q calls | precomputed `quad_edge_halflen` / `tri_edge_halflen` tensors | P5 −35 % at res 2.0 |
| `apply_welds` (earlier) | midpoint averaging | pure index redirect | unchanged speed, byte-stable |

### GPU?

`Project_Definition.md` §4.11 (the "out-of-scope" anti-goal list
that previously forbade GPU) has been **removed** in this revision —
GPU is now allowed in any phase.

After this round of vectorization the two hottest phases (P5
stitch, P7 bumper) are dominated by graph algorithms (`cKDTree`
pair-search and `scipy.sparse.csgraph.dijkstra`) whose CPU
implementations are already C-vectorized and stay roughly
**near-linear in quad count** through 950 k quads. A naive port of
SSSP to torch CUDA at this graph size would be slower than scipy
because CUDA kernel-launch latency (~10–50 μs / kernel × thousands
of iterative kernels) overwhelms the saved compute. A future move
to cuGraph SSSP / batched Bellman-Ford would start paying off
beyond **~10⁶ quads** — beyond the current corpus.

The phases that *would* gain from GPU today (P3 pose compose, P4
grid emit, P6 mapper centroid→pixel) collectively account for
**< 3 %** of total wall time after the vectorization pass, so
moving them adds engineering overhead without changing the bottom
line. Status: **not blocked by spec, deferred until corpus scale
makes it worth the launch-latency cost.**

---

## Per-case pipeline pictures

For each case: the **input PNG bundle** (`_main`, `_bump`, `_hole`)
followed by every phase picture (P1 → P2 → P3 → P4 → P5 → P6 → P7).
P6 colors: gold = yellow-mask quads, green = green-mask quads,
purple = purple-mask (hole) quads, grey = unmapped. Pictures
below were rendered at **`mesh_resolution = 2.0` px/cell with Fix 3
(`RENDER_SCALE = 2`) active** — equivalent to 4× the pre-Fix-3
quad count per panel, so the bump ramp is visibly smooth and the
purple-cut contour snap is at the new finer PNG mask granularity.

### box_unfolding

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/box_unfolding/box_unfolding_main.png) | ![](Origami_Gen_p6_mapper_verification/box_unfolding/box_unfolding_bump.png) | ![](Origami_Gen_p6_mapper_verification/box_unfolding/box_unfolding_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut |
|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/box_unfolding/parse.png) | ![](Origami_Gen_p6_mapper_verification/box_unfolding/topology.png) | ![](Origami_Gen_p6_mapper_verification/box_unfolding/fold.png) | ![](Origami_Gen_p6_mapper_verification/box_unfolding/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/box_unfolding/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/box_unfolding/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/box_unfolding/bump_p7.png) |

### cascade_5_deep

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/cascade_5_deep/cascade_5_deep_main.png) | ![](Origami_Gen_p6_mapper_verification/cascade_5_deep/cascade_5_deep_bump.png) | ![](Origami_Gen_p6_mapper_verification/cascade_5_deep/cascade_5_deep_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut |
|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/cascade_5_deep/parse.png) | ![](Origami_Gen_p6_mapper_verification/cascade_5_deep/topology.png) | ![](Origami_Gen_p6_mapper_verification/cascade_5_deep/fold.png) | ![](Origami_Gen_p6_mapper_verification/cascade_5_deep/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/cascade_5_deep/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/cascade_5_deep/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/cascade_5_deep/bump_p7.png) |

### closed_box

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/closed_box/closed_box_main.png) | ![](Origami_Gen_p6_mapper_verification/closed_box/closed_box_bump.png) | ![](Origami_Gen_p6_mapper_verification/closed_box/closed_box_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut |
|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/closed_box/parse.png) | ![](Origami_Gen_p6_mapper_verification/closed_box/topology.png) | ![](Origami_Gen_p6_mapper_verification/closed_box/fold.png) | ![](Origami_Gen_p6_mapper_verification/closed_box/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/closed_box/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/closed_box/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/closed_box/bump_p7.png) |

### corner_3panel

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/corner_3panel/corner_3panel_main.png) | ![](Origami_Gen_p6_mapper_verification/corner_3panel/corner_3panel_bump.png) | ![](Origami_Gen_p6_mapper_verification/corner_3panel/corner_3panel_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut |
|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/corner_3panel/parse.png) | ![](Origami_Gen_p6_mapper_verification/corner_3panel/topology.png) | ![](Origami_Gen_p6_mapper_verification/corner_3panel/fold.png) | ![](Origami_Gen_p6_mapper_verification/corner_3panel/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/corner_3panel/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/corner_3panel/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/corner_3panel/bump_p7.png) |

### cross

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/cross/cross_main.png) | ![](Origami_Gen_p6_mapper_verification/cross/cross_bump.png) | ![](Origami_Gen_p6_mapper_verification/cross/cross_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut |
|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/cross/parse.png) | ![](Origami_Gen_p6_mapper_verification/cross/topology.png) | ![](Origami_Gen_p6_mapper_verification/cross/fold.png) | ![](Origami_Gen_p6_mapper_verification/cross/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/cross/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/cross/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/cross/bump_p7.png) |

### cross_fold_demo

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/cross_fold_demo/cross_fold_demo_main.png) | ![](Origami_Gen_p6_mapper_verification/cross_fold_demo/cross_fold_demo_bump.png) | ![](Origami_Gen_p6_mapper_verification/cross_fold_demo/cross_fold_demo_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut |
|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/cross_fold_demo/parse.png) | ![](Origami_Gen_p6_mapper_verification/cross_fold_demo/topology.png) | ![](Origami_Gen_p6_mapper_verification/cross_fold_demo/fold.png) | ![](Origami_Gen_p6_mapper_verification/cross_fold_demo/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/cross_fold_demo/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/cross_fold_demo/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/cross_fold_demo/bump_p7.png) |

### l_shape

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/l_shape/l_shape_main.png) | ![](Origami_Gen_p6_mapper_verification/l_shape/l_shape_bump.png) | ![](Origami_Gen_p6_mapper_verification/l_shape/l_shape_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut |
|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/l_shape/parse.png) | ![](Origami_Gen_p6_mapper_verification/l_shape/topology.png) | ![](Origami_Gen_p6_mapper_verification/l_shape/fold.png) | ![](Origami_Gen_p6_mapper_verification/l_shape/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/l_shape/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/l_shape/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/l_shape/bump_p7.png) |

### long_thin_panel

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/long_thin_panel/long_thin_panel_main.png) | ![](Origami_Gen_p6_mapper_verification/long_thin_panel/long_thin_panel_bump.png) | ![](Origami_Gen_p6_mapper_verification/long_thin_panel/long_thin_panel_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut |
|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/long_thin_panel/parse.png) | ![](Origami_Gen_p6_mapper_verification/long_thin_panel/topology.png) | ![](Origami_Gen_p6_mapper_verification/long_thin_panel/fold.png) | ![](Origami_Gen_p6_mapper_verification/long_thin_panel/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/long_thin_panel/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/long_thin_panel/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/long_thin_panel/bump_p7.png) |

### mismatched_resolution

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/mismatched_resolution/mismatched_resolution_main.png) | ![](Origami_Gen_p6_mapper_verification/mismatched_resolution/mismatched_resolution_bump.png) | ![](Origami_Gen_p6_mapper_verification/mismatched_resolution/mismatched_resolution_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut |
|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/mismatched_resolution/parse.png) | ![](Origami_Gen_p6_mapper_verification/mismatched_resolution/topology.png) | ![](Origami_Gen_p6_mapper_verification/mismatched_resolution/fold.png) | ![](Origami_Gen_p6_mapper_verification/mismatched_resolution/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/mismatched_resolution/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/mismatched_resolution/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/mismatched_resolution/bump_p7.png) |

### multi_hole_strip

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/multi_hole_strip/multi_hole_strip_main.png) | ![](Origami_Gen_p6_mapper_verification/multi_hole_strip/multi_hole_strip_bump.png) | ![](Origami_Gen_p6_mapper_verification/multi_hole_strip/multi_hole_strip_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut |
|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/multi_hole_strip/parse.png) | ![](Origami_Gen_p6_mapper_verification/multi_hole_strip/topology.png) | ![](Origami_Gen_p6_mapper_verification/multi_hole_strip/fold.png) | ![](Origami_Gen_p6_mapper_verification/multi_hole_strip/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/multi_hole_strip/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/multi_hole_strip/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/multi_hole_strip/bump_p7.png) |

### single_fold

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/single_fold/single_fold_main.png) | ![](Origami_Gen_p6_mapper_verification/single_fold/single_fold_bump.png) | ![](Origami_Gen_p6_mapper_verification/single_fold/single_fold_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut |
|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/single_fold/parse.png) | ![](Origami_Gen_p6_mapper_verification/single_fold/topology.png) | ![](Origami_Gen_p6_mapper_verification/single_fold/fold.png) | ![](Origami_Gen_p6_mapper_verification/single_fold/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/single_fold/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/single_fold/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/single_fold/bump_p7.png) |

### staircase_3

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/staircase_3/staircase_3_main.png) | ![](Origami_Gen_p6_mapper_verification/staircase_3/staircase_3_bump.png) | ![](Origami_Gen_p6_mapper_verification/staircase_3/staircase_3_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut |
|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/staircase_3/parse.png) | ![](Origami_Gen_p6_mapper_verification/staircase_3/topology.png) | ![](Origami_Gen_p6_mapper_verification/staircase_3/fold.png) | ![](Origami_Gen_p6_mapper_verification/staircase_3/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/staircase_3/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/staircase_3/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/staircase_3/bump_p7.png) |

### tiny_panel

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/tiny_panel/tiny_panel_main.png) | ![](Origami_Gen_p6_mapper_verification/tiny_panel/tiny_panel_bump.png) | ![](Origami_Gen_p6_mapper_verification/tiny_panel/tiny_panel_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut |
|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/tiny_panel/parse.png) | ![](Origami_Gen_p6_mapper_verification/tiny_panel/topology.png) | ![](Origami_Gen_p6_mapper_verification/tiny_panel/fold.png) | ![](Origami_Gen_p6_mapper_verification/tiny_panel/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/tiny_panel/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/tiny_panel/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/tiny_panel/bump_p7.png) |

### u_shape

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/u_shape/u_shape_main.png) | ![](Origami_Gen_p6_mapper_verification/u_shape/u_shape_bump.png) | ![](Origami_Gen_p6_mapper_verification/u_shape/u_shape_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut |
|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/u_shape/parse.png) | ![](Origami_Gen_p6_mapper_verification/u_shape/topology.png) | ![](Origami_Gen_p6_mapper_verification/u_shape/fold.png) | ![](Origami_Gen_p6_mapper_verification/u_shape/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/u_shape/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/u_shape/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/u_shape/bump_p7.png) |

### zigzag_4

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/zigzag_4/zigzag_4_main.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_4/zigzag_4_bump.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_4/zigzag_4_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut |
|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/zigzag_4/parse.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_4/topology.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_4/fold.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_4/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_4/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_4/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_4/bump_p7.png) |

### zigzag_6

**Inputs (PNG bundle):**

| `_main.png` (panels + folds) | `_bump.png` (yellow / green) | `_hole.png` (purple cut) |
|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/zigzag_6/zigzag_6_main.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_6/zigzag_6_bump.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_6/zigzag_6_hole.png) |

**Pipeline:**

| P1 parse | P2 topology | P3 fold | P4 mesh | P5 stitch | P6 mapper | P7 bump+cut |
|---|---|---|---|---|---|---|
| ![](Origami_Gen_p6_mapper_verification/zigzag_6/parse.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_6/topology.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_6/fold.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_6/mesh_p4.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_6/stitch_p5.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_6/map_p6.png) | ![](Origami_Gen_p6_mapper_verification/zigzag_6/bump_p7.png) |

## Other Origami_Gen verification folders

- `Origami_Gen_dihedral_90/` — dihedral-angle verification renders
  (every fold ≡ 90°) per case.
- `Origami_Gen_P7_6_compare/` — P7.6 quad-split fallback comparison
  (default vs. stress).
- `Origami_Gen_p6_mapper_verification/SUMMARY.md` — per-case gate counts + composite storyboards.

## Legacy MOBIS_GEN inverse-pipeline folders

Phase-1..5 inverse-design output from prior MOBIS_GEN work, kept
for reference only:

- `step1_visualize/` — H5 mesh renders (40 files).
- `step2_mainplanes/` — region-growing plane segmentation.
- `step3_classify_blobs/` — main / flat-bump / bend-bump classify.
- `step4_blob_graph/` — blob-topology graph.
- `step5_collapse_smalls/` — small-region collapse.
