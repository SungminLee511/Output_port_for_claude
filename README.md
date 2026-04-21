# Output Port for Claude

This repo is used to share result images from Claude Code.

**Timezone: KST (UTC+9)** — Server time is 9 hours behind KST.

## MOBIS_GEN to_2d.ipynb — sol103_01 + remesh + equal aspect (2026-04-22 02:02 KST)

### 1. Point Cloud
![pointcloud](pointcloud.png)

### 2. Outer Loop
![outer_loop](outer_loop.png)

### 3. Region Growing (holes remeshed)
![regions_fixed](regions_fixed.png)

### 4. Flatten Result (Original / Flat / Bend)
![flatten_result](flatten_result.png)

### 5. Cylinder Detected (BFS all-node classification)
![cylinder_detected](cylinder_detected.png)

### 6. Unroll Before/After
![unroll_result](unroll_result.png)

### 7. Unroll Translation Heatmap
![unroll_heatmap](unroll_heatmap.png)
