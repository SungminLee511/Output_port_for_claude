import numpy as np
from PIL import Image, ImageDraw

# === PALETTE (Project Definition §1.3) ===
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)  # mountain fold
BLUE = (0, 0, 255)  # valley fold
YELLOW = (255, 255, 0)  # bump
GREEN = (0, 255, 0)  # bump
PURPLE = (128, 0, 128)  # hole / carve

# === SCALING ===
SCALE = 4  # 4 pixels per mm
PAD = 25 * SCALE  # 25 mm padding

# === DRAWING HELPERS ===
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

def make_bracket():
    """
    Designs a simple L-bracket: a 120x100 mm main plate with a 40x100 mm
    flange connected by a single vertical mountain fold. No additional
    features like bumps or holes are included.
    """
    # --- Geometry Definition (mm) ---
    W_A = 120  # Main plate width
    H_A = 100  # Main plate height (and flange height)
    W_B = 40   # Flange width

    # --- Canvas and Panel Layout (pixels) ---
    img_w = PAD + (W_A + W_B) * SCALE + PAD
    img_h = PAD + H_A * SCALE + PAD

    # Panel top-left origins
    origin_A = (PAD, PAD)
    origin_B = (PAD + W_A * SCALE, PAD)
    
    # --- Create Blank Canvases ---
    # The `bump` and `hole` layers must contain the panel mask even if empty.
    main_img = Image.new("RGB", (img_w, img_h), WHITE)
    bump_img = Image.new("RGB", (img_w, img_h), WHITE)
    hole_img = Image.new("RGB", (img_w, img_h), WHITE)

    draw_main = ImageDraw.Draw(main_img)
    draw_bump = ImageDraw.Draw(bump_img)
    draw_hole = ImageDraw.Draw(hole_img)

    # --- Draw Panel Masks on All Layers ---
    for d in [draw_main, draw_bump, draw_hole]:
        # Panel A (main plate)
        _rect(d, origin_A, 0, 0, W_A, H_A, fill=BLACK)
        # Panel B (flange)
        _rect(d, origin_B, 0, 0, W_B, H_A, fill=BLACK)

    # --- Draw Fold Line (main layer only) ---
    # This is a vertical mountain fold between panel A and B.
    # The fold line is 4px wide, centered on the panel boundary.
    fold_x = origin_B[0]
    fold_y0 = origin_A[1]
    fold_y1 = origin_A[1] + H_A * SCALE - 1
    
    draw_main.rectangle(
        (fold_x - 2, fold_y0, fold_x + 1, fold_y1),
        fill=RED
    )

    # --- Convert to NumPy arrays and return CaseBundle ---
    return CaseBundle(
        name="simple_l_bracket_basic",
        main_rgb=np.asarray(main_img, dtype=np.uint8),
        bump_rgb=np.asarray(bump_img, dtype=np.uint8),
        hole_rgb=np.asarray(hole_img, dtype=np.uint8),
    )