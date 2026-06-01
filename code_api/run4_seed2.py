import numpy as np
from PIL import Image, ImageDraw

# CaseBundle is pre-injected by the sandbox environment.

# === PIXEL CONTRACT (Project Definition §1.3) ===
WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
RED    = (255, 0,   0)        # mountain fold
BLUE   = (0,   0,   255)        # valley fold
YELLOW = (255, 255, 0)      # bump
GREEN  = (0, 255, 0)        # bump
PURPLE = (128, 0, 128)      # hole / carve

# === DRAWING TOOLKIT ===
SCALE = 4
PAD   = 25 * SCALE

def _box(origin, x_mm, y_mm, w_mm, h_mm):
    """Returns PIL.rectangle-ready (x0, y0, x1, y1) in pixel space."""
    ox, oy = origin
    return (
        ox + int(x_mm * SCALE),
        oy + int(y_mm * SCALE),
        ox + int((x_mm + w_mm) * SCALE) - 1,
        oy + int((y_mm + h_mm) * SCALE) - 1,
    )

def _rect(d, origin, x, y, w, h, fill):
    """Draws a rectangle relative to a panel's origin."""
    d.rectangle(_box(origin, x, y, w, h), fill=fill)

def _circ(d, origin, cx, cy, r, fill):
    """Draws a circle relative to a panel's origin."""
    d.ellipse(_box(origin, cx - r, cy - r, 2 * r, 2 * r), fill=fill)

def _rrect(d, origin, x, y, w, h, r, fill):
    """Draws a rounded rectangle relative to a panel's origin."""
    d.rounded_rectangle(
        _box(origin, x, y, w, h),
        radius=int(r * SCALE), fill=fill,
    )

def make_bracket():
    """
    Designs a simple 2-panel hinge bracket.
    Main plate (A) is 100x100 mm.
    A second plate (B) of 50x100 mm is attached via a vertical mountain fold.
    Default bump and hole features are added for testing downstream phases.
    """
    # 1. Geometry definitions (mm)
    W_A = 100
    H_A = 100
    W_B = 50
    H_B = 100

    # 2. Canvas size
    img_w = PAD + (W_A + W_B) * SCALE + PAD
    img_h = PAD + H_A * SCALE + PAD

    # 3. Panel origins (top-left pixel coordinates)
    AX0 = PAD
    AY0 = PAD
    BX0 = AX0 + W_A * SCALE
    BY0 = AY0

    pA = (AX0, AY0)
    pB = (BX0, BY0)

    # 4. Draw main_rgb layer
    main = Image.new("RGB", (img_w, img_h), WHITE)
    dm = ImageDraw.Draw(main)

    # Draw panels
    _rect(dm, pA, 0, 0, W_A, H_A, BLACK)
    _rect(dm, pB, 0, 0, W_B, H_B, BLACK)

    # Draw fold (4px wide mountain fold)
    fold_x = BX0
    fold_y0 = BY0
    fold_y1 = BY0 + H_B * SCALE
    dm.rectangle((fold_x - 2, fold_y0, fold_x + 1, fold_y1 - 1), fill=RED)

    # 5. Draw bump_rgb layer
    bump = Image.new("RGB", (img_w, img_h), WHITE)
    db = ImageDraw.Draw(bump)

    # Draw panel mask
    _rect(db, pA, 0, 0, W_A, H_A, BLACK)
    _rect(db, pB, 0, 0, W_B, H_B, BLACK)

    # Add a circular bump to panel A
    _circ(db, pA, 50, 50, 20, YELLOW) # cx, cy, r in mm

    # 6. Draw hole_rgb layer
    hole = Image.new("RGB", (img_w, img_h), WHITE)
    dh = ImageDraw.Draw(hole)

    # Draw panel mask
    _rect(dh, pA, 0, 0, W_A, H_A, BLACK)
    _rect(dh, pB, 0, 0, W_B, H_B, BLACK)

    # Add a rounded rectangular hole to panel B
    _rrect(dh, pB, 15, 30, 20, 40, 4, PURPLE) # x, y, w, h, r in mm

    # 7. Assemble the CaseBundle and return
    return CaseBundle(
        name="simple_hinge_100x100",
        main_rgb=np.asarray(main, dtype=np.uint8),
        bump_rgb=np.asarray(bump, dtype=np.uint8),
        hole_rgb=np.asarray(hole, dtype=np.uint8),
    )