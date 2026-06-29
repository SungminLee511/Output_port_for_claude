# GLS-Adjoint-Matching — Experiment Spec (2D forced-expanding kill-test)

**Audience:** Claude Code, running on a single A100.
**Goal:** Falsify (not confirm) the central hypothesis that GLS-weighting the Adjoint-Matching loss reduces mode collapse. Everything below is designed so that a *negative* result is just as informative as a positive one. Do not optimize for a positive result. Optimize for a clean, mechanism-isolated read.

---

## 0. One-paragraph context

We train a diffusion sampler (controlled SDE) to sample a Boltzmann target $\nu \propto e^{-E}$ using **Adjoint Matching (AM)**: regress a control field $u_\theta(x,t)$ onto a per-timestep target $m_t = -\sigma\,\hat a_t$, where $\hat a_t$ is the discrete (lean) adjoint propagated backward from $\hat a_1 = \nabla E(X_1)$. AM is known to suffer **mode collapse** on multimodal targets. We have derived that AM's loss is a **heteroscedastic regression** of $u_\theta$ onto a random target $m_t$ whose conditional covariance $\Sigma_t(x) = \mathrm{Cov}[m_t \mid X_t=x]$ is **amplified along the expanding "barrier" directions on a terminal time interval $[t^\ast,1]$**. The Gauss–Markov / GLS-optimal weight for such a regression is $W_t = \Sigma_t^{-1}$. We call AM with this weight **GLS-AM**.

## 1. What is already PROVEN (do not "fix" or modify these)

These are analytic results. Claude Code must implement them faithfully and must NOT alter them in an attempt to improve results.

- **(P1) Correctness-safety.** For *any* $W_t \succ 0$ applied to the AM matching loss with the measure frozen by stop-gradient, the unique critical point is unchanged: it remains the optimal control $u^\star$. ⇒ GLS-weighting cannot introduce target bias. (So: any quality change is about *optimization dynamics / collapse*, never about converging to the wrong thing.)
- **(P2) GLS optimality.** $W_t^\star = \Sigma_t^{-1}$ is the variance-minimizing (Aitken/Gauss–Markov) weight for the estimator of $\theta$, among all $W_t \succ 0$.
- **(P3) Forced expansion.** For the controlled Jacobian $G_t = \partial_x f + \sigma\,\partial_x u^\star_t$, with a driftless reference ($f=0$), $G_t = -\sigma^2 \nabla^2 V_t$. Wherever the target energy is non-convex ($\nabla^2 E \prec 0$, i.e. at barriers between modes), $G_t$ has a **positive eigenvalue** ⇒ the trajectory's first-variation flow $\Phi(1,t)$ is **expanding** along the inter-mode direction on a terminal interval. This is what makes $\Sigma_t$ large and anisotropic there.
- **(P4) Cheap estimation.** $\Sigma_t$ is estimable from quantities AM **already computes** ($\hat a_t$ requires $\Phi$ and $\nabla E$, both already formed for the target). No extra adjoint solves and no extra energy evaluations are needed to estimate $\Sigma_t$.

**Implication for the code:** the expensive ingredients ($\nabla E$, the adjoint $\hat a_t$) are computed once per trajectory for the AM target; $\Sigma_t$ is then estimated from the batch's stored $\{m_t^{(n)}\}$ at $O(\text{batch}\cdot d)$ extra cost. Estimating $\Sigma_t$ must NOT trigger additional energy or Jacobian evaluations.

## 2. What is HYPOTHESIS (these are what the experiment must try to KILL)

- **H1 (primary).** GLS-AM reduces mode collapse / improves mode coverage vs vanilla AM on a target where collapse is *forced*. (P1–P4 do not imply this; collapse is a global non-convex training pathology, and local variance-optimality may or may not help escape it.)
- **H2 (contribution-defining).** GLS-AM beats a **global proximal-clip** baseline at matched compute in the finite-variance regime. (If GLS-AM never beats proximal clipping, GLS-AM is "proximal-in-disguise" and is not a distinct contribution. Full H2 — the heavy-tail vs finite-variance regime split — is a *separate* future experiment; here we only get an early read.)
- **H3 (cheap-method).** The **rank-1** GLS weight (top expanding eigenvector only) retains most of the benefit of the **full** $\Sigma_t^{-1}$, so the method is cheap. (If rank-1 ≈ vanilla but full helps, the method needs full $\Sigma_t$ and is more expensive.)

## 3. Target distribution (forced-expanding, collapse-prone)

Balanced 2-component Gaussian mixture in $\mathbb{R}^2$ with a sharp barrier:

$$
\nu(x) = \tfrac12\,\mathcal N(x;\,\mu_-,\,s^2 I) + \tfrac12\,\mathcal N(x;\,\mu_+,\,s^2 I),\qquad
\mu_\pm = (\pm D,\,0),\quad E(x) = -\log \nu(x) + \text{const}.
$$

Default: $D = 3.0$, $s = 0.5$. Balanced weights are essential: collapse is then unambiguously visible as occupancy deviating from 50/50, with ground-truth occupancy known exactly.

**Why this target:** balanced ⇒ collapse is detectable; well-separated + small $s$ ⇒ deep barrier ⇒ $\nabla^2 E \prec 0$ strongly between modes ⇒ **P3 forced-expansion is active** ⇒ $\Sigma_t$ is large/anisotropic along the $x_1$ (inter-mode) axis near $t\to1$, which is exactly where GLS should act.

### 3a. Difficulty calibration (MANDATORY pre-step — the test is vacuous if the baseline does not collapse)

Before running the full grid, train **vanilla AM (config A0)** alone and confirm it collapses (occupancy of the minority mode $< 0.2$, ideally near 0) reliably across seeds. If A0 does **not** collapse at the defaults, make the target harder in this order until A0 collapses: (i) increase $D$ (3 → 4 → 5), (ii) decrease $s$ (0.5 → 0.35), (iii) reduce integration steps $N$ (100 → 50), (iv) increase noise $\sigma$. **Record the final calibrated settings**; all configs then use those identical settings. If A0 cannot be made to collapse, STOP and report that — the kill-test cannot run, and that itself is a finding.

## 4. Sampler (lean Adjoint Matching), exact spec

- **Horizon / grid:** $t \in [0,1]$, $N$ Euler–Maruyama steps, $h = 1/N$. Default $N=100$.
- **Reference:** driftless, $f \equiv 0$; constant scalar diffusion $\sigma$ (default $\sigma = 1.5$, may be changed by calibration). Forward step:
  $$X_{k+1} = X_k + h\,\sigma\,u_\theta(X_k, t_k) + \sqrt{h}\,\sigma\,\xi_k,\quad \xi_k \sim \mathcal N(0, I_2).$$
- **Prior:** $X_0 \sim \mathcal N(0, \sigma_0^2 I)$, default $\sigma_0 = 1.5$ (broad, so trajectories must be steered into *both* wells).
- **Control net $u_\theta$:** MLP, input $(x_1,x_2,\,\phi(t))$ with $\phi(t)=(t, \sin 2\pi t, \cos 2\pi t)$; 3 hidden layers × 128 units, SiLU; output $\in \mathbb R^2$. Identical architecture/init across ALL configs.
- **Training regime:** **on-policy, no replay buffer.** This is deliberate: on-policy training is exactly the regime where SOC samplers collapse, so it is the adversarial setting for H1. (The P4 cheap-estimation argument holds with "current batch" in place of "buffer.")
- **Adjoint target (lean, discrete-then-optimize = transpose of forward Jacobian):**
  $$\hat a_N = \nabla E(X_N),\qquad \hat a_k = \hat a_{k+1} + h\,\sigma\,\big(\partial_x u_\theta(X_k,t_k)\big)^{\!\top}\hat a_{k+1},\qquad m_k = -\sigma\,\hat a_k.$$
  Implement $(\partial_x u_\theta)^\top \hat a_{k+1}$ as a **vector–Jacobian product** (one autograd backward through $u_\theta$ at the detached $X_k$); do **not** form the full Jacobian. The trajectory $X$, the noise $\xi$, and $\hat a$ are all **detached** when forming $m_k$ (stop-gradient — required by P1).
- **Loss (per config, see §5):**
  $$\mathcal L(\theta) = \frac{1}{B}\sum_{n=1}^{B}\sum_{k=0}^{N-1} h\,\big(u_\theta(X_k^{(n)},t_k) - m_k^{(n)}\big)^{\!\top} W_k\,\big(u_\theta(X_k^{(n)},t_k) - m_k^{(n)}\big),$$
  with $m_k$ and $W_k$ **detached** (constants w.r.t. $\theta$).
- **Optimizer:** Adam, fixed LR across configs (default $3\times10^{-4}$). Batch $B=512$ trajectories. Steps: enough to converge or collapse (default 15k). Same for all configs (matched compute).
- **Energy-eval accounting:** count and report total $\nabla E$ / $E$ evaluations per config; these must be **equal** across configs (the GLS weight must add zero energy evals).

## 5. Configs (the W-shape axis × the normalization axis)

The entire content of GLS-AM is the choice of $W_k$. Quality differences must be attributable to $W_k$ **and nothing else** — same target, same net, same init, same LR, same steps, same energy budget.

$\Sigma_t$ is estimated per time-slice from the current batch by **spatial binning** (removes the between-state contaminant via the law of total covariance — see §6). Add a floor $\tau I$ before inverting (default $\tau = 10^{-3}\cdot \overline{\mathrm{tr}\,\Sigma_t}$).

### W-shape variants
- **A0 — Identity (vanilla AM):** $W_k = I$. Baseline.
- **A1 — Coordinate-diagonal:** $W_k = \mathrm{diag}(\hat\Sigma_{t_k})^{-1}$.
- **A2 — Rank-1 GLS:** $\hat\Sigma_{t_k} \approx s_k v_k v_k^\top + \tau I$ ($v_k$ = top eigenvector via power iteration on batch residuals); invert via Sherman–Morrison. Tests **H3**.
- **A3 — Full GLS:** $W_k = (\hat\Sigma_{t_k} + \tau I)^{-1}$. Tests **H1/H2**.

### Normalization axis (CRITICAL controls — prevents "win = effective LR schedule")
The GLS weight reweights both **across directions** (down-weight the expanding barrier direction) and **across time** (down-weight the high-variance terminal window). To isolate these and to rule out a trivial loss-rescaling effect, run each non-identity W under two normalizations:
- **NormA (per-slice trace-norm):** scale $W_k \leftarrow d\cdot W_k/\mathrm{tr}(W_k)$ so every slice has $\mathrm{tr}=d$. This **kills the temporal reweighting** and isolates the **directional** GLS effect.
- **NormB (single global scalar):** scale all $W_k$ by one constant so the batch-mean of $\mathrm{tr}(W_k)$ equals $d$. This **preserves both** temporal and directional reweighting — the full GLS mechanism.

### Baselines & sanities
- **PROX — global proximal clip:** vanilla AM ($W=I$) plus per-trajectory loss-weight clipping (clip the per-path total residual weight at the batch's, e.g., 90th percentile) — the standard anti-collapse mechanism we must beat. Tests **H2 (early read)**.
- **ORACLE — oracle-$\Sigma$ (sanity):** A3-NormB but with $\Sigma_t$ estimated from a long, well-mixed reference set (e.g. from true GMM samples pushed through the forward noising, or a very long-trained model). Upper bound on what perfect $\Sigma_t$ buys; if even ORACLE doesn't beat A0, H1 is dead regardless of estimation quality.
- **A3-RAW (sanity):** A3 with **no** normalization. If A3-RAW ≈ A3-NormB, scale doesn't matter; if A3-RAW behaves wildly differently, the benefit was partly a scale/LR artifact — flag it.

**Minimum config set to run (all × 5 seeds):**
`A0`, `A3-NormA`, `A3-NormB`, `PROX`, `A1-NormB`, `A2-NormB`, `ORACLE`, `A3-RAW`.

## 6. $\Sigma_t$ estimation (must use only already-computed quantities)

Per time-slice $t_k$, over the batch:
1. **Bin** the states $\{X_k^{(n)}\}_n$ on a 2D grid (default $12\times12$ over the occupied region).
2. Within each non-empty cell $c$, compute the sample covariance of the targets $\{m_k^{(n)} : X_k^{(n)}\in c\}$. (This conditions on $X_t$, removing the between-state mean spread $\mathrm{Cov}_x[\mu_t(x)]$ per the law of total covariance.)
3. $\hat\Sigma_{t_k} = $ occupancy-weighted average of the within-cell covariances. Floor cells with $<8$ points (skip them).
4. Rank-1: top eigenvector/eigenvalue of $\hat\Sigma_{t_k}$ by a few power-iteration steps.

This uses only the $m_k$ already formed for the AM target ⇒ **zero extra energy/adjoint cost** (verifies P4 operationally). Log the per-step wall-clock and energy-eval counts to confirm.

## 7. Metrics (compute all; per seed)

Sample $B_\text{eval}=20{,}000$ terminal states $X_1$ from the trained sampler.

- **(M1) Minority-mode occupancy** $= \min(\text{frac in well}_-,\ \text{frac in well}_+)$, assigning each $X_1$ to the nearest mode. Ground truth $=0.5$. **Primary H1 metric.** Collapse ⇒ near 0.
- **(M2) Mode recall** $= \#\{\text{modes with} \geq 1\% \text{ of mass}\} \in \{0,1,2\}$.
- **(M3) Sliced-2-Wasserstein** and **(M4) RBF-MMD** between sampler $X_1$ and exact GMM samples (exact samples are available — it's a known GMM). Report both.
- **(M5) Per-$t$ variance profile (mechanism confirmation):** $\mathrm{tr}(\hat\Sigma_{t_k})$ vs $t_k$, top-eigenvalue vs $t_k$, and the **angle between the top eigenvector of $\hat\Sigma_{t_k}$ and the inter-mode axis $(1,0)$** vs $t_k$. Prediction from P2/P3: trace and top-eigenvalue rise toward $t\to1$; the top eigenvector aligns with $(1,0)$ near $t\to1$. If this profile is absent, the mechanism is mis-specified (Threat B) — report it loudly.
- **(M6) Forced-expansion sanity:** along sampled trajectories, compute eigenvalues of $G_k = \sigma\,\partial_x u_\theta(X_k,t_k)$ in the barrier region ($|x_1|<1$); confirm $\max\mathrm{eig}(G_k) > 0$ on a terminal $t$-interval. Confirms P3 in situ.
- **(M7) log-likelihood / KL to GMM (optional):** if a cheap density estimate of $q_\theta(X_1)$ is available (KDE on samples is fine for 2D), report KL$(q_\theta\|\nu)$ via samples. Optional; M1/M3/M4 are the load-bearing ones.

## 8. Kill-conditions (STATED IN ADVANCE — apply exactly these)

Let $\text{occ}(\cdot)$ = M1 mean over seeds, with seed-std as the noise scale.

- **K-H1 (primary).** If $\text{occ}(\text{A3-NormB})$ and $\text{occ}(\text{A2-NormB})$ are **both within 1 seed-std of $\text{occ}(\text{A0})$** (and A0 collapsed), then the variance mechanism does **not** help collapse ⇒ **H1 FALSIFIED**; GLS-AM is downgraded to "provably-optimal-but-inert reweighting." Report this verdict plainly.
- **K-MECH (mechanism isolation).** The benefit must **track the weight**. Required pattern for H1 to be *supported*: $\text{occ}(\text{A3-NormB}) > \text{occ}(\text{A0})$ by $>2$ seed-std. Then read:
  - If $\text{A3-NormA} > \text{A0}$ ⇒ the **directional** reweighting alone helps (within-slice barrier-direction down-weighting).
  - If $\text{A3-NormB} > \text{A3-NormA}$ ⇒ the **temporal** reweighting adds value on top.
  - If $\text{A1-NormB} \approx \text{A0}$ but $\text{A3-NormB} > \text{A0}$ ⇒ **direction matters** (coordinate-diagonal misses it) — supports the rank-1 story.
  - If $\text{A2-NormB} \approx \text{A3-NormB}$ ⇒ **H3 SUPPORTED** (cheap rank-1 suffices).
  - If $\text{A3-RAW}$ diverges from $\text{A3-NormB}$ ⇒ part of the effect is scale/LR — **flag and discount** accordingly.
  - If $\text{ORACLE} \approx \text{A0}$ ⇒ even perfect $\Sigma_t$ is inert ⇒ **H1 dead** independent of estimation noise (strongest possible kill).
- **K-H2 (early read).** If $\text{occ}(\text{best GLS}) \leq \text{occ}(\text{PROX})$ within 1 seed-std ⇒ flag **"proximal-in-disguise risk"**; GLS-AM is not yet a distinct contribution on this target. (Definitive H2 needs the noise-regime sweep — separate experiment.)

Report which conditions fired, with the numbers, regardless of whether the outcome is favorable.

## 9. PyTorch scaffold (near-complete; fill only the marked TODOs)

```python
import math, json, time, numpy as np, torch, torch.nn as nn
torch.set_default_dtype(torch.float32)
DEV = "cuda" if torch.cuda.is_available() else "cpu"

# ---------------- Target ----------------
class GMM2D:
    def __init__(self, D=3.0, s=0.5):
        self.mu = torch.tensor([[-D,0.],[D,0.]], device=DEV); self.s = s
        self.logw = math.log(0.5)
    def log_nu(self, x):                      # (B,) up to const
        d2 = ((x[:,None,:]-self.mu[None])**2).sum(-1)/(self.s**2)
        logc = -0.5*d2 - math.log(2*math.pi*self.s**2) + self.logw
        return torch.logsumexp(logc, dim=1)
    def energy(self, x):  return -self.log_nu(x)
    def grad_energy(self, x):
        x = x.detach().requires_grad_(True)
        E = self.energy(x).sum()
        g, = torch.autograd.grad(E, x)
        return g.detach()
    def sample(self, n):                      # exact ground-truth samples
        k = torch.randint(0,2,(n,),device=DEV)
        return self.mu[k] + self.s*torch.randn(n,2,device=DEV)

# ---------------- Control net ----------------
class Control(nn.Module):
    def __init__(self, h=128):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(5,h), nn.SiLU(),
                                 nn.Linear(h,h), nn.SiLU(),
                                 nn.Linear(h,h), nn.SiLU(),
                                 nn.Linear(h,2))
    def forward(self, x, t):                  # x:(B,2) t:(B,1)
        feat = torch.cat([x, t, torch.sin(2*math.pi*t), torch.cos(2*math.pi*t)], -1)
        return self.net(feat)

# ---------------- Forward sim + lean adjoint ----------------
def rollout(u, tgt, B, N, sigma, sigma0):
    h = 1.0/N
    X = [torch.randn(B,2,device=DEV)*sigma0]
    ts = torch.linspace(0,1,N+1,device=DEV)
    for k in range(N):
        t = ts[k].expand(B,1)
        with torch.no_grad():
            drift = u(X[k], t)
        X.append(X[k] + h*sigma*drift + math.sqrt(h)*sigma*torch.randn(B,2,device=DEV))
    X = torch.stack(X,0).detach()             # (N+1,B,2)
    # lean adjoint backward, m_k = -sigma * a_k ; a_k = a_{k+1} + h*sigma*(du/dx)^T a_{k+1}
    a = tgt.grad_energy(X[N])                  # (B,2)
    M = [None]*(N+1); M[N] = -sigma*a
    for k in range(N-1,-1,-1):
        t = ts[k].expand(B,1)
        xk = X[k].detach().requires_grad_(True)
        uk = u(xk, t)
        vjp, = torch.autograd.grad(uk, xk, grad_outputs=a, retain_graph=False)  # (du/dx)^T a
        a = (a + h*sigma*vjp).detach()
        M[k] = (-sigma*a)
    M = torch.stack(M,0).detach()             # (N+1,B,2)
    return X, M, ts

# ---------------- Sigma_t estimation (binned within-state cov) ----------------
def estimate_Sigma(Xk, Mk, nbin=12, min_pts=8):
    # Xk:(B,2) Mk:(B,2) -> 2x2 occupancy-weighted within-cell covariance
    lo, hi = Xk.min(0).values, Xk.max(0).values
    span = (hi-lo).clamp(min=1e-6)
    idx = ((Xk-lo)/span*nbin).clamp(0,nbin-1-1e-4).long()
    flat = idx[:,0]*nbin + idx[:,1]
    Sig = torch.zeros(2,2,device=DEV); W = 0.0
    for c in flat.unique():
        m = (flat==c); 
        if m.sum() < min_pts: continue
        Y = Mk[m]; Yc = Y - Y.mean(0,keepdim=True)
        Sig += (Yc.T@Yc)/(m.sum()-1) * m.sum(); W += m.sum().item()
    return Sig/max(W,1.0)                       # E_x[Cov[m|x]]

# ---------------- Weight builders (per slice) ----------------
def make_W(Sig, mode, tau_rel=1e-3):
    tau = tau_rel*torch.trace(Sig).clamp(min=1e-8)
    if mode=="I":      W = torch.eye(2,device=DEV)
    elif mode=="diag": W = torch.diag(1.0/(torch.diag(Sig)+tau))
    elif mode=="full": W = torch.linalg.inv(Sig+tau*torch.eye(2,device=DEV))
    elif mode=="rank1":
        ev,evec = torch.linalg.eigh(Sig); s=ev[-1].clamp(min=0); v=evec[:,-1:]
        # (s v v^T + tau I)^-1 via Sherman-Morrison
        W = (1/tau)*(torch.eye(2,device=DEV) - (s/(s+tau))*(v@v.T))
    return W

def normalize_W(Ws, scheme):                   # Ws: list of (2,2)
    d=2
    if scheme=="A":   return [d*W/torch.trace(W).clamp(min=1e-8) for W in Ws]
    if scheme=="B":
        meantr = torch.stack([torch.trace(W) for W in Ws]).mean().clamp(min=1e-8)
        return [d*W/meantr for W in Ws]
    return Ws                                   # "raw"

# ---------------- One training run ----------------
def train(cfg, seed):
    torch.manual_seed(seed); np.random.seed(seed)
    tgt = GMM2D(cfg["D"], cfg["s"]); u = Control().to(DEV)
    opt = torch.optim.Adam(u.parameters(), lr=cfg["lr"])
    N,B,sigma,sigma0 = cfg["N"],cfg["B"],cfg["sigma"],cfg["sigma0"]
    nE = 0
    for step in range(cfg["steps"]):
        X, M, ts = rollout(u, tgt, B, N, sigma, sigma0); nE += B   # one grad_energy call per traj
        # build per-slice W (detached)
        with torch.no_grad():
            Ws=[]
            for k in range(N):
                Sig = estimate_Sigma(X[k], M[k]) if cfg["shape"]!="I" else torch.eye(2,device=DEV)
                Ws.append(make_W(Sig, cfg["shape"]))
            Ws = normalize_W(Ws, cfg["norm"])
        # loss
        h=1.0/N; loss=0.0
        xin = X[:N].reshape(-1,2); tin = ts[:N].repeat_interleave(B).reshape(-1,1)
        upred = u(xin, tin).reshape(N,B,2)
        for k in range(N):
            r = upred[k]-M[k]                  # M detached
            loss = loss + h*(r.unsqueeze(1)@Ws[k]@r.unsqueeze(2)).mean()
        # PROX baseline: clip per-trajectory total residual weight
        if cfg.get("prox"):
            with torch.no_grad():
                pw = ((upred-M[:N])**2).sum(-1).mean(0)        # (B,) per-traj
                thr = torch.quantile(pw, 0.9); scale=(thr/pw.clamp(min=1e-8)).clamp(max=1.0)
            r = (upred-M[:N]); loss = (h*(r**2).sum(-1)*scale[None]).mean()
        opt.zero_grad(); loss.backward(); opt.step()
    return u, tgt, nE

# ---------------- Eval / metrics ----------------
def terminal_samples(u, tgt, cfg, n=20000):
    N,sigma,sigma0=cfg["N"],cfg["sigma"],cfg["sigma0"]; h=1/N
    X=torch.randn(n,2,device=DEV)*sigma0; ts=torch.linspace(0,1,N+1,device=DEV)
    with torch.no_grad():
        for k in range(N):
            X = X + h*sigma*u(X, ts[k].expand(n,1)) + math.sqrt(h)*sigma*torch.randn(n,2,device=DEV)
    return X

def metrics(Xs, tgt):
    d = ((Xs[:,None,:]-tgt.mu[None])**2).sum(-1); lab = d.argmin(1)
    f0 = (lab==0).float().mean().item(); f1=1-f0
    occ_min = min(f0,f1); recall = int(f0>=0.01)+int(f1>=0.01)
    G = tgt.sample(Xs.shape[0])
    # sliced W2
    K=64; w2=0.0
    for _ in range(K):
        th=torch.randn(2,device=DEV); th/=th.norm()
        a=(Xs@th).sort().values; b=(G@th).sort().values
        w2+=((a-b)**2).mean().item()
    sw2=(w2/K)**0.5
    # RBF-MMD (subsample)
    def mmd(a,b,sig=1.0):
        def k(u,v): 
            d=((u[:,None]-v[None])**2).sum(-1); return torch.exp(-d/(2*sig**2))
        return (k(a,a).mean()+k(b,b).mean()-2*k(a,b).mean()).item()
    idx=torch.randperm(Xs.shape[0])[:2000]
    mmd_v = mmd(Xs[idx], G[idx])
    return dict(occ_min=occ_min, f0=f0, f1=f1, recall=recall, sliced_w2=sw2, mmd=mmd_v)
```

**Notes / required behavior for Claude Code:**
- Run §3a calibration FIRST. Then run the §5 config set × 5 seeds (seeds 0–4).
- Compute the §7 metrics for every run. Also compute and save the **M5 variance profile** (per-$t$ $\mathrm{tr}\,\hat\Sigma$, top-eig, eigenvector angle) for at least A0 and A3-NormB, and the **M6 expansion check**.
- Verify energy-eval counts are equal across configs (GLS adds none).
- Save raw per-seed numbers to `results.json`. Save the M5/M6 profiles to `profiles.json`. Save plots (occupancy bars per config; variance profile vs $t$; example terminal scatter per config) to PNGs.
- Do **NOT** add tricks, schedules, or extra losses not specified here. Do **NOT** tune $W$-normalization differently per config. Do **NOT** change the target between configs. Keep `M` and `W` detached. If you must deviate (e.g. numerical fix), record it in the report's "Deviations" section.
- If anything NaNs or diverges, reduce LR by 3× once and note it; if it still diverges, report the config as unstable rather than silently dropping it.
- Then fill out `GLS_AM_report.md` per the report-format spec.

## 10. Compute / runtime
2D, tiny nets, $N=100$, $B=512$, 15k steps ≈ a few minutes/run on an A100. Full grid (8 configs × 5 seeds = 40 runs) plus calibration should finish well under an hour. If slower, reduce steps to the point where A0 reliably collapses and the better configs reliably separate (report the step count used).
