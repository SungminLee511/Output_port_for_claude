"""
Step 18 -- theta-parameterized SCM prior (notes/20_plan.md Sec.3).

A TabPFN-v2-style structural-causal-model / random-network prior whose
hyperparameters are EXPOSED as a vector theta in [0,1]^12 instead of being
hard-coded.  Everything is generated on GPU and fully batched: depth and width
are realised by MASKING a fixed maximum architecture, so every dataset in a
batch may carry its own theta.  That is what makes theta-conditional training
affordable.

theta layout (d_theta = 12), all in [0,1]:
   0  depth              L = 1 + round(t*(L_MAX-1))
   1  width              W = 4 + round(t*(W_MAX-4))
   2  edge density       rho = 0.15 + 0.85*t
   3  activation mix: relu weight
   4  activation mix: periodic (sin) weight      (remainder -> identity/tanh/step)
   5  weight scale       s = 0.5 + 2.5*t
   6  propagation noise scale   sigma = 0.02 * exp(3.5*t)
   7  noise tail heaviness      t=0 Gaussian ... t=1 Student-t(df=2)
   8  categorical fraction      of features quantized to a small cardinality
   9  missing rate              entries replaced by the column median
  10  monotone warp strength    per-feature random power / rank warp
  11  label noise rate          y resampled uniformly with prob 0.25*t

NOT fitted (fixed by design, stated in the paper): the class-count law and the
feature-count law, because those are properties of the *task*, not of the
inductive bias, and are known at test time.
"""

import math

import torch

D_THETA = 12
L_MAX = 8
W_MAX = 64


def sample_theta(B, device, generator=None):
    return torch.rand(B, D_THETA, device=device, generator=generator)


def _student_t(shape, df, device, g=None):
    n = torch.randn(shape, device=device, generator=g)
    c = torch.distributions.Chi2(df).sample(shape).to(device) if False else None
    # chi2(df) = gamma(df/2, 2); sample via gamma without a torch generator dep
    u = torch._standard_gamma(torch.full(shape, df / 2.0, device=device)) * 2.0
    return n / torch.sqrt(u / df)


def _noise(shape, theta_heavy, device, g=None):
    """Interpolate Gaussian -> Student-t(2) by mixing on a per-dataset basis."""
    z = torch.randn(shape, device=device, generator=g)
    df = 2.0 + 28.0 * (1.0 - theta_heavy)              # (B,1,1) in [2,30]
    u = torch._standard_gamma((df / 2.0).expand(shape).contiguous()) * 2.0
    t = z / torch.sqrt(u / df)
    t = t / t.std(dim=1, keepdim=True).clamp_min(1e-6)
    return t


@torch.no_grad()
def sample_datasets(theta, n, d_max, device, n_cls_max=10, g=None):
    """theta: (B, D_THETA).  Returns X (B,n,d_max) float32 z-scored+padded,
    feat_mask (B,d_max), y (B,n) long, n_cls (B,) long."""
    B = theta.shape[0]
    t = theta
    L = (1 + torch.round(t[:, 0] * (L_MAX - 1))).long()            # (B,)
    W = (4 + torch.round(t[:, 1] * (W_MAX - 4))).long()
    rho = 0.15 + 0.85 * t[:, 2]
    p_relu, p_sin = t[:, 3], t[:, 4]
    wscale = (0.5 + 2.5 * t[:, 5]).view(B, 1, 1)
    nsig = (0.02 * torch.exp(2.3 * t[:, 6])).view(B, 1, 1)

    ar = torch.arange(W_MAX, device=device)
    wmask = (ar[None, :] < W[:, None]).float()                     # (B,W_MAX)

    # ---- root variables ----------------------------------------------------
    h = _noise((B, n, W_MAX), t[:, 7].view(B, 1, 1), device, g) * wmask[:, None]
    pool = [h]
    # ---- propagate ---------------------------------------------------------
    for l in range(L_MAX):
        Wl = torch.randn(B, W_MAX, W_MAX, device=device, generator=g)
        emask = (torch.rand(B, W_MAX, W_MAX, device=device, generator=g)
                 < rho.view(B, 1, 1)).float()
        Wl = Wl * emask * wmask[:, :, None] * wmask[:, None, :]
        Wl = Wl * wscale / (W.view(B, 1, 1).float() * rho.view(B, 1, 1)).sqrt()
        b = torch.randn(B, 1, W_MAX, device=device, generator=g) * 0.5 * wmask[:, None]
        z = torch.bmm(h, Wl) + b
        # per-node activation drawn from the theta-controlled mixture
        u = torch.rand(B, 1, W_MAX, device=device, generator=g)
        w_relu = p_relu.view(B, 1, 1)
        w_sin = (p_sin * (1 - p_relu)).view(B, 1, 1)
        rest = 1.0 - w_relu - w_sin
        a = torch.where(u < w_relu, torch.relu(z),
            torch.where(u < w_relu + w_sin, torch.sin(2.0 * z),
            torch.where(u < w_relu + w_sin + rest / 3, z,
            torch.where(u < w_relu + w_sin + 2 * rest / 3, torch.tanh(z),
                        (z > 0).float() * 2 - 1))))
        a = a + nsig * _noise((B, n, W_MAX), t[:, 7].view(B, 1, 1), device, g)
        a = a * wmask[:, None]
        a = a / a.std(dim=1, keepdim=True).clamp_min(1e-6)
        # layers beyond this dataset's depth are identity pass-through
        act = (l < L).float().view(B, 1, 1)
        h = act * a + (1 - act) * h
        pool.append(h)

    P = torch.stack(pool, 1)                                       # (B,L_MAX+1,n,W_MAX)
    P = P.permute(0, 2, 1, 3).reshape(B, n, (L_MAX + 1) * W_MAX)
    npool = (L_MAX + 1) * W_MAX
    valid = wmask.repeat(1, L_MAX + 1)                             # (B,npool)

    # ---- choose target node -----------------------------------------------
    # The target sits in a layer tl drawn uniformly among the active layers,
    # and features are drawn with weight decaying in |layer - tl|.  Sampling
    # the target from the deepest layer and features uniformly (the first
    # design) put most feature/target pairs many noisy nonlinear hops apart and
    # produced datasets that a GBDT could not beat the majority class on.
    lay_of = torch.arange(L_MAX + 1, device=device).repeat_interleave(W_MAX)
    tl = (1 + (torch.rand(B, device=device, generator=g)
               * L.float()).long()).clamp_max(L_MAX)               # (B,)
    KPAR = 8
    psel = (lay_of[None, :] == (tl[:, None] - 1)).float() * valid + 1e-8 * valid
    par = torch.multinomial(psel, KPAR, replacement=False, generator=g)  # (B,KPAR)
    kdeg = 1 + torch.randint(0, KPAR, (B,), device=device, generator=g)
    kmsk = (torch.arange(KPAR, device=device)[None, :] < kdeg[:, None]).float()
    pw = torch.randn(B, KPAR, device=device, generator=g) * kmsk
    Hpar = P.gather(2, par[:, None, :].expand(B, n, KPAR))          # (B,n,KPAR)
    pre = (Hpar * pw[:, None, :]).sum(-1)
    u = torch.rand(B, 1, device=device, generator=g)
    w_relu = p_relu.view(B, 1); w_sin = (p_sin * (1 - p_relu)).view(B, 1)
    rest = 1.0 - w_relu - w_sin
    yraw = torch.where(u < w_relu, torch.relu(pre),
           torch.where(u < w_relu + w_sin, torch.sin(2.0 * pre),
           torch.where(u < w_relu + w_sin + rest / 3, pre,
           torch.where(u < w_relu + w_sin + 2 * rest / 3, torch.tanh(pre),
                       (pre > 0).float() * 2 - 1))))
    yraw = yraw / yraw.std(1, keepdim=True).clamp_min(1e-6)
    yraw = yraw + nsig.view(B, 1) * _noise((B, n, 1), t[:, 7].view(B, 1, 1),
                                           device, g).squeeze(2)

    # ---- choose features: the target's parents are OBSERVED with prob .85,
    # the rest filled from layers near the target.  Making y an explicit
    # function of a small observed parent set is what makes the datasets
    # learnable; sampling features as graph *siblings* of y (the first two
    # designs) produced data a GBDT could not beat the majority class on.
    prox = torch.exp(-(lay_of[None, :] - tl[:, None]).abs().float() / 1.5)
    fw = valid * prox
    keep = (torch.rand(B, KPAR, device=device, generator=g) < 0.85).float() * kmsk
    fw.scatter_(1, par, 1e4 * keep + 1e-8)
    fw = fw + 1e-8 * valid
    fi = torch.multinomial(fw, d_max, replacement=False, generator=g)  # (B,d_max)
    X = P.gather(2, fi[:, None, :].expand(B, n, d_max))

    d_act = torch.minimum(W, torch.full_like(W, d_max))
    d_act = torch.clamp((d_act.float() * (0.4 + 0.6 * torch.rand(B, device=device,
                                                                 generator=g))).long(),
                        min(KPAR + 2, d_max), d_max)
    ard = torch.arange(d_max, device=device)
    fmask = (ard[None, :] < d_act[:, None]).float()

    # ---- feature post-processing ------------------------------------------
    X = (X - X.mean(1, keepdim=True)) / X.std(1, keepdim=True).clamp_min(1e-6)
    # monotone warp
    ws = t[:, 10].view(B, 1, 1)
    pw = torch.exp((torch.rand(B, 1, d_max, device=device, generator=g) * 2 - 1) * 2.0 * ws)
    X = torch.sign(X) * X.abs().clamp_min(1e-6).pow(pw)
    # categorical quantization
    catf = t[:, 8].view(B, 1, 1)
    iscat = (torch.rand(B, 1, d_max, device=device, generator=g) < catf).float()
    card = 2 + torch.randint(0, 8, (B, 1, d_max), device=device, generator=g).float()
    Xq = torch.round((X - X.min(1, keepdim=True).values) /
                     (X.max(1, keepdim=True).values - X.min(1, keepdim=True).values
                      ).clamp_min(1e-6) * (card - 1))
    X = iscat * Xq + (1 - iscat) * X
    # missing -> column median (matches the real-data preprocessing in data.py)
    mr = (0.3 * t[:, 9]).view(B, 1, 1)
    miss = (torch.rand(B, n, d_max, device=device, generator=g) < mr)
    med = X.median(dim=1, keepdim=True).values
    X = torch.where(miss, med.expand_as(X), X)
    X = (X - X.mean(1, keepdim=True)) / X.std(1, keepdim=True).clamp_min(1e-6)
    X = torch.nan_to_num(X) * fmask[:, None, :]

    # ---- target discretisation --------------------------------------------
    ncls = torch.where(torch.rand(B, device=device, generator=g) < 0.5,
                       torch.full((B,), 2, device=device, dtype=torch.long),
                       torch.randint(3, n_cls_max + 1, (B,), device=device,
                                     dtype=torch.long, generator=g))
    yraw = yraw + 1e-4 * torch.randn_like(yraw)
    r = yraw.argsort(1).argsort(1).float() / max(n - 1, 1)         # rank in [0,1]
    # unequal class widths -> class imbalance
    arc = torch.arange(n_cls_max, device=device)[None, :]
    wcut = (torch.rand(B, n_cls_max, device=device, generator=g) + 0.5) \
        * (arc < ncls[:, None]).float()
    cuts = (wcut / wcut.sum(1, keepdim=True)).cumsum(1)
    kmask = (arc < ncls[:, None] - 1).float()
    big = cuts * kmask + 10.0 * (1 - kmask)
    y = (r[:, :, None] > big[:, None, :]).sum(2).clamp_max(n_cls_max - 1)

    # ---- label noise -------------------------------------------------------
    lnr = (0.25 * t[:, 11]).view(B, 1)
    flip = torch.rand(B, n, device=device, generator=g) < lnr
    rnd = (torch.rand(B, n, device=device, generator=g) * ncls[:, None].float()).long()
    y = torch.where(flip, rnd.clamp_max(n_cls_max - 1), y)
    return X.float(), fmask, y.long(), ncls


if __name__ == "__main__":
    import numpy as np
    dev = "cuda"
    th = sample_theta(8, dev)
    X, fm, y, nc = sample_datasets(th, 512, 32, dev)
    print("X", X.shape, X.dtype, "finite", torch.isfinite(X).all().item())
    print("y", y.shape, "ncls", nc.tolist())
    for b in range(8):
        cnt = torch.bincount(y[b], minlength=10).tolist()
        print(f" b{b} d_act={int(fm[b].sum())} classes={cnt[:int(nc[b])]}")
    # learnability check: a logistic regression must beat majority class
    from sklearn.ensemble import HistGradientBoostingClassifier
    th = sample_theta(12, dev)
    X, fm, y, nc = sample_datasets(th, 600, 20, dev)
    gains = []
    for b in range(12):
        d = int(fm[b].sum())
        xb = X[b, :, :d].cpu().numpy(); yb = y[b].cpu().numpy()
        if len(np.unique(yb)) < 2:
            gains.append(None); continue
        tr, te = slice(0, 400), slice(400, 600)
        maj = np.bincount(yb[te]).max() / 200
        try:
            m = HistGradientBoostingClassifier(max_iter=60).fit(xb[tr], yb[tr])
            acc = (m.predict(xb[te]) == yb[te]).mean()
        except Exception:
            acc = float("nan")
        gains.append(round(float(acc - maj), 3))
    print("GBDT acc - majority:", gains)
