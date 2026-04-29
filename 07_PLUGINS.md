# SOFA - Plugin Analysis

**Source:** `applications/plugins/`

---

## Overview

SOFA has ~30 optional plugins. They extend the core with GPU acceleration, fluid dynamics, advanced collision, haptics, and more. Loaded at runtime via the plugin system.

---

## GPU Acceleration

### SofaCUDA

**The most comprehensive plugin.** CUDA implementations of nearly every core component.

| Category | CUDA Components |
|----------|----------------|
| State | `CudaMechanicalObject` — DOF storage on GPU |
| FEM Elastic | `CudaTetrahedronFEMForceField`, `CudaHexahedronFEMForceField`, `CudaTriangularFEMForceFieldOptim` |
| FEM Hyperelastic | `CudaStandardTetrahedralFEMForceField` |
| Springs | `CudaSpringForceField` |
| TensorMass | `CudaTetrahedralTensorMassForceField` |
| Mass | `CudaDiagonalMass`, `CudaUniformMass`, `CudaMeshMatrixMass` |
| Loads | `CudaConstantForceField`, `CudaLinearForceField`, `CudaPlaneForceField`, `CudaSphereForceField`, `CudaEllipsoidForceField` |
| Collision Geometry | `CudaPointModel`, `CudaLineModel`, `CudaTriangleModel`, `CudaSphereModel` |
| Collision Response | `CudaPenalityContactForceField` |
| Mapping Linear | `CudaBarycentricMapping`, `CudaIdentityMapping`, `CudaSubsetMapping`, `CudaBeamLinearMapping`, `CudaSubsetMultiMapping` |
| Mapping NonLinear | `CudaRigidMapping` |
| Constraints | `CudaFixedProjectiveConstraint`, `CudaLinearMovementProjectiveConstraint` |

**Architecture:** Each Cuda component wraps the CPU component and replaces inner loops with CUDA kernels. The `CudaMechanicalObject` keeps DOF vectors in GPU memory, avoiding host-device transfers.

**Use case:** Large deformable body simulations (soft tissue, cloth) where the number of elements justifies GPU overhead.

### SofaOpenCL

OpenCL counterpart to SofaCUDA. Less comprehensive but vendor-agnostic (AMD, Intel, NVIDIA). Similar component structure.

---

## Parallel Computing

### MultiThreading

CPU-level parallelism for core components:

| Component | Parallel Version | Description |
|-----------|-----------------|-------------|
| `TetrahedronFEMForceField` | `ParallelTetrahedronFEMForceField` | Parallel force computation |
| `HexahedronFEMForceField` | `ParallelHexahedronFEMForceField` | Parallel hex FEM |
| `SpringForceField` | `ParallelSpringForceField` | Parallel spring forces |
| `StiffSpringForceField` | `ParallelStiffSpringForceField` | Parallel damped springs |
| `MeshSpringForceField` | `ParallelMeshSpringForceField` | Parallel mesh springs |
| `CGLinearSolver` | `ParallelCGLinearSolver` | Parallel CG (sparse mat-vec) |
| `BruteForceBroadPhase` | `ParallelBruteForceBroadPhase` | Parallel broad phase |
| `BVHNarrowPhase` | `ParallelBVHNarrowPhase` | Parallel narrow phase |
| Animation Loop | `AnimationLoopParallelScheduler` | Multi-scene parallel execution |
| Beam Mapping | `BeamLinearMapping_mt` | Parallel beam mapping |
| Matrix | `ParallelCompressedRowSparseMatrixMechanical` | Parallel sparse matrix ops |

Also provides:
- `DataExchange` — thread-safe data sharing between parallel scenes
- `MeanComputation` — parallel reduction
- `ParallelImplementationsRegistry` — auto-swap CPU components with parallel versions

---

## Fluid Dynamics

### SofaEulerianFluid

Eulerian (grid-based) fluid simulation:

| Component | Description |
|-----------|-------------|
| `Fluid2D` | 2D Navier-Stokes on regular grid |
| `Fluid3D` | 3D Navier-Stokes on regular grid |
| `Grid2D` | 2D MAC (Marker-and-Cell) grid |
| `Grid3D` | 3D MAC grid |

**Theory:** Incompressible Navier-Stokes on staggered grid:
```
du/dt + (u . nabla)u = -1/rho * nabla(p) + nu * nabla^2(u) + f
nabla . u = 0    (incompressibility)
```

Solved via operator splitting:
1. Advection (semi-Lagrangian)
2. External forces
3. Diffusion (implicit)
4. Pressure projection (Poisson solve for incompressibility)

### DiffusionSolver (Plugin)

Standalone diffusion equation solver:
```
dT/dt = D * nabla^2(T)
```
Separate from the core `Diffusion/` component. Plugin variant with additional features.

---

## Advanced Collision

### SofaDistanceGrid

Precomputed signed distance field (SDF) for collision:

| Component | Description |
|-----------|-------------|
| `DistanceGrid` | 3D signed distance field on regular grid |
| `DistanceGridCollisionModel` | Collision model using SDF |
| `RigidDistanceGridDiscreteIntersection` | Rigid body SDF collision |
| `FFDDistanceGridDiscreteIntersection` | Deformable (FFD) SDF collision |
| `DistanceGridForceField` | Penalty forces from SDF |
| CUDA extensions | GPU-accelerated SDF collision |

**Theory:** Precompute signed distance `d(x)` for a mesh on a regular grid. At runtime, query `d(x)` for contact points in O(1) (trilinear interpolation). Normal = `nabla(d)`. Much faster than triangle-triangle tests for complex shapes.

### CollisionOBBCapsule

Extended collision primitives:
- **OBB (Oriented Bounding Box):** Tighter fit than AABB for rotated objects
- **Capsule:** Cylinder with hemispherical caps. Natural for limbs/tubes.

Intersection tests: OBB-OBB, OBB-Triangle, Capsule-Capsule, Capsule-Triangle, etc.

### BulletCollisionDetection

Bridge to the **Bullet Physics** library for collision detection. Uses Bullet's GJK/EPA algorithms and broadphase (DBVT). For complex collision scenarios where SOFA's native detection is insufficient.

### PersistentContact

Maintains contact information across time steps:
- `PersistentFrictionContact` — friction contact with memory
- `PersistentUnilateralInteractionConstraint` — persistent Signorini constraint
- `PersistentContactMapping` — stable contact point tracking

**Why:** Standard SOFA re-detects contacts each frame. Persistent contacts avoid jitter from contact point flickering (common in Gauss-Seidel solvers).

---

## Implicit Surfaces

### SofaImplicitField

Implicit surface representation (level sets):

| Component | Description |
|-----------|-------------|
| `ScalarField` | Base scalar field interface |
| `SphericalField` | Implicit sphere: `f(x) = ||x - c|| - r` |
| `BottleField` | Klein bottle implicit surface |
| `StarShapedField` | Star-shaped implicit surface |
| `DiscreteGridField` | Sampled scalar field on grid |
| `FieldToSurfaceMesh` | Marching cubes: isosurface extraction |
| `ImplicitSurfaceMapping` | Map DOFs to implicit surface |
| `MarchingCube` | Marching cubes implementation |

**Use case:** Free-form deformation, level-set cutting, surface reconstruction.

---

## Articulated Bodies

### ArticulatedSystemPlugin

Articulated rigid body chains (skeletons):

| Component | Description |
|-----------|-------------|
| `ArticulatedHierarchyContainer` | Joint hierarchy definition |
| `ArticulatedSystemMapping` | Maps joint angles → rigid body positions |
| `ArticulatedHierarchyController` | Interactive joint control |
| `BVHLoader` | Load BVH motion capture files |

**Theory:** Forward kinematics chain. Each joint has local transform. Global pose = product of parent transforms. The `ArticulatedSystemMapping` provides the Jacobian for force propagation.

---

## Mesh Operations

### SofaCarving

Real-time mesh cutting/carving:
- `CarvingManager` — detects tool-mesh intersection, removes elements
- Uses dynamic topology (TetrahedronSetTopologyModifier) to remove tetrahedra in contact with carving tool
- Application: surgical simulation

---

## Haptic Devices

| Plugin | Device |
|--------|--------|
| `Geomagic` | 3D Systems Geomagic Touch |
| `Haption` | Haption Virtuose |
| `Sensable` | Sensable Phantom (legacy) |
| `SixenseHydra` | Razer Hydra controller |
| `LeapMotion` | Leap Motion hand tracker |
| `Xitact` | Xitact IHP haptic |
| `SofaHAPI` | HAPI abstraction layer (multiple devices) |

All haptic plugins provide:
1. Device position/force reading
2. Mapping to a proxy point in the scene
3. Force feedback computation (typically via constraint-based contact)

---

## Other Utilities

| Plugin | Description |
|--------|-------------|
| `SofaMatrix` | Export/visualize system matrices (debug/analysis) |
| `SofaPardisoSolver` | Intel MKL PARDISO direct solver (fastest for large sparse systems) |
| `SofaNewmat` | Newmat matrix library bridge |
| `CImgPlugin` | Image I/O via CImg library |
| `VolumetricRendering` | Volume rendering (CT/MRI data) |
| `HeadlessRecorder` | Offscreen rendering to video |
| `SceneCreator` | Programmatic scene construction helpers |
| `SofaTest` | Test framework extensions |
| `image` | Image processing (filtering, segmentation) |

### SofaPardisoSolver

Intel PARDISO (via MKL) — arguably the fastest sparse direct solver available:
- Multithreaded factorization
- Supports symmetric, SPD, and general matrices
- Drop-in replacement for `SparseLDLSolver`
- Requires Intel MKL installation
