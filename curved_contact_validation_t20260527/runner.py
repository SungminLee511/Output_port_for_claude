"""
Common runner utility for curved-contact validation cases.

Captures NR convergence log, runs the solver, computes metrics, and saves
a 2-panel matplotlib figure (before/after) plus a JSON metrics file.
"""
import io
import os
import sys
import json
import time
import contextlib
import numpy as np
import torch

# Add project root for imports
HERE = os.path.dirname(os.path.abspath(__file__))
PROJ_ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
if PROJ_ROOT not in sys.path:
    sys.path.insert(0, PROJ_ROOT)

from postprocess.solver import static_structure_solver_with_contact


@contextlib.contextmanager
def capture_stdout():
    """Capture stdout to a string buffer while still printing."""
    class Tee(io.TextIOBase):
        def __init__(self, *targets):
            self.targets = targets
        def write(self, s):
            for t in self.targets:
                t.write(s)
            return len(s)
        def flush(self):
            for t in self.targets:
                t.flush()
    buf = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = Tee(old_stdout, buf)
    try:
        yield buf
    finally:
        sys.stdout = old_stdout


def parse_nr_log(log_text):
    """
    Parse 'NR Iter NN | ... | Res: X.XXe+YY | Rel: X.XXe+YY | Contact: ...'
    Returns list of dicts per iteration, per load step.
    """
    rows = []
    current_step = 1
    for line in log_text.splitlines():
        if "LOAD STEP" in line:
            try:
                current_step = int(line.split("LOAD STEP")[1].split("/")[0])
            except Exception:
                pass
        if "NR Iter" in line:
            try:
                iter_num = int(line.split("NR Iter")[1].split("|")[0].strip())
                res = float(line.split("Res:")[1].split("|")[0].strip())
                rel = float(line.split("Rel:")[1].split("|")[0].strip())
                contact_part = line.split("Contact:")[1].strip()
                has_contact = contact_part.startswith("True")
                stick = slip = None
                if "Stick:" in line:
                    stick = int(line.split("Stick:")[1].split("/")[0].strip())
                    slip = int(line.split("Slip:")[1].split("/")[0].strip())
                rows.append({
                    "load_step": current_step,
                    "iter": iter_num,
                    "res": res,
                    "rel": rel,
                    "contact": has_contact,
                    "stick": stick,
                    "slip": slip,
                })
            except Exception:
                pass
    return rows


def plot_convergence(nr_rows, title, save_path):
    """Plot residual vs iteration (log scale), split by load step."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(1, 1, figsize=(7, 4))
    by_step = {}
    for r in nr_rows:
        by_step.setdefault(r["load_step"], []).append(r)
    for step, rows in sorted(by_step.items()):
        xs = list(range(len(rows)))
        ys = [r["res"] for r in rows]
        ax.semilogy(xs, ys, marker='o', label=f'Load step {step}')
    ax.set_xlabel("NR iteration")
    ax.set_ylabel("Residual norm (free DoFs)")
    ax.set_title(title)
    ax.grid(True, which='both', alpha=0.3)
    ax.legend()
    plt.tight_layout()
    plt.savefig(save_path, dpi=130, bbox_inches='tight')
    print(f"  Saved: {save_path}")
    plt.close()


def plot_before_after(coords_before, coords_after,
                      meshes_def, slave_idx=None,
                      title="", save_path=None,
                      elev=18, azim=-65,
                      penetration_z=None, plate_z=None):
    """
    Plot two side-by-side 3D scenes (before & after solve).

    meshes_def: list of dicts {'tris': [F,3], 'color': str, 'alpha': float, 'name': str,
                               'node_slice': slice — into the full coords array}
        OR {'nodes_idx': Tensor[V], 'tris': [F,3] (indices into nodes_idx, NOT full)}
    Simpler form: {'tris_global': [F,3] of full-coords indices}

    slave_idx: optional Tensor of global slave node indices to mark red.
    """
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    def to_np(x):
        return x.detach().cpu().numpy() if isinstance(x, torch.Tensor) else x

    Vb = to_np(coords_before)
    Va = to_np(coords_after)

    fig = plt.figure(figsize=(13, 6))

    def render(ax, V, label):
        for m in meshes_def:
            F = to_np(m['tris_global'])
            polys = [V[face] for face in F]
            coll = Poly3DCollection(polys, alpha=m.get('alpha', 0.4),
                                    facecolor=m.get('color', 'C0'),
                                    edgecolor='k', linewidth=0.15)
            ax.add_collection3d(coll)
        if slave_idx is not None:
            sidx = to_np(slave_idx)
            ax.scatter(V[sidx, 0], V[sidx, 1], V[sidx, 2],
                       c='red', s=14, zorder=10, label='slave')
        # Auto-extent on union
        Vall = np.concatenate([Vb, Va], axis=0)
        mins = Vall.min(0); maxs = Vall.max(0)
        span = (maxs - mins).max() * 0.55
        mid = (mins + maxs) / 2
        ax.set_xlim(mid[0] - span, mid[0] + span)
        ax.set_ylim(mid[1] - span, mid[1] + span)
        ax.set_zlim(mid[2] - span, mid[2] + span)
        ax.set_xlabel('x'); ax.set_ylabel('y'); ax.set_zlabel('z')
        ax.set_title(label)
        ax.view_init(elev=elev, azim=azim)

    ax1 = fig.add_subplot(1, 2, 1, projection='3d')
    render(ax1, Vb, "Before solve")
    ax2 = fig.add_subplot(1, 2, 2, projection='3d')
    render(ax2, Va, "After solve (deformed)")

    plt.suptitle(title, fontsize=13)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=130, bbox_inches='tight')
        print(f"  Saved: {save_path}")
    plt.close()


def compute_penetration_metric(coords_def, slave_idx, master_faces, master_node_slice=None):
    """
    Use IGL to measure final penetration depth of slave nodes against master_faces.

    coords_def: deformed coords [N, 3]
    slave_idx:  [Ns] global node indices
    master_faces: [M, 3] global indices

    Returns dict with: max_penetration, mean_penetration, n_penetrating
    """
    try:
        import igl
    except ImportError:
        return {"error": "igl not available"}
    V = coords_def.detach().cpu().numpy()
    F = master_faces.detach().cpu().numpy()
    Vs = V[slave_idx.detach().cpu().numpy()]
    sqr_d, f_idx, c_pts = igl.point_mesh_squared_distance(Vs, V, F)
    face_normals = igl.per_face_normals(V, F, np.array([0., 0., 0.]))[f_idx]
    dvec = Vs - c_pts
    signed = np.sum(dvec * face_normals, axis=1)
    pen = -signed  # positive = penetrating
    pen_pos = pen[pen > 1e-9]
    return {
        "max_penetration": float(pen.max()) if pen.size else 0.0,
        "mean_penetration": float(pen.mean()) if pen.size else 0.0,
        "n_penetrating": int(pen_pos.size),
        "n_slave": int(slave_idx.numel()),
        "signed_distance_mean": float(signed.mean()),
    }


def run_case(name, coords, elements_volume, force, fixed,
             contact_pairs, material, output_dir,
             solver_kwargs=None, meshes_def=None, slave_idx_global=None,
             master_faces_for_metric=None):
    """
    Run a single contact case and dump:
      - <output_dir>/<name>_console.log   (full stdout)
      - <output_dir>/<name>_convergence.png
      - <output_dir>/<name>_geometry.png   (before/after)
      - <output_dir>/<name>_metrics.json

    solver_kwargs: dict of extra args to static_structure_solver_with_contact
    meshes_def: list for visualization (passed to plot_before_after)
    slave_idx_global: tensor of slave node indices (for plotting + metric)
    master_faces_for_metric: master face conn (for penetration metric)
    """
    os.makedirs(output_dir, exist_ok=True)
    default_kwargs = dict(
        contact_epsilon=1e6, nr_tol=1e-3, nr_max_iter=40,
        n_load_steps=1, mu_s=0.0, mu_d=0.0,
        dim=3, cg_start=False, dtype=torch.float64,
        device="cpu",
    )
    if solver_kwargs:
        default_kwargs.update(solver_kwargs)

    print(f"\n{'#'*70}\n# CASE: {name}\n{'#'*70}")
    t0 = time.time()
    with capture_stdout() as buf:
        try:
            u = static_structure_solver_with_contact(
                coords=coords, force=force, fixed=fixed,
                contact_pairs=contact_pairs,
                elements_volume=elements_volume,
                material=material,
                **default_kwargs,
            )
            failed = False
            err = None
        except Exception as e:
            u = None
            failed = True
            err = repr(e)
            print(f"!!! SOLVER RAISED: {err}")
    elapsed = time.time() - t0
    log_text = buf.getvalue()

    # Save full log
    log_path = os.path.join(output_dir, f"{name}_console.log")
    with open(log_path, "w") as f:
        f.write(log_text)
    print(f"  Saved: {log_path}")

    # Parse NR rows
    nr_rows = parse_nr_log(log_text)
    converged = ("CONVERGED" in log_text) and not failed

    # Convergence plot
    if nr_rows:
        plot_convergence(nr_rows, f"{name}: NR residual",
                         os.path.join(output_dir, f"{name}_convergence.png"))

    # Before/after geometry plot
    if meshes_def is not None and u is not None:
        coords_after = coords + u[:, :3]
        plot_before_after(coords, coords_after, meshes_def,
                          slave_idx=slave_idx_global,
                          title=f"{name}  (converged={converged})",
                          save_path=os.path.join(output_dir, f"{name}_geometry.png"))

    # Penetration metric
    pen_metric = None
    if u is not None and slave_idx_global is not None and master_faces_for_metric is not None:
        pen_metric = compute_penetration_metric(coords + u[:, :3],
                                                slave_idx_global,
                                                master_faces_for_metric)

    metrics = {
        "case": name,
        "converged": converged,
        "failed": failed,
        "error": err,
        "elapsed_sec": round(elapsed, 3),
        "n_nr_iters_total": len(nr_rows),
        "final_residual": nr_rows[-1]["res"] if nr_rows else None,
        "final_rel_residual": nr_rows[-1]["rel"] if nr_rows else None,
        "nr_iters_by_step": {},
        "max_displacement": float(u.abs().max().item()) if u is not None else None,
        "mean_displacement": float(u.abs().mean().item()) if u is not None else None,
        "penetration_metric": pen_metric,
        "solver_kwargs": {k: (v if isinstance(v, (int, float, str, bool)) else str(v))
                          for k, v in default_kwargs.items()},
    }
    for r in nr_rows:
        metrics["nr_iters_by_step"].setdefault(str(r["load_step"]), []).append(
            {"iter": r["iter"], "res": r["res"], "rel": r["rel"],
             "stick": r["stick"], "slip": r["slip"]})

    json_path = os.path.join(output_dir, f"{name}_metrics.json")
    with open(json_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"  Saved: {json_path}")

    return u, metrics
