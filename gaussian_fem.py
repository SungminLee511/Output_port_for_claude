"""
Gaussian FEM solver — energy-minimization CG with SGFEM enrichment.

Usage:
    solver = GaussianFEM(K=1024, broadening=1.5, enrichment="sgfem_linear")
    solver.fit(coords, elems, E, nu)
    u = solver.solve(f_ext, rbe2, n_iter=100)
"""
import torch
import torch.nn.functional as F


class GaussianFEM:
    def __init__(self, K=1024, broadening=1.5, enrichment="sgfem_linear",
                 fit_steps=300, device="cuda", seed=42):
        """
        Args:
            K: number of Gaussian centers
            broadening: sigma multiplier after fitting
            enrichment: "plain", "sgfem_linear", or "sgfem_quadratic"
            fit_steps: Adam steps for sigma optimization
            device: torch device
            seed: random seed for reproducibility
        """
        self.K = K
        self.broadening = broadening
        self.enrichment = enrichment
        self.fit_steps = fit_steps
        self.device = device
        self.seed = seed

        self.centers = None
        self.sigmas = None
        self.P = None
        self.K_e = None
        self.elems = None

    def fit(self, coords, elems, E, nu, K_e=None):
        """Fit Gaussians and build basis. Optionally provide precomputed K_e.

        Args:
            coords: (N, 3) node coordinates, float32, on device
            elems: (M, 4) tetrahedral elements, int64, on device
            E: Young's modulus
            nu: Poisson's ratio
            K_e: (M, 12, 12) precomputed element stiffness matrices.
                 If None, assembled internally.
        """
        self.elems = elems

        if K_e is not None:
            self.K_e = K_e
        else:
            self.K_e = _compute_c3d4_K_matrix(coords, elems, E, nu,
                                               device=self.device,
                                               dtype=torch.float32)

        self.centers, self.sigmas = self._fit_gaussians(coords)
        sb = self.sigmas * self.broadening
        self.P = self._build_basis(coords, self.centers, sb)
        return self

    def solve(self, f_ext, rbe2, n_iter=100, tol=1e-10):
        """Solve Ku=f via energy-minimization CG in Gaussian coefficient space.

        Args:
            f_ext: (N, 3) external force vector
            rbe2: (R,) fixed (Dirichlet) node indices
            n_iter: max CG iterations
            tol: relative residual tolerance

        Returns:
            u: (N, 3) displacement field, float32
        """
        P_d = self.P.double()
        N = f_ext.shape[0]
        K_c = self.P.shape[1]

        f_d = f_ext.double().clone()
        f_d[rbe2] = 0.0
        Ptf = (P_d.T @ f_d).reshape(K_c, 3)

        K_e = self.K_e
        elems = self.elems

        def apply_A(c):
            u = (P_d @ c).reshape(N, 3)
            u[rbe2] = 0.0
            Ku = _mesh_matvec(K_e, elems, u)
            Ku[rbe2] = 0.0
            return (P_d.T @ Ku).reshape(K_c, 3)

        c = torch.zeros(K_c, 3, device=self.device, dtype=torch.float64)
        r = Ptf - apply_A(c)
        p = r.clone()
        rr = (r * r).sum()
        r0_norm = r.norm().item()

        for it in range(n_iter):
            Ap = apply_A(p)
            pAp = (p * Ap).sum()
            if pAp.abs() < 1e-60:
                break
            alpha = rr / pAp
            c = c + alpha * p
            r = r - alpha * Ap
            r_norm = r.norm().item()
            if r_norm < tol * r0_norm:
                break
            rr_new = (r * r).sum()
            beta = rr_new / rr.clamp(min=1e-60)
            p = r + beta * p
            rr = rr_new

        u = (P_d @ c).reshape(N, 3).float()
        u[rbe2] = 0.0
        return u

    # ── Gaussian fitting ─────────────────────────────────────────

    def _fit_gaussians(self, coords):
        """FPS center placement + Adam sigma optimization."""
        torch.manual_seed(self.seed)
        N = coords.shape[0]
        K = self.K

        # Farthest point sampling
        d = torch.full((N,), float("inf"), device=self.device, dtype=coords.dtype)
        chosen = torch.zeros(K, dtype=torch.long, device=self.device)
        chosen[0] = torch.randint(N, (1,), device=self.device)
        for i in range(1, K):
            d = torch.minimum(d, ((coords - coords[chosen[i - 1]]) ** 2).sum(1))
            chosen[i] = d.argmax()
        centers = coords[chosen].clone().detach().requires_grad_(True)

        # Initialize sigmas from nearest-neighbor distance
        D_cc = torch.cdist(centers.unsqueeze(0), centers.unsqueeze(0)).squeeze(0)
        D_cc.fill_diagonal_(float("inf"))
        nn_dist = D_cc.min(dim=1).values
        log_sigmas = (nn_dist * 0.5).clamp(min=0.1).log().detach().requires_grad_(True)

        # Optimize: make Σ φ_k(x) ≈ 1 everywhere
        opt = torch.optim.Adam([centers, log_sigmas], lr=1e-2)
        sched = torch.optim.lr_scheduler.CosineAnnealingLR(
            opt, T_max=self.fit_steps, eta_min=1e-4)
        batch = min(4096, N)

        for step in range(self.fit_steps):
            opt.zero_grad()
            sigmas = log_sigmas.exp()
            idx = torch.randperm(N, device=self.device)[:batch]
            pts = coords[idx]
            D2 = ((pts.unsqueeze(1) - centers.unsqueeze(0)) ** 2).sum(-1)
            logits = -D2 / (2.0 * sigmas.unsqueeze(0) ** 2)
            phi = F.softplus(logits)
            S = phi.sum(dim=1)
            loss = ((S - 1.0) ** 2).mean()
            loss.backward()
            opt.step()
            sched.step()

        return centers.detach(), log_sigmas.exp().detach()

    # ── Basis construction ───────────────────────────────────────

    def _build_basis(self, coords, centers, sigmas):
        """Build P matrix according to enrichment type."""
        if self.enrichment == "plain":
            return self._plain_pou(coords, centers, sigmas)
        elif self.enrichment == "sgfem_linear":
            W = self._compute_W_linear(centers, sigmas)
            return self._sgfem_linear_pou(coords, centers, sigmas, W)
        elif self.enrichment == "sgfem_quadratic":
            W_l, W_q = self._compute_W_quadratic(centers, sigmas)
            return self._sgfem_quadratic_pou(coords, centers, sigmas, W_l, W_q)
        else:
            raise ValueError(f"Unknown enrichment: {self.enrichment}")

    @torch.no_grad()
    def _plain_pou(self, pts, centers, sigmas, chunk=4096):
        N, K = pts.shape[0], centers.shape[0]
        P = torch.empty(N, K, device=self.device, dtype=pts.dtype)
        for i0 in range(0, N, chunk):
            i1 = min(i0 + chunk, N)
            D2 = ((pts[i0:i1].unsqueeze(1) - centers.unsqueeze(0)) ** 2).sum(-1)
            logits = -D2 / (2.0 * sigmas.unsqueeze(0) ** 2)
            phi = F.softplus(logits)
            P[i0:i1] = phi / phi.sum(dim=1, keepdim=True).clamp(min=1e-30)
        return P

    @torch.no_grad()
    def _compute_W_linear(self, centers, sigmas):
        K = centers.shape[0]
        D2 = ((centers.unsqueeze(1) - centers.unsqueeze(0)) ** 2).sum(-1)
        logits = -D2 / (2.0 * sigmas.unsqueeze(0) ** 2)
        phi = F.softplus(logits)
        Ncc = phi / phi.sum(dim=1, keepdim=True).clamp(min=1e-30)
        rel = (centers.unsqueeze(1) - centers.unsqueeze(0)) / sigmas[None, :, None]
        return (Ncc.unsqueeze(-1) * rel).reshape(K, 3 * K)

    @torch.no_grad()
    def _sgfem_linear_pou(self, pts, centers, sigmas, W, chunk=4096):
        N, K = pts.shape[0], centers.shape[0]
        P = torch.empty(N, 4 * K, device=self.device, dtype=pts.dtype)
        for i0 in range(0, N, chunk):
            i1 = min(i0 + chunk, N)
            p = pts[i0:i1]
            D2 = ((p.unsqueeze(1) - centers.unsqueeze(0)) ** 2).sum(-1)
            logits = -D2 / (2.0 * sigmas.unsqueeze(0) ** 2)
            phi = F.softplus(logits)
            Nk = phi / phi.sum(dim=1, keepdim=True).clamp(min=1e-30)
            rel = (p.unsqueeze(1) - centers.unsqueeze(0)) / sigmas[None, :, None]
            E = (Nk.unsqueeze(-1) * rel).reshape(i1 - i0, 3 * K)
            Estar = E - Nk @ W.float()
            P[i0:i1, 0::4] = Nk
            P[i0:i1, 1::4] = Estar[:, 0::3]
            P[i0:i1, 2::4] = Estar[:, 1::3]
            P[i0:i1, 3::4] = Estar[:, 2::3]
        return P

    @torch.no_grad()
    def _compute_W_quadratic(self, centers, sigmas):
        K = centers.shape[0]
        D2 = ((centers.unsqueeze(1) - centers.unsqueeze(0)) ** 2).sum(-1)
        logits = -D2 / (2.0 * sigmas.unsqueeze(0) ** 2)
        phi = F.softplus(logits)
        Ncc = phi / phi.sum(dim=1, keepdim=True).clamp(min=1e-30)
        rel = (centers.unsqueeze(1) - centers.unsqueeze(0)) / sigmas[None, :, None]
        W_lin = (Ncc.unsqueeze(-1) * rel).reshape(K, 3 * K)
        r0, r1, r2 = rel[:, :, 0], rel[:, :, 1], rel[:, :, 2]
        W_quad = torch.stack([
            Ncc * r0 * r0, Ncc * r1 * r1, Ncc * r2 * r2,
            Ncc * r0 * r1, Ncc * r0 * r2, Ncc * r1 * r2,
        ], dim=-1).reshape(K, 6 * K)
        return W_lin, W_quad

    @torch.no_grad()
    def _sgfem_quadratic_pou(self, pts, centers, sigmas, W_l, W_q, chunk=2048):
        N, K = pts.shape[0], centers.shape[0]
        P = torch.empty(N, 10 * K, device=self.device, dtype=pts.dtype)
        for i0 in range(0, N, chunk):
            i1 = min(i0 + chunk, N)
            p = pts[i0:i1]
            C = i1 - i0
            D2 = ((p.unsqueeze(1) - centers.unsqueeze(0)) ** 2).sum(-1)
            logits = -D2 / (2.0 * sigmas.unsqueeze(0) ** 2)
            phi = F.softplus(logits)
            Nk = phi / phi.sum(dim=1, keepdim=True).clamp(min=1e-30)
            rel = (p.unsqueeze(1) - centers.unsqueeze(0)) / sigmas[None, :, None]

            P[i0:i1, 0::10] = Nk

            E_lin = (Nk.unsqueeze(-1) * rel).reshape(C, 3 * K)
            E_lin_star = E_lin - Nk @ W_l.float()
            P[i0:i1, 1::10] = E_lin_star[:, 0::3]
            P[i0:i1, 2::10] = E_lin_star[:, 1::3]
            P[i0:i1, 3::10] = E_lin_star[:, 2::3]

            r0, r1, r2 = rel[:, :, 0], rel[:, :, 1], rel[:, :, 2]
            E_quad = torch.stack([
                Nk * r0 * r0, Nk * r1 * r1, Nk * r2 * r2,
                Nk * r0 * r1, Nk * r0 * r2, Nk * r1 * r2,
            ], dim=-1).reshape(C, 6 * K)
            E_quad_star = E_quad - Nk @ W_q.float()
            P[i0:i1, 4::10] = E_quad_star[:, 0::6]
            P[i0:i1, 5::10] = E_quad_star[:, 1::6]
            P[i0:i1, 6::10] = E_quad_star[:, 2::6]
            P[i0:i1, 7::10] = E_quad_star[:, 3::6]
            P[i0:i1, 8::10] = E_quad_star[:, 4::6]
            P[i0:i1, 9::10] = E_quad_star[:, 5::6]
        return P


# ── Element stiffness matrix assembly (replaces Mesh-Solver import) ──

@torch.no_grad()
def _compute_c3d4_K_matrix(coords, elements, E, nu, device="cuda", dtype=torch.float32):
    """Assemble per-element stiffness matrices for C3D4 tetrahedra.

    Returns K: (M, 12, 12) element stiffness matrices.
    """
    coords = coords.to(device=device, dtype=dtype)
    elements = elements.to(device=device)

    # B matrix (strain-displacement): (M, 6, 12)
    coords_elem = coords[elements]  # (M, 4, 3)
    M = coords_elem.shape[0]
    ones = torch.ones((M, 4, 1), device=device, dtype=dtype)
    A = torch.cat((ones, coords_elem), dim=2)  # (M, 4, 4)
    invA = torch.inverse(A)
    grads = invA[:, 1:, :]  # (M, 3, 4)
    dN_dx, dN_dy, dN_dz = grads[:, 0], grads[:, 1], grads[:, 2]

    B = torch.zeros((M, 6, 12), device=device, dtype=dtype)
    for i in range(4):
        B[:, 0, i*3]   = dN_dx[:, i]
        B[:, 1, i*3+1] = dN_dy[:, i]
        B[:, 2, i*3+2] = dN_dz[:, i]
        B[:, 3, i*3]   = dN_dy[:, i]
        B[:, 3, i*3+1] = dN_dx[:, i]
        B[:, 4, i*3+1] = dN_dz[:, i]
        B[:, 4, i*3+2] = dN_dy[:, i]
        B[:, 5, i*3]   = dN_dz[:, i]
        B[:, 5, i*3+2] = dN_dx[:, i]

    # D matrix (elasticity): (6, 6)
    coef = E / ((1 + nu) * (1 - 2 * nu))
    D = coef * torch.tensor([
        [1-nu,  nu,   nu,   0,            0,            0           ],
        [nu,    1-nu, nu,   0,            0,            0           ],
        [nu,    nu,   1-nu, 0,            0,            0           ],
        [0,     0,    0,    (1-2*nu)/2,   0,            0           ],
        [0,     0,    0,    0,            (1-2*nu)/2,   0           ],
        [0,     0,    0,    0,            0,            (1-2*nu)/2  ],
    ], device=device, dtype=dtype)

    # Volume: (M,)
    p1 = coords[elements[:, 0]]
    v1 = coords[elements[:, 1]] - p1
    v2 = coords[elements[:, 2]] - p1
    v3 = coords[elements[:, 3]] - p1
    V = torch.abs(torch.det(torch.stack([v1, v2, v3], dim=1))) / 6.0

    # K = B^T D B * V
    DB = torch.matmul(D, B)
    K = torch.matmul(B.transpose(1, 2), DB)
    K *= V.view(-1, 1, 1)
    return K


# ── Mesh matvec (module-level, used by solve) ────────────────────

@torch.no_grad()
def _mesh_matvec(K_e, elems, u, chunk=10000):
    """Compute K_mesh @ u via element-wise scatter-add."""
    N = u.shape[0]
    result = torch.zeros(N, 3, device=u.device, dtype=torch.float64)
    u_d = u.double()
    for i0 in range(0, len(elems), chunk):
        i1 = min(i0 + chunk, len(elems))
        el = elems[i0:i1]
        K_ch = K_e[i0:i1].double().reshape(-1, 4, 3, 4, 3)
        u_el = u_d[el]
        Ku_el = torch.einsum("ciajb,cjb->cia", K_ch, u_el)
        for loc_i in range(4):
            result.index_add_(0, el[:, loc_i], Ku_el[:, loc_i])
    return result
