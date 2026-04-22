# Output Port for Claude

This repo is used to share result images from Claude Code.

**Timezone: KST (UTC+9)** — Server time is 9 hours behind KST.

---

# Origami-Gemini-Gen — Sharp Fold Rewrite (2026-04-23 KST)

**Changes:** Removed fillets, corner patches, stitcher. Panels snap together at fold edges. Sharp 90° folds with shared vertices.

## Phase 4: Mesh Generator (rewritten)
Structured quad grids per panel. Shared vertices at fold edges via tight-epsilon weld. No fillets, no tris. Red = free edges.
![phase4_results](phase4_results.png)

## Phase 5: Free Edge QA (rewritten — plot only)
No stitching. Just visualize free edges as red lines for QA.
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
