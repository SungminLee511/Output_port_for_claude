# SOFA - Linear Solvers

**Source:** `Sofa/Component/LinearSolver/`

---

## Overview

After the ODE solver assembles the linear system `A * x = b`, a linear solver computes `x`. SOFA provides direct, iterative, and preconditioned solvers.

The system matrix `A` typically has the form:
```
A = alpha_M * M + alpha_B * B + alpha_K * K
```
Where coefficients depend on the ODE integration scheme (e.g., for backward Euler: `alpha_M = 1+h*r_M`, `alpha_K = -h*(h+r_K)`).

---

## Direct Solvers (`Direct/`)

Factorize the matrix exactly. Guaranteed convergence but O(n^2) to O(n^3) cost.

| Solver | Algorithm | Matrix Type | Notes |
|--------|-----------|-------------|-------|
| `SparseLDLSolver` | LDL^T factorization | Symmetric | **Primary production solver.** Sparse, efficient. |
| `AsyncSparseLDLSolver` | Async LDL^T | Symmetric | Non-blocking factorization for parallel pipelines |
| `SparseLUSolver` | LU factorization | General | For non-symmetric systems |
| `SparseCholeskySolver` | LL^T (Cholesky) | SPD | Requires positive-definite matrix |
| `CholeskySolver` | Dense Cholesky | SPD | Small systems only |
| `SVDLinearSolver` | SVD | Any | Robust but expensive; handles rank-deficient |
| `BTDLinearSolver` | Block Tri-Diagonal | BTD | Exploits banded structure (1D chains) |
| `PrecomputedLinearSolver` | Pre-factored | Any | Offline factorization, online back-substitution |
| `EigenSimplicialLDLT` | Eigen LDL^T | Symmetric | Eigen backend |
| `EigenSimplicialLLT` | Eigen LL^T | SPD | Eigen backend |
| `EigenSparseLU` | Eigen SparseLU | General | Eigen backend |
| `EigenSparseQR` | Eigen SparseQR | Any | Eigen backend, least-squares capable |
| `EigenDirectSparseSolver` | Factory pattern | Any | Selects best Eigen solver |

### SparseLDLSolver Detail

The workhorse solver. LDL^T decomposition for symmetric matrices:
```
P * A * P^T = L * D * L^T
```
Where:
- `P` = permutation (reordering for fill-in reduction)
- `L` = lower triangular (unit diagonal)
- `D` = diagonal
- Solve: `x = P^T * L^{-T} * D^{-1} * L^{-1} * P * b`

**Key properties:**
- No square root (unlike Cholesky) → works for indefinite matrices
- Sparse storage → efficient for FEM matrices
- Reordering reduces fill-in (AMD, COLAMD)

---

## Iterative Solvers (`Iterative/`)

Approximate solution via iteration. O(n) per iteration, good for large systems.

| Solver | Algorithm | Matrix Required? | Notes |
|--------|-----------|-----------------|-------|
| `CGLinearSolver` | Conjugate Gradient | SPD | Classic CG. Cheapest per iteration. |
| `PCGLinearSolver` | Preconditioned CG | SPD | CG with preconditioner for faster convergence |
| `ShewchukPCGLinearSolver` | Shewchuk PCG | SPD | Optimized PCG implementation |
| `MinResLinearSolver` | MINRES | Symmetric | Handles indefinite symmetric systems |

### Conjugate Gradient (CG) Detail

Solves `A*x = b` for SPD matrix A:
```
r_0 = b - A*x_0
p_0 = r_0
for k = 0, 1, 2, ...:
    alpha_k = (r_k^T * r_k) / (p_k^T * A * p_k)
    x_{k+1} = x_k + alpha_k * p_k
    r_{k+1} = r_k - alpha_k * A * p_k
    beta_k = (r_{k+1}^T * r_{k+1}) / (r_k^T * r_k)
    p_{k+1} = r_{k+1} + beta_k * p_k
```

**Convergence:** Number of iterations ~ sqrt(condition_number(A)).

### Matrix-Free Mode (`GraphScattered`)

SOFA supports **matrix-free** CG where `A*v` is computed directly via force field visitors without assembling the global matrix:
```
A*v = alpha_M * M*v + alpha_B * B*v + alpha_K * K*v
```
Each force field contributes its `K*v` product via `addDForce()`.

**Advantages:** No matrix assembly, lower memory. Good for large systems.
**Disadvantages:** No preconditioner (condition number may be bad), no direct solver.

---

## Ordering Methods (`Ordering/`)

Reorder matrix rows/columns to reduce fill-in during factorization.

| Method | Algorithm | Notes |
|--------|-----------|-------|
| `AMDOrderingMethod` | Approximate Minimum Degree | Default for most direct solvers |
| `COLAMDOrderingMethod` | Column AMD | For LU factorization |
| `NaturalOrderingMethod` | No reordering | Identity permutation |

**Why ordering matters:** A sparse matrix A may have many non-zeros in L after factorization (fill-in). Good ordering minimizes fill-in → less memory, faster solve.

---

## Preconditioners (`Preconditioner/`)

Improve convergence of iterative solvers by approximating A^{-1}.

| Preconditioner | Type | Notes |
|----------------|------|-------|
| `JacobiPreconditioner` | Diagonal | `P = diag(A)^{-1}`. Simplest, modest improvement. |
| `BlockJacobiPreconditioner` | Block diagonal | `P = blockdiag(A)^{-1}`. Better for block systems (3x3 blocks per node). |
| `SSORPreconditioner` | Symmetric SOR | `P ~= (D+L) * D^{-1} * (D+L^T)`. Good for structured meshes. |
| `WarpPreconditioner` | Warped Jacobi | Accounts for element rotation in corotational FEM. |
| `PrecomputedWarpPreconditioner` | Precomputed + Warp | Offline factorization with rotation update. |
| `PrecomputedMatrixSystem` | Full precomputed | Stores entire factorization. |
| `RotationMatrixSystem` | Rotation-aware | Rotates the system for better conditioning. |

### Warp Preconditioner Theory

For corotational FEM, the stiffness matrix changes due to rotation:
```
K_global = sum_e R_e * K_0e * R_e^T
```

Standard preconditioners ignore this rotation, degrading performance. The Warp preconditioner:
1. Pre-computes `P_0 ~= K_0^{-1}` on the reference configuration
2. Each iteration: `P = R * P_0 * R^T` (rotate the preconditioner)

This dramatically improves CG convergence for rotating bodies.

---

## Solver Selection Guide

| Scenario | Recommended Solver |
|----------|-------------------|
| Small system (< 10K DOF) | `SparseLDLSolver` |
| Medium system (10K-100K DOF) | `SparseLDLSolver` or `PCGLinearSolver` |
| Large system (> 100K DOF) | `ShewchukPCGLinearSolver` + preconditioner |
| Non-symmetric (friction, contact) | `SparseLUSolver` or `MinResLinearSolver` |
| Real-time, low accuracy OK | `CGLinearSolver` (matrix-free, few iterations) |
| Banded structure (1D chain) | `BTDLinearSolver` |
| Rank-deficient / ill-conditioned | `SVDLinearSolver` |
| Parallel pipeline | `AsyncSparseLDLSolver` |

---

## Linear System Assembly (`LinearSystem/`)

The `LinearSystem` component manages global matrix assembly:

1. **MatrixLinearSystem:** Assembles into a global sparse matrix (CompressedRowSparse, Eigen, etc.)
2. **MatrixFreeSystem (GraphScattered):** No assembly; matrix-vector products computed on-the-fly via visitors
3. **PreconditionedMatrixFreeSystem:** Matrix-free with preconditioner applied

Assembly process:
```
1. Zero the global matrix
2. For each ForceField: addKToMatrix(A, factor)    // Stiffness contribution
3. For each Mass: addMToMatrix(A, factor)          // Mass contribution
4. For each Damping: addBToMatrix(A, factor)       // Damping contribution
5. Apply projective constraints (zero rows/cols for fixed DOFs)
```
