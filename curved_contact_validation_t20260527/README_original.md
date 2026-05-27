# Curved Contact Validation

User feedback (Korean → translated):

> "I'm using this solver to produce data for a robot hand grasping various objects.
> For right-angled objects, contact behaves well if set up correctly. But for
> things like **spheres**, it does not work well — I wanted to discuss this with
> Sungmin."

These are **investigative validation scripts** (not pytest unit tests). Each
case runs the production `static_structure_solver_with_contact` on a small
synthetic mesh, captures the full Newton-Raphson log, plots residual vs.
iteration, renders before/after geometry, and dumps a JSON metrics file.

## Folder layout

```
curved_contact_validation/
├── README.md
├── mesh_gen.py             # Synthetic mesh generators (box, icosphere, plate, pad)
├── runner.py               # Common driver: NR log parsing, viz, JSON metrics
├── case_baseline_box_on_plate.py
├── case_a_sphere_on_plate.py
├── case_b_plate_on_sphere.py
├── case_c_two_finger_grasp.py
├── run_all.py              # Master driver
└── results/                # Outputs (logs, PNG, JSON)
```

## Cases

| ID | Slave            | Master                | Loading                     | Purpose |
|----|------------------|-----------------------|-----------------------------|---------|
| baseline | Box bottom face | Flat plate triangles | Top of box pushed -Z        | Confirm "boxes converge" |
| a  | Sphere lower hem | Flat plate triangles  | Top of sphere pushed -Z     | Curved slave, flat master |
| b  | Punch bottom     | Sphere upper hem      | Top of punch pushed -Z      | **Curved master** (suspected failure) |
| c  | Pad inner faces  | Sphere left/right hem | Both pads pushed inward     | Real robot-grasp scenario |

Each case runs multiple variants (frictionless 1-step, frictionless N-step,
friction N-step, softer penalty) to disentangle the failure mode.

## Run

```bash
conda run -n SML_env python tests/curved_contact_validation/run_all.py
# or individual cases:
conda run -n SML_env python tests/curved_contact_validation/case_b_plate_on_sphere.py
```

Outputs land in `results/`:

- `<name>_console.log`    — full stdout, including per-NR-iter line
- `<name>_convergence.png` — log-scale residual per iteration, split by load step
- `<name>_geometry.png`    — before / after rendering (matplotlib 3D)
- `<name>_metrics.json`    — converged flag, residuals, max penetration

## Key metrics watched

- **Convergence**: did NR converge inside `nr_max_iter`?
- **Final residual**: how close to `nr_tol`?
- **Max penetration** (post-solve, via IGL `point_mesh_squared_distance`):
  for a working contact, penetration should be a small ε set by the penalty
  stiffness; for a broken contact, penetration grows uncontrolled.
- **Stick/slip counts**: oscillation across NR iterations signals tangent issues.

## What we expect to see (hypotheses to confirm/refute)

| Hypothesis | Mechanism |
|------------|-----------|
| H1: curved-master case (B,C) diverges or oscillates | Per-face flat normals jump between adjacent triangles → slave's closest-face index hops every NR iter → residual oscillates |
| H2: clamped barycentric weights (`mesh_gen.py` calls solver's helper which clamps weights to triangle) create discontinuity at edges/vertices | When closest point is outside triangle, the helper projects to nearest edge/vertex, but weight clamp produces an artificial spike in `K_sm`, `K_ms` |
| H3: load stepping helps but does not fix curved-master | Smaller increments reduce jumps but each load step still inherits flat-facet discrete normals |
| H4: friction (`mu_s > 0`) makes curved-master worse | Tangent stick stiffness is `ε_T · P`, but `P` itself flips as the master-face index hops |

After running, compare the four cases' convergence plots and final
penetration values.
