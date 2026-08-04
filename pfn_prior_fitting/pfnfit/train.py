"""
Step 19 -- pretraining loop.

One entry point serves every arm of E1 (notes/20_plan.md Sec.6): the arm is
determined entirely by the theta-sampler passed in.

  --arm cond      theta ~ U[0,1]^12, model conditions on theta   (the scorer)
  --arm broad     theta ~ U[0,1]^12, model ignores theta          (E1 arm A)
  --arm pistar    theta ~ pi* (+kernel), model ignores theta      (E1 arm B)
  --arm rand      theta ~ Dirichlet-random pi at matched entropy  (E1 control)
  --arm single    theta = argmax_k pi*_k                          (E1 control)

Context length is sampled per batch so the model sees a range of dataset sizes,
which is what makes a single checkpoint usable on real datasets of varying n.
"""

import argparse
import json
import math
import os
import time

import numpy as np
import torch
import torch.nn.functional as F

from .model import PFN2D, masked_logprobs
from .prior import D_THETA, sample_datasets, sample_theta

ROOT = os.path.dirname(os.path.abspath(__file__))
CKPT = os.path.abspath(os.path.join(ROOT, "..", "ckpt"))
os.makedirs(CKPT, exist_ok=True)
DEV = "cuda"


def make_sampler(arm, atoms=None, pi=None, h=0.1):
    if arm in ("cond", "broad"):
        return lambda B, g: sample_theta(B, DEV, g)
    if arm == "single":
        k = int(np.argmax(pi))
        a = torch.tensor(atoms[k], device=DEV, dtype=torch.float32)
        return lambda B, g: a[None].expand(B, D_THETA).clone()
    A = torch.tensor(atoms, device=DEV, dtype=torch.float32)
    P = torch.tensor(pi, device=DEV, dtype=torch.float32)

    def f(B, g):
        idx = torch.multinomial(P, B, replacement=True, generator=g)
        th = A[idx]
        th = th + (torch.rand(B, D_THETA, device=DEV, generator=g) * 2 - 1) * h
        return th.clamp(0, 1)
    return f


def train(arm, steps, seed, dm, nl, nh, bs, d_max, n_lo, n_hi, out,
          atoms=None, pi=None, h=0.1, log_every=500, ncls_max=10):
    torch.manual_seed(seed)
    g = torch.Generator(device=DEV); g.manual_seed(seed)
    samp = make_sampler(arm, atoms, pi, h)
    model = PFN2D(dm=dm, nl=nl, nh=nh, n_cls=ncls_max, d_max=d_max,
                  theta_cond=(arm == "cond")).to(DEV)
    nprm = sum(p.numel() for p in model.parameters()) / 1e6
    opt = torch.optim.AdamW(model.parameters(), lr=3e-4, weight_decay=0.01,
                            betas=(0.9, 0.98))
    sch = torch.optim.lr_scheduler.OneCycleLR(opt, 3e-4, total_steps=steps,
                                              pct_start=0.03)
    scaler = torch.amp.GradScaler("cuda")
    t0 = time.time(); hist = []
    for st in range(steps):
        n = int(np.random.default_rng(seed * 100003 + st).integers(n_lo, n_hi + 1))
        th = samp(bs, g)
        X, fm, y, nc = sample_datasets(th, n, d_max, DEV, ncls_max, g)
        mq, mc = PFN2D.masks(n, DEV, torch.float32)
        with torch.amp.autocast("cuda", dtype=torch.bfloat16):
            lg = model(X, fm, y, th, mq=mq, mc=mc)
            ar = torch.arange(ncls_max, device=DEV)
            lg = lg.masked_fill(~(ar[None, None, :] < nc[:, None, None]),
                                float("-inf"))
            loss = F.cross_entropy(lg.reshape(-1, ncls_max).float(),
                                   y.reshape(-1))
        opt.zero_grad(set_to_none=True)
        scaler.scale(loss).backward()
        scaler.unscale_(opt)
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        scaler.step(opt); scaler.update(); sch.step()
        if st % log_every == 0 or st == steps - 1:
            hist.append([st, float(loss.item())])
            el = time.time() - t0
            eta = el / max(st + 1, 1) * (steps - st - 1) / 60
            print(f"[{arm}/s{seed}] {st:7d} loss {loss.item():.4f} "
                  f"n={n} {el:7.1f}s eta {eta:6.1f}m", flush=True)
    p = os.path.join(CKPT, out)
    torch.save({"sd": model.state_dict(),
                "cfg": {"dm": dm, "nl": nl, "nh": nh, "d_max": d_max,
                        "ncls_max": ncls_max, "theta_cond": arm == "cond"},
                "arm": arm, "seed": seed, "steps": steps, "params_M": nprm,
                "hist": hist}, p)
    print(f"saved {p}  ({nprm:.2f}M params, {(time.time()-t0)/60:.1f} min)",
          flush=True)
    return p


def load(path, device=DEV):
    z = torch.load(path, map_location=device, weights_only=False)
    c = z["cfg"]
    m = PFN2D(dm=c["dm"], nl=c["nl"], nh=c["nh"], n_cls=c["ncls_max"],
              d_max=c["d_max"], theta_cond=c["theta_cond"]).to(device)
    m.load_state_dict(z["sd"]); m.eval()
    return m, z


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True)
    ap.add_argument("--steps", type=int, default=40000)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--dm", type=int, default=256)
    ap.add_argument("--nl", type=int, default=12)
    ap.add_argument("--nh", type=int, default=8)
    ap.add_argument("--bs", type=int, default=4)
    ap.add_argument("--d_max", type=int, default=32)
    ap.add_argument("--n_lo", type=int, default=256)
    ap.add_argument("--n_hi", type=int, default=512)
    ap.add_argument("--pi", default=None, help="json with atoms + pi")
    ap.add_argument("--h", type=float, default=0.1)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    atoms = pi = None
    if a.pi:
        z = json.load(open(a.pi))
        atoms, pi = np.array(z["atoms"], dtype=np.float32), np.array(z["pi"])
    out = a.out or f"{a.arm}_s{a.seed}.pt"
    train(a.arm, a.steps, a.seed, a.dm, a.nl, a.nh, a.bs, a.d_max,
          a.n_lo, a.n_hi, out, atoms, pi, a.h)
