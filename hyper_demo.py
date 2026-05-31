import time
import warnings
warnings.filterwarnings('ignore')

import torch
import numpy as np
import matplotlib.pyplot as plt

from tensormesh import Mesh, ElementAssembler
from tensormesh.dataset.mesh import gen_cube

torch.set_default_dtype(torch.float64)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print('device:', device)
if device.type == 'cuda':
    print('GPU:', torch.cuda.get_device_name(0))

L, W, H = 1.0, 0.2, 0.2
mesh = gen_cube(chara_length=0.06, left=0, right=L, bottom=0, top=W, front=0, back=H).double().to(device)
print(f'Mesh: {mesh.n_points} nodes, {mesh.n_elements} {mesh.default_element_type} elements')

class NeoHookean(ElementAssembler):
    def __post_init__(self, mu, lam):
        self.mu = mu
        self.lam = lam

    def element_energy(self, gradu):
        dim = gradu.shape[-1]
        I = torch.eye(dim, device=gradu.device, dtype=gradu.dtype)
        F = I + gradu
        J = torch.clamp(torch.det(F), min=1e-6)
        I1 = (F ** 2).sum()
        logJ = torch.log(J)
        return 0.5 * self.mu * (I1 - 3) - self.mu * logJ + 0.5 * self.lam * logJ ** 2

E, nu = 1.0e6, 0.45
mu_  = E / (2 * (1 + nu))
lam_ = E * nu / ((1 + nu) * (1 - 2 * nu))
print(f'E = {E:.2e} Pa,  nu = {nu},  mu = {mu_:.3e},  lam = {lam_:.3e}')

model = NeoHookean.from_mesh(mesh, mu=mu_, lam=lam_).to(device)

pts = mesh.points
eps = 1e-5

fixed = torch.abs(pts[:, 0]) < eps                     # left face
tip   = pts[:, 0] > L - eps                            # right face
print(f'Clamped nodes : {int(fixed.sum())}')
print(f'Tip nodes     : {int(tip.sum())}')

P_total = -200.0                                       # 200 N, downward
f_ext_full = torch.zeros_like(pts)
f_ext_full[tip, 1] = P_total / int(tip.sum())
print(f'||f_ext_full|| = {f_ext_full.norm().item():.4e}')

u = torch.zeros_like(pts, requires_grad=True)
mask = (~fixed).unsqueeze(1).to(u.dtype)

n_steps = 8
disp_hist, load_hist = [], []

t0 = time.time()
for step in range(1, n_steps + 1):
    scale = step / n_steps
    f_ext = f_ext_full * scale
    opt = torch.optim.LBFGS([u], lr=1.0, max_iter=80, max_eval=100,
                            tolerance_grad=1e-7, tolerance_change=1e-9,
                            history_size=100, line_search_fn='strong_wolfe')

    def closure():
        opt.zero_grad()
        u_act = u * mask
        Eint = model.energy(point_data={'u': u_act})
        Wext = (f_ext * u_act).sum()
        loss = Eint - Wext
        if loss.requires_grad:
            loss.backward()
        return loss

    Lv = opt.step(closure).item()
    tip_uy = (u[tip][:, 1].mean()).item()
    disp_hist.append(tip_uy)
    load_hist.append(abs(P_total * scale))
    print(f'step {step}: P={abs(P_total*scale):6.1f} N,  Π={Lv:+.3e},  tip uy = {tip_uy:+.4f} m')

if device.type == 'cuda':
    torch.cuda.synchronize()
print(f'\nTotal solve time: {time.time()-t0:.2f} s')

fig, ax = plt.subplots(figsize=(6, 4))
ax.plot(load_hist, [abs(d) for d in disp_hist], 'o-', color='C0')
ax.set_xlabel('tip load |P| (N)')
ax.set_ylabel('|tip y-displacement| (m)')
ax.set_title('Load–displacement (Neo-Hookean, finite strain)')
ax.grid(True, alpha=0.4)
plt.tight_layout()
plt.savefig('hyper_load_disp.png', dpi=120, bbox_inches='tight')
plt.show()

u_np = (u * mask).detach().cpu().numpy()
pts_np = pts.cpu().numpy()
deformed = pts_np + u_np
mag = np.linalg.norm(u_np, axis=1)

fig = plt.figure(figsize=(13, 5))
for k, view in enumerate([(20, -65), (0, -90)]):
    ax = fig.add_subplot(1, 2, k + 1, projection='3d')
    ax.scatter(pts_np[:, 0], pts_np[:, 2], pts_np[:, 1], c='lightgray', s=4, alpha=0.3, label='undeformed')
    sc = ax.scatter(deformed[:, 0], deformed[:, 2], deformed[:, 1], c=mag, cmap='viridis', s=15)
    ax.set_box_aspect([L, H, max(W, 0.4)])
    ax.view_init(elev=view[0], azim=view[1])
    ax.set_xlabel('x'); ax.set_ylabel('z'); ax.set_zlabel('y')
    ax.set_title('perspective' if k == 0 else 'side view (xy)')
plt.colorbar(sc, ax=fig.get_axes(), shrink=0.6, label='|u| (m)')
plt.suptitle(f'Hyperelastic cantilever — final tip displacement {abs(disp_hist[-1]):.3f} m  ({abs(disp_hist[-1])/L*100:.1f}% of L)', y=1.02)
plt.savefig('hyper_deformed.png', dpi=120, bbox_inches='tight')
plt.show()
