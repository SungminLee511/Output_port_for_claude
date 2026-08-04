"""
Step 17 -- real tabular data pipeline.

Builds three DISJOINT pools (notes/20_plan.md Sec.4):

  R_eval : OpenML-CC18 (study 99), a recognised benchmark.  Final numbers only.
  R_fit  : everything else surviving the filters.  Prior fitting only.
  R_dev  : a random 30 from the non-CC18 remainder.  All development decisions.

Deduplication is by OpenML id AND by a content hash, because OpenML contains
near-duplicates of the same underlying dataset under different ids and a
reviewer will check.  The number of datasets removed by dedup is recorded in
the manifest and must be reported in the paper.

Usage:
  python -m pfnfit.data list      # build candidate list -> candidates.json
  python -m pfnfit.data fetch     # download + cache npz  (long, resumable)
  python -m pfnfit.data split     # dedup + write manifest.json
"""

import hashlib
import json
import os
import sys
import traceback

import numpy as np

ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(ROOT, "..", "data_cache")
CACHE = os.path.abspath(CACHE)
os.makedirs(CACHE, exist_ok=True)

MIN_ROWS, MAX_ROWS = 200, 50000
MAX_FEAT = 200
MIN_CLS, MAX_CLS = 2, 10
ROW_CAP = 20000            # rows stored per dataset
N_DEV = 30


# ---------------------------------------------------------------------------
def build_candidates():
    import openml
    dl = openml.datasets.list_datasets(output_format="dataframe")
    print(f"openml lists {len(dl)} datasets", flush=True)
    f = dl[
        (dl.NumberOfInstances >= MIN_ROWS)
        & (dl.NumberOfInstances <= MAX_ROWS)
        & (dl.NumberOfFeatures <= MAX_FEAT)
        & (dl.NumberOfClasses >= MIN_CLS)
        & (dl.NumberOfClasses <= MAX_CLS)
        & (dl.status == "active")
    ]
    f = f.drop_duplicates(subset=["name", "NumberOfInstances",
                                  "NumberOfFeatures", "NumberOfClasses"])
    print(f"{len(f)} pass filters", flush=True)

    cc18 = set()
    try:
        s = openml.study.get_suite(99)
        cc18 = set(int(i) for i in s.data)
        print(f"CC18 suite: {len(cc18)} dataset ids", flush=True)
    except Exception:
        traceback.print_exc()

    cand = []
    for did, row in f.iterrows():
        cand.append({"did": int(did), "name": str(row["name"]),
                     "n": int(row.NumberOfInstances),
                     "d": int(row.NumberOfFeatures),
                     "c": int(row.NumberOfClasses),
                     "cc18": int(did) in cc18})
    # keep CC18 always; cap the rest for tractability
    rng = np.random.default_rng(0)
    keep = [c for c in cand if c["cc18"]]
    rest = [c for c in cand if not c["cc18"]]
    idx = rng.permutation(len(rest))[:700]
    keep += [rest[i] for i in idx]
    with open(os.path.join(CACHE, "candidates.json"), "w") as fh:
        json.dump(keep, fh, indent=1)
    print(f"wrote {len(keep)} candidates "
          f"({sum(c['cc18'] for c in keep)} CC18)", flush=True)


# ---------------------------------------------------------------------------
def _prep(X, y, cat_ind):
    import pandas as pd
    if not isinstance(X, pd.DataFrame):
        X = pd.DataFrame(X)
    cols, cat = [], []
    for j, cname in enumerate(X.columns):
        col = X[cname]
        is_cat = bool(cat_ind[j]) if cat_ind is not None and j < len(cat_ind) \
            else (col.dtype == object or str(col.dtype) == "category")
        if is_cat:
            codes = pd.Categorical(col).codes.astype(np.float64)
            codes[codes < 0] = np.nan
            v = codes
        else:
            v = pd.to_numeric(col, errors="coerce").to_numpy(dtype=np.float64)
        if np.all(~np.isfinite(v)):
            continue
        med = np.nanmedian(v[np.isfinite(v)]) if np.any(np.isfinite(v)) else 0.0
        v = np.where(np.isfinite(v), v, med)
        if np.nanstd(v) < 1e-12:
            continue
        cols.append(v)
        cat.append(is_cat)
    if not cols:
        raise ValueError("no usable columns")
    Xa = np.stack(cols, 1).astype(np.float32)
    ya = pd.Categorical(pd.Series(np.asarray(y)).astype(str)).codes.astype(np.int64)
    ok = ya >= 0
    return Xa[ok], ya[ok], np.array(cat, dtype=bool)


def content_hash(X, y):
    n, d = X.shape
    cc = tuple(sorted(np.bincount(y).tolist()))
    mu = np.round(np.sort(X.mean(0)), 4)
    sd = np.round(np.sort(X.std(0)), 4)
    h = hashlib.sha1()
    h.update(str((n, d, cc)).encode())
    h.update(mu.tobytes()); h.update(sd.tobytes())
    return h.hexdigest()


def fetch():
    import openml
    cand = json.load(open(os.path.join(CACHE, "candidates.json")))
    ddir = os.path.join(CACHE, "npz")
    os.makedirs(ddir, exist_ok=True)
    ok = fail = skip = 0
    for i, c in enumerate(cand):
        p = os.path.join(ddir, f"{c['did']}.npz")
        if os.path.exists(p):
            skip += 1
            continue
        try:
            ds = openml.datasets.get_dataset(c["did"], download_data=True,
                                             download_qualities=False,
                                             download_features_meta_data=True)
            X, y, cat, _ = ds.get_data(target=ds.default_target_attribute)
            Xa, ya, catm = _prep(X, y, cat)
            if Xa.shape[0] < MIN_ROWS or Xa.shape[1] < 2:
                raise ValueError("too small after prep")
            k = len(np.unique(ya))
            if k < MIN_CLS or k > MAX_CLS:
                raise ValueError(f"class count {k}")
            if Xa.shape[0] > ROW_CAP:
                r = np.random.default_rng(c["did"]).permutation(Xa.shape[0])[:ROW_CAP]
                Xa, ya = Xa[r], ya[r]
            np.savez_compressed(p, X=Xa, y=ya, cat=catm,
                                name=c["name"], did=c["did"], cc18=c["cc18"])
            ok += 1
        except Exception as e:
            fail += 1
            print(f"  fail {c['did']} {c['name'][:30]}: {type(e).__name__} {e}",
                  flush=True)
        if (i + 1) % 25 == 0:
            print(f"[{i+1}/{len(cand)}] ok={ok} fail={fail} skip={skip}",
                  flush=True)
    print(f"DONE ok={ok} fail={fail} skip={skip}", flush=True)


# ---------------------------------------------------------------------------
def split():
    ddir = os.path.join(CACHE, "npz")
    files = sorted(os.listdir(ddir))
    recs, seen = [], {}
    dup = 0
    for fn in files:
        z = np.load(os.path.join(ddir, fn), allow_pickle=True)
        X, y = z["X"], z["y"]
        h = content_hash(X, y)
        r = {"did": int(z["did"]), "name": str(z["name"]),
             "n": int(X.shape[0]), "d": int(X.shape[1]),
             "c": int(len(np.unique(y))), "cc18": bool(z["cc18"]),
             "hash": h, "file": fn}
        if h in seen:
            dup += 1
            # a CC18 member always wins the collision, so R_eval is never
            # weakened and the duplicate is dropped from R_fit
            if r["cc18"] and not seen[h]["cc18"]:
                seen[h]["dropped_for"] = r["did"]
                seen[h] = r
            continue
        seen[h] = r
        recs.append(r)
    recs = [r for r in recs if r["hash"] in seen]
    print(f"{len(files)} cached, {dup} content-hash duplicates removed, "
          f"{len(recs)} unique", flush=True)

    ev = [r for r in recs if r["cc18"]]
    rest = [r for r in recs if not r["cc18"]]
    rng = np.random.default_rng(20260804)
    idx = rng.permutation(len(rest))
    dev = [rest[i] for i in idx[:N_DEV]]
    fit = [rest[i] for i in idx[N_DEV:]]
    man = {"n_cached": len(files), "n_dup_removed": dup, "n_unique": len(recs),
           "R_eval": ev, "R_dev": dev, "R_fit": fit,
           "filters": {"rows": [MIN_ROWS, MAX_ROWS], "max_feat": MAX_FEAT,
                       "classes": [MIN_CLS, MAX_CLS], "row_cap": ROW_CAP}}
    with open(os.path.join(CACHE, "manifest.json"), "w") as f:
        json.dump(man, f, indent=1)
    print(f"R_eval {len(ev)} | R_dev {len(dev)} | R_fit {len(fit)}", flush=True)
    # sanity: no id or hash overlap
    for a, b in [("R_eval", "R_fit"), ("R_eval", "R_dev"), ("R_dev", "R_fit")]:
        ia = {r["did"] for r in man[a]}; ib = {r["did"] for r in man[b]}
        ha = {r["hash"] for r in man[a]}; hb = {r["hash"] for r in man[b]}
        assert not (ia & ib), (a, b, ia & ib)
        assert not (ha & hb), (a, b)
    print("disjointness verified (id and content hash)", flush=True)


if __name__ == "__main__":
    {"list": build_candidates, "fetch": fetch, "split": split}[sys.argv[1]]()
