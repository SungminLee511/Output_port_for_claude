# Output Port

Files Claude moved here are visible on GitHub.

## Step 1 — Read mesh and visualize

Loaded all 40 HD Mobis H5 files via the I0 H5 ingest (solver-ID
remap), rendered each shell with matplotlib's `Poly3DCollection`
(Lambert shading from a single light, gray colormap, light edge
lines).  Per-render time ~9 s × 40 = ~6 min serial.

Geometry repeats within a family (8 geometry families × 5 load-case
variants = 40 files), so the 5 variants of each family render
identically.  The gallery below shows the canonical first variant of
each family; all 40 PNGs are in `step1_visualize/`.

### Family gallery — one canonical variant per family

| family 1 (`_410_*`) | family 2 (`_420_*`) | family 3 (`_430_*`) | family 4 (`_440_*`) |
|---|---|---|---|
| ![f1](step1_visualize/sol103_01_410_08_mesh.png) | ![f2](step1_visualize/sol103_06_420_08_mesh.png) | ![f3](step1_visualize/sol103_11_430_08_mesh.png) | ![f4](step1_visualize/sol103_16_440_08_mesh.png) |

| family 5 (`_450_*`) | family 6 (`_461_*`) | family 7 (`_462_*`) | family 8 (`_463_*`) |
|---|---|---|---|
| ![f5](step1_visualize/sol103_21_450_08_mesh.png) | ![f6](step1_visualize/sol103_26_461_08_mesh.png) | ![f7](step1_visualize/sol103_31_462_08_mesh.png) | ![f8](step1_visualize/sol103_36_463_08_mesh.png) |

### All 40 PNGs

`step1_visualize/sol103_<NN>_<YYY>_<ZZ>_mesh.png` — one per H5 file.

### `tmp/`
Earlier deliverables, kept for reference.
