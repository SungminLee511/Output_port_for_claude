# SOFA Framework v25.12.00 - Folder Structure Analysis

**Repo:** https://github.com/sofa-framework/sofa (tag: v25.12.00)
**Local:** `/home/SOLVERX/sofa/src/`
**Size:** ~599 MB

---

## Top-Level Layout

```
sofa/src/
├── Sofa/                    # Core framework + all physics components
│   ├── framework/           # Low-level foundation (types, math, simulation engine)
│   ├── Component/           # All physics modules (FEM, collision, solvers, etc.)
│   └── GL/                  # OpenGL rendering layer
│       └── Component/       # GL visual components
│       └── Sofa.GL_test/    # GL test suite
│
├── applications/            # End-user applications and plugins
│   ├── guis/                # GUI frontends
│   ├── plugins/             # Optional plugin modules (~30+)
│   └── projects/            # Standalone executables (runSofa, Modeler, etc.)
│
├── examples/                # Scene files and tutorials
│   ├── Benchmark/           # Performance benchmarks
│   ├── Component/           # Per-component example scenes
│   ├── Demos/               # Full demo scenes
│   ├── Objects/             # Object-level examples
│   ├── SimpleAPI/           # SimpleAPI usage examples
│   └── Tutorials/           # Step-by-step tutorials
│
├── extlibs/                 # Vendored external libraries
│   ├── difflib/             # Diff utilities
│   └── stb/                 # stb single-header libs (image I/O)
│
├── cmake/                   # CMake build modules
├── scripts/                 # Build/utility scripts
├── share/                   # Shared resources
├── tools/                   # Developer tools
│
├── CMakeLists.txt           # Root build file
├── CMakePresets.json         # CMake presets
├── flake.nix / flake.lock   # Nix build support
└── package.nix
```

---

## Sofa/framework/ - Foundation Layer

The lowest layer. Everything else depends on this.

```
framework/
├── Config/          # Build configuration, platform detection
├── Type/            # Basic types: Vec, Mat, Quat, fixed_array, RGBAColor
├── DefaultType/     # Mechanical DOF types: Vec3d, Vec3f, Rigid3d, Rigid3f
├── Helper/          # Logging, file system, factory, random, TagFactory
├── Geometry/        # Geometric primitives: Triangle, Tetrahedron, Hexahedron, Edge
├── Topology/        # Topology data structures (abstract)
├── LinearAlgebra/   # Matrix types: CompressedRowSparse, BlockDiag, FullMatrix, EigenSparse
├── Core/            # Object model: BaseObject, DataEngine, ObjectFactory, CollisionModel, Behavior
├── Simulation/      # Simulation loop, DAG/tree graph, visitors
│   ├── Common/      # Common simulation utilities
│   ├── Core/        # Core simulation (Node, DAGNode)
│   └── Graph/       # Scene graph implementation (DAGSimulation)
├── SimpleApi/       # Simplified scene creation API
├── Framework/       # Meta-package aggregating all framework modules
└── Testing/         # Test infrastructure (GTest integration)
```

**Key design:** SOFA uses a **scene graph** (DAG) where each node owns mechanical states, force fields, solvers, constraints, and mappings. The `Core/` module defines the abstract interfaces; `Simulation/` runs the graph traversal via **visitors**.

---

## Sofa/Component/ - Physics & Algorithm Library

All physics modules live here. This is the bulk of the codebase.

```
Component/
├── AnimationLoop/       # Top-level simulation loop controllers
├── ODESolver/           # Time integration schemes
│   ├── Forward/         # Explicit methods (Euler, RK2, RK4, CentralDifference)
│   └── Backward/        # Implicit methods (EulerImplicit, Newmark, BDF, NR, Static, VariationalSymplectic)
│
├── LinearSolver/        # Linear system solvers
│   ├── Direct/          # LDL, LLT, LU, QR, SVD, Cholesky, BTD, Async variants
│   ├── Iterative/       # CG, PCG, MinRes, ShewchukPCG, MatrixFree
│   ├── Ordering/        # Reordering: AMD, COLAMD, Natural
│   └── Preconditioner/  # Jacobi, BlockJacobi, SSOR, Warp, PrecomputedWarp
│
├── LinearSystem/        # Global linear system assembly
│
├── SolidMechanics/      # Deformable body physics
│   ├── FEM/
│   │   ├── Elastic/     # Linear elastic FEM (Tet, Hex, Tri, Quad, Beam, Corotational)
│   │   ├── HyperElastic/# Nonlinear hyperelastic (NeoHookean, MooneyRivlin, Ogden, Costa, etc.)
│   │   └── NonUniform/  # Spatially varying material FEM
│   ├── Spring/          # Spring-based force fields (20+ types)
│   └── TensorMass/      # Tensor-mass formulation
│
├── Mass/                # Mass models
│                        #   DiagonalMass, UniformMass, MeshMatrixMass
│
├── MechanicalLoad/      # External loads
│                        #   Gravity, ConstantForce, SurfacePressure, Torsion,
│                        #   EdgePressure, TrianglePressure, Damping, etc.
│
├── Constraint/          # Boundary conditions & constraints
│   ├── Projective/      # Direct projection (FixedConstraint, LinearMovement, Attach, etc.)
│   └── Lagrangian/      # Lagrange multiplier framework
│       ├── Model/       # Constraint types (Bilateral, Unilateral, Sliding, Stopper, AugLag)
│       ├── Solver/      # Constraint solvers (GaussSeidel, LCP, NNCG, BlockGS)
│       └── Correction/  # Constraint correction (Generic, LinearSolver, Precomputed, Uncoupled)
│
├── Collision/           # Collision detection & response
│   ├── Detection/
│   │   ├── Algorithm/   # Broad phase (BruteForce, SAP, IncrSAP) + Narrow phase (BVH, RayTrace)
│   │   └── Intersection/# Intersection tests (Discrete, Proximity, LocalMinDist, CCD)
│   ├── Geometry/        # Collision primitives (Point, Line, Triangle, Sphere, Cylinder, Cube, Tet, Ray)
│   └── Response/
│       ├── Contact/     # Contact handling (Penalty, Friction, Stick, AugLag, RuleBasedManager)
│       └── Mapper/      # Contact mappers (Barycentric, Identity, Rigid, Subset)
│
├── Mapping/             # DOF mappings between mechanical models
│   ├── Linear/          # Barycentric, Identity, Skinning, Beam, Subset, CenterOfMass, etc.
│   ├── NonLinear/       # Rigid, Distance, Area, Volume, Square mappings
│   └── MappedMatrix/    # Mapped matrix assembly
│
├── Topology/            # Mesh topology management
│   ├── Container/
│   │   ├── Constant/    # Static topology (MeshTopology)
│   │   ├── Dynamic/     # Dynamic topology (PointSet, EdgeSet, TriangleSet, QuadSet, TetraSet, HexaSet)
│   │   └── Grid/        # Grid topologies (Regular, Sparse, Cylinder)
│   ├── Mapping/         # Topology-to-topology mappings (Hexa2Tet, Quad2Tri, Tetra2Tri, etc.)
│   └── Utility/         # Topology utilities (TopologicalChangeProcessor)
│
├── Diffusion/           # Heat diffusion FEM (TetrahedronDiffusionFEMForceField)
│
├── Engine/              # Data processing engines
│   ├── Analyze/         # Analysis engines
│   ├── Generate/        # Generation engines (MeshGeneration, etc.)
│   ├── Select/          # Selection engines (BoxROI, SphereROI, etc.)
│   └── Transform/       # Transform engines
│
├── IO/                  # File I/O
│   └── Mesh/            # Mesh file readers (VTK, STL, OBJ, GMSH, etc.)
│
├── StateContainer/      # MechanicalObject (holds DOF state vectors: x, v, f)
├── Controller/          # User interaction controllers
├── Haptics/             # Haptic device integration
├── Playback/            # Simulation recording/playback
├── SceneUtility/        # Scene helpers (InfoComponent, APIVersion)
├── Setting/             # Global settings
└── Visual/              # Visual models (OglModel, etc.)
```

---

## applications/ - Plugins & Executables

```
applications/
├── guis/                         # GUI implementations
├── projects/
│   ├── runSofa/                  # Main simulation runner
│   ├── Modeler/                  # Visual scene editor
│   ├── SofaPhysicsAPI/           # C API for external integration
│   ├── SceneChecking/            # Scene validation
│   └── sofaProjectExample/       # Plugin template
│
└── plugins/
    ├── SofaCUDA/                 # CUDA GPU acceleration
    ├── SofaOpenCL/               # OpenCL GPU acceleration
    ├── MultiThreading/           # Parallel execution
    ├── SofaDistanceGrid/         # Distance field collision
    ├── SofaEulerianFluid/        # Eulerian fluid simulation
    ├── SofaImplicitField/        # Implicit surface representation
    ├── SofaCarving/              # Real-time mesh carving
    ├── SofaMatrix/               # Matrix export/debug
    ├── SofaPardisoSolver/        # Intel PARDISO direct solver
    ├── SofaNewmat/               # Newmat matrix library bridge
    ├── DiffusionSolver/          # Diffusion equation plugin
    ├── ArticulatedSystemPlugin/  # Articulated body dynamics
    ├── CollisionOBBCapsule/      # OBB and capsule collision
    ├── BulletCollisionDetection/ # Bullet physics collision
    ├── PersistentContact/        # Persistent contact tracking
    ├── CImgPlugin/               # CImg image processing
    ├── VolumetricRendering/      # Volume rendering
    ├── image/                    # Image processing plugin
    ├── HeadlessRecorder/         # Offscreen rendering
    ├── SceneCreator/             # Programmatic scene creation
    ├── SofaTest/                 # Test framework plugin
    ├── Geomagic/                 # Geomagic haptic device
    ├── Haption/                  # Haption haptic device
    ├── Sensable/                 # Sensable haptic device
    ├── LeapMotion/               # Leap Motion controller
    ├── SixenseHydra/             # Razer Hydra controller
    ├── Xitact/                   # Xitact haptic device
    └── SofaHAPI/                 # HAPI haptic abstraction
```

---

## Module Dependency Flow

```
Type → DefaultType → Helper → Geometry → Topology (framework)
                                   ↓
                            LinearAlgebra
                                   ↓
                                Core (ObjectModel, Behavior, CollisionModel)
                                   ↓
                              Simulation (DAG graph, visitors)
                                   ↓
                    ┌──────────────┼──────────────────┐
                    ↓              ↓                  ↓
              Component/*     GL/Component      applications/*
```

---

## Key Architectural Patterns

1. **Scene Graph (DAG):** Simulation is a directed acyclic graph. Each node can hold MechanicalObject (state), ForceField, Solver, Constraint, Mapping. Visitors traverse the graph to assemble/solve.

2. **Multi-model:** A single scene can contain multiple mechanical models at different resolutions (visual mesh, collision mesh, FEM mesh) linked via Mappings.

3. **Visitor Pattern:** ODE solvers trigger visitors (MechanicalComputeForceVisitor, MechanicalIntegrationVisitor, etc.) that walk the graph to accumulate forces, assemble matrices, and propagate states.

4. **Plugin Architecture:** Everything is a plugin. Components register via `ObjectFactory`. Plugins can be loaded at runtime.

5. **Template Mechanism:** Most components are C++ templates parameterized by DOF type (`Vec3d`, `Vec3f`, `Rigid3d`, etc.), allowing the same algorithm for different data types.
