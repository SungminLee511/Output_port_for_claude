from __future__ import annotations

import json
import math
import argparse
import subprocess
import sys
from pathlib import Path

import h5py
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np


DATASET_DIR = Path("../data_port/huggingface_datasets/solverx/lg-vs_JIG/data_v2")
OUT_DIR = Path("results/pointclouds")
STAMP = "t20260617"
MAX_POINTS = 60000


ATTRIBUTES = [
    ("eigvec_translation_mag", "Mode-shape translation magnitude", "magnitude"),
    ("fixed_one_hot", "Fixed node indicator", "class"),
    ("blob_id_per_node", "Connected blob id", "class"),
    ("CONTACT_geodesic", "CONTACT geodesic feature", "continuous"),
    ("RBE2_geodesic_top1", "RBE2 nearest geodesic", "continuous"),
    ("RBE3_geodesic_top1", "RBE3 nearest geodesic", "continuous"),
    ("curv_mean", "Mean curvature", "continuous"),
    ("contact_distance", "CONTACT distance combined", "continuous"),
]


def finite_clip(values: np.ndarray, lower: float = 1.0, upper: float = 99.0) -> np.ndarray:
    values = np.asarray(values, dtype=np.float64)
    finite = values[np.isfinite(values)]
    if finite.size < 2:
        return values
    lo, hi = np.percentile(finite, [lower, upper])
    if lo == hi:
        return values
    return np.clip(values, lo, hi)


def load_attribute(h5: h5py.File, name: str, n: int) -> np.ndarray:
    if name == "eigvec_translation_mag":
        eigvec = h5["eigvec"][0, :, :3]
        return np.linalg.norm(eigvec, axis=1)
    if name == "contact_distance":
        parts = []
        for key in ["CONTACT_geodesic", "CONTACT_dijkstra", "CONTACT_dijkstra_length"]:
            if key in h5:
                arr = np.asarray(h5[key][:], dtype=np.float64)
                arr = finite_clip(arr)
                finite = arr[np.isfinite(arr)]
                if finite.size:
                    scale = np.nanmax(finite) - np.nanmin(finite)
                    if scale > 0:
                        arr = (arr - np.nanmin(finite)) / scale
                parts.append(arr)
        if not parts:
            return np.full(n, np.nan)
        return np.nanmean(np.vstack(parts), axis=0)
    if name in h5:
        arr = np.asarray(h5[name][:])
        if arr.ndim > 1:
            arr = np.linalg.norm(arr, axis=1)
        return arr
    return np.full(n, np.nan)


def save_view(sample: str, coords: np.ndarray, values: np.ndarray, attr: str, label: str, kind: str, freq: float) -> Path:
    out = OUT_DIR / f"{sample}_{attr}_{STAMP}.png"
    if out.exists() and out.stat().st_size > 0:
        print(f"{sample}: skip existing {attr}", flush=True)
        return out

    n = len(coords)
    stride = max(1, math.ceil(n / MAX_POINTS))
    pts = coords[::stride]
    vals = values[::stride]

    fig, axes = plt.subplots(1, 3, figsize=(13.2, 4.4))

    cmap = "viridis"
    if kind == "class":
        finite = vals[np.isfinite(vals)]
        if finite.size:
            unique = len(np.unique(finite))
        else:
            unique = 0
        cmap = "tab20" if unique <= 20 else "turbo"
    else:
        vals = finite_clip(vals)

    views = [("XY", 0, 1), ("XZ", 0, 2), ("YZ", 1, 2)]
    sc = None
    for ax, (view, a, b) in zip(axes, views):
        sc = ax.scatter(pts[:, a], pts[:, b], c=vals, s=0.55, cmap=cmap, alpha=0.72, linewidths=0)
        ax.set_title(view)
        ax.set_xlabel("xyz"[a] + " m")
        ax.set_ylabel("xyz"[b] + " m")
        ax.set_aspect("equal", adjustable="box")
        ax.grid(alpha=0.15)
    fig.colorbar(sc, ax=axes.ravel().tolist(), shrink=0.78, pad=0.015)
    fig.suptitle(f"{sample} | {label} | f={freq:.1f} Hz | shown={len(pts):,}/{n:,}")
    fig.tight_layout()

    fig.savefig(out, dpi=170)
    plt.close(fig)
    return out


def process_case(path: Path) -> dict:
    sample = path.stem
    with h5py.File(path, "r") as h5:
        coords = h5["coords"][:]
        freq = float(np.ravel(h5["frequency_hz"][:])[0])
        outputs = []
        for attr, label, kind in ATTRIBUTES:
            print(f"{sample}: rendering {attr}", flush=True)
            values = load_attribute(h5, attr, len(coords))
            out = save_view(sample, coords, values, attr, label, kind, freq)
            outputs.append(str(out))
    return {"sample": sample, "frequency_hz": freq, "files": outputs}


def process_one(sample: str, attr: str) -> Path:
    attr_map = {name: (label, kind) for name, label, kind in ATTRIBUTES}
    if attr not in attr_map:
        raise KeyError(attr)
    path = DATASET_DIR / f"{sample}.h5"
    label, kind = attr_map[attr]
    with h5py.File(path, "r") as h5:
        coords = h5["coords"][:]
        freq = float(np.ravel(h5["frequency_hz"][:])[0])
        values = load_attribute(h5, attr, len(coords))
        return save_view(sample, coords, values, attr, label, kind, freq)


def run_queue() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(DATASET_DIR.glob("*.h5"))
    total = len(files) * len(ATTRIBUTES)
    done = 0
    failed = []
    for path in files:
        sample = path.stem
        for attr, _, _ in ATTRIBUTES:
            out = OUT_DIR / f"{sample}_{attr}_{STAMP}.png"
            if out.exists() and out.stat().st_size > 0:
                done += 1
                continue
            print(f"QUEUE {done}/{total}: {sample} {attr}", flush=True)
            try:
                cmd = [sys.executable, __file__, "--one", sample, attr]
                result = subprocess.run(cmd)
                if result.returncode == 0 and out.exists() and out.stat().st_size > 0:
                    done += 1
                else:
                    failed.append({"sample": sample, "attr": attr, "returncode": result.returncode})
                    print(f"FAILED {sample} {attr} rc={result.returncode}", flush=True)
            except Exception as exc:
                failed.append({"sample": sample, "attr": attr, "error": repr(exc)})
                print(f"FAILED {sample} {attr} exc={exc!r}", flush=True)
    manifest = {
        "total_expected": total,
        "completed_png": len(list(OUT_DIR.glob(f"*_{STAMP}.png"))),
        "failed": failed,
    }
    (OUT_DIR / "queue_manifest.json").write_text(json.dumps(manifest, indent=2))
    print("POINTCLOUD_QUEUE_DONE", flush=True)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--one", nargs=2, metavar=("SAMPLE", "ATTR"))
    parser.add_argument("--queue", action="store_true")
    args = parser.parse_args()
    if args.one:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        out = process_one(args.one[0], args.one[1])
        print(out, flush=True)
        return
    if args.queue:
        run_queue()
        return

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(DATASET_DIR.glob("*.h5"))
    if not files:
        raise FileNotFoundError(f"No H5 files found under {DATASET_DIR}")
    manifest = []
    for i, path in enumerate(files, 1):
        print(f"[{i}/{len(files)}] {path.name}", flush=True)
        manifest.append(process_case(path))
    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print("POINTCLOUD_VIS_DONE", flush=True)


if __name__ == "__main__":
    main()
