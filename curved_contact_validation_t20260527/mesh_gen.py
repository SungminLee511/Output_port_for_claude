"""
Mesh generators for curved-contact validation cases.

Provides:
  - make_box_tet(...)        : axis-aligned box, tetrahedralized
  - make_icosphere(...)       : geodesic sphere by icosahedron subdivision
                                returns vertices + triangle faces (surface mesh)
  - make_solid_sphere_tet(...) : volumetric sphere via Delaunay tetrahedralization
                                 of icosphere surface + interior points
  - make_plate(...)          : flat rectangular plate (2 tris)
  - make_finger_pad_tet(...) : small flat box (used as robot fingertip pad)

All generators return torch tensors (default device='cpu', dtype=float64) and
the connectivity is right-handed.
"""
import math
import numpy as np
import torch


# -------------------------------------------------------------
# Plate (master surface or flat slave)
# -------------------------------------------------------------
def make_plate(size=2.0, z=0.0, nx=2, ny=2, device="cpu", dtype=torch.float64):
    """
    Flat plate triangulated as a regular grid.
        size : side length (centered at origin in XY)
        z    : Z coordinate of the plate
        nx,ny: number of *cells* per side (>= 1). Vertices = (nx+1)*(ny+1).

    Returns:
        nodes [V, 3], faces [M, 3]
    """
    xs = np.linspace(-size / 2, size / 2, nx + 1)
    ys = np.linspace(-size / 2, size / 2, ny + 1)
    X, Y = np.meshgrid(xs, ys, indexing='xy')
    V = np.stack([X.flatten(), Y.flatten(), np.full(X.size, z)], axis=1)

    faces = []
    for j in range(ny):
        for i in range(nx):
            a = j * (nx + 1) + i
            b = a + 1
            c = a + (nx + 1)
            d = c + 1
            # Two triangles, normals pointing +Z
            faces.append([a, b, d])
            faces.append([a, d, c])
    F = np.array(faces, dtype=np.int64)

    return (torch.tensor(V, device=device, dtype=dtype),
            torch.tensor(F, device=device, dtype=torch.long))


# -------------------------------------------------------------
# Solid box, tetrahedralized
# -------------------------------------------------------------
def make_box_tet(size=(1.0, 1.0, 1.0), center=(0.0, 0.0, 0.5),
                 nx=2, ny=2, nz=2, device="cpu", dtype=torch.float64):
    """
    Axis-aligned solid box, structured grid → 6 tets per voxel.

    Returns:
        nodes [V, 3], elements ['C3D4' : Tensor [M, 4]],
        bottom_nodes (slave candidates, indices of z=zmin),
        top_nodes (force application, indices of z=zmax)
    """
    sx, sy, sz = size
    cx, cy, cz = center
    xs = np.linspace(cx - sx / 2, cx + sx / 2, nx + 1)
    ys = np.linspace(cy - sy / 2, cy + sy / 2, ny + 1)
    zs = np.linspace(cz - sz / 2, cz + sz / 2, nz + 1)

    V = np.zeros(((nx + 1) * (ny + 1) * (nz + 1), 3))
    idx = lambda i, j, k: i + j * (nx + 1) + k * (nx + 1) * (ny + 1)
    for k in range(nz + 1):
        for j in range(ny + 1):
            for i in range(nx + 1):
                V[idx(i, j, k)] = [xs[i], ys[j], zs[k]]

    # 6 tets per cube — Delaunay-compatible decomposition
    tets = []
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):
                n0 = idx(i, j, k)
                n1 = idx(i + 1, j, k)
                n2 = idx(i + 1, j + 1, k)
                n3 = idx(i, j + 1, k)
                n4 = idx(i, j, k + 1)
                n5 = idx(i + 1, j, k + 1)
                n6 = idx(i + 1, j + 1, k + 1)
                n7 = idx(i, j + 1, k + 1)
                # Canonical 6-tet split
                tets += [
                    [n0, n1, n2, n6],
                    [n0, n2, n3, n6],
                    [n0, n3, n7, n6],
                    [n0, n7, n4, n6],
                    [n0, n4, n5, n6],
                    [n0, n5, n1, n6],
                ]
    F = np.array(tets, dtype=np.int64)

    # Slave / boundary node ids
    bottom = [idx(i, j, 0) for j in range(ny + 1) for i in range(nx + 1)]
    top = [idx(i, j, nz) for j in range(ny + 1) for i in range(nx + 1)]

    return (torch.tensor(V, device=device, dtype=dtype),
            {'C3D4': torch.tensor(F, device=device, dtype=torch.long)},
            torch.tensor(bottom, device=device, dtype=torch.long),
            torch.tensor(top, device=device, dtype=torch.long))


# -------------------------------------------------------------
# Icosphere (surface mesh only)
# -------------------------------------------------------------
def _icosahedron():
    """Unit-radius icosahedron, 12 verts, 20 tri faces."""
    phi = (1.0 + math.sqrt(5.0)) / 2.0
    V = np.array([
        [-1,  phi, 0], [1,  phi, 0], [-1, -phi, 0], [1, -phi, 0],
        [0, -1,  phi], [0, 1,  phi], [0, -1, -phi], [0, 1, -phi],
        [phi, 0, -1], [phi, 0, 1], [-phi, 0, -1], [-phi, 0, 1],
    ], dtype=np.float64)
    V = V / np.linalg.norm(V, axis=1, keepdims=True)

    F = np.array([
        [0, 11, 5], [0, 5, 1], [0, 1, 7], [0, 7, 10], [0, 10, 11],
        [1, 5, 9], [5, 11, 4], [11, 10, 2], [10, 7, 6], [7, 1, 8],
        [3, 9, 4], [3, 4, 2], [3, 2, 6], [3, 6, 8], [3, 8, 9],
        [4, 9, 5], [2, 4, 11], [6, 2, 10], [8, 6, 7], [9, 8, 1],
    ], dtype=np.int64)
    return V, F


def make_icosphere(radius=0.5, center=(0.0, 0.0, 0.0), level=2,
                   device="cpu", dtype=torch.float64):
    """
    Generate icosphere by subdividing icosahedron `level` times.
    level=0 → 12 verts, 20 faces
    level=1 → 42 verts, 80 faces
    level=2 → 162 verts, 320 faces
    level=3 → 642 verts, 1280 faces
    """
    V, F = _icosahedron()
    for _ in range(level):
        midpoints = {}
        new_F = []
        V_list = list(V)

        def mid(a, b):
            key = (min(a, b), max(a, b))
            if key in midpoints:
                return midpoints[key]
            m = (V_list[a] + V_list[b]) * 0.5
            m = m / np.linalg.norm(m)
            V_list.append(m)
            midpoints[key] = len(V_list) - 1
            return midpoints[key]

        for tri in F:
            a, b, c = tri
            ab = mid(a, b)
            bc = mid(b, c)
            ca = mid(c, a)
            new_F.extend([
                [a, ab, ca],
                [b, bc, ab],
                [c, ca, bc],
                [ab, bc, ca],
            ])
        V = np.array(V_list)
        F = np.array(new_F, dtype=np.int64)

    V = V * radius + np.array(center)
    return (torch.tensor(V, device=device, dtype=dtype),
            torch.tensor(F, device=device, dtype=torch.long))


# -------------------------------------------------------------
# Solid sphere — tetrahedralize an icosphere with interior points
# -------------------------------------------------------------
def make_solid_sphere_tet(radius=0.5, center=(0.0, 0.0, 0.0), level=1,
                          n_interior_shells=2, device="cpu", dtype=torch.float64):
    """
    Solid sphere: icosphere surface + concentric interior point shells,
    Delaunay-tetrahedralized.

    Returns:
        nodes [V, 3], elements ['C3D4' : Tensor [M, 4]],
        surface_nodes (indices of nodes on outer sphere),
        surface_faces [F, 3] (triangle indices on outer sphere — into nodes array),
        top_nodes (indices of nodes near +z pole, for force application),
        bottom_nodes (indices of nodes near -z pole, for slave selection)
    """
    from scipy.spatial import Delaunay

    V_surf, F_surf = make_icosphere(radius=radius, center=(0, 0, 0), level=level,
                                    device="cpu", dtype=torch.float64)
    V_surf_np = V_surf.numpy()
    F_surf_np = F_surf.numpy()

    # Interior shells: scale outer sphere inward
    pts_list = [V_surf_np]
    for s in range(1, n_interior_shells + 1):
        scale = 1.0 - s / (n_interior_shells + 1)
        # Use fewer points on inner shells via stride
        if scale < 0.3:
            # Center single point
            pts_list.append(np.array([[0.0, 0.0, 0.0]]))
        else:
            # Take every other vertex
            stride = max(1, s)
            pts_list.append(V_surf_np[::stride] * scale)
    V_np = np.unique(np.concatenate(pts_list, axis=0), axis=0)

    # Delaunay tetrahedralization
    delaunay = Delaunay(V_np)
    tets = delaunay.simplices.astype(np.int64)

    # Filter degenerate tets (volume threshold)
    p0 = V_np[tets[:, 0]]; p1 = V_np[tets[:, 1]]; p2 = V_np[tets[:, 2]]; p3 = V_np[tets[:, 3]]
    vol = np.abs(np.einsum('ij,ij->i', np.cross(p1 - p0, p2 - p0), p3 - p0)) / 6.0
    tets = tets[vol > 1e-9]

    # Ensure right-handed (signed volume > 0)
    sv = np.einsum('ij,ij->i', np.cross(p1 - p0, p2 - p0), p3 - p0)[vol > 1e-9]
    flip = sv < 0
    tets[flip] = tets[flip][:, [0, 2, 1, 3]]

    # Map original surface verts to new indices in V_np
    # (since np.unique can reorder), we rebuild by spatial match
    surf_node_map = []
    for v in V_surf_np:
        d = np.linalg.norm(V_np - v, axis=1)
        surf_node_map.append(int(np.argmin(d)))
    surf_node_map = np.array(surf_node_map, dtype=np.int64)

    # Surface faces in new indexing
    F_remapped = surf_node_map[F_surf_np]
    surface_nodes = np.unique(F_remapped.flatten())

    # Translate to center
    V_np = V_np + np.array(center)

    # Top / bottom nodes (poles)
    z = V_np[:, 2]
    z_max = z.max()
    z_min = z.min()
    top = np.where(z > z_max - 0.1 * radius)[0]
    bot = np.where(z < z_min + 0.1 * radius)[0]

    return (
        torch.tensor(V_np, device=device, dtype=dtype),
        {'C3D4': torch.tensor(tets, device=device, dtype=torch.long)},
        torch.tensor(surface_nodes, device=device, dtype=torch.long),
        torch.tensor(F_remapped, device=device, dtype=torch.long),
        torch.tensor(top, device=device, dtype=torch.long),
        torch.tensor(bot, device=device, dtype=torch.long),
    )


# -------------------------------------------------------------
# Robot finger pad (small flat box)
# -------------------------------------------------------------
def make_finger_pad_tet(size=(0.6, 0.6, 0.2), center=(0, 0, 0),
                        nx=2, ny=2, nz=1, device="cpu", dtype=torch.float64):
    """
    A small box used as a robot fingertip pad. Same as make_box_tet but
    returns +x face nodes (toward target) and -x face nodes (back, for grip force).
    """
    sx, sy, sz = size
    cx, cy, cz = center
    xs = np.linspace(cx - sx / 2, cx + sx / 2, nx + 1)
    ys = np.linspace(cy - sy / 2, cy + sy / 2, ny + 1)
    zs = np.linspace(cz - sz / 2, cz + sz / 2, nz + 1)

    V = np.zeros(((nx + 1) * (ny + 1) * (nz + 1), 3))
    idx = lambda i, j, k: i + j * (nx + 1) + k * (nx + 1) * (ny + 1)
    for k in range(nz + 1):
        for j in range(ny + 1):
            for i in range(nx + 1):
                V[idx(i, j, k)] = [xs[i], ys[j], zs[k]]

    tets = []
    for k in range(nz):
        for j in range(ny):
            for i in range(nx):
                n0 = idx(i, j, k); n1 = idx(i + 1, j, k); n2 = idx(i + 1, j + 1, k)
                n3 = idx(i, j + 1, k); n4 = idx(i, j, k + 1); n5 = idx(i + 1, j, k + 1)
                n6 = idx(i + 1, j + 1, k + 1); n7 = idx(i, j + 1, k + 1)
                tets += [
                    [n0, n1, n2, n6], [n0, n2, n3, n6], [n0, n3, n7, n6],
                    [n0, n7, n4, n6], [n0, n4, n5, n6], [n0, n5, n1, n6],
                ]
    F = np.array(tets, dtype=np.int64)

    plus_x = [idx(nx, j, k) for k in range(nz + 1) for j in range(ny + 1)]
    minus_x = [idx(0, j, k) for k in range(nz + 1) for j in range(ny + 1)]

    return (torch.tensor(V, device=device, dtype=dtype),
            {'C3D4': torch.tensor(F, device=device, dtype=torch.long)},
            torch.tensor(plus_x, device=device, dtype=torch.long),
            torch.tensor(minus_x, device=device, dtype=torch.long))


# -------------------------------------------------------------
# Helper to extract triangular boundary surface of a tet mesh
# -------------------------------------------------------------
def extract_tet_boundary_faces(tets):
    """
    Given a tet connectivity [M, 4], return the boundary triangles [F, 3]
    (faces appearing exactly once across the mesh).
    """
    tets_np = tets.cpu().numpy() if isinstance(tets, torch.Tensor) else tets
    # All 4 faces per tet (each as sorted-tuple for hashing)
    face_table = {}
    face_list = []
    for t in tets_np:
        for tri in ([t[0], t[1], t[2]], [t[0], t[1], t[3]],
                    [t[0], t[2], t[3]], [t[1], t[2], t[3]]):
            key = tuple(sorted(tri))
            face_table[key] = face_table.get(key, 0) + 1
            face_list.append((key, tri))
    boundary = []
    seen = set()
    for key, tri in face_list:
        if face_table[key] == 1 and key not in seen:
            seen.add(key)
            boundary.append(tri)
    return np.array(boundary, dtype=np.int64)


# -------------------------------------------------------------
# Mesh visualization helper (matplotlib 3D)
# -------------------------------------------------------------
def plot_meshes_3d(meshes, slave_nodes=None, master_faces=None,
                   title="", save_path=None, elev=20, azim=-60):
    """
    meshes: list of dicts: {'nodes': [V,3], 'tris': [F,3], 'color': str, 'alpha': float, 'name': str}
    slave_nodes: optional list of (nodes, indices) tuples (red dots)
    master_faces: optional list of (nodes, faces) tuples (highlight)
    """
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection

    fig = plt.figure(figsize=(7, 6))
    ax = fig.add_subplot(111, projection='3d')

    for m in meshes:
        V = m['nodes'].cpu().numpy() if isinstance(m['nodes'], torch.Tensor) else m['nodes']
        F = m['tris'].cpu().numpy() if isinstance(m['tris'], torch.Tensor) else m['tris']
        polys = [V[face] for face in F]
        coll = Poly3DCollection(polys, alpha=m.get('alpha', 0.4),
                                facecolor=m.get('color', 'C0'),
                                edgecolor='k', linewidth=0.2)
        ax.add_collection3d(coll)

    if slave_nodes is not None:
        for V, idx in slave_nodes:
            V = V.cpu().numpy() if isinstance(V, torch.Tensor) else V
            idx = idx.cpu().numpy() if isinstance(idx, torch.Tensor) else idx
            ax.scatter(V[idx, 0], V[idx, 1], V[idx, 2], c='red', s=18, label='slave', zorder=5)

    # Auto-extent
    all_V = np.concatenate([m['nodes'].cpu().numpy() if isinstance(m['nodes'], torch.Tensor)
                            else m['nodes'] for m in meshes], axis=0)
    mins = all_V.min(0); maxs = all_V.max(0)
    span = (maxs - mins).max() * 0.55
    mid = (mins + maxs) / 2
    ax.set_xlim(mid[0] - span, mid[0] + span)
    ax.set_ylim(mid[1] - span, mid[1] + span)
    ax.set_zlim(mid[2] - span, mid[2] + span)
    ax.set_xlabel('x'); ax.set_ylabel('y'); ax.set_zlabel('z')
    ax.set_title(title)
    ax.view_init(elev=elev, azim=azim)
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=130, bbox_inches='tight')
        print(f"  Saved: {save_path}")
    plt.close()


if __name__ == "__main__":
    print("=== Self-test mesh_gen.py ===")
    V, F = make_plate(size=2.0, z=0.0, nx=3, ny=3)
    print(f"plate: V={V.shape}, F={F.shape}")

    V, E, bot, top = make_box_tet(size=(1, 1, 1), center=(0, 0, 0.5), nx=2, ny=2, nz=2)
    print(f"box: V={V.shape}, tets={E['C3D4'].shape}, bottom={bot.shape}, top={top.shape}")

    V, F = make_icosphere(radius=0.5, level=2)
    print(f"icosphere lvl2: V={V.shape}, F={F.shape}")

    V, E, sn, sf, top, bot = make_solid_sphere_tet(radius=0.5, level=1, n_interior_shells=2)
    print(f"solid sphere: V={V.shape}, tets={E['C3D4'].shape}, surf={sn.shape}, surf_F={sf.shape}, top={top.shape}, bot={bot.shape}")
