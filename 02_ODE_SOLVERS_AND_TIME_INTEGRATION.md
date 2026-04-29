# SOFA - ODE Solvers & Time Integration Theory

**Source:** `Sofa/Component/ODESolver/`

---

## Overview

SOFA's ODE solvers discretize Newton's second law (or first-order diffusion equations) in time. The governing equation is:

```
M * a = f_ext + f_int(x, v)
```

Where:
- `M` = mass matrix
- `a` = acceleration
- `f_ext` = external forces (gravity, loads)
- `f_int(x, v)` = internal forces (elastic, damping), depends on position `x` and velocity `v`

Linearized internal forces: `f_int ~= f_int(x0,v0) + K*dx + B*dv`
- `K = df/dx` = stiffness matrix (tangent)
- `B = df/dv` = damping matrix

Additionally, **Rayleigh damping** is supported globally:
```
C_rayleigh = r_M * M + r_K * K
```

---

## Forward (Explicit) Solvers

### 1. EulerExplicitSolver

**Location:** `ODESolver/Forward/EulerExplicitSolver.h`

Two variants controlled by `d_symplectic`:

**Standard Euler (symplectic=false):**
```
x_{n+1} = x_n + v_n * dt
v_{n+1} = v_n + a_n * dt
```
- Order: 1st
- Stability: Conditionally stable. dt < 2/omega_max (CFL condition).
- Position updated with OLD velocity.

**Symplectic Euler (symplectic=true, default):**
```
v_{n+1} = v_n + a_n * dt
x_{n+1} = x_n + v_{n+1} * dt
```
- Order: 1st (but symplectic = energy-preserving structure)
- Position updated with NEW velocity.
- More robust for oscillatory systems (springs, etc.)
- Does NOT require solving a linear system if mass is diagonal.

**Computation flow:**
1. Accumulate forces: `f = f_ext + f_int(x_n, v_n)`
2. Solve `M * a = f` (trivial if diagonal mass)
3. Apply projective constraints
4. Update v, then x (or x, then v)

---

### 2. CentralDifferenceSolver (Verlet / Leapfrog)

**Location:** `ODESolver/Forward/CentralDifferenceSolver.h`

**Equations:**
```
a_n = M^{-1} * (f_ext + f_int - C * v_n)
v_{n+1/2} = v_{n-1/2} + a_n * dt
x_{n+1} = x_n + v_{n+1/2} * dt
```

- Order: 2nd (time-centered differences)
- Symplectic, explicit
- Same CFL stability requirement as explicit Euler but better accuracy
- Used in explicit dynamics (crash, blast, high-speed impact)
- Equivalent to Stoermer-Verlet / Leapfrog method

**Integration factor matrix:**
```
         x_t   v_t   a_t
x_{t+h}:  1    dt    dt^2
v_{t+h}:  0    1     dt
```

---

### 3. RungeKutta2Solver (Midpoint Method)

**Location:** `ODESolver/Forward/RungeKutta2Solver.h`

**Equations:**
```
k1 = f(t_n, x_n)
k2 = f(t_n + dt/2, x_n + dt/2 * k1)
x_{n+1} = x_n + dt * k2
```

- Order: 2nd
- Explicit, non-symplectic
- Better accuracy than Euler, still conditionally stable

---

### 4. RungeKutta4Solver (Classical RK4)

**Location:** `ODESolver/Forward/RungeKutta4Solver.h`

**Equations:**
```
k1 = f(t_n, y_n)
k2 = f(t_n + dt/2, y_n + dt/2 * k1)
k3 = f(t_n + dt/2, y_n + dt/2 * k2)
k4 = f(t_n + dt, y_n + dt * k3)
y_{n+1} = y_n + dt/6 * (k1 + 2*k2 + 2*k3 + k4)
```

- Order: 4th
- Explicit, 4 force evaluations per step
- High accuracy but expensive; conditionally stable

---

### 5. DampVelocitySolver

**Location:** `ODESolver/Forward/DampVelocitySolver.h`

- Trivial solver that applies velocity damping each step
- `v_{n+1} = v_n * (1 - damping)`

---

## Backward (Implicit) Solvers

### 6. EulerImplicitSolver (Backward Euler)

**Location:** `ODESolver/Backward/EulerImplicitSolver.h`

**Reference:** Baraff & Witkin, "Large Steps in Cloth Simulation," SIGGRAPH 1998

**2nd Order (default):**
```
x_{t+h} = x_t + h * v_{t+h}
v_{t+h} = v_t + h * a_{t+h}
```

Unknown: `dv = v_{t+h} - v_t`

Newton's law linearized:
```
M * dv = h * (f(t) + K*h*(v+dv) + (B - r_M*M + r_K*K)*(v+dv))
```

Rearranged into linear system:
```
A * dv = b
```
Where:
```
A = (1 + h*r_M)*M - h*B - h*(h + r_K)*K
b = h * (f(t) + (h + r_K)*K*v + B*v - r_M*M*v)
```

With projective constraints (projection matrix P):
```
P * A * P * dv = P * b
```

**1st Order mode** (d_firstOrder=true):
```
(M + h*K) * v_{t+h} = f_ext
```
Used for quasi-static / diffusion problems.

**Trapezoidal Rule** (d_trapezoidalScheme=true):
```
A = (1 + h/2*r_M)*M - h/2*B - h/2*(h + r_K)*K
b = h/2 * (2*f(t) + (h + r_K)*K*v + B*v - r_M*M*v)
```
- 2nd order accuracy in time (vs 1st order for standard backward Euler)

**Properties:**
- Unconditionally stable (A-stable)
- 1st order accurate (2nd with trapezoidal)
- Numerical damping (high frequencies damped more)
- Requires solving a linear system each step
- Warm-start supported (reuses previous solution)

---

### 7. NewmarkImplicitSolver

**Location:** `ODESolver/Backward/NewmarkImplicitSolver.h`

**Newmark-beta family equations:**
```
x_{t+h} = x_t + h*v_t + h^2/2 * ((1 - 2*beta)*a_t + 2*beta*a_{t+h})
v_{t+h} = v_t + h * ((1 - gamma)*a_t + gamma*a_{t+h})
```

**Parameters:**
- `gamma` (default 0.5): controls numerical dissipation
- `beta` (default 0.25): controls stability and accuracy

**Common configurations:**

| gamma | beta | Name | Order | Stability |
|-------|------|------|-------|-----------|
| 0.5   | 0.25 | Average acceleration (trapezoidal) | 2nd | Unconditionally stable |
| 0.5   | 1/6  | Linear acceleration | 2nd | Conditionally stable |
| 0.5   | 0    | Central difference (explicit) | 2nd | Conditionally stable |
| > 0.5 | (2*gamma-1)^2/4 | HHT-alpha variant | 2nd | Unconditionally stable + dissipation |

**Linear system (unknown: a_{t+h}):**
```
((1 + h*gamma*r_M)*M + (h^2*beta + h*gamma*r_K)*K) * a_{t+h} = RHS
```

**Properties:**
- 2nd order accurate for gamma=0.5
- Controllable numerical dissipation via gamma
- Widely used in structural dynamics

---

### 8. BDFOdeSolver (Backward Differentiation Formula)

**Location:** `ODESolver/Backward/BDFOdeSolver.h`

Extends `BaseLinearMultiStepMethod`. Multi-step implicit method using past states.

**BDF-k formula (k-step):**
```
sum_{j=0}^{k} a_j * x_{n+1-j} = h * b_0 * f(t_{n+1}, x_{n+1})
```

- BDF-1 = Backward Euler
- BDF-2: 2nd order, A-stable
- BDF-k: up to order k, stability decreases with k (BDF-1 to BDF-6 are stable; BDF-7+ unstable)

**Properties:**
- Multi-step: uses history of past solutions
- Coefficients recomputed dynamically based on stored time samples
- Good for stiff systems

---

### 9. StaticSolver

**Location:** `ODESolver/Backward/StaticSolver.h`

Solves the **static equilibrium** (no inertia, no velocity):
```
f_int(x) + f_ext = 0
```

**Method:** Delegates to **NewtonRaphsonSolver** for nonlinear iteration:
```
K * dx = -R(x)     (R = residual = f_int + f_ext)
x_{k+1} = x_k + dx
```

Repeat until convergence (absolute/relative residual or correction tolerance).

**Properties:**
- No time dependence
- Uses Newton-Raphson with tangent stiffness
- Multiple convergence criteria (absolute, relative, correction-based)

---

### 10. NewtonRaphsonSolver

**Location:** `ODESolver/Backward/NewtonRaphsonSolver.h`

Standalone Newton-Raphson iteration controller. Used by StaticSolver and potentially by other solvers.

**Convergence measures available:**
- `AbsoluteConvergenceMeasure`: ||R|| < tol
- `RelativeInitialConvergenceMeasure`: ||R|| / ||R_0|| < tol
- `RelativeSuccessiveConvergenceMeasure`: ||R_k - R_{k-1}|| / ||R_k|| < tol
- `AbsoluteEstimateDifferenceMeasure`: ||dx|| < tol
- `RelativeEstimateDifferenceMeasure`: ||dx|| / ||x|| < tol

---

### 11. VariationalSymplecticSolver

**Location:** `ODESolver/Backward/VariationalSymplecticSolver.h`

**Reference:** Kharevych et al., "Geometric, Variational Integrators for Computer Animation," SCA 2006

**Theory:** Derived from discrete Hamilton's principle (variational integrator). Minimizes the discrete action sum, leading to:
- Exact symplectic structure preservation
- Exact momentum conservation
- Near-exact energy conservation (bounded drift)

**Implementation:**
- `alpha = 0.5` (quadratic accuracy)
- Newton iteration to solve implicit step
- Can log Hamiltonian energy for verification
- Supports both explicit and implicit modes

**Properties:**
- Symplectic (structure-preserving)
- Excellent long-term energy behavior
- More expensive than standard implicit Euler
- Ideal for conservative systems and long simulations

---

## Summary Table

| Solver | Type | Order | Stability | Linear System? | Best For |
|--------|------|-------|-----------|---------------|----------|
| EulerExplicit (symplectic) | Explicit | 1 | Conditional | No (if diagonal M) | Fast, simple dynamics |
| CentralDifference | Explicit | 2 | Conditional | No (if diagonal M) | Explicit dynamics, impact |
| RungeKutta2 | Explicit | 2 | Conditional | No | Better accuracy, moderate cost |
| RungeKutta4 | Explicit | 4 | Conditional | No | High accuracy explicit |
| EulerImplicit | Implicit | 1 (2 w/ trap) | Unconditional | Yes | Stiff systems, cloth, soft bodies |
| Newmark | Implicit | 2 | Unconditional* | Yes | Structural dynamics |
| BDF | Implicit | 1-6 | Unconditional (k<=6) | Yes | Stiff ODEs, multi-step |
| Static | N/A | N/A | N/A | Yes (NR) | Equilibrium problems |
| VariationalSymplectic | Implicit | 2 | Unconditional | Yes (Newton) | Energy-preserving, long-term |

*Unconditionally stable for gamma=0.5, beta>=0.25
