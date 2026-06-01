from __future__ import annotations

import numpy as np
from PIL import Image, ImageDraw

# CaseBundle is pre-injected into the global scope.

# ─── palette (Project Definition §1.3) ────────────────────────────────
WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
RED    = (255, 0,   0)        # mountain fold
BLUE   = (0,   0,   255)        # valley fold
YELLOW = (255, 255, 0)      # bump
GREEN  = (0,   255, 0)        # bump
PURPLE = (128, 0,   128)      # hole / carve

# ─── geometry and layout ──────────────────────────────────────────────
SCALE = 4
PAD   = 25 * SCALE

# Panel dimensions (mm)
W_A = 140
H_A = 230
W_B = 50
H_B = 172
B_UP = 12
H_B_BELOW = H_B - B_UP  # 160 mm
W_C = 50
H_C = 10

TOP_STACK = H_C + B_UP
IMG_W = PAD + W_A * SCALE + W_B * SCALE + PAD
IMG_H = PAD + TOP_STACK * SCALE + H_A * SCALE + PAD

# Panel top-left origins (pixels)
AX0 = PAD
AY0 = PAD + TOP_STACK * SCALE
BX0 = AX0 + W_A * SCALE
BY0 = AY0 - B_UP * SCALE
CX0 = BX0
CY0 = BY0 - H_C * SCALE

# Dictionary of panel origins and dimensions (mm)
PANEL_GEOMETRY = {
    "A": ((AX0, AY0), W_A, H_A),
    "B": ((BX0, BY0), W_B, H_B),
    "C": ((CX0, CY0), W_C, H_C),
}

# ─── drawing helpers ──────────────────────────────────────────────────
def _box(origin, x_mm, y_mm, w_mm, h_mm):
    ox, oy = origin
    return (
        ox + int(x_mm * SCALE),
        oy + int(y_mm * SCALE),
        ox + int((x_mm + w_mm) * SCALE) - 1,
        oy + int((y_mm + h_mm) * SCALE) - 1,
    )

def _rect(d, origin, x, y, w, h, fill):
    d.rectangle(_box(origin, x, y, w, h), fill=fill)

def _circ(d, origin, cx, cy, r, fill):
    d.ellipse(_box(origin, cx - r, cy - r, 2 * r, 2 * r), fill=fill)

def _rrect(d, origin, x, y, w, h, r, fill):
    d.rounded_rectangle(
        _box(origin, x, y, w, h),
        radius=int(r * SCALE), fill=fill,
    )

def _draw_fold(draw, axis, position, start, end, color):
    """Draw a 4-pixel-wide fold band."""
    if axis == "V":
        # Vertical fold at x=position
        draw.rectangle((position - 2, start, position + 1, end - 1), fill=color)
    else:
        # Horizontal fold at y=position
        draw.rectangle((start, position - 2, end - 1, position + 1), fill=color)

def make_bracket() -> CaseBundle:
    """
    Designs a feature-rich automotive L-bracket modeled after the HD Mobis style.
    It has a main plate, a right flange, and a small top cap.
    Features include boss stiffeners, a long bead, bolt holes, and a cutout.
    """
    # ─── main_rgb layer ──────────────────────────────────────────────────
    main_img = Image.new("RGB", (IMG_W, IMG_H), WHITE)
    dm = ImageDraw.Draw(main_img)

    for origin, w, h in PANEL_GEOMETRY.values():
        dm.rectangle((origin[0], origin[1], origin[0] + w * SCALE - 1, origin[1] + h * SCALE - 1), fill=BLACK)

    # Fold A (main) <-> B (flange): RED / Mountain / Vertical
    # The fold spans the vertical overlap of the two panels.
    fold_ab_start_y = AY0
    fold_ab_end_y = BY0 + H_B * SCALE
    _draw_fold(dm, "V", BX0, fold_ab_start_y, fold_ab_end_y, RED)

    # Fold B (flange) <-> C (cap): BLUE / Valley / Horizontal
    fold_bc_start_x = BX0
    fold_bc_end_x = BX0 + W_B * SCALE
    _draw_fold(dm, "H", BY0, fold_bc_start_x, fold_bc_end_x, BLUE)


    # ─── bump_rgb layer ──────────────────────────────────────────────────
    bump_img = Image.new("RGB", (IMG_W, IMG_H), WHITE)
    db = ImageDraw.Draw(bump_img)

    for origin, w, h in PANEL_GEOMETRY.values():
        db.rectangle((origin[0], origin[1], origin[0] + w * SCALE - 1, origin[1] + h * SCALE - 1), fill=BLACK)

    pA_origin = PANEL_GEOMETRY["A"][0]
    pB_origin = PANEL_GEOMETRY["B"][0]

    # Panel A: 4 yellow boss-stiffener bumps
    boss_dims = (30, 30)
    boss_radius = 6
    boss_coords = [
        (25, 35), (95, 35),
        (25, 185), (95, 185),
    ]
    for cx, cy in boss_coords:
        _rrect(db, pA_origin, cx, cy, boss_dims[0], boss_dims[1], boss_radius, YELLOW)

    # Panel B: 1 yellow long stiffener bead
    _rrect(db, pB_origin, 15, 16, 20, 140, 8, YELLOW)


    # ─── hole_rgb layer ──────────────────────────────────────────────────
    hole_img = Image.new("RGB", (IMG_W, IMG_H), WHITE)
    dh = ImageDraw.Draw(hole_img)

    for origin, w, h in PANEL_GEOMETRY.values():
        dh.rectangle((origin[0], origin[1], origin[0] + w * SCALE - 1, origin[1] + h * SCALE - 1), fill=BLACK)

    # Panel A: Bolt holes inside the boss stiffeners
    hole_radius = 2.5
    for cx, cy in boss_coords:
        hole_cx = cx + boss_dims[0] / 2
        hole_cy = cy + boss_dims[1] / 2
        _circ(dh, pA_origin, hole_cx, hole_cy, hole_radius, PURPLE)

    # Panel A: 2 additional purple bolt circles
    _circ(dh, pA_origin, 70, 20, 4, PURPLE)
    _circ(dh, pA_origin, 70, 210, 4, PURPLE)

    # Panel A: 1 purple rounded-rectangle cutout
    _rrect(dh, pA_origin, 50, 90, 40, 50, 8, PURPLE)


    # ─── Finalize and return CaseBundle ──────────────────────────────────
    return CaseBundle(
        name="automotive_l_bracket_simple",
        main_rgb=np.asarray(main_img, dtype=np.uint8),
        bump_rgb=np.asarray(bump_img, dtype=np.uint8),
        hole_rgb=np.asarray(hole_img, dtype=np.uint8),
    )