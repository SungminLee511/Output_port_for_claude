import time, warnings
warnings.filterwarnings('ignore')
import torch
import numpy as np
import matplotlib.pyplot as plt

from tensormesh import Mesh
from tensormesh.dataset.mesh import gen_cube
from tensormesh.assemble import LinearElasticityElementAssembler, ContactAssembler

torch.set_default_dtype(torch.float64)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print('device:', device)
if device.type == 'cuda':
    print('GPU:', torch.cuda.get_device_name(0))

Lx, Ly, Lz = 3.0, 1.5, 3.0
mesh = gen_cube(chara_length=0.18, left=0, right=Lx, bottom=0, top=Ly, front=0, back=Lz).double().to(device)
print(f'Mesh: {mesh.n_points} nodes, {mesh.n_elements} {mesh.default_element_type} elements')

E_block = 1.0e7
nu = 0.3
elast = LinearElasticityElementAssembler.from_mesh(mesh, E=E_block, nu=nu).to(device)
print(f'Elastic block: E = {E_block:.2e} Pa, ν = {nu}')

pts = mesh.points
eps_t = 1e-5
bottom_mask = pts[:, 1] < eps_t
top_mask    = pts[:, 1] > Ly - eps_t
print(f'Bottom nodes : {int(bottom_mask.sum())}')
print(f'Top nodes    : {int(top_mask.sum())}')

R_sphere = 0.5
cx, cz = Lx / 2, Lz / 2
gap0 = 1e-3
sphere_center0 = torch.tensor([cx, Ly + R_sphere + gap0, cz], dtype=torch.float64, device=device)
print(f'Sphere R = {R_sphere}, center starts at {sphere_center0.tolist()}')

class SpherePenalty(ContactAssembler):
    def __post_init__(self, sphere_center, R, k):
        self.sphere_center = sphere_center
        self.R = R
        self.k = k

    def element_energy(self, x, displacement):
        x_def = x + displacement
        dist = (x_def - self.sphere_center).norm()
        pen = torch.clamp(self.R - dist, min=0.0)
        return 0.5 * self.k * pen ** 2

contact = SpherePenalty.from_mesh(
    mesh,
    boundary_mask=top_mask,
    quadrature_order=2,
    sphere_center=sphere_center0,
    R=R_sphere,
    k=1.0e9,
).to(device)
print('Contact assembler built.')

delta_max = 0.05
n_steps = 10
schedule = np.linspace(0.0, delta_max, n_steps + 1)[1:]

u = torch.zeros_like(pts, requires_grad=True)
deltas, forces_FEM, max_pen_hist = [], [], []

t0 = time.time()
for s, delta in enumerate(schedule):
    sphere_y = Ly + R_sphere + gap0 - delta
    contact.sphere_center = torch.tensor([cx, sphere_y, cz], dtype=torch.float64, device=device)

    opt = torch.optim.LBFGS([u], lr=1.0, max_iter=100, history_size=100, line_search_fn='strong_wolfe')

    def closure():
        opt.zero_grad()
        u_act = u * (~bottom_mask).unsqueeze(-1).to(u.dtype)
        Eel = elast.energy(point_data={'displacement': u_act})
        Ec  = contact.energy(point_data={'displacement': u_act})
        loss = Eel + Ec
        if loss.requires_grad:
            loss.backward()
        return loss

    Lv = opt.step(closure).item()

    with torch.no_grad():
        u.data.mul_((~bottom_mask).unsqueeze(-1).to(u.dtype))
        x_def_top = pts[top_mask] + u[top_mask]
        d = (x_def_top - contact.sphere_center).norm(dim=1)
        max_pen = (R_sphere - d).clamp(min=0).max().item()

    # Reaction at bottom: dE_el/du (only elastic part, that's what the support holds)
    u_clone = u.detach().clone().requires_grad_(True)
    Eel_c = elast.energy(point_data={'displacement': u_clone})
    Eel_c.backward()
    Fy_bottom = u_clone.grad[bottom_mask, 1].sum().item()

    deltas.append(delta); forces_FEM.append(Fy_bottom); max_pen_hist.append(max_pen)
    print(f'step {s+1:2d}: δ={delta:.4f},  Π={Lv:+.3e},  F = {Fy_bottom:+.3e} N,  max penetration = {max_pen:.2e} m')

if device.type == 'cuda':
    torch.cuda.synchronize()
print(f'\nTotal solve: {time.time()-t0:.1f} s')

E_star = E_block / (1 - nu ** 2)
deltas_arr = np.array(deltas)
F_hertz = (4 / 3) * E_star * np.sqrt(R_sphere) * deltas_arr ** 1.5

fig, axes = plt.subplots(1, 2, figsize=(13, 4))
ax = axes[0]
ax.plot(deltas, np.array(forces_FEM) / 1e3, 'o-', label='penalty FEM', lw=2)
ax.plot(deltas, F_hertz / 1e3, '--', label='Hertz analytic (half-space)', lw=2)
ax.set_xlabel('press depth δ (m)'); ax.set_ylabel('reaction force F (kN)')
ax.set_title('Force–penetration'); ax.grid(True, alpha=0.4); ax.legend()

ax = axes[1]
ax.semilogy(deltas, max_pen_hist, 'o-', color='C2')
ax.set_xlabel('press depth δ (m)'); ax.set_ylabel('max residual penetration (m)')
ax.set_title('Penalty residual'); ax.grid(True, alpha=0.4)

plt.tight_layout()
plt.savefig('contact_curves.png', dpi=120, bbox_inches='tight')
plt.show()

u_np = u.detach().cpu().numpy()
pts_np = pts.cpu().numpy()

top_pts = pts_np[top_mask.cpu().numpy()]
top_u   = u_np[top_mask.cpu().numpy()]
top_def = top_pts + top_u

fig = plt.figure(figsize=(13, 5))

# 3D dimple
ax1 = fig.add_subplot(121, projection='3d')
sc = ax1.plot_trisurf(top_def[:, 0], top_def[:, 2], top_def[:, 1], cmap='viridis', linewidth=0.1, alpha=0.9)
ax1.set_xlabel('x'); ax1.set_ylabel('z'); ax1.set_zlabel('y (deformed)')
ax1.set_title('Top surface — contact dimple')
ax1.view_init(elev=20, azim=-65)
plt.colorbar(sc, ax=ax1, shrink=0.6, label='y (m)')

# 2D slice along z = Lz/2
ax2 = fig.add_subplot(122)
mid = np.abs(top_pts[:, 2] - Lz / 2) < 0.1
order = np.argsort(top_pts[mid, 0])
ax2.plot(top_pts[mid, 0][order], top_def[mid, 1][order], 'o-', label='deformed surface')
ax2.axhline(Ly, color='k', ls='--', alpha=0.5, label='undeformed')

theta = np.linspace(np.pi/2 - 0.6, np.pi/2 + 0.6, 80)
sphere_y_final = Ly + R_sphere + 1e-3 - delta_max
ax2.plot(cx + R_sphere * np.cos(theta), sphere_y_final - R_sphere * np.sin(theta), color='C3', lw=2, label='sphere (final)')
ax2.set_xlabel('x (m)'); ax2.set_ylabel('y (m)')
ax2.set_xlim(0, Lx); ax2.set_ylim(Ly - 0.15, Ly + 0.55)
ax2.set_aspect('equal')
ax2.set_title('Cross-section at z = Lz/2')
ax2.grid(True, alpha=0.4); ax2.legend()

plt.tight_layout()
plt.savefig('contact_dimple.png', dpi=120, bbox_inches='tight')
plt.show()
