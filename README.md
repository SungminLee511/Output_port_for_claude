# Output Port for Claude

This repo is used to share result images from Claude Code.

**Timezone: KST (UTC+9)** — Server time is 9 hours behind KST.

## Results

### Migrated from Claude_Authorized

![comparison_plot](comparison_plot.png)
![comparison_plot2](comparison_plot2.png)
![comparison_plot3](comparison_plot3.png)
![comparison_plot4](comparison_plot4.png)
![cell_8_output](cell_8_output.png)
![autoresearch_progress](autoresearch_progress.png)

### Moldflow FEM Filling Solver — Test Results

**Cell 3: Mesh Generation** — 75 nodes, 160 tet elements, volume verified
![cell3_mesh_nodes](cell3_mesh_nodes.png)

**Cell 4: Boundary Classification** — Inlet (red), Wall (blue), Interior (gray)
![cell4_boundary](cell4_boundary.png)

**Cell 7: Stokes Solve** — Velocity magnitude & pressure (isothermal, constant viscosity)
![cell7_stokes_solve](cell7_stokes_solve.png)

**Cell 8: Isothermal Filling Pipeline** — 10 timesteps
![cell8_filling_isothermal](cell8_filling_isothermal.png)

**Cell 9: Cross-WLF Viscosity** — log10(viscosity) and log10(shear rate) distributions
![cell9_cross_wlf](cell9_cross_wlf.png)

**Cell 10: Thermal Coupling** — Temperature at final vs initial time
![cell10_thermal](cell10_thermal.png)

**Cell 11: VOF Fill Front** — Fill fraction advancing from inlet over 20 timesteps
![cell11_vof](cell11_vof.png)
