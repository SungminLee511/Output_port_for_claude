# Output Port for Claude

This repo is used to share result images from Claude Code.

**Timezone: KST (UTC+9)** — Server time is 9 hours behind KST.

---

# Origami-Gemini-Gen — Full Pipeline Results (2026-04-22 23:58 KST)

## Phase 0: Test Image Generator
11 diverse 전개도 (unfolding diagram) test cases generated programmatically.
![phase0_overview](phase0_overview.png)

## Phase 1: Image Parser
Panel extraction, fold line detection (red=+z, blue=-z), yellow region segmentation.
![phase1_results](phase1_results.png)

## Phase 2: Topology Builder
BFS fold tree from panel adjacency graph. Root = largest panel.
![phase2_results](phase2_results.png)

## Phase 3: 3D Folder
Cascading 90° rotations around fold axes. Panels trimmed by fillet radius.
![phase3_results](phase3_results.png)

## Phase 4: Mesh Generator
Structured quad grids + quarter-cylinder fillets + spherical corner patches. All 11 cases PASS.
![phase4_results](phase4_results.png)

### L-Shape Detail (3D + Side View)
![phase4_lshape](phase4_lshape.png)

### Multi-Case Detail
![phase4_multi](phase4_multi.png)

## Phase 5: Stitcher
Proximity-based free-edge welding + global vertex dedup. Red = free edges.
![phase5_results](phase5_results.png)

### L-Shape Before vs After
![phase5_l_shape](phase5_l_shape.png)

### T-Shape Before vs After
![phase5_t_shape](phase5_t_shape.png)

### Cross Before vs After
![phase5_cross](phase5_cross.png)

## Phase 6: Bump & Cut
Yellow = +z bump, Green = -z bump, Purple = hole cut. Smoothstep ramp.

### Overview: Before vs After (8 cases)
![phase6_results](phase6_results.png)

### L-Shape Detail
![phase6_l_shape](phase6_l_shape.png)

### T-Shape Detail
![phase6_t_shape](phase6_t_shape.png)

### Cross Detail
![phase6_cross](phase6_cross.png)
