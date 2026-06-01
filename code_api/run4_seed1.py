from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw

# This module is executed in a sandbox where `CaseBundle` is a
# pre-injected global. You do not need to and cannot import it.
#
# from origami_gen.corpus.utils._registry import CaseBundle


# === PIXEL CONTRACT & DRAWING CONSTANTS ===

# palette (Project Definition §1.3)
WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
RED    = (255, 0,   0)        # mountain fold
BLUE   = (0,   0,   255)        # valley fold
YELLOW = (255, 255, 0)      # bump
GREEN  = (0,   255, 0)        # bump
PURPLE = (128, 0, 128)      # hole / carve

# scaling — convention: 4 pixels per mm + 25 mm padding on
# every side.
SCALE = 4
PAD   = 25 * SCALE


# === DRAWING HELPERS ===

def _box(origin: tuple[int, int], x_mm: float, y_mm: float, w_mm: float, h_mm: float) -> tuple[int, int, int, int]:
    """Returns PIL.rectangle-ready (x0, y0, x1, y1) in pixel space
    relative to a panel's top-left origin."""
    ox, oy = origin
    return (
        ox + int(x_mm * SCALE),
        oy + int(y_mm * SCALE),
        ox + int((x_mm + w_mm) * SCALE) - 1,
        oy + int((y_mm + h_mm) * SCALE) - 1,
    )

def _rect(d: ImageDraw.ImageDraw, origin: tuple[int, int], x: float, y: float, w: float, h: float, fill: tuple[int, int, int]):
    """Draws a rectangle using mm-based coordinates relative to a
    panel origin."""
    d.rectangle(_box(origin, x, y, w, h), fill=fill)


def make_bracket() -> CaseBundle:
    """Generates a 3-panel L-bracket.

    The layout consists of a main plate, a flange folding off its
    right side, and a cap panel folding off the top of the flange.

    - Panel A: Main plate (100x180 mm)
    - Panel B: Flange (50x180 mm)
    - Panel C: Top cap (50x20 mm)

    Folds:
    - A↔B: Vertical mountain fold.
    - B↔C: Horizontal mountain fold.

    No bumps or holes are included, per the simple design request.
    """
    # --- Geometry Definition (mm) ---
    W_A = 100
    H_A = 180
    W_B = 50
    H_B = 180
    W_C = 50
    H_C = 20

    # --- Canvas and Panel Layout (pixels) ---
    # The unfolded layout places panel C above panel B, which is to the
    # right of panel A.
    #      +---+ (C)
    #  +---+---+
    #  | A | B |
    #  +---+---+
    img_w = PAD + (W_A + W_B) * SCALE + PAD
    img_h = PAD + (H_C + H_A) * SCALE + PAD

    # Panel top-left origins in pixel coordinates
    pC_origin = (PAD + W_A * SCALE, PAD)
    pA_origin = (PAD, PAD + H_C * SCALE)
    pB_origin = (PAD + W_A * SCALE, PAD + H_C * SCALE)

    panels = [
        (pA_origin, W_A, H_A),
        (pB_origin, W_B, H_B),
        (pC_origin, W_C, H_C),
    ]

    # --- Image Generation ---
    main_img = Image.new("RGB", (img_w, img_h), WHITE)
    bump_img = Image.new("RGB", (img_w, img_h), WHITE)
    hole_img = Image.new("RGB", (img_w, img_h), WHITE)

    dm = ImageDraw.Draw(main_img)
    db = ImageDraw.Draw(bump_img)
    dh = ImageDraw.Draw(hole_img)

    # Draw panel masks (black rectangles) on all three layers
    for d in [dm, db, dh]:
        for origin, w, h in panels:
            _rect(d, origin, 0, 0, w, h, BLACK)

    # Draw folds (4px wide) on the main layer only
    # A↔B: Vertical mountain fold at the right edge of panel A.
    fold_AB_x = pA_origin[0] + W_A * SCALE
    fold_AB_y_start = pA_origin[1]
    fold_AB_y_end = pA_origin[1] + H_A * SCALE
    dm.rectangle(
        (fold_AB_x - 2, fold_AB_y_start, fold_AB_x + 1, fold_AB_y_end - 1),
        fill=RED
    )

    # B↔C: Horizontal mountain fold at the top edge of panel B.
    fold_BC_y = pB_origin[1]
    fold_BC_x_start = pB_origin[0]
    fold_BC_x_end = pB_origin[0] + W_B * SCALE
    dm.rectangle(
        (fold_BC_x_start, fold_BC_y - 2, fold_BC_x_end - 1, fold_BC_y + 1),
        fill=RED
    )

    # --- Finalize and Return ---
    main_rgb = np.array(main_img, dtype=np.uint8)
    bump_rgb = np.array(bump_img, dtype=np.uint8)
    hole_rgb = np.array(hole_img, dtype=np.uint8)

    return CaseBundle(
        name="l_bracket_3_panel_simple",
        main_rgb=main_rgb,
        bump_rgb=bump_rgb,
        hole_rgb=hole_rgb,
    )