"""
Smoke test S03 -- the decisive question left by S02:

  Does the NPMLE-over-pi contribution (the "empirical Bayes" part, Thm 5)
  grow with K, or is it an artefact of the log K slack in Theorem 4?

Design: theta is now CONTINUOUS, 7-dimensional
    theta = [onehot4(type), complexity c, noise nu, sparsity s],  c,nu,s in [0,1]
so ONE trained network can be evaluated on ANY finite grid {theta_k}_{k<K}
without retraining.  We evaluate K in {4, 16, 64} on the same corpus.

The corpus ("real data" stand-in) is drawn from a deliberately PEAKED
continuous theta-distribution, so a uniform grid prior is genuinely bad and the
NPMLE has something to find.

Also reported: (log K - H(pi*)) / N_SCORE, the exact size of the prior-weight
term that separates uniform mixing from pi*-mixing.  If the measured
uniform-minus-NPMLE gap equals this quantity, then the NPMLE is buying nothing
beyond the trivial log-K term and the empirical-Bayes framing of deployment
mode M1 is dead (M2 would be unaffected -- it is a different mechanism).
"""

import json
import math
import os
import time

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

torch.backends.cuda.matmul.allow_tf32 = True
DEV = "cuda" if torch.cuda.is_available() else "cpu"
OUT = os.path.dirname(os.path.abspath(__file__))

D_MAX = 8
N_ROWS = 64
N_SCORE = 48
TDIM = 7
NTYPE = 4


# ---------------------------------------------------------------------------
# Continuous-theta generator family.
# ---------------------------------------------------------------------------
def gen_theta(rng, t, c, nu, s, n, d):
    x = rng.standard_normal((n, d)).astype(np.float32)
    nrel = max(1, int(round(d * (0.25 + 0.75 * s))))
    rel = rng.permutation(d)[:nrel]
    xr = x[:, rel]
    dr = nrel
    if t == 0:                                   # linear
        w = rng.standard_normal(dr)
        lg = xr @ w
    elif t == 1:                                 # mlp
        h = 2 + int(round(c * 30))
        W1 = rng.standard_normal((dr, h)) / math.sqrt(dr)
        b1 = rng.standard_normal(h) * 0.5
        W2 = rng.standard_normal(h) / math.sqrt(h)
        lg = np.tanh(xr @ W1 + b1) @ W2
    elif t == 2:                                 # axis-aligned tree
        depth = 1 + int(round(c * 4))
        idx = np.zeros(n, dtype=np.int64)
        for _ in range(depth):
            f = int(rng.integers(0, dr))
            th = rng.standard_normal() * 0.7
            idx = idx * 2 + (xr[:, f] > th).astype(np.int64)
        lg = (rng.standard_normal(2 ** depth) * 2.0)[idx]
    else:                                        # rbf
        ncen = 1 + int(round(c * 7))
        C = rng.standard_normal((ncen, dr))
        ls = rng.uniform(0.5, 1.5, size=ncen)
        a = rng.standard_normal(ncen) * 2.0
        d2 = ((xr[:, None, :] - C[None]) ** 2).sum(-1)
        lg = (np.exp(-d2 / (2 * ls[None] ** 2)) * a[None]).sum(-1)
    lg = lg / (lg.std() + 1e-6)
    scale = math.exp(math.log(5.0) * (1 - nu) + math.log(0.4) * nu)
    p = 1.0 / (1.0 + np.exp(-scale * lg))
    y = (rng.random(n) < p).astype(np.int64)
    xp = np.zeros((n, D_MAX), dtype=np.float32)
    xp[:, :d] = (x - x.mean(0)) / (x.std(0) + 1e-6)
    m = np.zeros(D_MAX, dtype=np.float32)
    m[:d] = 1.0
    return xp, y, m


def theta_vec(t, c, nu, s):
    v = np.zeros(TDIM, dtype=np.float32)
    v[t] = 1.0
    v[4], v[5], v[6] = c, nu, s
    return v


def sample_batch(rng, bs, n=N_ROWS):
    X = np.zeros((bs, n, D_MAX), dtype=np.float32)
    Y = np.zeros((bs, n), dtype=np.int64)
    M = np.zeros((bs, D_MAX), dtype=np.float32)
    T = np.zeros((bs, TDIM), dtype=np.float32)
    for b in range(bs):
        t = int(rng.integers(0, NTYPE))
        c, nu, s = rng.random(3)
        d = int(rng.integers(3, D_MAX + 1))
        X[b], Y[b], M[b] = gen_theta(rng, t, c, nu, s, n, d)
        T[b] = theta_vec(t, c, nu, s)
    return (torch.from_numpy(X), torch.from_numpy(Y),
            torch.from_numpy(M), torch.from_numpy(T))


def sample_corpus(rng, nds, n=N_ROWS):
    """PEAKED theta distribution: mostly deep low-noise trees."""
    X = np.zeros((nds, n, D_MAX), dtype=np.float32)
    Y = np.zeros((nds, n), dtype=np.int64)
    M = np.zeros((nds, D_MAX), dtype=np.float32)
    for b in range(nds):
        t = 2 if rng.random() < 0.7 else 1
        c = rng.beta(5, 2)
        nu = rng.beta(2, 5)
        s = rng.beta(5, 2)
        d = int(rng.integers(3, D_MAX + 1))
        X[b], Y[b], M[b] = gen_theta(rng, t, c, nu, s, n, d)
    return (torch.from_numpy(X).to(DEV), torch.from_numpy(Y).to(DEV),
            torch.from_numpy(M).to(DEV))


# ---------------------------------------------------------------------------
# Model (same architecture as S01, continuous theta embedding).
# ---------------------------------------------------------------------------
def build_mask(n, dev):
    L = 1 + 2 * n
    m = torch.zeros(L, L, dtype=torch.bool, device=dev)
    m[:, 0] = True
    for i in range(n):
        qi, ki = 1 + 2 * i, 2 + 2 * i
        m[qi, qi] = True
        m[ki, ki] = True
        for j in range(i):
            m[qi, 2 + 2 * j] = True
            m[ki, 2 + 2 * j] = True
    return m


class Block(nn.Module):
    def __init__(self, dm, nh):
        super().__init__()
        self.n1, self.n2 = nn.LayerNorm(dm), nn.LayerNorm(dm)
        self.att = nn.MultiheadAttention(dm, nh, batch_first=True)
        self.mlp = nn.Sequential(nn.Linear(dm, 4 * dm), nn.GELU(),
                                 nn.Linear(4 * dm, dm))

    def forward(self, h, am):
        z = self.n1(h)
        a, _ = self.att(z, z, z, attn_mask=~am, need_weights=False)
        h = h + a
        return h + self.mlp(self.n2(h))


class ThetaPFN(nn.Module):
    def __init__(self, dm=192, nl=8, nh=6):
        super().__init__()
        self.emb_x = nn.Linear(D_MAX * 2, dm)
        self.emb_y = nn.Embedding(2, dm)
        self.emb_t = nn.Sequential(nn.Linear(TDIM, dm), nn.GELU(),
                                   nn.Linear(dm, dm))
        self.role = nn.Embedding(2, dm)
        self.blocks = nn.ModuleList([Block(dm, nh) for _ in range(nl)])
        self.nf = nn.LayerNorm(dm)
        self.head = nn.Linear(dm, 2)

    def forward(self, X, Y, M, T, am):
        B, n, _ = X.shape
        xin = torch.cat([X, M[:, None, :].expand(B, n, D_MAX)], -1)
        ex = self.emb_x(xin)
        q = ex + self.role.weight[0]
        kv = ex + self.emb_y(Y) + self.role.weight[1]
        seq = torch.stack([q, kv], 2).reshape(B, 2 * n, -1)
        h = torch.cat([self.emb_t(T)[:, None, :], seq], 1)
        for b in self.blocks:
            h = b(h, am)
        return self.head(self.nf(h[:, 1::2]))


def train(steps, bs=32, lr=3e-4, seed=0):
    rng = np.random.default_rng(seed)
    torch.manual_seed(seed)
    model = ThetaPFN().to(DEV)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    sch = torch.optim.lr_scheduler.OneCycleLR(opt, lr, total_steps=steps,
                                              pct_start=0.05)
    am = build_mask(N_ROWS, DEV)
    scaler = torch.amp.GradScaler("cuda")
    t0 = time.time()
    for s in range(steps):
        X, Y, M, T = sample_batch(rng, bs)
        X, Y, M, T = X.to(DEV), Y.to(DEV), M.to(DEV), T.to(DEV)
        with torch.amp.autocast("cuda", dtype=torch.bfloat16):
            loss = F.cross_entropy(model(X, Y, M, T, am).reshape(-1, 2),
                                   Y.reshape(-1))
        opt.zero_grad(set_to_none=True)
        scaler.scale(loss).backward()
        scaler.unscale_(opt)
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        scaler.step(opt); scaler.update(); sch.step()
        if s % 500 == 0 or s == steps - 1:
            print(f"step {s:6d} loss {loss.item():.4f} {time.time()-t0:7.1f}s",
                  flush=True)
    return model, am


# ---------------------------------------------------------------------------
# Grids.
# ---------------------------------------------------------------------------
def grid(K):
    g = []
    if K == 4:
        for t in range(4):
            g.append(theta_vec(t, .5, .5, .5))
    elif K == 16:
        for t in range(4):
            for c in (.25, .75):
                for nu in (.25, .75):
                    g.append(theta_vec(t, c, nu, .5))
    elif K == 64:
        for t in range(4):
            for c in (.125, .375, .625, .875):
                for nu in (.25, .75):
                    for s in (.25, .75):
                        g.append(theta_vec(t, c, nu, s))
    else:
        raise ValueError(K)
    assert len(g) == K, len(g)
    return np.stack(g)


@torch.no_grad()
def rowlogp(model, am, X, Y, M, G, chunk=100):
    K = G.shape[0]
    B, n, _ = X.shape
    out = torch.zeros(B, K, n, device=DEV)
    Gt = torch.from_numpy(G).to(DEV)
    for k in range(K):
        for i in range(0, B, chunk):
            j = min(i + chunk, B)
            T = Gt[k][None].expand(j - i, TDIM)
            with torch.amp.autocast("cuda", dtype=torch.bfloat16):
                lg = model(X[i:j], Y[i:j], M[i:j], T, am)
            lp = F.log_softmax(lg.float(), -1)
            out[i:j, k] = lp.gather(2, Y[i:j][..., None])[..., 0]
    return out


def npmle(logL, iters=3000, tol=1e-11):
    K = logL.shape[1]
    logpi = np.full(K, -np.log(K))
    prev = -np.inf
    for _ in range(iters):
        z = logpi[None] + logL
        z = z - z.max(1, keepdims=True)
        r = np.exp(z); r /= r.sum(1, keepdims=True)
        pi = np.clip(r.mean(0), 1e-300, None)
        logpi = np.log(pi / pi.sum())
        zz = logpi[None] + logL
        obj = (zz.max(1) + np.log(np.exp(zz - zz.max(1, keepdims=True)).sum(1))).mean()
        if abs(obj - prev) < tol:
            break
        prev = obj
    return np.exp(logpi)


def mix_loss(rlp, logpi):
    ls = rlp[:, :, :N_SCORE].sum(2).cpu().numpy()
    lo = rlp[:, :, N_SCORE:].sum(2).cpu().numpy()
    a = logpi[None] + ls
    a -= a.max(1, keepdims=True)
    w = np.exp(a); w /= w.sum(1, keepdims=True)
    b = np.log(w + 1e-300) + lo
    tot = b.max(1) + np.log(np.exp(b - b.max(1, keepdims=True)).sum(1))
    return -tot / (N_ROWS - N_SCORE)


def main():
    steps = int(os.environ.get("STEPS", 40000))
    ck = os.path.join(OUT, "s03_model.pt")
    model = ThetaPFN().to(DEV)
    if os.path.exists(ck) and os.environ.get("REUSE", "1") == "1":
        model.load_state_dict(torch.load(ck)); am = build_mask(N_ROWS, DEV)
        print("loaded checkpoint", flush=True)
    else:
        model, am = train(steps)
        torch.save(model.state_dict(), ck)
    model.eval()

    rng = np.random.default_rng(1234)
    Xf, Yf, Mf = sample_corpus(rng, 600)          # fit corpus
    Xe, Ye, Me = sample_corpus(np.random.default_rng(5678), 600)  # held out

    res = {"steps": steps, "N_SCORE": N_SCORE, "n_fit": 600, "n_eval": 600,
           "corpus": "peaked: 70% tree / 30% mlp, c~Beta(5,2), nu~Beta(2,5), s~Beta(5,2)"}
    tab = {}
    for K in (4, 16, 64):
        G = grid(K)
        logL_fit = rowlogp(model, am, Xf, Yf, Mf, G).sum(2).cpu().numpy()
        pi = npmle(logL_fit)
        rlp = rowlogp(model, am, Xe, Ye, Me, G)
        Lu = mix_loss(rlp, np.full(K, -np.log(K)))
        Ln = mix_loss(rlp, np.log(pi + 1e-300))
        ev = -rlp[:, :, N_SCORE:].mean(2).cpu().numpy()
        H = float(-(pi * np.log(pi + 1e-300)).sum())
        tab[K] = {
            "uniform_mix": float(Lu.mean()),
            "npmle_mix": float(Ln.mean()),
            "gap_uniform_minus_npmle": float((Lu - Ln).mean()),
            "logK_minus_H_over_nscore": float((math.log(K) - H) / N_SCORE),
            "best_fixed_atom": float(ev.mean(0).min()),
            "per_dataset_oracle": float(ev.min(1).mean()),
            "npmle_vs_bestfixed": float((Ln - ev[:, int(ev.mean(0).argmin())]).mean()),
            "npmle_beats_bestfixed_frac": float((Ln < ev[:, int(ev.mean(0).argmin())]).mean()),
            "npmle_beats_uniform_frac": float((Ln < Lu).mean()),
            "pi_entropy_nats": H,
            "pi_max": float(pi.max()),
            "pi_eff_support_expH": float(math.exp(H)),
            "pi_top5": np.round(np.sort(pi)[::-1][:5], 4).tolist(),
        }
        print(f"K={K:3d} done", flush=True)
    res["by_K"] = tab
    print(json.dumps(res, indent=2), flush=True)
    with open(os.path.join(OUT, "s03_results.json"), "w") as f:
        json.dump(res, f, indent=2)

    print("\n--- VERDICT ---")
    print(f"{'K':>4} {'unif':>8} {'npmle':>8} {'gap':>8} {'logK-H/n':>9} "
          f"{'eff.supp':>9} {'win%':>6} {'vs bestfix':>11}")
    for K in (4, 16, 64):
        t = tab[K]
        print(f"{K:>4} {t['uniform_mix']:8.4f} {t['npmle_mix']:8.4f} "
              f"{t['gap_uniform_minus_npmle']:8.4f} "
              f"{t['logK_minus_H_over_nscore']:9.4f} "
              f"{t['pi_eff_support_expH']:9.2f} "
              f"{t['npmle_beats_bestfixed_frac']*100:5.1f}% "
              f"{t['npmle_vs_bestfixed']:+11.4f}")


if __name__ == "__main__":
    main()
