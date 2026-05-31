import time, warnings
warnings.filterwarnings('ignore')
import torch
import numpy as np
import matplotlib.pyplot as plt

from tensormesh import Condenser, ElementAssembler, MassElementAssembler, Mesh, NodeAssembler
from tensormesh.sparse import SparseMatrix

torch.set_default_dtype(torch.float64)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print('device:', device)
if device.type == 'cuda':
    print('GPU:', torch.cuda.get_device_name(0))

class CurlCurl(ElementAssembler):
    def forward(self, gradu, gradv):
        z = torch.zeros_like(gradu[0])
        cu = torch.stack((torch.stack((z, -gradu[2], gradu[1])),
                          torch.stack((gradu[2], z, -gradu[0])),
                          torch.stack((-gradu[1], gradu[0], z))))
        cv = torch.stack((torch.stack((z, -gradv[2], gradv[1])),
                          torch.stack((gradv[2], z, -gradv[0])),
                          torch.stack((-gradv[1], gradv[0], z))))
        return cu.T @ cv


class DivStab(ElementAssembler):
    def __post_init__(self, h2=1.0):
        self.h2 = h2
    def forward(self, gradu, gradv):
        return self.h2 * torch.outer(gradu, gradv)


class PressStab(ElementAssembler):
    def forward(self, gradu, gradv):
        return gradu @ gradv


class PressCoupling(ElementAssembler):
    def __post_init__(self):
        self.component = 0
    def forward(self, u, gradv):
        return u * gradv[self.component]
    def __call__(self, *args, **kwargs):
        mats = []
        for c in range(self.dimension):
            self.component = c
            mats.append(super().__call__(*args, **kwargs))
        n_points = mats[0].shape[0]
        return SparseMatrix(
            -torch.cat([m.edata for m in mats]),
            torch.cat([self.dimension * m.row + c for c, m in enumerate(mats)]),
            torch.cat([m.col for m in mats]),
            shape=(self.dimension * n_points, n_points),
        )


class VectorLoad(NodeAssembler):
    def forward(self, v, f):
        return v * f


class CurlProjection(NodeAssembler):
    def forward(self, v, gradA):
        return v * torch.stack((gradA[2, 1] - gradA[1, 2],
                                gradA[0, 2] - gradA[2, 0],
                                gradA[1, 0] - gradA[0, 1]))

print('Assembler classes defined.')

def current_source(points, cx, cy, radius, J0):
    dx = points[:, 0] - cx; dy = points[:, 1] - cy
    mag = J0 * torch.exp(-(dx ** 2 + dy ** 2) / (2 * radius ** 2))
    return torch.stack([torch.zeros_like(mag), torch.zeros_like(mag), mag], dim=1)


def tangential_mask(points, atol=1e-9):
    x, y, z = points[:, 0], points[:, 1], points[:, 2]
    on_x = (x.abs() < atol) | ((x - 1).abs() < atol)
    on_y = (y.abs() < atol) | ((y - 1).abs() < atol)
    on_z = (z.abs() < atol) | ((z - 1).abs() < atol)
    return torch.stack([on_y | on_z, on_x | on_z, on_x | on_y], dim=1).flatten().contiguous()


chara_length = 0.08
mesh = Mesh.gen_cube(chara_length=chara_length, order=1).double().to(device)
n_points = mesh.n_points
points = mesh.points
print(f'Mesh: {n_points} nodes, {mesh.n_elements} elements')

J0 = 100.0
current = current_source(points, 0.5, 0.5, radius=0.08, J0=J0)
print(f'Current peak: {current.norm(dim=1).max().item():.2f}')

h2 = chara_length ** 2

t0 = time.time()
A_block = CurlCurl.from_mesh(mesh).to(device)()
Su      = DivStab.from_mesh(mesh, h2=h2).to(device)()
Sp      = PressStab.from_mesh(mesh).to(device)()
B_block = PressCoupling.from_mesh(mesh).to(device)()
if device.type == 'cuda':
    torch.cuda.synchronize()
print(f'Assembly time: {time.time()-t0:.2f} s')

K = SparseMatrix.combine([
    [A_block + Su,  B_block],
    [-1.0 * B_block.T, Sp],
])
print(f'K shape : {K.shape},  nnz = {K.values.numel()}')

rhs_u = VectorLoad.from_mesh(mesh).to(device)(point_data={'f': current}, batch_size=-1)
rhs_p = torch.zeros(n_points, dtype=points.dtype, device=device)
rhs = torch.cat([rhs_u, rhs_p])
print(f'RHS shape: {rhs.shape}')

dmask = torch.cat([tangential_mask(points), mesh.boundary_mask])
print(f'Dirichlet DOFs: {int(dmask.sum())} / {dmask.numel()}')

cond = Condenser(dmask, torch.zeros_like(rhs)).to(device)
K_red, rhs_red = cond(K, rhs)
print(f'K_red shape: {K_red.shape}')

t0 = time.time()
sol = cond.recover(K_red.solve(rhs_red, backend='cudss', method='lu', verbose=False))
if device.type == 'cuda':
    torch.cuda.synchronize()
print(f'Sparse solve: {time.time()-t0:.2f} s')

A = sol[:3 * n_points].reshape(n_points, 3)
print(f'||A||_inf = {A.abs().max().item():.4e}')

M = MassElementAssembler.from_mesh(mesh).to(device)()
curl_rhs = CurlProjection.from_mesh(mesh).to(device)(point_data={'A': A}, batch_size=-1).reshape(n_points, 3)
t0 = time.time()
B = torch.stack([M.solve(curl_rhs[:, c], backend='cudss', method='lu', verbose=False) for c in range(3)], dim=1)
if device.type == 'cuda':
    torch.cuda.synchronize()
print(f'L2-projection (3 components): {time.time()-t0:.2f} s')
print(f'||B||_inf = {B.abs().max().item():.4e}')

pts_np = points.cpu().numpy()
A_np = A.cpu().numpy()
B_np = B.cpu().numpy()
J_np = current.cpu().numpy()

slab = np.abs(pts_np[:, 2] - 0.5) < chara_length * 0.6
print(f'Mid-z slab nodes: {slab.sum()}')

fig, axes = plt.subplots(1, 3, figsize=(15, 5))

ax = axes[0]
sc = ax.scatter(pts_np[slab, 0], pts_np[slab, 1], c=np.linalg.norm(J_np[slab], axis=1), cmap='inferno', s=22)
plt.colorbar(sc, ax=ax, label='|J|', shrink=0.85)
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_aspect('equal')
ax.set_title('Current density |J|')

ax = axes[1]
sc = ax.scatter(pts_np[slab, 0], pts_np[slab, 1], c=np.linalg.norm(A_np[slab], axis=1), cmap='viridis', s=22)
plt.colorbar(sc, ax=ax, label='|A|', shrink=0.85)
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_aspect('equal')
ax.set_title('Vector potential |A|')

ax = axes[2]
B_xy = B_np[slab][:, :2]
scale = max(np.linalg.norm(B_xy, axis=1).max() * 12, 1e-6)
ax.quiver(pts_np[slab, 0], pts_np[slab, 1], B_xy[:, 0], B_xy[:, 1], scale=scale, width=0.004)
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.set_aspect('equal')
ax.set_title('Magnetic field B = ∇ × A')

plt.suptitle('3D Magnetostatics — z = 0.5 slice', y=1.02)
plt.tight_layout()
plt.savefig('maxwell_slice.png', dpi=120, bbox_inches='tight')
plt.show()

mid = slab
r = np.linalg.norm(pts_np[mid, :2] - np.array([0.5, 0.5]), axis=1)
B_az = np.abs(B_np[mid, 0] * (-(pts_np[mid, 1] - 0.5) / np.maximum(r, 1e-9)) +
              B_np[mid, 1] * ((pts_np[mid, 0] - 0.5) / np.maximum(r, 1e-9)))

# Bin
bins = np.linspace(0.0, 0.5, 14)
mids, vals = [], []
for i in range(len(bins) - 1):
    sel = (r >= bins[i]) & (r < bins[i + 1])
    if sel.sum() > 2:
        mids.append(0.5 * (bins[i] + bins[i + 1]))
        vals.append(B_az[sel].mean())

fig, ax = plt.subplots(figsize=(7, 4.5))
ax.plot(mids, vals, 'o-', label='TensorMesh (azimuthal mean)')
# Analytic 1/r scaled to fit far-field
r_fit = np.array(mids[-3:])
b_fit = np.array(vals[-3:])
C = (r_fit * b_fit).mean()
ax.plot(mids, C / np.array(mids), '--', color='C3', label=f'1/r fit  (B ≈ {C:.3f}/r)')
ax.set_xlabel('r from wire centerline'); ax.set_ylabel('azimuthal |B|')
ax.set_title('Magnetic field magnitude vs radius'); ax.grid(True, alpha=0.4); ax.legend()
plt.tight_layout()
plt.savefig('maxwell_ampere.png', dpi=120, bbox_inches='tight')
plt.show()
