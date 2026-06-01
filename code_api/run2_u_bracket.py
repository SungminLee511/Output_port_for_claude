from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw
import math

# This module is a Python sheet-metal designer for the Origami_Gen v3 toolchain.
# It defines a make_bracket() function that draws a U-channel bracket.

# CaseBundle is pre-injected into the module's globals by the sandbox.


# --- PIXEL CONTRACT (Project Definition §1.3) ---
WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
RED    = (255, 0,   0)        # mountain fold
BLUE   = (0,   0,   255)        # valley fold
YELLOW = (255, 255, 0)      # bump
GREEN  = (0,   255, 0)        # bump
PURPLE = (128, 0,   128)      # hole / carve

# --- SCALING CONVENTION ---
# 4 pixels per mm + 25 mm padding on every side.
SCALE = 4
PAD   = 25 * SCALE

# --- DRAWING HELPERS ---
def _box(origin: tuple[int, int], x_mm: float, y_mm: float, w_mm: float, h_mm: float) -> tuple[int, int, int, int]:
    """Returns PIL.rectangle-ready (x0, y0, x1, y1) in pixel space."""
    ox, oy = origin
    return (
        ox + int(x_mm * SCALE),
        oy + int(y_mm * SCALE),
        ox + int((x_mm + w_mm) * SCALE) - 1,
        oy + int((y_mm + h_mm) * SCALE) - 1,
    )

def _rect(d: ImageDraw.ImageDraw, origin: tuple[int, int], x: float, y: float, w: float, h: float, fill: tuple[int, int, int]):
    """Draws a rectangle using the _box helper."""
    d.rectangle(_box(origin, x, y, w, h), fill=fill)

def _circ(d: ImageDraw.ImageDraw, origin: tuple[int, int], cx: float, cy: float, r: float, fill: tuple[int, int, int]):
    """Draws a circle/ellipse using the _box helper."""
    d.ellipse(_box(origin, cx - r, cy - r, 2 * r, 2 * r), fill=fill)


def make_bracket() -> "CaseBundle":
    """
    Designs a U-channel mounting bracket as per the user's intent.
    - Main plate: 180x100 mm
    - Flanges: Two 180x60 mm flanges on the left and right.
    - Folds: Two vertical mountain folds.
    - Features: One central circular bolt hole on the main plate.
    """
    # --- GEOMETRY (mm) ---
    W_M = 100.0  # Main plate width
    H_M = 180.0  # Main plate height
    W_F = 60.0   # Flange width
    H_F = H_M    # Flange height

    # --- CANVAS SETUP ---
    img_w = PAD + int((W_F + W_M + W_F) * SCALE) + PAD
    img_h = PAD + int(H_M * SCALE) + PAD

    # --- PANEL ORIGINS (top-left pixel coordinates) ---
    LX0 = PAD
    LY0 = PAD
    pL = (LX0, LY0)

    MX0 = LX0 + int(W_F * SCALE)
    MY0 = LY0
    pM = (MX0, MY0)

    RX0 = MX0 + int(W_M * SCALE)
    RY0 = LY0
    pR = (RX0, RY0)

    panel_defs = [
        (pL, W_F, H_F),
        (pM, W_M, H_M),
        (pR, W_F, H_F),
    ]

    # --- IMAGE CREATION ---
    main = Image.new("RGB", (img_w, img_h), WHITE)
    bump = Image.new("RGB", (img_w, img_h), WHITE)
    hole = Image.new("RGB", (img_w, img_h), WHITE)
    
    dm = ImageDraw.Draw(main)
    db = ImageDraw.Draw(bump)
    dh = ImageDraw.Draw(hole)
    drawers = [dm, db, dh]

    # --- DRAW PANEL MASKS (on all three layers) ---
    for origin, w_mm, h_mm in panel_defs:
        for d in drawers:
            _rect(d, origin, 0, 0, w_mm, h_mm, fill=BLACK)

    # --- DRAW FOLDS (main layer only) ---
    fold_y_start = MY0
    fold_y_end = MY0 + int(H_M * SCALE)
    
    # Left fold (L-M): 4px wide red line
    dm.rectangle((MX0 - 2, fold_y_start, MX0 + 1, fold_y_end - 1), fill=RED)
    
    # Right fold (M-R): 4px wide red line
    dm.rectangle((RX0 - 2, fold_y_start, RX0 + 1, fold_y_end - 1), fill=RED)

    # --- DRAW FEATURES (hole layer only) ---
    # Central circular bolt hole, 5mm radius
    hole_radius_mm = 5.0
    _circ(dh, pM, W_M / 2.0, H_M / 2.0, hole_radius_mm, PURPLE)
    
    # Bump layer has no features as per the request.

    # --- PACKAGE AND RETURN ---
    return CaseBundle(
        name="u_channel_mount",
        main_rgb=np.asarray(main, dtype=np.uint8),
        bump_rgb=np.asarray(bump, dtype=np.uint8),
        hole_rgb=np.asarray(hole, dtype=np.uint8),
    )