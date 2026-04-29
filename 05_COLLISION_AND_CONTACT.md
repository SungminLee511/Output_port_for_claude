# SOFA - Collision Detection & Contact Response

**Source:** `Sofa/Component/Collision/`

---

## Pipeline Overview

SOFA uses a multi-phase collision pipeline:

```
1. Broad Phase  →  candidate pairs (AABB overlap)
2. Narrow Phase →  exact contact points (geometry tests)
3. Contact Response → forces or constraints to resolve penetration
```

Orchestrated by `CollisionPipeline` (the animation loop calls it each step).

---

## 1. Collision Geometry (`Geometry/`)

Geometric primitives that wrap the mechanical model for collision.

| Primitive | Class | Dimension | Notes |
|-----------|-------|-----------|-------|
| Point | `PointCollisionModel` | 0D | Vertex-based |
| Line/Edge | `LineCollisionModel` | 1D | Edge segments |
| Triangle | `TriangleCollisionModel` | 2D | Surface triangles |
| Sphere | `SphereCollisionModel` | 0D | Per-vertex radius |
| Cylinder | `CylinderCollisionModel` | 1D | Capsule-like |
| Cube (AABB) | `CubeCollisionModel` | 3D | Axis-aligned bounding box |
| Tetrahedron | `TetrahedronCollisionModel` | 3D | Volumetric |
| Ray | `RayCollisionModel` | 1D | For picking/haptics |
| TriangleOctree | `TriangleOctreeCollisionModel` | 2D | Octree-accelerated triangles |

Each collision model references a `MechanicalState` (the DOFs) and builds a bounding volume hierarchy.

---

## 2. Broad Phase — Detection/Algorithm

Fast elimination of non-colliding pairs using bounding volumes.

| Algorithm | Class | Complexity | Notes |
|-----------|-------|------------|-------|
| Brute Force | `BruteForceBroadPhase` | O(n^2) | Tests all pairs. Simple baseline. |
| Direct SAP | `DirectSAP` | O(n log n) | Sweep-and-Prune along 3 axes |
| Incremental SAP | `IncrSAP` | O(n + k) | Maintains sorted lists frame-to-frame. Best for coherent motion. |
| Ray Trace | `RayTraceDetection` | O(n) | Ray casting for specific queries |

### Sweep-and-Prune (SAP) Theory

Project AABBs onto each axis. Sort endpoints. Overlapping intervals on ALL 3 axes → candidate pair.

```
For each axis (X, Y, Z):
    Sort AABB min/max endpoints
    Scan: if min_A < max_B and min_B < max_A → overlap on this axis
Pair overlaps on all 3 axes → broad phase hit
```

Incremental SAP maintains sorted lists and only processes changes (insertions/removals of overlaps).

---

## 3. Narrow Phase — Detection/Algorithm

Exact geometric intersection tests on candidate pairs from broad phase.

| Algorithm | Class | Notes |
|-----------|-------|-------|
| BVH Narrow Phase | `BVHNarrowPhase` | Bounding volume hierarchy traversal |
| Direct SAP Narrow Phase | `DirectSAPNarrowPhase` | SAP-based narrow phase |
| Ray Trace Narrow Phase | `RayTraceNarrowPhase` | Ray-based |

---

## 4. Intersection Tests — Detection/Intersection

Compute actual contact points, normals, and penetration depths.

| Intersection | Class | Type | Notes |
|-------------|-------|------|-------|
| Discrete | `DiscreteIntersection` | Static | Point-in-time overlap test |
| Min Proximity | `MinProximityIntersection` | Proximity | Alarm distance + contact distance |
| New Proximity | `NewProximityIntersection` | Proximity | Improved proximity tests |
| Local Min Distance | `LocalMinDistance` | Proximity | Per-element minimum distance |
| CCD Tight Inclusion | `CCDTightInclusionIntersection` | Continuous | **Continuous collision detection** — no tunneling |

### Proximity Intersection Theory

Instead of testing exact intersection, uses two distance thresholds:

```
d_alarm > d_contact > 0
```

- `d < d_alarm`: enter narrow phase (broad phase reports pair)
- `d < d_contact`: generate contact (create constraint/force)
- `d = 0`: actual penetration

This allows response BEFORE penetration occurs (more stable).

### Supported Primitive Pairs

Intersection tests exist for combinations:
- Point-Point, Point-Line, Point-Triangle
- Line-Line, Line-Triangle
- Triangle-Triangle
- Sphere-Point, Sphere-Triangle
- Tetrahedron-Point
- Ray-Triangle, Ray-Sphere

### Continuous Collision Detection (CCD)

`CCDTightInclusionIntersection` implements the Tight Inclusion CCD method:
- Tests if two moving primitives intersect during the time interval [t, t+dt]
- Prevents tunneling (thin objects passing through each other)
- More expensive than discrete tests but physically correct

---

## 5. Contact Response (`Response/`)

### Contact Mappers (`Response/Mapper/`)

Map contact points (which may be at arbitrary positions on surfaces) to the mechanical DOFs:

| Mapper | Description |
|--------|-------------|
| `BarycentricContactMapper` | Barycentric interpolation within elements |
| `IdentityContactMapper` | 1:1 mapping (contact point = DOF) |
| `RigidContactMapper` | For rigid bodies |
| `SubsetContactMapper` | Subset of existing DOFs |
| `TetrahedronBarycentricContactMapper` | Barycentric within tetrahedra |

### Contact Models (`Response/Contact/`)

How the contact is enforced mechanically:

#### Penalty-Based

| Contact | Description | Equation |
|---------|-------------|----------|
| `BarycentricPenalityContact` | Penalty spring at contact | `f = k * penetration` |
| `PenalityContactForceField` | Force field implementation | Adds penalty forces |

**Theory:** Place a virtual spring at each contact point:
```
f_N = k_N * max(0, -gap)    (normal force, proportional to penetration)
```

**Pros:** Simple, no system modification.
**Cons:** Penetration always occurs; stiff penalty → ill-conditioning.

#### Constraint-Based (Lagrangian)

| Contact | Description |
|---------|-------------|
| `FrictionContact` | Coulomb friction constraint |
| `BarycentricStickContact` | Bilateral (glue) constraint |
| `StickContactConstraint` | Stick constraint variant |
| `AugmentedLagrangianResponse` | Augmented Lagrangian contact |

**Theory (Signorini + Coulomb):**

Normal contact (Signorini conditions):
```
gap >= 0        (no penetration)
lambda_N >= 0   (repulsive normal force only)
gap * lambda_N = 0  (complementarity)
```

Friction (Coulomb's law):
```
||f_T|| <= mu * f_N           (friction cone)
||f_T|| < mu * f_N → v_T = 0  (stick)
||f_T|| = mu * f_N → v_T = -alpha * f_T  (slip)
```

Solved via the **constraint solver** (see Constraint module).

#### Rule-Based Manager

`RuleBasedContactManager`: Selects contact response type based on collision model pair. E.g., use penalty for rigid-rigid, Lagrangian for deformable-rigid.

---

## 6. Constraint Framework (`Constraint/`)

### Lagrangian Constraint Architecture

SOFA's Lagrangian constraint framework uses the **compliance formulation**:

```
1. Free motion:     M*a_free = f    →  x_free, v_free (ignoring constraints)
2. Constraint:      H * lambda = delta_v  (constraint violation correction)
3. Correction:      v = v_free + W * lambda   (W = compliance matrix = H * A^{-1} * H^T)
```

Where:
- `H` = constraint Jacobian (maps DOF velocities to constraint space)
- `lambda` = Lagrange multipliers (constraint forces)
- `W` = Delassus operator / compliance matrix

### Constraint Solvers (`Lagrangian/Solver/`)

| Solver | Algorithm | Notes |
|--------|-----------|-------|
| `GenericConstraintSolver` | Gauss-Seidel on W | **Primary solver.** Iterative resolution of constraint problem. |
| `BlockGaussSeidelConstraintSolver` | Block GS | Groups constraints into blocks |
| `LCPConstraintSolver` | Linear Complementarity Problem | For unilateral contact (Signorini) |
| `NNCGConstraintSolver` | Nonlinear NCG | Nonlinear conjugate gradient variant |
| `ImprovedJacobiConstraintSolver` | Improved Jacobi | Parallel-friendly |
| `UnbuiltConstraintSolver` | Unbuilt W | Doesn't assemble full W matrix (memory efficient) |

### GenericConstraintSolver Detail

The main algorithm:
```
1. Compute free motion (ODE solve without constraints)
2. Compute constraint violations delta
3. Build compliance matrix W = H * A^{-1} * H^T
4. Solve: W * lambda = delta  subject to constraint laws
   - Gauss-Seidel iteration (process one constraint at a time)
   - Each constraint applies its own resolution law (bilateral, unilateral, friction)
5. Apply corrections: dx = A^{-1} * H^T * lambda
```

### Constraint Types (`Lagrangian/Model/`)

| Constraint | Type | Equation |
|------------|------|----------|
| `BilateralLagrangianConstraint` | Equality | `g(x) = 0` (rigid attachment) |
| `UnilateralLagrangianConstraint` | Inequality | `g(x) >= 0, lambda >= 0` (contact) |
| `SlidingLagrangianConstraint` | Mixed | Slide along edge/surface |
| `StopperLagrangianConstraint` | Inequality | Limit joint range |
| `FixedLagrangianConstraint` | Equality | Fix DOFs via Lagrange multipliers |
| `UniformLagrangianConstraint` | Equality | Uniform constraint on DOFs |
| `AugmentedLagrangianConstraint` | Augmented | `g(x) = 0` with penalty regularization |

### Constraint Corrections (`Lagrangian/Correction/`)

Compute `A^{-1} * H^T * lambda` efficiently:

| Correction | Method |
|------------|--------|
| `GenericConstraintCorrection` | Uses the associated linear solver |
| `LinearSolverConstraintCorrection` | Direct use of linear solver's factorization |
| `PrecomputedConstraintCorrection` | Pre-inverts compliance offline |
| `UncoupledConstraintCorrection` | Diagonal approximation (fast but less accurate) |

### Projective Constraints (`Projective/`)

Direct modification of the system (not Lagrange multipliers):

| Constraint | Description |
|------------|-------------|
| `FixedProjectiveConstraint` | Zero displacement (Dirichlet BC) |
| `FixedPlaneProjectiveConstraint` | Fix DOFs on a plane |
| `PartialFixedProjectiveConstraint` | Fix some components only |
| `LinearMovementProjectiveConstraint` | Prescribed displacement over time |
| `LinearVelocityProjectiveConstraint` | Prescribed velocity |
| `AttachProjectiveConstraint` | Attach two objects (shared DOFs) |
| `PositionBasedDynamicsProjectiveConstraint` | PBD-style constraint |
| `SkeletalMotionProjectiveConstraint` | Skeletal animation driving |
| `DirectionProjectiveConstraint` | Constrain to move along a direction |
| `ProjectToPlaneConstraint` | Project onto plane |
| `ProjectToLineConstraint` | Project onto line |
| `ProjectToPointConstraint` | Project onto point |

Projective constraints work by zeroing rows/columns in the system matrix and modifying the RHS.

---

## Full Collision Pipeline Flow

```
AnimationStep:
│
├── 1. computeCollision()
│   ├── Broad Phase: identify candidate pairs (SAP/BruteForce)
│   ├── Narrow Phase: compute exact contacts (BVH traversal)
│   └── Create Contact objects (penalty forces or Lagrangian constraints)
│
├── 2. freeMotion() [if using constraint-based]
│   ├── ODE solver computes free position/velocity (no contact)
│   └── Assemble constraint Jacobian H
│
├── 3. solveConstraints()
│   ├── Build compliance W = H * A^{-1} * H^T
│   ├── Gauss-Seidel: find lambda satisfying Signorini + Coulomb
│   └── Apply correction: dx = A^{-1} * H^T * lambda
│
└── 4. Update positions, velocities
```
