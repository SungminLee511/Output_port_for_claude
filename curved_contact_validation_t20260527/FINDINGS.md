# Curved-Contact Validation — Findings

**Date:** 2026-05-27
**Reviewer claim (translated):**
> *"Right-angled objects work fine, but **spheres do not**."*

**Verdict:** **CLAIM CONFIRMED.** The penalty N2S contact solver in
`postprocess/solver.py` has severe stability problems whenever a curved master
surface is involved, and friction makes it dramatically worse — even when the
master surface is flat.

---

## Results summary

`contact_epsilon = 1e6`, `nr_tol = 1e-3`, `nr_max_iter = 40-50`, `E = 1e7 Pa`,
`nu = 0.3`.  All tests on CPU, double precision.

| Case | Geometry | Friction | Load steps | Converged | Total NR iters | Final residual | Max penetration (m) | Max ‖u‖ (m) |
|---|---|---|---|---|---|---|---|---|
| baseline | box ↔ flat plate | — | 1 | ✅ | 2 | 7.3e-13 | 5.9e-5 | 1.2e-4 |
| baseline | box ↔ flat plate | μs=0.3 | 1 | ✅ | 4 | 4.1e-2 | 5.9e-5 | 1.2e-4 |
| a-frictionless-1step | sphere (slave) ↔ flat plate | — | 1 | ✅ | 2 | 1.0e-10 | 3.0e-4 | 4.4e-3 |
| a-frictionless-4step | sphere (slave) ↔ flat plate | — | 4 | ✅ | 8 | 7.1e-10 | 3.0e-4 | 3.1e-2 |
| a-friction-4step | sphere (slave) ↔ flat plate | μs=0.3 | 4 | ⚠️ "True" but blew up at step 3 | 84 | **1.1e+17** | **4.6e+9** | **1.7e+14** |
| b-frictionless-1step | punch ↔ **curved sphere master** | — | 1 | ❌ | 50 | 3.0e+4 | 1.8e+11 | 2.6e+13 |
| b-frictionless-8step | punch ↔ **curved sphere master** | — | 8×40 | ❌ | 320 | 6.1e+5 | -5.5e+13 | 1.0e+14 |
| b-softer-eps (ε=1e4) | punch ↔ **curved sphere master** | — | 4 | ❌ | 160 | 9.0e+4 | 2.1e+12 | 1.6e+14 |
| b-friction-8step | punch ↔ **curved sphere master** | μs=0.3 | 8×40 | ❌ | 320 | 2.7e+45 | 6.8e+38 | 1.9e+39 |
| c-frictionless-1step | two pads ↔ sphere | — | 1 | ❌ | 50 | 5.8e+22 | 1.2e+18 | 1.8e+18 |
| c-frictionless-8step | two pads ↔ sphere | — | 8×40 | ❌ | 320 | 5.2e+54 | 6.5e+35 | 7.6e+35 |
| c-friction-8step | two pads ↔ sphere | μs=0.5 | 8×40 | ❌ | 320 | **5.8e+79** | 3.3e+73 | 4.7e+73 |

(The "converged" flag for `a-friction` is a parser artifact — earlier load
steps converged but step 3 diverged. The huge residual / displacement reveals
the true state.)

### What converged

- **Boxes-on-plate**, both frictionless and with friction. Clean: 2-4 NR iters,
  residual to machine precision, microscopic max penetration (~ε_N⁻¹).
- **Frictionless sphere-on-flat-plate**. Flat master keeps every slave node on
  one of two coplanar triangles, so the per-face normal is the same constant
  +Z. With this property, the curved slave reduces to "a bunch of points
  pushed onto a plane", which the penalty method handles cleanly.

### What blew up

- **Friction with a curved slave**, even when master is flat (case A). The
  first two load steps converged; the third detonated. This is *new*
  information — was not implied by the original review.
- **Anything with curved master** (cases B and C), regardless of friction
  setting, load stepping, or penalty stiffness. Even a softer penalty
  (`ε_N = 1e4`) and `n_load_steps = 8` did not save it.

---

## Root-cause hypotheses (ordered by evidence)

### 1. Per-face flat normals jump between adjacent triangles (curved master) — **STRONGLY SUPPORTED**

`check_contact_igl` calls `igl.per_face_normals` and grabs the normal of the
single closest face for each slave. Between successive NR iterations the
closest face flips as `u` updates. The contact direction `n` changes
discretely → `K_N = ε_N · nnᵀ` changes by an order-one rotation in 3×3 space
→ NR's linearization is wrong by a finite amount, so the next step lands
nowhere near the solution.

**Evidence:** Cases B and C show `Contact: True/False` flickering between
iterations (e.g. case B step 4 lines 12-33: contact-false, contact-false,
... contact-true at iter 33 with residual 10⁁15, then contact-false again).
This is the smoking gun — the slave nodes are being kicked through the
master surface and bouncing back across multiple faces each iter.

### 2. `compute_triangle_barycentric_gpu` clamps weights, creating discontinuity at triangle edges — **SUPPORTED**

Lines 329–331 of `solver.py`:
```python
weights = torch.clamp(torch.stack([u, v, w], dim=1), 0.0, 1.0)
weights = weights / torch.sum(weights, dim=1, keepdim=True)
```

When the closest point on a triangle is on an edge or vertex (typical for
slave nodes contacting a faceted sphere), the unclamped barycentric weights
would be negative outside the triangle. The clamp + renormalize produces a
*different* set of weights than the true projection onto the next-best
triangle. Around a triangle edge this creates a 0/1 discontinuity in `N_i`
across slave-master pairs.

Combined with hypothesis 1, this means both `n` AND `N_i` jump discretely
across NR iterations near edges. NR was never going to handle that.

### 3. Friction Δu_T has no history; the tangent-plane projection `P = I - nnᵀ` itself flips with normals — **NEW & STRONGLY SUPPORTED**

`compute_friction_apply_tensors` uses `delta_u_T = u_s - Σ N_i u_mᵢ` projected
into the current `P`. If the closest face flips between iterations, `P` flips
with it, and the *same physical Δu* becomes a *different Δu_T*. This causes
nodes to oscillate stick↔slip aggressively.

**Evidence:** In case A step 3 (line 22-39 of the log) the stick/slip counts
oscillate wildly: `0/7 → 0/2 → 52/56 → 0/33 → 0/18 → …`, while residual
swings between 10² and 10¹⁷.

Even in case A where the master is FLAT (so hypothesis 1 should not apply),
friction still detonates — this strongly implicates the no-history Δu_T
treatment as a second independent failure mode.

### 4. The simplified (stick-only) tangent stiffness underestimates the true Jacobian on slip nodes — **CONSISTENT**

The friction TODO doc itself flags this (§3.2: "If convergence is poor,
implement the consistent tangent and switch to GMRES"). The non-symmetric
slip term `μ_d · ε_N · t̂ ⊗ n` is missing. On a curved master where many
nodes are in slip, this is half the Jacobian.

### 5. (Minor) Single-pass contact detection without smoothing — **WEAKLY SUPPORTED**

Each NR iteration recomputes contact from scratch, so contact pairs flicker
in and out. For curved surfaces a "persistent contact" scheme (keep the same
master-face index across iters unless the closest-face moves more than X
triangles away) would smooth this out.

---

## Why "boxes work"

In case `baseline_box_on_plate`:
- Master = plate, 18 triangles, all coplanar, all normals = +ẑ.
- Slave = box bottom, 9 nodes, perfectly aligned to plate Z.
- Closest-face for each slave never changes, normals never change, barycentric
  weights are stable. Hypothesis 1 cannot trigger.
- Friction works too because `P = I - ẑẑᵀ` is constant.

This is a degenerate "good" geometry. Any real curved master breaks it.

---

## Proposed remediations (in priority order)

1. **Smooth/average vertex normals on curved master.** Replace
   `igl.per_face_normals[f_idx]` with a per-vertex average normal, then
   interpolate by barycentric `N_i` on the closest face. This is the standard
   FEA fix for faceted-master N2S contact and removes hypothesis 1's
   discrete-jump problem. ~30 lines of code.

2. **Persistent contact history across NR iters.** Cache `(closest_face_idx,
   barycentric)` per slave from the previous iter; only re-detect if the
   slave's new position moves more than a few triangle hops. Removes the
   "flicker" seen in case B.

3. **Skip clamping in `compute_triangle_barycentric_gpu` and instead reproject
   to the actual closest triangle.** Or, better, use the IGL closest-point
   output directly and recompute weights against the chosen triangle without
   clamping. Eliminates hypothesis 2.

4. **Friction Δu_T with accumulated history.** Store per-slave-node
   accumulated tangential displacement across load steps and use that for
   trial force. Removes oscillation in stick/slip.

5. **Implement the consistent slip tangent + switch to GMRES** (already
   recommended by the friction TODO doc).

6. **Tighter detection tolerance + smaller initial penalty + ramp ε_N across
   load steps.** Quick mitigation while the proper fixes are implemented.

If only one fix is implemented, **#1 (smooth normals)** has the highest
impact-per-effort.

---

## Files in this report

```
tests/curved_contact_validation/
├── README.md                          # how to run, layout
├── FINDINGS.md                        # this file
├── mesh_gen.py                        # synthetic mesh generators
├── runner.py                          # NR-log capture, viz, JSON metrics
├── case_baseline_box_on_plate.py      # ✅ works
├── case_a_sphere_on_plate.py          # ✅ frictionless, ❌ friction
├── case_b_plate_on_sphere.py          # ❌ across the board
├── case_c_two_finger_grasp.py         # ❌ catastrophic
├── run_all.py
└── results/                           # console logs + PNG + JSON per variant
```

Each variant produced `*_console.log`, `*_convergence.png` (residual vs iter
on log scale), `*_geometry.png` (before/after 3D render), and
`*_metrics.json` (machine-readable summary).
