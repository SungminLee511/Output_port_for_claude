# SOFA - Mass, Loads, Mappings & Simulation Loop

**Source:** `Sofa/Component/Mass/`, `MechanicalLoad/`, `Mapping/`, `AnimationLoop/`

---

## 1. Mass Models (`Mass/`)

Mass defines the inertia matrix M in `M*a = f`.

| Mass Type | Class | Description |
|-----------|-------|-------------|
| Diagonal Mass | `DiagonalMass` | Lumped mass. M is diagonal. Each node gets `m_i = rho * V_i / n_nodes`. Cheapest. |
| Uniform Mass | `UniformMass` | Same mass for every node. M = m * I. Simplest. |
| Mesh Matrix Mass | `MeshMatrixMass` | Consistent mass matrix from FEM shape functions. M is sparse, non-diagonal. Most accurate. |

### Consistent vs Lumped Mass

**Consistent (MeshMatrixMass):**
```
M_ij = integral(rho * N_i * N_j * dV)
```
Non-diagonal, couples neighboring nodes. Better accuracy for wave propagation and eigenvalue problems.

**Lumped (DiagonalMass):**
```
M_ii = sum_j M_ij^consistent    (row-sum lumping)
```
Diagonal → trivial inversion → no linear solver needed for explicit methods.

**Rigid Mass** (`RigidMassType`): 6x6 mass matrix (3 translational + 3 rotational inertia).

---

## 2. Mechanical Loads (`MechanicalLoad/`)

External forces applied to the system.

| Load | Description | Equation |
|------|-------------|----------|
| `Gravity` | Uniform gravity | `f_i = m_i * g` |
| `ConstantForceField` | Constant force on nodes | `f_i = F` (user-specified) |
| `LinearForceField` | Time-varying force | `f(t) = f_0 + t * df/dt` |
| `SurfacePressureForceField` | Pressure on surface | `f = p * n * A` (follower force) |
| `TaitSurfacePressureForceField` | Tait equation pressure | `p = p0 * ((V0/V)^gamma - 1)` (closed volume) |
| `TrianglePressureForceField` | Pressure on triangles | Distributed to triangle nodes |
| `QuadPressureForceField` | Pressure on quads | Distributed to quad nodes |
| `EdgePressureForceField` | Force along edges | Line load |
| `TorsionForceField` | Torque | `tau = T * r x n` |
| `OscillatingTorsionPressureForceField` | Oscillating torque | Time-periodic torsion |
| `PlaneForceField` | Half-space repulsion | `f = k * max(0, -d)` (floor contact) |
| `SphereForceField` | Sphere repulsion | Pushes nodes out of sphere |
| `EllipsoidForceField` | Ellipsoid repulsion | Pushes out of ellipsoid |
| `ConicalForceField` | Cone repulsion | Pushes out of cone |
| `DiagonalVelocityDampingForceField` | Per-axis damping | `f = -c_i * v_i` (different per axis) |
| `UniformVelocityDampingForceField` | Uniform damping | `f = -c * v` |

### Follower Forces

`SurfacePressureForceField` is a **follower force**: the force direction changes with deformation (tracks surface normal). This contributes to the tangent stiffness:
```
K_pressure = d(p*n*A)/dx ≠ 0
```
Important for stability of pressure-loaded structures (e.g., inflatable objects).

---

## 3. Mappings (`Mapping/`)

Mappings connect DOFs at different levels of the scene graph. They propagate positions downward and forces upward.

### Theory

A mapping `phi` relates a parent (coarse) state `X` to a child (fine) state `x`:
```
x = phi(X)          (position mapping)
v = J * V           (velocity mapping, J = d(phi)/dX is the Jacobian)
F_parent += J^T * f_child   (force mapping, transpose)
```

For the stiffness:
```
K_parent += J^T * K_child * J + geometric_stiffness
```

### Linear Mappings (`Linear/`)

| Mapping | Description |
|---------|-------------|
| `BarycentricMapping` | Barycentric coordinates within elements. Most general. |
| `IdentityMapping` | 1:1 correspondence (x = X) |
| `SubsetMapping` | Child is a subset of parent nodes |
| `SkinningMapping` | Skeleton-based (bone weights) |
| `BeamLinearMapping` | Points along beam elements |
| `CenterOfMassMapping` | Maps to center of mass |
| `DeformableOnRigidFrameMapping` | Deformable + rigid coupling |
| `LineSetSkinningMapping` | Skinning along line set |
| `TubularMapping` | Maps tube surface from centerline |
| `LinearMapping` | General linear J |
| `IdentityMultiMapping` | Identity for multi-models |
| `SubsetMultiMapping` | Subset for multi-models |
| `DistanceToPlaneMapping` | Signed distance to plane |

### Non-Linear Mappings (`NonLinear/`)

| Mapping | Description | Jacobian |
|---------|-------------|----------|
| `RigidMapping` | Rigid body transform | `J = [I, -[r]x]` (rotation contribution) |
| `DistanceMapping` | Edge lengths | `J_ij = (x_i - x_j) / ||x_i - x_j||` |
| `DistanceFromTargetMapping` | Distance to target points | Similar to above |
| `SquareDistanceMapping` | Squared edge lengths | `J = 2*(x_i - x_j)` |
| `SquareMapping` | Square of input | `J = 2*x` |
| `AreaMapping` | Triangle areas | Derivative of cross product |
| `VolumeMapping` | Tetrahedron volumes | Derivative of triple product |
| `DistanceMultiMapping` | Multi-model distance | Cross-model Jacobian |

### Multi-Model Architecture

SOFA's key strength: **multiple representations of the same object**:

```
                FEM Model (coarse tet mesh)
                    |
         ┌─────────┼──────────┐
         ↓         ↓          ↓
   Visual Model  Collision  Haptic
  (fine surface)  (surface)  (proxy)
```

Each level connected by a Mapping:
- FEM mesh (mechanical): coarse, drives physics
- Visual mesh: fine, for rendering (BarycentricMapping from FEM)
- Collision mesh: medium, for contact detection (BarycentricMapping)
- Haptic proxy: single point, for haptic device (RigidMapping)

---

## 4. Animation Loop (`AnimationLoop/`)

The top-level simulation controller. Defines the order of operations per step.

### DefaultAnimationLoop (implicit in framework)

```
1. beginStep(dt)
2. computeCollision()           // collision pipeline
3. computeForces()              // accumulate f = f_ext + f_int
4. solve()                      // ODE solver → linear system → linear solver
5. mechanicalIntegration()      // update x, v
6. endStep()
```

### FreeMotionAnimationLoop (for constraint-based contact)

```
1. beginStep(dt)
2. computeCollision()
3. freeMotion()                 // solve without constraints → x_free, v_free
4. computeConstraints()         // build H, compute violations
5. solveConstraints()           // find lambda via GenericConstraintSolver
6. applyCorrections()           // x = x_free + correction
7. endStep()
```

This is the **corrective motion** approach:
- Step 1: Predict (ignore constraints)
- Step 2: Correct (apply constraint forces to eliminate violations)

---

## 5. State Container (`StateContainer/`)

### MechanicalObject

The central DOF container. Stores:

| Vector | Symbol | Description |
|--------|--------|-------------|
| position | `x` | Current positions |
| velocity | `v` | Current velocities |
| force | `f` | Accumulated forces |
| rest position | `x0` | Reference configuration |
| free position | `xfree` | Position after free motion (before constraints) |
| free velocity | `vfree` | Velocity after free motion |
| dx | `dx` | Position correction |

Supports multiple DOF types: `Vec3d`, `Vec3f`, `Vec2d`, `Vec1d`, `Rigid3d`, `Rigid3f`.

---

## 6. Diffusion (`Diffusion/`)

### TetrahedronDiffusionFEMForceField

Solves the heat/diffusion equation on tet meshes:
```
dT/dt = nabla . (D * nabla T)
```

Discretized via FEM:
```
C * dT/dt + K_diff * T = 0
```
Where:
- `C` = capacity matrix (analogous to mass matrix)
- `K_diff` = diffusion stiffness matrix
- `D` = diffusivity tensor

Used with 1st-order implicit Euler for stability:
```
(C + h * K_diff) * T_{n+1} = C * T_n
```

---

## 7. Topology (`Topology/`)

### Container Types

| Topology | Description |
|----------|-------------|
| `MeshTopology` (Constant) | Static mesh, immutable |
| `PointSetTopologyContainer` | Dynamic point set |
| `EdgeSetTopologyContainer` | Dynamic edges |
| `TriangleSetTopologyContainer` | Dynamic triangles |
| `QuadSetTopologyContainer` | Dynamic quads |
| `TetrahedronSetTopologyContainer` | Dynamic tetrahedra |
| `HexahedronSetTopologyContainer` | Dynamic hexahedra |
| `RegularGridTopology` | Regular Cartesian grid |
| `SparseGridTopology` | Adaptive sparse grid (voxelization) |
| `CylinderGridTopology` | Cylindrical grid |

### Dynamic Topology

Supports runtime mesh modification:
- Point/element addition/removal
- Topology events propagated to all components
- Used for cutting, tearing, remeshing

### Topology Mappings

Convert between topology levels:
- `Hexa2TetraTopologicalMapping`: Split hexahedra into tetrahedra
- `Quad2TriangleTopologicalMapping`: Split quads into triangles
- `Tetra2TriangleTopologicalMapping`: Extract surface from volume
