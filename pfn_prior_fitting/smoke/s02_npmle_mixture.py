"""
Smoke test S02 -- threats T-D (NPMLE degeneracy), the *predictive* claim
(Remark 5.2(b)), and observable O1 (out-of-family detection).

Uses the network trained by s01 (s01_model.pt).  NO retraining anywhere.
This is deployment mode M1 of math/01_setup.md Sec.6.

Protocol, matched to actual deployment:
  each dataset has n = 64 rows; rows [0, N_SCORE) are the *context/score* rows
  (labels known, as in any tabular task) and rows [N_SCORE, n) are the *eval*
  rows.  We score l_k on the score rows only, form weights
      w_k(D) proportional to pi_k * exp(l_k^score(D)),
  and measure predictive log-loss on the eval rows.  No eval-row label is ever
  used to choose k.  This is the honest version of O1.

Comparators on eval rows:
  fixed k          (K of them)
  uniform mixture  (pi = 1/K)                      -- Theorem 4 with log K slack
  NPMLE mixture    (pi = pi*, fitted by Cor. 5.1)
  oracle best k in hindsight, per dataset          -- upper bound we must not beat
  oracle single best k globally                    -- the "T-D collapse" baseline
"""

import json
import os

import numpy as np
import torch
import torch.nn.functional as F

import s01_theta_recovery as S1

DEV = S1.DEV
OUT = os.path.dirname(os.path.abspath(__file__))
K = S1.K
N_ROWS = S1.N_ROWS
N_SCORE = 48
D_MAX = S1.D_MAX


# ---------------------------------------------------------------------------
# Out-of-family generators.  None of these is in {linear, mlp, tree, rbf}.
# ---------------------------------------------------------------------------
def gen_periodic(rng, n, d):
    x = S1._sample_x(rng, n, d)
    w = rng.standard_normal(d)
    f = rng.uniform(3.0, 8.0)
    lg = np.sin(f * (x @ w) / np.sqrt(d))
    return x, S1._bern(rng, lg, 6.0)


def gen_discrete(rng, n, d):
    """Categorical-like covariates: x quantized to 3 levels, XOR-ish label."""
    x = np.round(S1._sample_x(rng, n, d)).clip(-1, 1).astype(np.float32)
    a, b = rng.choice(d, size=2, replace=(d < 2))
    lg = 3.0 * (x[:, a] * x[:, b])
    return x, S1._bern(rng, lg, 1.0)


def gen_noisy(rng, n, d):
    """In-family mean function, 35% label noise -- tests the noise model."""
    x, y = S1.gen_linear(rng, n, d)
    flip = rng.random(n) < 0.35
    return x, np.where(flip, 1 - y, y)


OOF = [gen_periodic, gen_discrete, gen_noisy]
OOF_NAMES = ["periodic", "discrete_xor", "label_noise_35"]


def sample_from(rng, gen, nds, n=N_ROWS):
    X = np.zeros((nds, n, D_MAX), dtype=np.float32)
    Y = np.zeros((nds, n), dtype=np.int64)
    M = np.zeros((nds, D_MAX), dtype=np.float32)
    for b in range(nds):
        d = int(rng.integers(3, D_MAX + 1))
        x, y = gen(rng, n, d)
        X[b, :, :d] = (x - x.mean(0)) / (x.std(0) + 1e-6)
        M[b, :d] = 1.0
        Y[b] = y
    return (torch.from_numpy(X).to(DEV), torch.from_numpy(Y).to(DEV),
            torch.from_numpy(M).to(DEV))


# ---------------------------------------------------------------------------
# Per-row log-probs under every k, single forward pass per k.
# ---------------------------------------------------------------------------
@torch.no_grad()
def rowlogp(model, am, X, Y, M):
    """(B, K, n) log q^{(k)}(y_i | x_i, D_{<i})."""
    B, n, _ = X.shape
    out = torch.zeros(B, K, n, device=DEV)
    for k in range(K):
        Kk = torch.full((B,), k, dtype=torch.long, device=DEV)
        with torch.amp.autocast("cuda", dtype=torch.bfloat16):
            lg = model(X, Y, M, Kk, am)
        lp = F.log_softmax(lg.float(), -1)
        out[:, k] = lp.gather(2, Y[..., None])[..., 0]
    return out


# ---------------------------------------------------------------------------
# NPMLE, Corollary 5.1.  All in log space.
# ---------------------------------------------------------------------------
def npmle(logL, iters=2000, tol=1e-10):
    """logL: (M, K) with logL[m,k] = l_k(D_m).  Returns pi* on the simplex."""
    logpi = np.full(K, -np.log(K))
    prev = -np.inf
    for _ in range(iters):
        z = logpi[None, :] + logL                       # (M,K)
        z = z - z.max(1, keepdims=True)
        r = np.exp(z)
        r = r / r.sum(1, keepdims=True)                 # responsibilities
        pi = r.mean(0)
        pi = np.clip(pi, 1e-300, None)
        logpi = np.log(pi / pi.sum())
        # objective
        zz = logpi[None, :] + logL
        obj = (zz.max(1) + np.log(np.exp(zz - zz.max(1, keepdims=True)).sum(1))).mean()
        if abs(obj - prev) < tol:
            break
        prev = obj
    return np.exp(logpi), obj


def mixture_eval(rlp, logpi):
    """Eval-row mean log-loss of the sequential Bayesian mixture with prior pi.
    rlp: (B,K,n).  Weights come from score rows only."""
    ls = rlp[:, :, :N_SCORE].sum(2).cpu().numpy()       # (B,K)
    lo = rlp[:, :, N_SCORE:].sum(2).cpu().numpy()       # (B,K)
    a = logpi[None, :] + ls
    a = a - a.max(1, keepdims=True)
    w = np.exp(a)
    w = w / w.sum(1, keepdims=True)
    # exact sequential mixture over eval rows = logsumexp over k of (log w + lo)
    b = np.log(w + 1e-300) + lo
    tot = b.max(1) + np.log(np.exp(b - b.max(1, keepdims=True)).sum(1))
    return -tot / (N_ROWS - N_SCORE), w


def main():
    model = S1.ThetaPFN().to(DEV)
    model.load_state_dict(torch.load(os.path.join(OUT, "s01_model.pt")))
    model.eval()
    am = S1.build_mask(N_ROWS, DEV)

    res = {"N_SCORE": N_SCORE, "n_rows": N_ROWS, "K": K,
           "components": S1.COMP, "oof": OOF_NAMES}

    # --- corpus: deliberately uneven, known pi_true --------------------------
    pi_true = np.array([0.10, 0.15, 0.50, 0.25])
    M_FIT = 400
    rng = np.random.default_rng(4242)
    counts = rng.multinomial(M_FIT, pi_true)
    Xs, Ys, Ms, lab = [], [], [], []
    for k in range(K):
        if counts[k] == 0:
            continue
        X, Y, Mm = sample_from(rng, S1.GENS[k], int(counts[k]))
        Xs.append(X); Ys.append(Y); Ms.append(Mm)
        lab += [k] * int(counts[k])
    Xf, Yf, Mf = torch.cat(Xs), torch.cat(Ys), torch.cat(Ms)
    rlp_fit = rowlogp(model, am, Xf, Yf, Mf)
    logL_fit = rlp_fit.sum(2).cpu().numpy()             # full-dataset l_k

    pi_star, obj = npmle(logL_fit)
    res["pi_true"] = pi_true.tolist()
    res["pi_star"] = pi_star.tolist()
    res["npmle_obj_per_dataset"] = float(obj)
    res["pi_star_entropy_nats"] = float(-(pi_star * np.log(pi_star + 1e-300)).sum())
    res["pi_star_max"] = float(pi_star.max())
    res["tv_pi_star_vs_true"] = float(0.5 * np.abs(pi_star - pi_true).sum())

    # --- held-out in-family evaluation --------------------------------------
    rng2 = np.random.default_rng(777)
    counts2 = rng2.multinomial(400, pi_true)
    Xs, Ys, Ms = [], [], []
    for k in range(K):
        if counts2[k] == 0:
            continue
        X, Y, Mm = sample_from(rng2, S1.GENS[k], int(counts2[k]))
        Xs.append(X); Ys.append(Y); Ms.append(Mm)
    Xe, Ye, Me = torch.cat(Xs), torch.cat(Ys), torch.cat(Ms)
    rlp = rowlogp(model, am, Xe, Ye, Me)

    ev = -rlp[:, :, N_SCORE:].mean(2).cpu().numpy()     # (B,K) per-row loss
    res["fixed_k_loss"] = {S1.COMP[k]: float(ev[:, k].mean()) for k in range(K)}
    res["oracle_per_dataset_best_k"] = float(ev.min(1).mean())
    res["oracle_global_best_k"] = float(ev.mean(0).min())
    unif, _ = mixture_eval(rlp, np.full(K, -np.log(K)))
    npm, w = mixture_eval(rlp, np.log(pi_star + 1e-300))
    res["uniform_mixture_loss"] = float(unif.mean())
    res["npmle_mixture_loss"] = float(npm.mean())
    res["mean_max_weight"] = float(w.max(1).mean())
    # paired: how often NPMLE mixture beats the globally-best fixed k
    kbest = int(ev.mean(0).argmin())
    res["global_best_k_name"] = S1.COMP[kbest]
    res["npmle_beats_globalbest_frac"] = float((npm < ev[:, kbest]).mean())
    res["npmle_minus_globalbest"] = float((npm - ev[:, kbest]).mean())

    # --- O1: out-of-family detection ----------------------------------------
    score_in = (torch.logsumexp(
        torch.tensor(np.log(pi_star + 1e-300), device=DEV, dtype=torch.float32)[None, :]
        + rlp[:, :, :N_SCORE].sum(2), dim=1) / N_SCORE).cpu().numpy()
    o1 = {"in_family_score": float(score_in.mean()),
          "in_family_evalloss": float(npm.mean())}
    aucs = {}
    for name, g in zip(OOF_NAMES, OOF):
        rngo = np.random.default_rng(hash(name) % 2**31)
        Xo, Yo, Mo = sample_from(rngo, g, 200)
        rlpo = rowlogp(model, am, Xo, Yo, Mo)
        npo, _ = mixture_eval(rlpo, np.log(pi_star + 1e-300))
        so = (torch.logsumexp(
            torch.tensor(np.log(pi_star + 1e-300), device=DEV, dtype=torch.float32)[None, :]
            + rlpo[:, :, :N_SCORE].sum(2), dim=1) / N_SCORE).cpu().numpy()
        # AUC of "score separates in-family from this OOF family"
        a = np.concatenate([score_in, so])
        y = np.concatenate([np.ones_like(score_in), np.zeros_like(so)])
        order = np.argsort(a)
        ranks = np.empty_like(order, dtype=float)
        ranks[order] = np.arange(1, len(a) + 1)
        n1, n0 = y.sum(), (1 - y).sum()
        auc = (ranks[y == 1].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)
        aucs[name] = {"auc": float(auc), "score": float(so.mean()),
                      "evalloss": float(npo.mean())}
    o1["oof"] = aucs
    # correlation between score and eval loss, pooled
    allsc = [score_in] + [None] * 0
    res["O1"] = o1

    print(json.dumps(res, indent=2), flush=True)
    with open(os.path.join(OUT, "s02_results.json"), "w") as f:
        json.dump(res, f, indent=2)

    print("\n--- VERDICT ---")
    print(f"T-D  pi* = {np.round(pi_star,3).tolist()}  (true {pi_true.tolist()})"
          f"  max={pi_star.max():.3f}  entropy={res['pi_star_entropy_nats']:.3f}")
    print(f"PRED npmle-mix {res['npmle_mixture_loss']:.4f} | "
          f"uniform-mix {res['uniform_mixture_loss']:.4f} | "
          f"global-best-k({res['global_best_k_name']}) {res['oracle_global_best_k']:.4f} | "
          f"per-dataset-oracle {res['oracle_per_dataset_best_k']:.4f}")
    print(f"     beats global-best-k on {res['npmle_beats_globalbest_frac']*100:.1f}% "
          f"of datasets, delta {res['npmle_minus_globalbest']:+.4f} nats/row")
    for n_, v in aucs.items():
        print(f"O1   {n_:16s} AUC {v['auc']:.3f}  score {v['score']:.4f} "
              f"(in-family {o1['in_family_score']:.4f})  evalloss {v['evalloss']:.4f}")


if __name__ == "__main__":
    main()
