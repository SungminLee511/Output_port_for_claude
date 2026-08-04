"""
Smoke test S04 -- the decisive M2 test (math/01_setup.md Sec.6, mode M2).

Three *unconditional* PFNs, identical architecture / steps / optimizer / seeds,
differing ONLY in the distribution over theta used to generate pretraining data:

  A  pi_0    broad:  t ~ U{0..3},  c,nu,s ~ U[0,1]         "TabPFN as shipped"
  B  pi*     NPMLE fit on the fit-corpus (K=64 grid, S03), smoothed by a
             uniform kernel of half-width = half the grid spacing            "ours"
  C  true    the actual corpus theta-law                    oracle upper bound

Evaluated on (1) held-out corpus datasets and (2) held-out BROAD datasets.
(2) is the generality check a reviewer will demand: does fitting the prior to a
corpus destroy performance off-corpus?

Pre-registered decision rule (ideas/13_smoke_S03.md Sec.14.4):
  B ~= A                 -> M2 fails, empirical-Bayes contribution is dead
  A > B ~= C             -> M2 works, this is the paper

2 seeds per arm.  Per-dataset paired differences and win rates are reported,
not just means (threat T-E has already fired twice).
"""

import json
import math
import os
import time

import numpy as np
import torch
import torch.nn.functional as F

import s03_scale_K as S3

DEV = S3.DEV
OUT = os.path.dirname(os.path.abspath(__file__))
D_MAX, N_ROWS, N_SCORE, TDIM = S3.D_MAX, S3.N_ROWS, S3.N_SCORE, S3.TDIM
ZERO_T = torch.zeros(TDIM)


# ---------------------------------------------------------------------------
# theta samplers
# ---------------------------------------------------------------------------
def th_broad(rng):
    return int(rng.integers(0, 4)), *rng.random(3)


def th_true(rng):
    t = 2 if rng.random() < 0.7 else 1
    return t, rng.beta(5, 2), rng.beta(2, 5), rng.beta(5, 2)


def make_th_pistar(pi, G, half=(0.125, 0.25, 0.25)):
    """Sample an atom from pi*, then jitter the continuous knobs by a uniform
    kernel of half-width = half the K=64 grid spacing in each coordinate
    (c spacing .25 -> half .125; nu,s spacing .5 -> half .25)."""
    K = len(pi)

    def f(rng):
        k = int(rng.choice(K, p=pi))
        v = G[k]
        t = int(np.argmax(v[:4]))
        c = float(np.clip(v[4] + rng.uniform(-half[0], half[0]), 0, 1))
        nu = float(np.clip(v[5] + rng.uniform(-half[1], half[1]), 0, 1))
        s = float(np.clip(v[6] + rng.uniform(-half[2], half[2]), 0, 1))
        return t, c, nu, s
    return f


def batch_from(rng, sampler, bs, n=N_ROWS):
    X = np.zeros((bs, n, D_MAX), dtype=np.float32)
    Y = np.zeros((bs, n), dtype=np.int64)
    M = np.zeros((bs, D_MAX), dtype=np.float32)
    for b in range(bs):
        t, c, nu, s = sampler(rng)
        d = int(rng.integers(3, D_MAX + 1))
        X[b], Y[b], M[b] = S3.gen_theta(rng, t, c, nu, s, n, d)
    return torch.from_numpy(X), torch.from_numpy(Y), torch.from_numpy(M)


# ---------------------------------------------------------------------------
def train_uncond(sampler, steps, seed, bs=32, lr=3e-4, tag=""):
    rng = np.random.default_rng(1000 + seed)
    torch.manual_seed(seed)
    model = S3.ThetaPFN().to(DEV)
    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=0.01)
    sch = torch.optim.lr_scheduler.OneCycleLR(opt, lr, total_steps=steps,
                                              pct_start=0.05)
    am = S3.build_mask(N_ROWS, DEV)
    scaler = torch.amp.GradScaler("cuda")
    t0 = time.time()
    for st in range(steps):
        X, Y, M = batch_from(rng, sampler, bs)
        X, Y, M = X.to(DEV), Y.to(DEV), M.to(DEV)
        T = ZERO_T.to(DEV)[None].expand(bs, TDIM)
        with torch.amp.autocast("cuda", dtype=torch.bfloat16):
            loss = F.cross_entropy(model(X, Y, M, T, am).reshape(-1, 2),
                                   Y.reshape(-1))
        opt.zero_grad(set_to_none=True)
        scaler.scale(loss).backward()
        scaler.unscale_(opt)
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        scaler.step(opt); scaler.update(); sch.step()
        if st % 2500 == 0 or st == steps - 1:
            print(f"  [{tag}] step {st:6d} loss {loss.item():.4f} "
                  f"{time.time()-t0:6.1f}s", flush=True)
    return model, am


@torch.no_grad()
def eval_uncond(model, am, X, Y, M, chunk=100):
    """Per-dataset mean NLL and accuracy on eval rows [N_SCORE, n)."""
    B = X.shape[0]
    nll = np.zeros(B); acc = np.zeros(B)
    for i in range(0, B, chunk):
        j = min(i + chunk, B)
        T = ZERO_T.to(DEV)[None].expand(j - i, TDIM)
        with torch.amp.autocast("cuda", dtype=torch.bfloat16):
            lg = model(X[i:j], Y[i:j], M[i:j], T, am).float()
        lp = F.log_softmax(lg, -1)[:, N_SCORE:]
        yy = Y[i:j][:, N_SCORE:]
        nll[i:j] = (-lp.gather(2, yy[..., None])[..., 0]).mean(1).cpu().numpy()
        acc[i:j] = (lp.argmax(-1) == yy).float().mean(1).cpu().numpy()
    return nll, acc


def eval_set(rng, sampler, nds):
    X, Y, M = batch_from(rng, sampler, nds)
    return X.to(DEV), Y.to(DEV), M.to(DEV)


def main():
    steps = int(os.environ.get("STEPS", 25000))
    seeds = [int(x) for x in os.environ.get("SEEDS", "0,1").split(",")]
    NEV = int(os.environ.get("NEV", 800))

    # --- refit pi* from the S03 theta-conditional model ----------------------
    tm = S3.ThetaPFN().to(DEV)
    tm.load_state_dict(torch.load(os.path.join(OUT, "s03_model.pt")))
    tm.eval()
    am = S3.build_mask(N_ROWS, DEV)
    G = S3.grid(64)
    Xf, Yf, Mf = S3.sample_corpus(np.random.default_rng(1234), 600)
    logL = S3.rowlogp(tm, am, Xf, Yf, Mf, G).sum(2).cpu().numpy()
    pi = S3.npmle(logL)
    del tm
    torch.cuda.empty_cache()
    print(f"pi* eff.support {math.exp(-(pi*np.log(pi+1e-300)).sum()):.2f}, "
          f"max {pi.max():.3f}", flush=True)

    arms = {"A_broad": th_broad,
            "B_pistar": make_th_pistar(pi, G),
            "C_true": th_true}

    # --- held-out evaluation sets (fixed across all arms and seeds) ----------
    Xc, Yc, Mc = eval_set(np.random.default_rng(90210), th_true, NEV)
    Xb, Yb, Mb = eval_set(np.random.default_rng(90211), th_broad, NEV)

    res = {"steps": steps, "seeds": seeds, "n_eval": NEV,
           "pi_star_eff_support": float(math.exp(-(pi*np.log(pi+1e-300)).sum())),
           "kernel_halfwidth": [0.125, 0.25, 0.25]}
    per = {}      # arm -> seed -> dict of arrays
    for name, samp in arms.items():
        per[name] = {}
        for sd in seeds:
            print(f"=== {name} seed {sd} ===", flush=True)
            m, amm = train_uncond(samp, steps, sd, tag=f"{name}/s{sd}")
            m.eval()
            nc, ac = eval_uncond(m, amm, Xc, Yc, Mc)
            nb, ab = eval_uncond(m, amm, Xb, Yb, Mb)
            per[name][sd] = {"corpus_nll": nc, "corpus_acc": ac,
                             "broad_nll": nb, "broad_acc": ab}
            print(f"  corpus NLL {nc.mean():.4f} acc {ac.mean():.4f} | "
                  f"broad NLL {nb.mean():.4f} acc {ab.mean():.4f}", flush=True)
            del m
            torch.cuda.empty_cache()

    summ = {}
    for name in arms:
        cs = np.stack([per[name][sd]["corpus_nll"] for sd in seeds])   # (S,B)
        bs_ = np.stack([per[name][sd]["broad_nll"] for sd in seeds])
        ca = np.stack([per[name][sd]["corpus_acc"] for sd in seeds])
        ba = np.stack([per[name][sd]["broad_acc"] for sd in seeds])
        summ[name] = {
            "corpus_nll_mean": float(cs.mean()),
            "corpus_nll_seed_sd": float(cs.mean(1).std()),
            "corpus_acc_mean": float(ca.mean()),
            "broad_nll_mean": float(bs_.mean()),
            "broad_nll_seed_sd": float(bs_.mean(1).std()),
            "broad_acc_mean": float(ba.mean()),
        }
    res["summary"] = summ

    # paired per-dataset comparisons, seed-averaged
    def avg(name, key):
        return np.stack([per[name][sd][key] for sd in seeds]).mean(0)

    pairs = {}
    for a, b in [("A_broad", "B_pistar"), ("A_broad", "C_true"),
                 ("B_pistar", "C_true")]:
        for key, lbl in [("corpus_nll", "corpus"), ("broad_nll", "broad")]:
            d = avg(a, key) - avg(b, key)          # >0 means b better
            pairs[f"{b}_vs_{a}_{lbl}"] = {
                "mean_delta_nats": float(d.mean()),
                "b_wins_frac": float((d > 0).mean()),
                "median_delta": float(np.median(d)),
                "q10": float(np.quantile(d, .1)),
                "q90": float(np.quantile(d, .9)),
            }
    res["paired"] = pairs

    print(json.dumps(res, indent=2), flush=True)
    with open(os.path.join(OUT, "s04_results.json"), "w") as f:
        json.dump(res, f, indent=2)

    print("\n--- VERDICT ---")
    print(f"{'arm':>10} {'corpusNLL':>10} {'+-seed':>7} {'corpusACC':>10} "
          f"{'broadNLL':>9} {'broadACC':>9}")
    for name in arms:
        s = summ[name]
        print(f"{name:>10} {s['corpus_nll_mean']:10.4f} "
              f"{s['corpus_nll_seed_sd']:7.4f} {s['corpus_acc_mean']:10.4f} "
              f"{s['broad_nll_mean']:9.4f} {s['broad_acc_mean']:9.4f}")
    for k, v in pairs.items():
        print(f"{k:>32}: delta {v['mean_delta_nats']:+.4f} "
              f"win {v['b_wins_frac']*100:5.1f}% med {v['median_delta']:+.4f}")


if __name__ == "__main__":
    main()
