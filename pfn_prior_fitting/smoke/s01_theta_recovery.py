"""
Smoke test S01 -- threats T-A, T-B, and Warning 2.3 (order incoherence).

Question this script answers, and nothing more:

  Train ONE theta-conditional PFN on a synthetic prior family {P_k}_{k<K}.
  On held-out datasets D ~ P_{k*} with KNOWN k*:

  (T-A)  Does  argmax_k  l_k(D) := sum_i log q(y_i | x_i, D_{<i}, k)  recover k*?
  (2.3)  Is the spread of l_k(D) over row orderings sigma comparable to, or
         larger than, the spread over k?  If sigma-spread >> k-spread the
         whole construction is dead (math/01_setup.md Sec.8 item 2).
  (T-B)  Is the theta-conditioning used at all, i.e. is l_k(D) non-constant
         in k?

Deliberate design choice: the covariate law p(x) is IDENTICAL across all k
(x ~ N(0, I_d), d drawn from a k-independent distribution). Hence the
partial-likelihood caveat of Theorem 2 / Warning 2.2 is inert here and any
failure observed is attributable to the network, not to the covariate term.

Nothing here is a contribution. It is a kill test.
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
torch.backends.cudnn.allow_tf32 = True

DEV = "cuda" if torch.cuda.is_available() else "cpu"
OUT = os.path.dirname(os.path.abspath(__file__))

# ----------------------------------------------------------------------------
# 1. Prior family.  K components, binary classification, shared covariate law.
# ----------------------------------------------------------------------------
D_MAX = 8
N_ROWS = 64
K = 4
COMP = ["linear", "mlp", "tree", "rbf"]


def _sample_x(rng, n, d):
    return rng.standard_normal((n, d)).astype(np.float32)


def _bern(rng, logit, scale):
    p = 1.0 / (1.0 + np.exp(-scale * logit))
    return (rng.random(p.shape) < p).astype(np.int64)


def gen_linear(rng, n, d):
    x = _sample_x(rng, n, d)
    w = rng.standard_normal(d)
    lg = x @ w
    lg = lg / (lg.std() + 1e-6)
    return x, _bern(rng, lg, rng.uniform(1.0, 4.0))


def gen_mlp(rng, n, d):
    x = _sample_x(rng, n, d)
    h = rng.uniform(4, 16)
    h = int(h)
    W1 = rng.standard_normal((d, h)) / math.sqrt(d)
    b1 = rng.standard_normal(h) * 0.5
    W2 = rng.standard_normal(h) / math.sqrt(h)
    lg = np.tanh(x @ W1 + b1) @ W2
    lg = lg / (lg.std() + 1e-6)
    return x, _bern(rng, lg, rng.uniform(1.0, 4.0))


def gen_tree(rng, n, d):
    x = _sample_x(rng, n, d)
    depth = int(rng.integers(2, 5))
    idx = np.zeros(n, dtype=np.int64)
    for _ in range(depth):
        f = int(rng.integers(0, d))
        t = rng.standard_normal() * 0.7
        idx = idx * 2 + (x[:, f] > t).astype(np.int64)
    leaf_lg = rng.standard_normal(2 ** depth) * 2.0
    lg = leaf_lg[idx]
    return x, _bern(rng, lg, rng.uniform(1.0, 3.0))


def gen_rbf(rng, n, d):
    x = _sample_x(rng, n, d)
    c = int(rng.integers(2, 6))
    C = rng.standard_normal((c, d))
    s = rng.uniform(0.5, 1.5, size=c)
    a = rng.standard_normal(c) * 2.0
    dist2 = ((x[:, None, :] - C[None, :, :]) ** 2).sum(-1)
    lg = (np.exp(-dist2 / (2 * s[None, :] ** 2)) * a[None, :]).sum(-1)
    lg = lg / (lg.std() + 1e-6)
    return x, _bern(rng, lg, rng.uniform(1.0, 4.0))


GENS = [gen_linear, gen_mlp, gen_tree, gen_rbf]


def sample_dataset(rng, k, n=N_ROWS):
    d = int(rng.integers(3, D_MAX + 1))
    x, y = GENS[k](rng, n, d)
    xp = np.zeros((n, D_MAX), dtype=np.float32)
    xp[:, :d] = (x - x.mean(0)) / (x.std(0) + 1e-6)
    mask = np.zeros(D_MAX, dtype=np.float32)
    mask[:d] = 1.0
    return xp, y, mask


def sample_batch(rng, bs, n=N_ROWS, k=None):
    X = np.zeros((bs, n, D_MAX), dtype=np.float32)
    Y = np.zeros((bs, n), dtype=np.int64)
    M = np.zeros((bs, D_MAX), dtype=np.float32)
    Kk = np.zeros(bs, dtype=np.int64)
    for b in range(bs):
        kk = int(rng.integers(0, K)) if k is None else k
        X[b], Y[b], M[b] = sample_dataset(rng, kk, n)
        Kk[b] = kk
    return (torch.from_numpy(X), torch.from_numpy(Y),
            torch.from_numpy(M), torch.from_numpy(Kk))


# ----------------------------------------------------------------------------
# 2. Model.  Dual-token causal PFN: prediction at row i depends on
#    (x_i, D_{<i}, theta) exactly.  All n prequential terms in ONE forward pass
#    (math/01_setup.md Sec.7).
# ----------------------------------------------------------------------------
def build_mask(n, dev):
    """Sequence layout: [theta] + [q_0, kv_0, q_1, kv_1, ...].
    q_i  = query token for row i   (carries x_i only)
    kv_i = context token for row i (carries x_i and y_i)
    Allowed: q_i -> theta, kv_j (j<i), itself.
             kv_i -> theta, kv_j (j<=i).  (kv never sees q: q is read-only.)
    """
    L = 1 + 2 * n
    m = torch.zeros(L, L, dtype=torch.bool, device=dev)  # True = allowed
    m[:, 0] = True
    for i in range(n):
        qi, ki = 1 + 2 * i, 2 + 2 * i
        m[qi, qi] = True
        m[ki, ki] = True
        for j in range(i):
            m[qi, 2 + 2 * j] = True
            m[ki, 2 + 2 * j] = True
    m[0, 0] = True
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
    def __init__(self, dm=128, nl=6, nh=4, ncls=2, k=K):
        super().__init__()
        self.emb_x = nn.Linear(D_MAX * 2, dm)          # x and feature mask
        self.emb_y = nn.Embedding(ncls, dm)
        self.emb_t = nn.Embedding(k, dm)
        self.role = nn.Embedding(2, dm)                # 0=query, 1=context
        self.blocks = nn.ModuleList([Block(dm, nh) for _ in range(nl)])
        self.nf = nn.LayerNorm(dm)
        self.head = nn.Linear(dm, ncls)

    def forward(self, X, Y, M, Kk, am):
        B, n, _ = X.shape
        xin = torch.cat([X, M[:, None, :].expand(B, n, D_MAX)], -1)
        ex = self.emb_x(xin)
        q = ex + self.role.weight[0]
        kv = ex + self.emb_y(Y) + self.role.weight[1]
        seq = torch.stack([q, kv], 2).reshape(B, 2 * n, -1)
        h = torch.cat([self.emb_t(Kk)[:, None, :], seq], 1)
        for b in self.blocks:
            h = b(h, am)
        hq = self.nf(h[:, 1::2])                       # query positions
        return self.head(hq)                           # (B, n, ncls)


# ----------------------------------------------------------------------------
# 3. Train.
# ----------------------------------------------------------------------------
def train(steps=12000, bs=32, lr=3e-4, seed=0, log_every=250):
    rng = np.random.default_rng(seed)
    torch.manual_seed(seed)
    model = ThetaPFN().to(DEV)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, lr, total_steps=steps,
                                                pct_start=0.05)
    am = build_mask(N_ROWS, DEV)
    scaler = torch.amp.GradScaler("cuda")
    t0 = time.time()
    for s in range(steps):
        X, Y, M, Kk = sample_batch(rng, bs)
        X, Y, M, Kk = X.to(DEV), Y.to(DEV), M.to(DEV), Kk.to(DEV)
        with torch.amp.autocast("cuda", dtype=torch.bfloat16):
            lg = model(X, Y, M, Kk, am)
            loss = F.cross_entropy(lg.reshape(-1, 2), Y.reshape(-1))
        opt.zero_grad(set_to_none=True)
        scaler.scale(loss).backward()
        scaler.unscale_(opt)
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        scaler.step(opt)
        scaler.update()
        sched.step()
        if s % log_every == 0 or s == steps - 1:
            print(f"step {s:6d}  loss {loss.item():.4f}  "
                  f"{time.time()-t0:7.1f}s", flush=True)
    return model, am


# ----------------------------------------------------------------------------
# 4. Evaluate: l_k(D) for all k, over several row orderings sigma.
# ----------------------------------------------------------------------------
@torch.no_grad()
def score_all_k(model, am, X, Y, M, n_perm=8, seed=123):
    """Return L of shape (B, K, n_perm): l_k(D) under ordering sigma."""
    g = torch.Generator(device="cpu").manual_seed(seed)
    B, n, _ = X.shape
    out = torch.zeros(B, K, n_perm)
    for p in range(n_perm):
        perm = torch.arange(n) if p == 0 else torch.randperm(n, generator=g)
        Xp, Yp = X[:, perm], Y[:, perm]
        for k in range(K):
            Kk = torch.full((B,), k, dtype=torch.long, device=DEV)
            with torch.amp.autocast("cuda", dtype=torch.bfloat16):
                lg = model(Xp, Yp, M, Kk, am)
            lp = F.log_softmax(lg.float(), -1)
            out[:, k, p] = lp.gather(2, Yp[..., None])[..., 0].sum(1).cpu()
    return out


def main():
    steps = int(os.environ.get("STEPS", 12000))
    model, am = train(steps=steps)
    model.eval()

    rng = np.random.default_rng(9999)
    NPD = 64          # held-out datasets per component
    NPERM = 8
    res = {"K": K, "components": COMP, "n_rows": N_ROWS,
           "n_datasets_per_comp": NPD, "n_perm": NPERM, "steps": steps}

    conf = np.zeros((K, K), dtype=int)
    sig_spread, k_spread, gaps = [], [], []
    for kstar in range(K):
        X, Y, M, _ = sample_batch(rng, NPD, k=kstar)
        X, Y, M = X.to(DEV), Y.to(DEV), M.to(DEV)
        L = score_all_k(model, am, X, Y, M, n_perm=NPERM).numpy()  # (B,K,P)
        Lbar = L.mean(2)                                           # (B,K)
        pred = Lbar.argmax(1)
        for p in pred:
            conf[kstar, p] += 1
        # Warning 2.3 diagnostics, in nats per row.
        sig_spread.append((L.std(2) / N_ROWS).mean())
        k_spread.append((Lbar.std(1) / N_ROWS).mean())
        srt = np.sort(Lbar, 1)
        gaps.append(((srt[:, -1] - srt[:, -2]) / N_ROWS).mean())
        # per-permutation argmax stability
        pk = L.argmax(1)                                           # (B,P)
        stab = (pk == pk[:, :1]).mean()
        res[f"perm_argmax_agree_k{kstar}"] = float(stab)

    res["confusion"] = conf.tolist()
    res["accuracy"] = float(np.trace(conf) / conf.sum())
    res["sigma_spread_nats_per_row"] = float(np.mean(sig_spread))
    res["k_spread_nats_per_row"] = float(np.mean(k_spread))
    res["top2_gap_nats_per_row"] = float(np.mean(gaps))
    res["ratio_sigma_over_k"] = float(np.mean(sig_spread) / (np.mean(k_spread) + 1e-12))

    print(json.dumps(res, indent=2), flush=True)
    with open(os.path.join(OUT, "s01_results.json"), "w") as f:
        json.dump(res, f, indent=2)
    torch.save(model.state_dict(), os.path.join(OUT, "s01_model.pt"))

    print("\n--- VERDICT ---")
    print(f"T-A  theta recovery accuracy : {res['accuracy']:.3f}  "
          f"(chance {1/K:.3f})")
    print(f"2.3  sigma-spread / k-spread : {res['ratio_sigma_over_k']:.3f}  "
          f"(want << 1)")
    print(f"T-B  k-spread (nats/row)     : {res['k_spread_nats_per_row']:.5f}  "
          f"(want >> 0)")


if __name__ == "__main__":
    main()
