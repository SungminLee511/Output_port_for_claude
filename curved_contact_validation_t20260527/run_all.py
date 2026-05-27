"""
Master driver — runs all four validation cases sequentially and prints a summary.
"""
import os, sys, json
import importlib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

cases = [
    "case_baseline_box_on_plate",
    "case_a_sphere_on_plate",
    "case_b_plate_on_sphere",
    "case_c_two_finger_grasp",
]

print("=" * 70)
print("CURVED CONTACT VALIDATION — RUN ALL")
print("=" * 70)

for c in cases:
    print(f"\n>>>>> {c} <<<<<")
    mod = importlib.import_module(c)
    # Each module has __main__-style runs in its own __main__ block
    # but we re-invoke its main code by reloading
    exec(open(os.path.join(HERE, c + ".py")).read(), {"__name__": "__main__",
                                                       "__file__": os.path.join(HERE, c + ".py")})

# Aggregate metrics
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
out_dir = os.path.join(HERE, "results")
rows = []
for fn in sorted(os.listdir(out_dir)):
    if fn.endswith("_metrics.json"):
        with open(os.path.join(out_dir, fn)) as f:
            m = json.load(f)
        rows.append(m)

print(f"{'case':60s} {'converged':>10s} {'iters':>6s} {'final_res':>12s} {'max_pen':>10s}")
print("-" * 105)
for m in rows:
    pen = (m.get('penetration_metric') or {}).get('max_penetration', None)
    pen_str = f"{pen:.3e}" if pen is not None else "n/a"
    print(f"{m['case'][:60]:60s} {str(m['converged']):>10s} "
          f"{m['n_nr_iters_total']:>6d} {m['final_residual']:>12.3e} {pen_str:>10s}")
