# SOFA Framework Analysis — 2026-04-29 12:16 KST

8 markdown documents analyzing the SOFA v25.12.00 codebase.

---

## 01 - Folder Structure
Full directory tree analysis of the 600MB repo. Core framework, components, plugins, examples.

[01_FOLDER_STRUCTURE.md](01_FOLDER_STRUCTURE.md)

---

## 02 - ODE Solvers & Time Integration
All 11 ODE solvers: Euler explicit/implicit, Newmark, BDF, CentralDifference, RK2/4, Static, VariationalSymplectic. Full equations.

[02_ODE_SOLVERS_AND_TIME_INTEGRATION.md](02_ODE_SOLVERS_AND_TIME_INTEGRATION.md)

---

## 03 - Solid Mechanics & FEM
Linear elastic (corotational, tet, hex, tri, beam) + hyperelastic (NeoHookean, MooneyRivlin, Ogden, Costa, etc.). Strain energy functions and SPK tensors.

[03_SOLID_MECHANICS_AND_FEM.md](03_SOLID_MECHANICS_AND_FEM.md)

---

## 04 - Linear Solvers
Direct (LDL, LU, Cholesky, SVD), iterative (CG, PCG, MINRES), preconditioners (Jacobi, SSOR, Warp), ordering (AMD, COLAMD).

[04_LINEAR_SOLVERS.md](04_LINEAR_SOLVERS.md)

---

## 05 - Collision & Contact
Full pipeline: broad phase (SAP), narrow phase (BVH), intersection tests (proximity, CCD), response (penalty, Lagrangian friction, Signorini+Coulomb).

[05_COLLISION_AND_CONTACT.md](05_COLLISION_AND_CONTACT.md)

---

## 06 - Mass, Loads, Mappings & Simulation Loop
Mass types, external loads, multi-model mappings, animation loop, topology, diffusion.

[06_MASS_LOADS_MAPPINGS_AND_SIMULATION_LOOP.md](06_MASS_LOADS_MAPPINGS_AND_SIMULATION_LOOP.md)

---

## 07 - Plugins
SofaCUDA, SofaOpenCL, MultiThreading, EulerianFluid, DistanceGrid, ImplicitField, ArticulatedSystem, Carving, Haptics, PARDISO.

[07_PLUGINS.md](07_PLUGINS.md)

---

## 08 - SOFA vs Mesh_Solver Comparison
Side-by-side comparison: elements, materials, solvers, contact, I/O, GPU, performance, when to use each.

[08_COMPARISON_SOFA_VS_MESH_SOLVER.md](08_COMPARISON_SOFA_VS_MESH_SOLVER.md)
