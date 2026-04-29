# SOFA - Solid Mechanics & FEM Theory

**Source:** `Sofa/Component/SolidMechanics/`

---

## Overview

SOFA's solid mechanics module provides force fields (internal force computation) for deformable bodies. It covers:

1. **FEM/Elastic** - Linear elastic finite elements (small/moderate deformation)
2. **FEM/HyperElastic** - Nonlinear hyperelastic finite elements (large deformation)
3. **FEM/NonUniform** - Spatially varying material properties
4. **Spring** - Spring-based force models (mass-spring systems)
5. **TensorMass** - Tensor-mass formulation

---

## 1. Linear Elastic FEM (`FEM/Elastic/`)

### Governing Equation

Linear elasticity assumes small strains. The constitutive law (Hooke's law):

```
sigma = D : epsilon
```

Where:
- `sigma` = Cauchy stress tensor
- `epsilon` = infinitesimal strain tensor: epsilon = 1/2 (grad(u) + grad(u)^T)
- `D` = 4th-order elasticity tensor (depends on E, nu)

For isotropic materials in Voigt notation:
```
D = E/((1+nu)(1-2*nu)) * [1-nu  nu    nu    0        0        0      ]
                          [nu    1-nu  nu    0        0        0      ]
                          [nu    nu    1-nu  0        0        0      ]
                          [0     0     0     (1-2nu)/2 0       0      ]
                          [0     0     0     0    (1-2nu)/2    0      ]
                          [0     0     0     0        0    (1-2nu)/2  ]
```

### Element Types

| ForceField | Element | Nodes | Methods | Notes |
|------------|---------|-------|---------|-------|
| `TetrahedronFEMForceField` | Tet4 | 4 | Small, Large, Polar, SVD corotational | Most commonly used |
| `TetrahedralCorotationalFEMForceField` | Tet4 | 4 | Corotational only | Optimized corotational |
| `FastTetrahedralCorotationalForceField` | Tet4 | 4 | Fast corotational | GPU-friendly |
| `HexahedronFEMForceField` | Hex8 | 8 | Small, Large, Polar corotational | 8-node brick |
| `HexahedralFEMForceField` | Hex8 | 8 | Large deformation variant | Legacy |
| `TriangularFEMForceField` | Tri3 | 3 | Small, Large | 2D/shell |
| `TriangularFEMForceFieldOptim` | Tri3 | 3 | Optimized | Cache-friendly |
| `TriangularAnisotropicFEMForceField` | Tri3 | 3 | Anisotropic | Directional stiffness |
| `QuadBendingFEMForceField` | Quad4 | 4 | Bending | Plate bending |
| `BeamFEMForceField` | Beam2 | 2 | Euler-Bernoulli | 1D beam |

### Corotational Formulation

**Problem with linear FEM:** Pure rotation causes spurious strain (ghost forces).

**Solution:** Corotational method extracts rotation R from deformation gradient F, then computes forces in the corotated frame:

```
F = R * U           (polar decomposition)
epsilon_corot = U - I    (strain in material frame)
f_local = K_0 * (U - I)  (force in material frame)
f_global = R * f_local    (rotate back to world)
```

**Rotation extraction methods in SOFA:**

| Method | Description | Cost | Accuracy |
|--------|-------------|------|----------|
| `SMALL` | No rotation extraction | Cheapest | Only for small rotations |
| `LARGE` | QR decomposition | Moderate | Good |
| `POLAR` | Polar decomposition (R = F * U^{-1}) | Moderate | Good |
| `SVD` | SVD of F (handles inversions) | Expensive | Best, handles inverted elements |

**Reference:** Nesme, Payan, Faure, "Efficient, Physically Plausible Finite Elements," Eurographics 2005

### FEM Assembly

For each element e:
```
K_e = integral(B^T * D * B * dV)   (element stiffness)
f_e = K_e * u_e                     (element force)
```
Where `B` = strain-displacement matrix (shape function gradients).

For tetrahedra (constant strain): `K_e = V * B^T * D * B` (single integration point).
For hexahedra: 2x2x2 Gauss quadrature (8 integration points).

---

## 2. Hyperelastic FEM (`FEM/HyperElastic/`)

### Theory

For large deformations, linear elasticity is insufficient. Hyperelastic materials are defined by a **strain energy density function** `W(C)` where:

```
F = dx/dX          (deformation gradient)
C = F^T * F         (right Cauchy-Green deformation tensor)
J = det(F)          (volume ratio)
I1 = tr(C)          (first invariant)
I2 = 1/2 * (tr(C)^2 - tr(C^2))  (second invariant)
I3 = det(C) = J^2   (third invariant)
```

**Second Piola-Kirchhoff stress:**
```
S = 2 * dW/dC
```

**Elasticity tensor (material tangent):**
```
C_mat = 4 * d^2W / (dC dC)
```

### Base Interface (`HyperelasticMaterial`)

```cpp
class HyperelasticMaterial {
    virtual Real getStrainEnergy(StrainInformation*, MaterialParameters&);
    virtual void deriveSPKTensor(StrainInformation*, MaterialParameters&, MatrixSym& S);
    virtual void applyElasticityTensor(StrainInformation*, MaterialParameters&, MatrixSym& H, MatrixSym& output);
    virtual void ElasticityTensor(StrainInformation*, MaterialParameters&, Matrix6& C);
};
```

`StrainInformation` holds: `C`, `trC`, `J`, `trC^2`, eigenvalues/eigenvectors.

### Material Models

#### Neo-Hookean (Compressible)
**Reference:** Bonet & Wood, "Nonlinear Continuum Mechanics for FEA," 2008

```
W = mu/2 * (I1 - 3) - mu * ln(J) + lambda/2 * (ln(J))^2
```

**Parameters:** mu (shear modulus), lambda (Lame's first parameter)
- `mu = E / (2*(1+nu))`
- `lambda = E*nu / ((1+nu)*(1-2*nu))`

**SPK stress:**
```
S = mu * I + (lambda * ln(J) - mu) * C^{-1}
```

#### Mooney-Rivlin
```
W = c1 * (I1_bar - 3) + c2 * (I2_bar - 3) + k0/2 * (ln(J))^2
```
Where `I1_bar = I1 * J^{-2/3}`, `I2_bar = I2 * J^{-4/3}` (deviatoric invariants).

**Parameters:** c1, c2, k0 (bulk modulus)

#### St. Venant-Kirchhoff
```
W = lambda/2 * (tr(E))^2 + mu * tr(E^2)
```
Where `E = 1/2 * (C - I)` is the Green-Lagrange strain.

**Note:** Simplest hyperelastic model but non-physical under compression (non-convex).

#### Ogden
```
W = sum_p (mu_p / alpha_p) * (lambda1^alpha_p + lambda2^alpha_p + lambda3^alpha_p - 3)
```
Where `lambda_i` are principal stretches. General model that subsumes Neo-Hookean and Mooney-Rivlin.

#### Stable Neo-Hookean
Modification of Neo-Hookean to handle element inversion gracefully.

#### Costa (Anisotropic)
```
W = a/2 * (exp(Q) - 1)
Q = b_ff*E_ff^2 + b_ss*E_ss^2 + b_nn*E_nn^2 + 2*b_fs*E_fs^2 + ...
```
Used for biological soft tissue (heart, arterial walls). Exponential form captures strain stiffening.

#### Boyce-Arruda (8-chain)
Rubber-like materials. Based on statistical mechanics of polymer chains.

#### Veronda-Westman
Biological tissue model:
```
W = c1 * (exp(c2*(I1-3)) - 1) - c1*c2/2 * (I2 - 3)
```

#### Plastic Material
Extension with plasticity (yield surface, plastic flow).

### Element Types for Hyperelastic

| ForceField | Description |
|------------|-------------|
| `TetrahedronHyperelasticityFEMForceField` | Main hyperelastic tet element. Supports all material models above. |
| `StandardTetrahedralFEMForceField` | Alternative implementation |

---

## 3. NonUniform FEM (`FEM/NonUniform/`)

Supports spatially varying material properties within elements. Useful for:
- Heterogeneous tissues
- Graded materials
- Topology-based property assignment

---

## 4. Spring-Based Models (`Spring/`)

Spring models approximate elasticity without full FEM. Faster but less accurate.

### Types

| ForceField | Description | Theory |
|------------|-------------|--------|
| `SpringForceField` | Basic linear spring | `f = -k * (||x2-x1|| - L0)` |
| `StiffSpringForceField` | Spring with damping | `f = -k*dl - d*dv` |
| `MeshSpringForceField` | Springs along mesh edges | Auto-generated from topology |
| `RestShapeSpringsForceField` | Springs to rest position | `f = -k * (x - x_rest)` |
| `PolynomialSpringsForceField` | Polynomial spring law | `f = sum(a_i * dl^i)` |
| `TriangularBendingSprings` | Bending resistance on triangles | Dihedral angle springs |
| `FastTriangularBendingSprings` | Optimized bending | Cache-friendly version |
| `QuadBendingSprings` / `QuadularBendingSprings` | Quad bending | Cross-diagonal springs |
| `AngularSpringForceField` | Angular (rotational) spring | `tau = -k * d_theta` |
| `FrameSpringForceField` | 6-DOF rigid frame spring | Translation + rotation springs |
| `JointSpringForceField` | Joint constraint spring | Articulated body joints |
| `GearSpringForceField` | Gear coupling | Rotation coupling |
| `RegularGridSpringForceField` | Grid-based springs | Regular lattice |
| `RepulsiveSpringForceField` | Compression-only spring | `f = -k * dl` only if `dl < 0` |
| `VectorSpringForceField` | Vector (directional) spring | Force along specific direction |

### Bending Springs Theory

For thin shells/cloth without full shell elements:
```
M_bend = k_bend * (theta - theta_0)
```
Where `theta` is the dihedral angle between adjacent triangles. Converts to forces on the 4 vertices of the two triangles sharing an edge.

---

## 5. TensorMass Formulation (`TensorMass/`)

Alternative to standard FEM stiffness. Pre-computes per-edge tensors that relate displacement differences to forces:

```
f_i = sum_j T_ij * (u_j - u_i)
```

Where `T_ij` is a 3x3 tensor. Equivalent to FEM for constant-strain elements but with a different assembly structure. Can be more efficient for certain operations.

---

## Comparison: When to Use What

| Scenario | Recommended |
|----------|-------------|
| Small deformation, linear material | `TetrahedronFEMForceField` (SMALL method) |
| Moderate deformation, linear material | `TetrahedronFEMForceField` (POLAR/SVD corotational) |
| Large deformation, nonlinear material | `TetrahedronHyperelasticityFEMForceField` |
| Rubber/biological tissue | Hyperelastic (NeoHookean, MooneyRivlin, Ogden, Costa) |
| Real-time, low accuracy OK | Springs (`MeshSpringForceField`) |
| Cloth/thin shell | `TriangularFEMForceField` + `TriangularBendingSprings` |
| Beam structures | `BeamFEMForceField` |
