# Output Port

Files Claude moved here are visible on GitHub.

## Step 1 — Read mesh and visualize

Loaded `sol103_01_410_08.h5` via the I0 H5 ingest (solver-ID remap),
rendered the shell with matplotlib's `Poly3DCollection` (Lambert
shading from a single light, gray colormap, light edge lines).
Render took **9.2 s** for 71,504 nodes / 69,722 quads / 1,468 tris.

![mesh](step1_visualize/sol103_01_410_08_mesh.png)

### `tmp/`
Earlier deliverables, kept for reference.
