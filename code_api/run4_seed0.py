from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw

# CaseBundle is pre-injected into the module's global scope.


# ─── PIXEL PALETTE (Project Definition §1.3) ──────────────────────
WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
RED    = (255, 0,   0)        # mountain fold
BLUE   = (0,   0,   255)        # valley fold
YELLOW = (255, 255, 0)      # bump
GREEN  = (0,   255, 0)        # bump
PURPLE = (128, 0,   128)      # hole / carve


# ─── GEOMETRY & SCALING CONSTANTS ─────────────────────────────────
SCALE = 4  # 4 pixels per mm
PAD   = 25 * SCALE


# ─── DRAWING HELPERS ──────────────────────────────────────────────
def _box(origin: tuple[int, int], x_mm: float, y_mm: float, w_mm: float, h_mm: float) -> tuple[int, int, int, int]:
    """Returns a PIL.rectangle-ready (x0, y0, x1, y1) tuple."""
    ox, oy = origin
    return (
        ox + int(x_mm * SCALE),
        oy + int(y_mm * SCALE),
        ox + int((x_mm + w_mm) * SCALE) - 1,
        oy + int((y_mm + h_mm) * SCALE) - 1,
    )


def make_bracket() -> CaseBundle:
    """
    Designs a simple channel bracket with a main plate and three flanges.

    Layout (unfolded):
          ┌─────┐
          │ Top │
    ┌─────┼─────┼─────┐
    │Left │ Main│Right│
    └─────┼─────┼─────┘

    All flanges are attached with mountain folds. No additional
    features like holes or bumps are included, per the simple request.
    """
    # ─── 1. Define Geometry (all dimensions in mm) ────────────────
    W_M = 160.0  # Main plate width
    H_M = 100.0  # Main plate height
    W_L = 25.0   # Left flange width
    W_R = 25.0   # Right flange width
    H_T = 25.0   # Top flange height

    # ─── 2. Calculate Canvas Size ─────────────────────────────────
    canvas_w_mm = W_L + W_M + W_R
    canvas_h_mm = H_T + H_M

    img_w = PAD + int(canvas_w_mm * SCALE) + PAD
    img_h = PAD + int(canvas_h_mm * SCALE) + PAD

    # ─── 3. Define Panel Origins (top-left corner in pixels) ──────
    # The layout is arranged as a cross shape centered on the canvas.
    pT_x = PAD + int(W_L * SCALE)
    pT_y = PAD
    pT = (pT_x, pT_y)

    pM_x = PAD + int(W_L * SCALE)
    pM_y = PAD + int(H_T * SCALE)
    pM = (pM_x, pM_y)

    pL_x = PAD
    pL_y = PAD + int(H_T * SCALE)
    pL = (pL_x, pL_y)

    pR_x = PAD + int((W_L + W_M) * SCALE)
    pR_y = PAD + int(H_T * SCALE)
    pR = (pR_x, pR_y)

    panels = [
        (pM, W_M, H_M),  # Main plate
        (pT, W_M, H_T),  # Top flange (same width as main)
        (pL, W_L, H_M),  # Left flange (same height as main)
        (pR, W_R, H_M),  # Right flange (same height as main)
    ]

    # ─── 4. Create Images and Draw Panel Masks ────────────────────
    main_img = Image.new("RGB", (img_w, img_h), WHITE)
    bump_img = Image.new("RGB", (img_w, img_h), WHITE)
    hole_img = Image.new("RGB", (img_w, img_h), WHITE)

    drawers = [ImageDraw.Draw(img) for img in [main_img, bump_img, hole_img]]

    for d in drawers:
        for origin, w_mm, h_mm in panels:
            d.rectangle(_box(origin, 0, 0, w_mm, h_mm), fill=BLACK)

    # ─── 5. Draw Folds (on main_img only) ──────────────────────────
    dm = drawers[0]
    
    # Fold M <-> T (horizontal mountain fold)
    fold_MT_y = pM_y
    fold_MT_x0 = pM_x
    fold_MT_x1 = pM_x + int(W_M * SCALE)
    dm.rectangle((fold_MT_x0, fold_MT_y - 2, fold_MT_x1 - 1, fold_MT_y + 1), fill=RED)

    # Fold L <-> M (vertical mountain fold)
    fold_LM_x = pM_x
    fold_LM_y0 = pM_y
    fold_LM_y1 = pM_y + int(H_M * SCALE)
    dm.rectangle((fold_LM_x - 2, fold_LM_y0, fold_LM_x + 1, fold_LM_y1 - 1), fill=RED)

    # Fold M <-> R (vertical mountain fold)
    fold_MR_x = pR_x
    fold_MR_y0 = pR_y
    fold_MR_y1 = pR_y + int(H_M * SCALE)
    dm.rectangle((fold_MR_x - 2, fold_MR_y0, fold_MR_x + 1, fold_MR_y1 - 1), fill=RED)

    # ─── 6. Convert to Numpy and Return CaseBundle ────────────────
    main_rgb = np.array(main_img, dtype=np.uint8)
    bump_rgb = np.array(bump_img, dtype=np.uint8)
    hole_rgb = np.array(hole_img, dtype=np.uint8)

    return CaseBundle(
        name="channel_bracket_simple",
        main_rgb=main_rgb,
        bump_rgb=bump_rgb,
        hole_rgb=hole_rgb,
    )