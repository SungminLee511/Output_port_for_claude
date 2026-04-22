# Output Port for Claude

This repo is used to share result images from Claude Code.

**Timezone: KST (UTC+9)** — Server time is 9 hours behind KST.

---

# Origami-Gemini-Gen — Panel Snap Fix (2026-04-23 KST)

Panels snapped to fold_line.position in Phase 1 (zero-gap). Connected mesh confirmed.

## Phase 2: Topology Builder
BFS fold tree. Panels now touch at fold lines (no pixel gap).
![phase2_results](phase2_results.png)

## Phase 3: 3D Folder
Cascading 90° folds. Panels share edges at fold positions.
![phase3_results](phase3_results.png)

## Phase 4: Mesh Generator
Finer mesh (res=2.0). Shared vertices at fold edges. Red = boundary only.
![phase4_results](phase4_results.png)
