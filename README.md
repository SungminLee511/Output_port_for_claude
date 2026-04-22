# Output Port for Claude

This repo is used to share result images from Claude Code.

**Timezone: KST (UTC+9)** — Server time is 9 hours behind KST.

---

# Origami-Gemini-Gen — Full Pipeline (2026-04-23 KST)

Sharp 90° folds. No fillets. Panels snap together at fold edges with shared vertices.

## Phase 0: Test Image Generator
11 diverse 전개도 test cases with bump/hole overlays.
![phase0_overview](phase0_overview.png)

## Phase 1: Image Parser
Panel extraction, fold lines (red=+z, blue=-z), color masks (Y/G/P).
![phase1_results](phase1_results.png)

## Phase 2: Topology Builder
BFS fold tree. Root = largest panel. Color = BFS depth.
![phase2_results](phase2_results.png)

## Phase 3: 3D Folder
Cascading 90° folds. No fillet gap — panels touch at fold edges.
![phase3_results](phase3_results.png)

## Phase 4: Mesh Generator
Structured quad grids. Shared vertices at fold edges. Red = free edges.
![phase4_results](phase4_results.png)

## Phase 5: Free Edge QA
Plot-only. Red = free (boundary) edges. No stitching.
![phase5_results](phase5_results.png)

### L-Shape (3D + Side)
![phase5_l_shape](phase5_l_shape.png)

### T-Shape (3D + Side)
![phase5_t_shape](phase5_t_shape.png)

### Cross (3D + Side)
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
