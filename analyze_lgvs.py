from __future__ import annotations

import json
import math
from pathlib import Path

import h5py
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


DATASET_DIR = Path("../data_port/huggingface_datasets/solverx/lg-vs_JIG/data_v2")
RESULTS_DIR = Path("results")


def scalar_value(h5: h5py.File, key: str, default=np.nan):
    if key not in h5:
        return default
    value = h5[key][()]
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    arr = np.asarray(value)
    if arr.shape == ():
        item = arr.item()
        if isinstance(item, bytes):
            return item.decode("utf-8", errors="replace")
        return item
    if arr.size == 1:
        item = arr.reshape(-1)[0].item()
        if isinstance(item, bytes):
            return item.decode("utf-8", errors="replace")
        return item
    return arr.tolist()


def count_rows(h5: h5py.File, key: str) -> int:
    if key not in h5:
        return 0
    shape = h5[key].shape
    return int(shape[0]) if shape else 1


def finite_stats(arr: np.ndarray) -> dict[str, float]:
    arr = np.asarray(arr)
    arr = arr[np.isfinite(arr)]
    if arr.size == 0:
        return {"min": np.nan, "mean": np.nan, "max": np.nan}
    return {
        "min": float(np.min(arr)),
        "mean": float(np.mean(arr)),
        "max": float(np.max(arr)),
    }


def summarize_file(path: Path) -> dict:
    with h5py.File(path, "r") as h5:
        coords = h5["coords"][:]
        mins = coords.min(axis=0)
        maxs = coords.max(axis=0)
        spans = maxs - mins
        cbar_length = h5["CBAR_length"][:] if "CBAR_length" in h5 else np.array([])
        cbar_radius = h5["CBAR_radius"][:] if "CBAR_radius" in h5 else np.array([])
        conm2_mass = h5["CONM2_mass"][:] if "CONM2_mass" in h5 else np.array([])
        fixed = h5["fixed_one_hot"][:] if "fixed_one_hot" in h5 else np.array([])
        contact_active = h5["contact_edge_active"][:] if "contact_edge_active" in h5 else np.array([])
        freq = float(np.ravel(h5["frequency_hz"][:])[0]) if "frequency_hz" in h5 else np.nan
        eigval = float(np.ravel(h5["eigval"][:])[0]) if "eigval" in h5 else np.nan

        return {
            "sample": path.stem,
            "group": path.stem.split("_")[0],
            "file_mb": path.stat().st_size / 1024 / 1024,
            "nodes": count_rows(h5, "coords"),
            "ctetra": count_rows(h5, "CTETRA"),
            "cbar": count_rows(h5, "CBAR"),
            "conm2": count_rows(h5, "CONM2_mass"),
            "surface_triangles": count_rows(h5, "surface_triangles"),
            "surface_triangles_p2": count_rows(h5, "surface_triangles_p2"),
            "rbe2_edges": h5["rbe2_edge_index"].shape[1] if "rbe2_edge_index" in h5 else 0,
            "rbe3_edges": h5["rbe3_edge_index"].shape[1] if "rbe3_edge_index" in h5 else 0,
            "contact_pairs": count_rows(h5, "contact_id"),
            "contact_edges": count_rows(h5, "contact_edge_active"),
            "contact_edges_active": int(np.sum(contact_active)) if contact_active.size else 0,
            "fixed_nodes": int(np.sum(fixed > 0)) if fixed.size else 0,
            "n_blobs": int(scalar_value(h5, "n_blobs", 0)),
            "total_mass_kg": float(scalar_value(h5, "total_mass_kg", np.nan)),
            "payload_mass_kg": float(np.sum(conm2_mass)) if conm2_mass.size else 0.0,
            "frequency_hz": freq,
            "eigval": eigval,
            "bbox_x_m": float(spans[0]),
            "bbox_y_m": float(spans[1]),
            "bbox_z_m": float(spans[2]),
            "bbox_diag_m": float(np.linalg.norm(spans)),
            "bbox_volume_m3": float(np.prod(spans)),
            "cbar_length_mean_m": finite_stats(cbar_length)["mean"],
            "cbar_length_max_m": finite_stats(cbar_length)["max"],
            "cbar_radius_mean_m": finite_stats(cbar_radius)["mean"],
            "pipeline_version": scalar_value(h5, "pipeline_version_str", ""),
            "pipeline_git_sha": scalar_value(h5, "pipeline_git_sha", ""),
        }


def save_dataframe_outputs(df: pd.DataFrame) -> None:
    df.to_csv(RESULTS_DIR / "lgvs_sample_summary.csv", index=False)
    grouped = df.groupby("group").agg(
        samples=("sample", "count"),
        frequency_mean_hz=("frequency_hz", "mean"),
        frequency_min_hz=("frequency_hz", "min"),
        frequency_max_hz=("frequency_hz", "max"),
        mass_mean_kg=("total_mass_kg", "mean"),
        nodes_mean=("nodes", "mean"),
        ctetra_mean=("ctetra", "mean"),
    )
    grouped.to_csv(RESULTS_DIR / "lgvs_group_summary.csv")
    payload = {
        "n_samples": int(len(df)),
        "total_size_gb": float(df["file_mb"].sum() / 1024),
        "frequency_hz": {
            "min": float(df["frequency_hz"].min()),
            "mean": float(df["frequency_hz"].mean()),
            "max": float(df["frequency_hz"].max()),
        },
        "total_mass_kg": {
            "min": float(df["total_mass_kg"].min()),
            "mean": float(df["total_mass_kg"].mean()),
            "max": float(df["total_mass_kg"].max()),
        },
        "groups": grouped.reset_index().to_dict(orient="records"),
    }
    (RESULTS_DIR / "summary.json").write_text(json.dumps(payload, indent=2))


def scatter(df: pd.DataFrame, x: str, y: str, out: str, title: str) -> None:
    fig, ax = plt.subplots(figsize=(8, 5))
    colors = df["group"].map({"g1": "#31688e", "g2": "#35b779"}).fillna("#444")
    ax.scatter(df[x], df[y], c=colors, s=70, alpha=0.82, edgecolor="white", linewidth=0.6)
    for _, row in df.iterrows():
        ax.annotate(row["sample"], (row[x], row[y]), fontsize=6, alpha=0.7)
    ax.set_xlabel(x)
    ax.set_ylabel(y)
    ax.set_title(title)
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / out, dpi=180)
    plt.close(fig)


def make_plots(df: pd.DataFrame) -> None:
    plt.style.use("seaborn-v0_8-whitegrid")

    fig, ax = plt.subplots(figsize=(10, 5))
    order = df.sort_values("frequency_hz")
    ax.bar(order["sample"], order["frequency_hz"], color=order["group"].map({"g1": "#31688e", "g2": "#35b779"}))
    ax.set_ylabel("first natural frequency (Hz)")
    ax.set_xlabel("sample")
    ax.set_title("LG-VS jig first natural frequency by sample")
    ax.tick_params(axis="x", labelrotation=90, labelsize=6)
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "frequency_by_sample.png", dpi=180)
    plt.close(fig)

    fig, axes = plt.subplots(2, 2, figsize=(10, 8))
    for ax, col, title in [
        (axes[0, 0], "frequency_hz", "Frequency Hz"),
        (axes[0, 1], "total_mass_kg", "Total Mass kg"),
        (axes[1, 0], "nodes", "Node Count"),
        (axes[1, 1], "ctetra", "CTETRA Count"),
    ]:
        for group, part in df.groupby("group"):
            ax.hist(part[col], bins=10, alpha=0.58, label=group)
        ax.set_title(title)
        ax.legend()
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "distribution_grid.png", dpi=180)
    plt.close(fig)

    scatter(df, "total_mass_kg", "frequency_hz", "mass_vs_frequency.png", "Mass vs first natural frequency")
    scatter(df, "nodes", "frequency_hz", "nodes_vs_frequency.png", "Mesh size vs first natural frequency")
    scatter(df, "n_blobs", "frequency_hz", "blobs_vs_frequency.png", "Disconnected blobs vs first natural frequency")
    scatter(df, "contact_edges_active", "frequency_hz", "contact_vs_frequency.png", "Active contact edges vs first natural frequency")

    corr_cols = [
        "frequency_hz", "total_mass_kg", "payload_mass_kg", "nodes", "ctetra", "cbar",
        "n_blobs", "fixed_nodes", "contact_edges_active", "rbe2_edges", "rbe3_edges",
        "bbox_diag_m", "bbox_volume_m3",
    ]
    corr = df[corr_cols].corr(numeric_only=True)
    fig, ax = plt.subplots(figsize=(10, 8))
    im = ax.imshow(corr.values, vmin=-1, vmax=1, cmap="coolwarm")
    ax.set_xticks(range(len(corr_cols)), corr_cols, rotation=90, fontsize=7)
    ax.set_yticks(range(len(corr_cols)), corr_cols, fontsize=7)
    fig.colorbar(im, ax=ax, shrink=0.78)
    ax.set_title("Feature correlation matrix")
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / "correlation_matrix.png", dpi=180)
    plt.close(fig)


def sample_geometry_plot(sample_path: Path, out_name: str, max_points: int = 50000) -> None:
    with h5py.File(sample_path, "r") as h5:
        coords = h5["coords"][:]
        freq = float(np.ravel(h5["frequency_hz"][:])[0])
        fixed = h5["fixed_one_hot"][:] if "fixed_one_hot" in h5 else np.zeros(len(coords), dtype=np.int32)
        contact = h5["CONTACT_geodesic"][:] if "CONTACT_geodesic" in h5 else np.full(len(coords), np.nan)

    stride = max(1, math.ceil(len(coords) / max_points))
    pts = coords[::stride]
    fixed_pts = fixed[::stride] > 0
    contact_vals = contact[::stride]
    color = np.where(fixed_pts, np.nanmin(contact_vals[np.isfinite(contact_vals)]) if np.isfinite(contact_vals).any() else 0, contact_vals)

    fig = plt.figure(figsize=(8, 7))
    ax = fig.add_subplot(111, projection="3d")
    ax.scatter(pts[:, 0], pts[:, 1], pts[:, 2], c=color, s=0.35, cmap="viridis", alpha=0.75)
    if fixed_pts.any():
        fp = pts[fixed_pts]
        ax.scatter(fp[:, 0], fp[:, 1], fp[:, 2], c="#d62728", s=4, label="fixed")
        ax.legend(loc="upper right")
    ax.set_title(f"{sample_path.stem} point cloud, f={freq:.1f} Hz")
    ax.set_xlabel("x m")
    ax.set_ylabel("y m")
    ax.set_zlabel("z m")
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / out_name, dpi=180)
    plt.close(fig)


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(DATASET_DIR.glob("*.h5"))
    if not files:
        raise FileNotFoundError(f"No H5 files found under {DATASET_DIR}")

    rows = []
    for i, path in enumerate(files, 1):
        print(f"[{i}/{len(files)}] summarizing {path.name}", flush=True)
        rows.append(summarize_file(path))

    df = pd.DataFrame(rows).sort_values(["group", "sample"])
    save_dataframe_outputs(df)
    make_plots(df)

    low = df.loc[df["frequency_hz"].idxmin(), "sample"]
    high = df.loc[df["frequency_hz"].idxmax(), "sample"]
    median = df.iloc[(df["frequency_hz"] - df["frequency_hz"].median()).abs().argsort().iloc[0]]["sample"]
    for sample, out in [
        (low, "geometry_lowest_frequency.png"),
        (median, "geometry_median_frequency.png"),
        (high, "geometry_highest_frequency.png"),
    ]:
        print(f"plotting geometry {sample}", flush=True)
        sample_geometry_plot(DATASET_DIR / f"{sample}.h5", out)

    top_corr = (
        df.drop(columns=["sample", "group", "pipeline_version", "pipeline_git_sha"])
        .corr(numeric_only=True)["frequency_hz"]
        .drop("frequency_hz")
        .sort_values(key=lambda s: s.abs(), ascending=False)
    )
    lines = [
        "# LG-VS Analysis Results",
        "",
        f"Samples analyzed: {len(df)}",
        f"Total H5 size: {df['file_mb'].sum() / 1024:.2f} GB",
        f"Frequency range: {df['frequency_hz'].min():.2f} - {df['frequency_hz'].max():.2f} Hz",
        f"Mean frequency: {df['frequency_hz'].mean():.2f} Hz",
        f"Mass range: {df['total_mass_kg'].min():.2f} - {df['total_mass_kg'].max():.2f} kg",
        "",
        "## Strongest Absolute Correlations With Frequency",
        "",
    ]
    for name, value in top_corr.head(12).items():
        lines.append(f"- `{name}`: {value:.4f}")
    lines += [
        "",
        "## Generated Files",
        "",
        "- `lgvs_sample_summary.csv`",
        "- `lgvs_group_summary.csv`",
        "- `summary.json`",
        "- `frequency_by_sample.png`",
        "- `distribution_grid.png`",
        "- `mass_vs_frequency.png`",
        "- `nodes_vs_frequency.png`",
        "- `blobs_vs_frequency.png`",
        "- `contact_vs_frequency.png`",
        "- `correlation_matrix.png`",
        "- `geometry_lowest_frequency.png`",
        "- `geometry_median_frequency.png`",
        "- `geometry_highest_frequency.png`",
        "",
    ]
    (RESULTS_DIR / "REPORT.md").write_text("\n".join(lines))
    print("LGVS_ANALYSIS_DONE", flush=True)


if __name__ == "__main__":
    main()

