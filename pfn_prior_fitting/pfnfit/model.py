"""
Step 19 -- theta-conditional PFN at real scale.

Architecture: TabPFN-v2-style 2D attention over a (rows x features) grid of cell
tokens, alternating
    ROW attention   : across rows, within a feature column   (causal, see below)
    FEATURE attention: across features, within a row         (unmasked)
so the model is *equivariant to feature permutation* and *exchangeable-by-
construction across rows except for the causal order*.  No positional embedding
is used on either axis.

Exact single-pass prequential evaluation (math/01_setup.md Sec.7).  Two streams:

    C[i,j] = emb(x_ij) + emb(y_i)      context stream, carries the label
    Q[i,j] = emb(x_ij)                 query stream,   never carries y_i

    ROW:  Q  <- cross-attend to  [BOS, C[0..i-1]]      (strictly causal)
          C  <- self-attend  to  [BOS, C[0..i]]        (causal, inclusive)
    FEAT: Q  <- self-attend within row i over j        (Q only)
          C  <- self-attend within row i over j        (C only)

The head reads Q[i,:] pooled over j.  Therefore the prediction at row i is a
function of (x_i, D_{<i}, theta) and nothing else, and ALL n prequential terms
come out of ONE forward pass.  A BOS context row is prepended so that row 0 has
a non-empty key set (otherwise softmax over an all-masked row is NaN).
"""

import math

import torch
import torch.nn as nn
import torch.nn.functional as F

from .prior import D_THETA


class RowFeatBlock(nn.Module):
    def __init__(self, dm, nh):
        super().__init__()
        self.nh = nh
        self.dh = dm // nh
        self.n1 = nn.LayerNorm(dm); self.n2 = nn.LayerNorm(dm)
        self.n3 = nn.LayerNorm(dm)
        self.qr = nn.Linear(dm, dm); self.kr = nn.Linear(dm, dm)
        self.vr = nn.Linear(dm, dm); self.or_ = nn.Linear(dm, dm)
        self.qf = nn.Linear(dm, dm); self.kf = nn.Linear(dm, dm)
        self.vf = nn.Linear(dm, dm); self.of = nn.Linear(dm, dm)
        self.mlp = nn.Sequential(nn.Linear(dm, 3 * dm), nn.GELU(),
                                 nn.Linear(3 * dm, dm))

    def _split(self, x, B, S, L):
        return x.view(B * S, L, self.nh, self.dh).transpose(1, 2)

    def _merge(self, x, B, S, L, dm):
        return x.transpose(1, 2).reshape(B * S, L, dm).view(B, S, L, dm)

    def row_attn(self, Qs, Ks, Vs, mask, B, d, n, nk, dm):
        # (B, n, d, dm) -> per-column sequences of length n
        q = Qs.permute(0, 2, 1, 3).reshape(B * d, n, dm)
        k = Ks.permute(0, 2, 1, 3).reshape(B * d, nk, dm)
        v = Vs.permute(0, 2, 1, 3).reshape(B * d, nk, dm)
        q = q.view(B * d, n, self.nh, self.dh).transpose(1, 2)
        k = k.view(B * d, nk, self.nh, self.dh).transpose(1, 2)
        v = v.view(B * d, nk, self.nh, self.dh).transpose(1, 2)
        o = F.scaled_dot_product_attention(q, k, v, attn_mask=mask)
        o = o.transpose(1, 2).reshape(B * d, n, dm).view(B, d, n, dm)
        return o.permute(0, 2, 1, 3)

    def feat_attn(self, X, fmask, B, n, d, dm):
        z = X.reshape(B * n, d, dm)
        q = self.qf(z).view(B * n, d, self.nh, self.dh).transpose(1, 2)
        k = self.kf(z).view(B * n, d, self.nh, self.dh).transpose(1, 2)
        v = self.vf(z).view(B * n, d, self.nh, self.dh).transpose(1, 2)
        m = fmask[:, None, :].expand(B, n, d).reshape(B * n, 1, 1, d)
        m = torch.where(m > 0, 0.0, float("-inf"))
        o = F.scaled_dot_product_attention(q, k, v, attn_mask=m)
        o = o.transpose(1, 2).reshape(B * n, d, dm).view(B, n, d, dm)
        return self.of(o)

    def forward(self, Q, C, bos, fmask, mq, mc):
        B, n, d, dm = Q.shape
        zq, zc = self.n1(Q), self.n1(C)
        Cx = torch.cat([bos.expand(B, 1, d, dm), zc], 1)          # (B,n+1,d,dm)
        kk, vv = self.kr(Cx), self.vr(Cx)
        Q = Q + self.or_(self.row_attn(self.qr(zq), kk, vv, mq, B, d, n, n + 1, dm))
        C = C + self.or_(self.row_attn(self.qr(zc), kk, vv, mc, B, d, n, n + 1, dm))
        Q = Q + self.feat_attn(self.n2(Q), fmask, B, n, d, dm)
        C = C + self.feat_attn(self.n2(C), fmask, B, n, d, dm)
        Q = Q + self.mlp(self.n3(Q))
        C = C + self.mlp(self.n3(C))
        return Q, C


class PFN2D(nn.Module):
    def __init__(self, dm=160, nl=8, nh=8, n_cls=10, d_max=32,
                 theta_cond=True):
        super().__init__()
        self.dm, self.n_cls, self.d_max = dm, n_cls, d_max
        self.theta_cond = theta_cond
        self.cell = nn.Linear(3, dm)              # value, is-categorical, is-pad
        self.ycls = nn.Embedding(n_cls + 1, dm)   # +1 unused slot
        self.bos = nn.Parameter(torch.randn(1, 1, 1, dm) * 0.02)
        self.theta = nn.Sequential(nn.Linear(D_THETA, dm), nn.GELU(),
                                   nn.Linear(dm, dm))
        self.blocks = nn.ModuleList([RowFeatBlock(dm, nh) for _ in range(nl)])
        self.nf = nn.LayerNorm(dm)
        self.head = nn.Sequential(nn.Linear(dm, dm), nn.GELU(),
                                  nn.Linear(dm, n_cls))

    @staticmethod
    def masks(n, device, dtype):
        """mq: strictly causal (query row i sees keys 0..i, key 0 = BOS,
        key t>0 = context row t-1, so effectively rows < i).
        mc: inclusive (context row i sees rows <= i)."""
        ar = torch.arange(n, device=device)
        ak = torch.arange(n + 1, device=device)
        mq = (ak[None, :] <= ar[:, None])
        mc = (ak[None, :] <= ar[:, None] + 1)
        f = lambda m: torch.where(m, torch.zeros((), device=device, dtype=dtype),
                                  torch.full((), float("-inf"), device=device,
                                             dtype=dtype))
        return f(mq)[None, None], f(mc)[None, None]

    def forward(self, X, fmask, y, theta, catmask=None, mq=None, mc=None):
        """X (B,n,d) z-scored, fmask (B,d), y (B,n) long, theta (B,D_THETA)."""
        B, n, d = X.shape
        dev = X.device
        if mq is None:
            mq, mc = self.masks(n, dev, torch.float32)
        cm = catmask if catmask is not None else torch.zeros(B, d, device=dev)
        feat = torch.stack([X,
                            cm[:, None, :].expand(B, n, d),
                            fmask[:, None, :].expand(B, n, d)], -1)
        E = self.cell(feat)                                    # (B,n,d,dm)
        Q = E
        C = E + self.ycls(y.clamp(0, self.n_cls))[:, :, None, :]
        if self.theta_cond:
            t = self.theta(theta)[:, None, None, :]
            Q = Q + t
            C = C + t
        bos = self.bos
        for blk in self.blocks:
            Q, C = blk(Q, C, bos, fmask, mq, mc)
        h = (self.nf(Q) * fmask[:, None, :, None]).sum(2) \
            / fmask.sum(1).clamp_min(1)[:, None, None]
        return self.head(h)                                    # (B,n,n_cls)


def masked_logprobs(logits, y, ncls):
    """log-softmax restricted to the first ncls classes, gathered at y."""
    B, n, C = logits.shape
    ar = torch.arange(C, device=logits.device)
    m = (ar[None, None, :] < ncls[:, None, None])
    lg = logits.masked_fill(~m, float("-inf"))
    lp = F.log_softmax(lg.float(), -1)
    return lp.gather(2, y[..., None].clamp(0, C - 1))[..., 0], lp


if __name__ == "__main__":
    dev = "cuda"
    from .prior import sample_theta, sample_datasets
    torch.manual_seed(0)
    m = PFN2D().to(dev)
    print("params", sum(p.numel() for p in m.parameters()) / 1e6, "M")
    th = sample_theta(4, dev)
    X, fm, y, nc = sample_datasets(th, 128, 32, dev)
    with torch.amp.autocast("cuda", dtype=torch.bfloat16):
        lg = m(X, fm, y, th)
    print("logits", lg.shape, torch.isfinite(lg).all().item())

    # ---- leakage test: prediction at row i must not depend on y_i ----------
    m.eval()
    with torch.no_grad():
        base = m(X, fm, y, th).float()
        y2 = y.clone()
        y2[:, 5] = (y2[:, 5] + 1) % nc.clamp_min(2)[:, None].squeeze(1)
        alt = m(X, fm, y2, th).float()
    d5 = (base[:, 5] - alt[:, 5]).abs().max().item()
    d6 = (base[:, 6] - alt[:, 6]).abs().max().item()
    d4 = (base[:, 4] - alt[:, 4]).abs().max().item()
    print(f"LEAKAGE TEST  |dlogit| at row 5 (own label changed) = {d5:.3e} "
          f"(must be 0)")
    print(f"              |dlogit| at row 4 (earlier row)       = {d4:.3e} "
          f"(must be 0)")
    print(f"              |dlogit| at row 6 (later row)         = {d6:.3e} "
          f"(must be > 0)")
    assert d5 == 0.0 and d4 == 0.0 and d6 > 0
    print("PASS: causal structure is exact.")
