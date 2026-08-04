"""
Step 20 -- score real datasets under a grid of theta atoms, then fit pi* by NPMLE.

The theta-conditional checkpoint q(. | ., theta) turns every real dataset D_m
into a K-vector of prequential log-likelihoods

    logL[m,k] = (1/|P|) sum_{sigma in P} sum_i log q(y_sigma(i) | x_sigma(i),
                                                     D_sigma(<i), theta_k)

which is exactly the quantity Theorem 3 / Theorem 5 need.  Averaging over a
small set of orderings P is the fix for Warning 2.3 (order dependence): the
score we report is an average of exact prequential scores, not an approximation
of a marginal likelihood.

Real datasets are put in the SAME representation the prior emits (per-column
z-score after median imputation, feature padding with a mask), so the model is
never asked to extrapolate on scale.

  python -m pfnfit.score score --ckpt ckpt/cond_s0.pt --pool R_fit
  python -m pfnfit.score npmle --scores runs/score_R_fit.npz
"""

import argparse
import json
import os
import time

import numpy as np
import torch

from .model import PFN2D, masked_logprobs
from .prior import D_THETA
from .train import load

ROOT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.abspath(os.path.join(ROOT, "..", "data_cache"))
RUNS = os.path.abspath(os.path.join(ROOT, "..", "runs"))
os.makedirs(RUNS, exist_ok=True)
DEV = "cuda"


# ---------------------------------------------------------------------------
def sobol_atoms(K, seed=0):
    """Scrambled Sobol points in [0,1]^12 -- a low-discrepancy atom set is the
    right default for an NPMLE support: it covers the cube far more evenly than
    iid uniform at the same K, and the NPMLE is invariant to how atoms were
    drawn."""
    s = torch.quasirandom.SobolEngine(D_THETA, scramble=True, seed=seed)
    return s.draw(K).numpy().astype(np.float32)


def load_real(rec, n, d_max, rng, n_cls_max=10):
    """One cached OpenML table -> (X (n,d_max), fmask (d_max,), y (n,), ncls).

    Rows are subsampled without replacement when the table is larger than n and
    WITH replacement otherwise (so that every dataset contributes the same n
    prequential terms and logL is comparable across datasets -- a dataset with
    more rows must not get a larger score just for being long)."""
    z = np.load(os.path.join(CACHE, "npz", rec["file"]), allow_pickle=True)
    X, y = z["X"].astype(np.float64), z["y"].astype(np.int64)
    N, d = X.shape
    idx = rng.choice(N, n, replace=N < n)
    X, y = X[idx], y[idx]
    # relabel to 0..k-1 on the subsample and drop the dataset if it collapsed
    u, y = np.unique(y, return_inverse=True)
    k = len(u)
    if k < 2 or k > n_cls_max:
        return None
    if d > d_max:
        # keep the d_max columns with the highest |corr| to a one-hot of y is a
        # supervised choice and would leak; take a random subset instead.
        c = rng.permutation(d)[:d_max]
        X = X[:, c]
        d = d_max
    mu, sd = X.mean(0), X.std(0)
    X = (X - mu) / np.maximum(sd, 1e-6)
    Xp = np.zeros((n, d_max), dtype=np.float32)
    Xp[:, :d] = np.nan_to_num(X).astype(np.float32)
    fm = np.zeros(d_max, dtype=np.float32)
    fm[:d] = 1.0
    return Xp, fm, y.astype(np.int64), k


@torch.no_grad()
def score_pool(ckpt, pool, K, P, n, seed, atom_seed, out, chunk=8, limit=None):
    model, meta = load(ckpt)
    d_max = meta["cfg"]["d_max"]
    ncm = meta["cfg"]["ncls_max"]
    assert meta["cfg"]["theta_cond"], "scoring needs a theta-conditional model"
    man = json.load(open(os.path.join(CACHE, "manifest.json")))
    recs = man[pool] if limit is None else man[pool][:limit]
    A = sobol_atoms(K, atom_seed)
    At = torch.tensor(A, device=DEV)
    mq, mc = PFN2D.masks(n, DEV, torch.float32)

    logL = np.full((len(recs), K), np.nan, dtype=np.float64)
    keep, t0 = [], time.time()
    for m, rec in enumerate(recs):
        rng = np.random.default_rng(seed * 1000003 + rec["did"])
        r = load_real(rec, n, d_max, rng, ncm)
        if r is None:
            continue
        Xn, fmn, yn, k = r
        acc = np.zeros(K, dtype=np.float64)
        for p in range(P):
            o = rng.permutation(n) if p else np.arange(n)
            Xo = torch.tensor(Xn[o], device=DEV)[None]
            yo = torch.tensor(yn[o], device=DEV)[None]
            fo = torch.tensor(fmn, device=DEV)[None]
            nc = torch.tensor([k], device=DEV)
            for s in range(0, K, chunk):
                b = min(chunk, K - s)
                with torch.amp.autocast("cuda", dtype=torch.bfloat16):
                    lg = model(Xo.expand(b, n, d_max), fo.expand(b, d_max),
                               yo.expand(b, n), At[s:s + b], mq=mq, mc=mc)
                lp, _ = masked_logprobs(lg.float(), yo.expand(b, n),
                                        nc.expand(b))
                acc[s:s + b] += lp.sum(1).double().cpu().numpy()
        logL[m] = acc / P
        keep.append(m)
        if len(keep) % 10 == 0:
            el = time.time() - t0
            print(f"[{len(keep)}/{len(recs)}] did={rec['did']} n_cls={k} "
                  f"best={logL[m].max():.1f} worst={logL[m].min():.1f} "
                  f"{el/60:.1f}m eta {el/len(keep)*(len(recs)-len(keep))/60:.1f}m",
                  flush=True)
    keep = np.array(keep)
    np.savez(out, logL=logL[keep], atoms=A,
             did=np.array([recs[i]["did"] for i in keep]),
             n=n, P=P, pool=pool, ckpt=os.path.basename(ckpt))
    print(f"saved {out}  {len(keep)}/{len(recs)} datasets x {K} atoms "
          f"({(time.time()-t0)/60:.1f} min)", flush=True)
    return out


# ---------------------------------------------------------------------------
def npmle(logL, iters=5000, tol=1e-12):
    """Kiefer-Wolfowitz NPMLE by EM (math/01_setup.md Cor 5.1).  Concave in pi,
    so the fixed point is global."""
    M, K = logL.shape
    logpi = np.full(K, -np.log(K))
    prev = -np.inf
    for it in range(iters):
        z = logpi[None, :] + logL
        mx = z.max(1, keepdims=True)
        w = np.exp(z - mx)
        s = w.sum(1, keepdims=True)
        obj = float((np.log(s) + mx).sum()) / M
        r = w / s
        pi = np.clip(r.mean(0), 1e-300, None)
        logpi = np.log(pi / pi.sum())
        if obj - prev < tol and it > 50:
            break
        prev = obj
    return np.exp(logpi), obj, it


def ess(pi):
    p = pi / pi.sum()
    return float(1.0 / (p ** 2).sum())


NAMES = ["depth", "width", "density", "relu", "sin", "wscale", "nsig",
         "heavy", "catfrac", "missing", "warp", "lnoise"]


def report(path, out_md=None):
    z = np.load(path, allow_pickle=True)
    logL, A = z["logL"], z["atoms"]
    M, K = logL.shape
    pi, obj, it = npmle(logL)
    n = int(z["n"])
    # per-dataset comparison of the mixture against the single best atom
    zz = np.log(pi)[None, :] + logL
    mx = zz.max(1, keepdims=True)
    mix = (np.log(np.exp(zz - mx).sum(1, keepdims=True)) + mx)[:, 0]
    best_marg = logL.max(1)
    unif = (np.log(np.exp(logL - logL.max(1, keepdims=True)).sum(1)) - np.log(K)
            + logL.max(1))
    mean = pi @ A
    lines = []
    lines.append(f"# Step 20 -- pi* fitted on {str(z['pool'])} "
                 f"(M={M}, K={K}, n={n}, P={int(z['P'])})\n")
    lines.append(f"checkpoint `{str(z['ckpt'])}`\n")
    lines.append(f"NPMLE converged in {it} EM iters, "
                 f"objective {obj:.2f} nats/dataset, ESS = {ess(pi):.1f} atoms "
                 f"of {K}, support(pi > 1e-4) = {int((pi > 1e-4).sum())}\n")
    lines.append("| quantity | nats/dataset |\n|---|---|")
    lines.append(f"| mixture under pi* | {mix.mean()/n:+.4f} |")
    lines.append(f"| mixture under uniform pi_0 | {unif.mean()/n:+.4f} |")
    lines.append(f"| best single atom per dataset (oracle) | "
                 f"{best_marg.mean()/n:+.4f} |")
    lines.append(f"| single best atom overall | {logL.mean(0).max()/n:+.4f} |\n")
    lines.append("## P1: does pi* move theta the predicted way?\n")
    lines.append("| coord | E_pi0[theta] | E_pi*[theta] | shift | P1 predicts |")
    lines.append("|---|---|---|---|---|")
    pred = {"catfrac": "lower", "missing": "lower", "lnoise": "lower",
            "sin": "lower"}
    for j, nm in enumerate(NAMES):
        lines.append(f"| {nm} | {A[:, j].mean():.3f} | {mean[j]:.3f} | "
                     f"{mean[j]-A[:, j].mean():+.3f} | {pred.get(nm, '-')} |")
    ok = all(mean[NAMES.index(k)] < A[:, NAMES.index(k)].mean()
             for k in pred)
    lines.append(f"\n**P1 direction test: {'PASS' if ok else 'FAIL'}** "
                 f"({sum(mean[NAMES.index(k)] < A[:, NAMES.index(k)].mean() for k in pred)}/4 "
                 f"coordinates moved as pre-registered)\n")
    top = np.argsort(-pi)[:10]
    lines.append("## top atoms\n")
    lines.append("| rank | pi_k | " + " | ".join(NAMES) + " |")
    lines.append("|---" * (len(NAMES) + 2) + "|")
    for r, k in enumerate(top):
        lines.append(f"| {r+1} | {pi[k]:.4f} | "
                     + " | ".join(f"{A[k, j]:.2f}" for j in range(D_THETA))
                     + " |")
    txt = "\n".join(lines)
    print(txt)
    p = os.path.join(RUNS, os.path.basename(path).replace(".npz", "_pi.json"))
    json.dump({"atoms": A.tolist(), "pi": pi.tolist(), "obj": obj,
               "ess": ess(pi), "M": M, "K": K, "n": n}, open(p, "w"))
    print(f"\nsaved {p}", flush=True)
    if out_md:
        open(out_md, "w").write(txt + "\n")
    return p


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["score", "npmle"])
    ap.add_argument("--ckpt", default="ckpt/cond_s0.pt")
    ap.add_argument("--pool", default="R_fit")
    ap.add_argument("--K", type=int, default=256)
    ap.add_argument("--P", type=int, default=2)
    ap.add_argument("--n", type=int, default=512)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--atom_seed", type=int, default=0)
    ap.add_argument("--chunk", type=int, default=8)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--scores", default=None)
    ap.add_argument("--out", default=None)
    ap.add_argument("--md", default=None)
    a = ap.parse_args()
    if a.cmd == "score":
        out = a.out or os.path.join(RUNS, f"score_{a.pool}.npz")
        score_pool(a.ckpt, a.pool, a.K, a.P, a.n, a.seed, a.atom_seed, out,
                   a.chunk, a.limit)
    else:
        report(a.scores or os.path.join(RUNS, f"score_{a.pool}.npz"), a.md)
