# TensorMesh — Complete API Reference

> A fast, differentiable, JIT-free, debugging-friendly finite element library for PyTorch.
> Source: https://github.com/camlab-ethz/TensorMesh (Apache-2.0). Version `0.1.1`.

This document maps out **every public symbol** of TensorMesh and what it can do, organized module by module. It is exhaustive — every assembler, every solver backend, every mesh generator, every visualization helper.

---

## 0. What can TensorMesh actually do?

### Capabilities (built from the source + example gallery)
- **PDEs** — Poisson, Laplace, heat (parabolic), wave (hyperbolic), Allen–Cahn phase field, magnetostatics (Maxwell, stabilized nodal curl-curl), Helmholtz (planned).
- **Solid mechanics** — small-strain linear elasticity, Neo-Hookean hyperelasticity, J2 (von Mises) plasticity with isotropic hardening, penalty-based contact, Hertzian contact, large-deformation Newton solves, modal/eigen analyses.
- **Fluid mechanics** — incompressible Navier-Stokes (lid-driven cavity, cylinder flow, flow past obstacles), Rayleigh-Bénard, Taylor-Green vortex.
- **Inverse design / optimization** — coefficient-field identification, density-based topology optimization (compliance, thermal), Optimality Criteria (OC) and (separate) MMA optimizer; everything autograd-traced end to end.
- **Physics-informed ML** — train a neural network to minimize the assembled Galerkin residual.
- **Dataset generation** — large batches of analytical / FEM-solved Poisson, Heat, Wave, Linear Elasticity samples for ML training.
- **Distributed multi-GPU assembly** — element-partition + ghost-node + threaded local assembly + global scatter via `torch-sla`'s `DSparseTensor`.
- **h-adaptivity, mesh I/O**, **graph coloring / partitioning**, **mixed-element meshes** (e.g. triangles + quads in the same domain), **high-order elements up to p=10**.
- **End-to-end autograd** through assembly + sparse solve + condensation, on CPU and GPU, with multiple solver backends (`scipy`, `eigen`, `pytorch`, `cupy`, `cudss`, `petsc`, `pyamg`).

### High-level workflow
**`Mesh → Assembler → SparseMatrix → Condenser → Solve`**

```python
import math, torch
from tensormesh import ElementAssembler, NodeAssembler, Mesh, Condenser

mesh = Mesh.gen_rectangle(chara_length=0.05)

class Laplace(ElementAssembler):
    def forward(self, gradu, gradv):
        return gradu @ gradv

class Source(NodeAssembler):
    def forward(self, v, f):
        return f * v

x, y = mesh.points[:, 0], mesh.points[:, 1]
f_vals = 2 * math.pi**2 * torch.sin(math.pi * x) * torch.sin(math.pi * y)

K = Laplace.from_mesh(mesh)()
b = Source.from_mesh(mesh)(point_data={"f": f_vals})

cond = Condenser(mesh.boundary_mask)
K_, b_ = cond(K, b)
u_ = K_.solve(b_)
u = cond.recover(u_)
```

Move to GPU with `mesh = mesh.cuda()`; enable inverse problems with `mesh.points.requires_grad_(True)`.

### Package import surface (top-level `tensormesh.__init__`)
```python
Mesh, Condenser
ElementAssembler, NodeAssembler, FacetAssembler
LaplaceElementAssembler, MassElementAssembler, LinearElasticityElementAssembler
const_node_assembler, func_node_assembler
Transformation, Element
Line, Triangle, Quadrilateral, Tetrahedron, Hexahedron, Prism, Pyramid
element_type2order, element_type2dimension, element_type2element, element_types
DistributedMesh, distributed_element_assemble, distributed_element_assemble_to_sparse, distributed_node_assemble
MeshGen
from .functional import *
__version__
```

---

## 1. `tensormesh.mesh`

### 1.1 `tensormesh.Mesh` *(nn.Module)*

FEM mesh — interpolation-node coordinates, per-element-type connectivity, and per-point / per-cell / global field data. Mixed-element meshes are supported via `cells` being a `BufferDict` keyed by element-type string.

#### Constructor
```python
Mesh(mesh: meshio.Mesh, reorder: bool = False)
```
- `reorder`: convert connectivity from Gmsh/VTK order → internal lex order via `Element.reorder`.
- Boolean point/cell/field arrays whose key starts with `is_` or ends with `_mask` are auto-converted to `bool`.

#### Attributes
| Name | Type | Description |
|---|---|---|
| `points` | `torch.Tensor [\|V\|, D]` | interpolation-node coordinates (includes high-order nodes when p≥2) |
| `cells` | `BufferDict[str, LongTensor [\|C_e\|, B_e]]` | element connectivity per element-type |
| `point_data` | `BufferDict[str, Tensor]` | per-point fields |
| `cell_data` | `nn.ModuleDict[str, BufferDict[str, Tensor]]` | per-element fields (outer key = element type) |
| `field_data` | `BufferDict[str, Tensor]` | global named fields |
| `cell_sets` | `dict` | meshio's native cell-set dict |
| `dim2eletyp` | `Dict[int, List[str]]` | dimension → list of element-type strings |
| `default_eletyp` | `str` or `List[str]` | element type(s) of highest spatial dimension |

#### Properties
- `dim → int` — spatial dimension (`2` or `3`).
- `dtype → torch.dtype` — floating dtype of `points`.
- `device → torch.device`.
- `n_points → int` — `|V|`.
- `n_elements → int` — total elements over `default_element_type`.
- `boundary_mask → Tensor [bool, |V|]` — reads `point_data["is_boundary"]` or `"boundary_mask"`.
- `default_element_type → str | List[str]` — alias for `default_eletyp`.

#### Methods
- `register_point_data(key, value) → self` — register a per-point buffer.
- `register_element_data(key, value: Tensor | Dict[str,Tensor]) → self`.
- `to_meshio(reorder=False) → meshio.Mesh`.
- `save(file_name, file_format=None) → self` *(alias `to_file`)* — writes via meshio. For `.vtk/.vtu`, pads to 3D and reorders to Gmsh/VTK.
- `clone() → Mesh` — autograd-preserving deep copy (round-trips through meshio).
- `node_adjacency(element_type=None) → SparseMatrix` — `[|V|,|V|]` adjacency (fully-connected within each element).
- `element_adjacency(element_type=None) → SparseMatrix` — `[|C|,|C|]` adjacency through shared facets.
- `partition(n_parts, method='spectral', element_type=None) → Tensor[long, n_elements]` — methods: `'spectral'`, `'metis'`.
- `color(element_type=None) → Tensor[long, n_elements]` — greedy GPU graph coloring.
- `elements(element_type=None) → Tensor | Dict[str, Tensor]` — flexible getter:
  - `None` → default element(s); `"all"` → dict of all; `int` → all of that dimension (`-1` = `self.dim`); `str` → single; `Iterable[str]` → dict subset.
- `plot(values=None, save_path=None, dt=None, show_mesh=False, fix_clim=False, show=False, **kwargs)`:
  - no `values` → wireframe;
  - dict of `[|V|]` tensors → multi-panel static image;
  - dict of lists / 2D tensors → mp4/gif animation (frames per list entry).
- `__repr__`, `__str__` — pretty dump of shapes / dtypes.

#### Class methods (constructors)
- `from_meshio(mesh, reorder=False) → Mesh`
- `read(file_name, file_format=None, reorder=False) → Mesh` *(alias `from_file`)*.

#### Static methods (built-in generators — delegate to `tensormesh.dataset`)
All accept `chara_length=0.1`, `order=1`, `visualize=False`, `cache_path=None`; gmsh-backed; cached `.msh` in `.gmsh_cache/`.

| Method | Signature highlights |
|---|---|
| `gen_rectangle` | `element_type="tri"`, `left/right/bottom/top` |
| `gen_hollow_rectangle` | `element_type="quad"`, outer + inner bounds |
| `gen_circle` | `element_type="tri"`, `cx, cy, r` |
| `gen_hollow_circle` | `element_type="quad"`, `cx, cy, r_inner, r_outer` |
| `gen_L` | `element_type="quad"`, `left, right, bottom, top, top_inner, right_inner` |
| `gen_cube` | `left, right, bottom, top, front, back` (always tetrahedral) |
| `gen_hollow_cube` | outer + inner box bounds |
| `gen_sphere` | `cx, cy, cz, r` |
| `gen_hollow_sphere` | `cx, cy, cz, r_inner, r_outer` |

Each populates `point_data["is_boundary"]` plus geometric face/edge sub-masks (e.g. `is_left_boundary`, `is_outer_top_boundary`, `is_inner_boundary`, …).

### 1.2 `tensormesh.mesh.coloring.graph_coloring`
```python
graph_coloring(adjacency: SparseMatrix, max_iter: int = 100) → LongTensor
```
GPU-parallel randomized Jones–Plassmann-style coloring. Conflict edges recolored from `[0, 6 + i//5)` palette. Aims at ~5–8 colors for planar graphs.

### 1.3 `tensormesh.mesh.partition.graph_partition`
```python
graph_partition(adjacency: SparseMatrix, n_parts: int, method: str = 'spectral') → LongTensor
```
Methods:
- `'spectral'` — recursive Fiedler-vector bisection; dense `eigh` for blocks <2048, `torch.lobpcg` otherwise.
- `'metis'` — `pymetis.part_graph`; falls back to spectral if `pymetis` missing.

### 1.4 `tensormesh.mesh.partition.partition_mesh`
```python
partition_mesh(mesh, n_parts, method='coordinate', ghost_nodes=True) → List[Optional[Mesh]]
```
Element-partition with ghost nodes. Methods: `'coordinate'` (RCB), `'spectral'`, `'metis'`. Each submesh gets `point_data["orig_nid"]` = global node IDs.

### 1.5 `tensormesh.mesh.adjacency` (low-level helpers)
- `cum_dict(d) → Dict[str, (start, end)]`
- `dense_connect(x) → Tensor [2, n_batch * n_node²]` — all-pairs within each row.
- `coalesce(edges, n_points) → Tensor` — dedupe edge columns via sparse coalesce.
- `facet_connect(facet, element_ids) → Tensor [2, 2 * n_shared_facets]`.
- `node_adjacency(elements, n_points) → SparseMatrix`
- `element_adjacency(elements: Dict[str, Tensor]) → SparseMatrix`

---

## 2. `tensormesh.element`

Public symbols (re-exported from `tensormesh.element.__init__`):
```
Element, Line, Triangle, Quadrilateral, Tetrahedron, Hexahedron, Prism, Pyramid
Transformation, Polynomial, Polynomials
element_type2dimension, element_type2order, element_type2element, element_types
```

### 2.1 Element classes (used as classes, not instances — all methods are class methods)

Common class attributes: `dim`, `n_vertex`, `n_edge`, `n_face`, `n_cell`, `points: Tensor [V, D]`, `vertex`, `edge`, `face`, `cell`, `is_mix_facet: bool` (only `Pyramid` and `Prism` are mixed).

| Class | string prefix | dim | facet type(s) | poly space | element-type strings (orders) |
|---|---|---|---|---|---|
| `Line` | `line` | 1 | — | tensor | `line, line3..line11` (1–10) |
| `Triangle` | `triangle` | 2 | `Line` | simplex | `triangle, triangle6, …, triangle66` (1–10) |
| `Quadrilateral` | `quad` | 2 | `Line` | tensor | `quad, quad8, quad9, …, quad121` (1–10) |
| `Tetrahedron` | `tetra` | 3 | `Triangle` | simplex | `tetra, tetra10, …, tetra286` (1–10) |
| `Hexahedron` | `hexahedron` | 3 | `Quadrilateral` | tensor | `hexahedron, hex20, hex27, …, hex1000` (1–9 + 20-node serendipity) |
| `Pyramid` | `pyramid` | 3 | `(Triangle, Quadrilateral)` | `pyr_exp` | `pyramid, pyramid14` (1–2) |
| `Prism` (wedge) | `wedge` | 3 | `(Triangle, Quadrilateral)` | `pri_exp` | `wedge, wedge18, …, wedge550` (1–9) |

Class methods (all):
- `reorder(elements, to_gmsh=True) → Tensor` — permute connectivity between TensorMesh internal (lex) ⇄ Gmsh/VTK ordering.
- `get_gmsh_permutation(n_nodes, device='cpu') → LongTensor`.
- `get_facet_type() → Type[Element] | Tuple[Type[Element], Type[Element]]`.
- `get_n_facet() → int` (edges if 2D, faces if 3D).
- `get_n_basis(order=1) → int`.
- `get_tri_mask() / get_quad_mask() → Tensor[bool, n_face]` (only when `is_mix_facet`).
- `get_contour(order) → LongTensor` (2D boundary CCW; Triangle/Quadrilateral only).
- Basis / poly / quadrature: `get_basis(order=1, dtype, device)`, `get_facet(order=1)`, `get_edge(order)`, `get_polynomial(order, dtype, device)`, `get_quadrature(order, dtype, device)`, `get_facet_quadrature(order, transform=True, dtype, device)`, `get_basis_fns(order, dtype, device)`, `get_basis_grad_fns(order, dtype, device)`.
- Jacobian: `eval_cell_jacobian(quadrature, element_coords, basis_order)`, `eval_shape_val(...)`, `eval_shape_grad(element_coords, ...)`, `eval_facet_cell_jacobian(...)`, `eval_facet_jacobian(...)`.
- Facet-mapping polynomials / normals: `get_local_facet_mapping_fns`, `get_local_facet_mapping_grad_fns`, `get_outwards_facet_normal`.
- Connectivity remapping: `element_to_facet(elements, order)`, `element_to_edge(elements, order, unique=True)`.

### 2.2 `tensormesh.element.Transformation` *(nn.Module)*

The geometric machinery for one element-type block of a mesh. Caches Jacobians, shape values, shape gradients, and facet quantities lazily as buffers (so they follow `.to()`, `.cuda()`, `.double()`).

```python
Transformation(points: Tensor, elements: Tensor, element_type: str, quadrature_order: int = 2)
```

Cached lazily as properties (also registered as buffers when accessed):
| Property | Shape |
|---|---|
| `shape_val` *(alias `phi`)* | `[N_q, N_b]` |
| `shape_grad` *(alias `gradphi`)* | `[N_e, N_q, N_b, D]` |
| `jacobian` *(alias `J`, `G`)* | `[N_e, N_q, D, D]` |
| `detJ`, `JxW` *(alias `GxW`)* | `[N_e, N_q]` |
| `facets`, `facet_quadrature`, `facet_shape_val`, `facet_shape_grad`, `facet_jacobian` *(alias `F`)* | per-facet shapes |
| `nanson_scale` *(alias `n`)*, `detF`, `FxW` | facet integration weights |

Methods:
- `update_points(points)` — replace coordinates for moving-mesh / optimization; reuses connectivity.
- `batch_quadrature(start, batch)`, `batch_elements_coords(start, batch)`, `batch_shape_val(start, batch)`, `batch_shape_grad_jxw(element_start=0, element_batch=-1, quadrature_start=0, quadrature_batch=-1)`.

### 2.3 `tensormesh.element.Polynomial` / `Polynomials` *(nn.Module)*

Multivariate polynomial(s) with buffers `_coef` and `_exp`. Public methods: `forward(x)`, `get_exp_terms(x)`, `deriv(var_ind=0)`, `grad()`, `reset_coef(coef)`, `repeat(*args)`, plus `Polynomials.stack(...)`, `reshape`, `transpose`, `map`, `map_exp_terms`.

Classmethods (polynomial-space factories on `Polynomial`):
- `lin_exp(n_vars, dtype, device)` — constant + 1 linear term per var.
- `poly_exp(n_vars, dim, dtype, device)` — simplex space (deg≤dim).
- `tens_exp(n_vars, dim, dtype, device)` — tensor product `(dim+1)**n_vars`.
- `pyr_exp(order, dtype, device)` — pyramid space.
- `pri_exp(order, dtype, device)` — prism space.

### 2.4 Element-type lookup tables
- `element_type2dimension: Dict[str, int]` (61 keys; `vertex=0`, `line=1`, etc.)
- `element_type2order: Dict[str, int]` (same key set)
- `element_types: List[str]` — canonical list of every recognized type string.
- `element_type2element(x: str) → Type[Element]` — dispatches via alphabetic prefix.

### 2.5 Internal / supporting modules
- `tensormesh.element.quadrature` — `lin/tri/tet/quad/hex/pyr/pri_quadrature(order, dtype, device)` returning `(weights, points)`. Orders 1–7 supported across all rules. Plus facet rules `facet_quadrature_2d`, `tet_facet_quadrature`, `hex_facet_quadrature`, `mix_facet_quadrature_3d`.
- `tensormesh.element.basis` — reference-element node generators & facet-index helpers (`lin_basis, tri_basis, quad_basis, tet_basis, hex_basis, pyr_basis, pri_basis`, plus `facet_basis_index_2d`, `tet_facet_basis_index`, `hex_facet_basis_index`, `mix_facet_basis_index`, `edge_index`).
- `tensormesh.element.normal` — `outwards_normal_2d(points, edges)`, `outwards_normal_3d(points, faces)`.
- `tensormesh.element.plot` — `plot_1d`, `plot_2d`, `plot_3d` (basis-function visualization).
- `tensormesh.element.types` — `Tensorx1 … Tensorx5`, `Tuple2DInt` typing aliases.

---

## 3. `tensormesh.assemble`

Three base classes plus a ready-made physics module.

### 3.1 `tensormesh.ElementAssembler` *(nn.Module — abstract)*

Assemble bilinear form `a(u,v) = ∫_Ω f(u,v) dΩ` into a global sparse matrix. Subclass and override `forward` (and optionally `element_energy` for energy-based variational problems).

**Forward signature options** (any subset of these kwargs the base class infers from `forward`'s parameter names):
- `u, v` — shape value (0D `[]`).
- `gradu, gradv` — physical shape gradient (1D `[D]`).
- `x` — physical coordinate (`[D]`).
- `gradx` — `[D, D]` (∂x / ∂ξ).
- any `point_data` key → value at quad point; `"grad" + key` → gradient.

**Return shape**: `[B, B]` scalar problems or `[B, B, H, H]` vector problems (H = DOFs per node).

**Public methods**:
- `__call__(points=None, func=None, point_data=None, element_data=None, scalar_data=None, batch_size=-1) → SparseMatrix`.
- `energy(...) → Tensor` (scalar) — integrate `element_energy` over the domain; useful for hyperelastic / phase-field; differentiable; `.backward()` gives internal force.
- `element_energy(**kwargs)` — override for energy-based forms (returns scalar).
- `__post_init__(*args, **kwargs)` — override to store extra constructor data.
- `type(dtype)` — cast to `float32` / `float64` (returns self).

**Constructors**:
- `from_mesh(mesh, quadrature_order=2, project='reduce', *args, **kwargs)` *(classmethod)*
- `from_assembler(obj, *args, **kwargs)` — share projector/transformation/edges of an existing assembler (cheap).

### 3.2 `tensormesh.NodeAssembler` *(nn.Module — abstract)*

Assemble linear form `l(v) = ∫_Ω f(v) dΩ` into a global vector.

**Forward kwargs**: `v, gradv, x, gradx, <point_data_key>, grad<point_data_key>`. Returns `[B]` or `[B, H]`.

**Methods**:
- `__call__(points=None, func=None, point_data=None, scalar_data=None, batch_size=1) → Tensor`.
- `compile(mode='disable', fullgraph=False, dynamic=None, backend='inductor', **kwargs)` — enable vmap-free fast path. Modes: `'disable'` (recommended, just vmap bypass), or any `torch.compile` mode (`'default'`, `'reduce-overhead'`, `'max-autotune'`, …). Up to 5–30× speedup.
- `flat_mode()` — alias for `compile('disable')`.
- `reset_compile()` — disable fast path.
- `type(dtype)`.

**Constructors**:
- `from_mesh(mesh, quadrature_order=2, project='reduce', *args, **kwargs)`
- `from_elements(points, elements: Dict[str, Tensor], quadrature_order=2, device='cpu', dtype=torch.float32, project='reduce', *args, **kwargs)`
- `from_assembler(obj, *args, **kwargs)`.

### 3.3 `tensormesh.FacetAssembler` *(nn.Module — abstract)*

Boundary-integral assembler. Handles mixed (tri+quad) facets on pyramids / prisms.

**Forward kwargs** keep the basis dimension intact: `u, v` are 1D `[B]`; `gradu, gradv` are `[B, D]`; `x` is `[D]`; `gradx` is `[D, D]`; `point_data` keys / gradients trailing.

**Methods**:
- `__call__(points=None, func=None, point_data=None) → Tensor`
- `type(dtype)`.

**Constructors**:
- `from_mesh(mesh, boundary_mask=None, quadrature_order=2, project='reduce', *args, **kwargs)` — `boundary_mask` may be `None` (uses `mesh.boundary_mask`), a key into `point_data`, or a 1D bool Tensor.
- `from_elements(points, elements, boundary_mask, quadrature_order=2, device='cpu', dtype=torch.float32, project='reduce', *args, **kwargs)`
- `from_assembler(obj, *args, **kwargs)`.

### 3.4 Projectors *(`tensormesh.assemble.projector`)*

Element-to-global scatter base class (no public methods of its own).

#### `ReduceProjector(Projector)`
```python
ReduceProjector(indices, from_shape, to_shape, use_fp64=False)
```
Backed by `torch.Tensor.index_add_`. `use_fp64=True` accumulates in `float64` for determinism.

#### `SparseProjector(Projector)`
```python
SparseProjector(from_, to_, from_shape, to_shape, dtype=None)
```
Backed by a CSR `torch.sparse` matrix-vector product. Faster on backends with good sparse SpMV. Has `.type(dtype)`.

### 3.5 Built-in assemblers *(`tensormesh.assemble.builtin`)*

#### `LaplaceElementAssembler(ElementAssembler)`
$K^e_{ij} = \int \nabla N_i \cdot \nabla N_j\,d\Omega$. `forward(gradu, gradv) = gradu @ gradv`.

#### `MassElementAssembler(ElementAssembler)`
$M^e_{ij} = \int N_i N_j\,d\Omega$. `forward(u, v) = u * v`.

#### `LinearElasticityElementAssembler(ElementAssembler)`
Constructor params (via `__post_init__`): `E=1.0`, `nu=0.3`.
- `forward(gradu, gradv) = Ba.T @ C @ Bb` (Voigt-form).
- `element_energy(graddisplacement)` — strain-energy density (small strain).

#### `NeoHookeanModel(ElementAssembler)`
Energy-based. Constructor (`from_mesh(...)` + `E=1.0, nu=0.3`):
$\Psi = \tfrac{\mu}{2}(I_1 - d) - \mu\ln J + \tfrac{\lambda}{2}(\ln J)^2$.
- `element_energy(graddisplacement)`.
- `energy(u: Tensor) → Tensor` — total strain energy; differentiable, `.backward()` gives internal force.

#### `J2Plasticity(ElementAssembler)`
Rate-independent J2 plasticity with isotropic hardening. Args: `material=None, E=200e9, nu=0.3, sig0=250e6, H=1e9`.
- Stores `history` dict per element type: `{"eps_p": [n_elem, n_quad, 3, 3], "alpha": [n_elem, n_quad]}`.
- `element_energy(graddisplacement, eps_p_n, alpha_n)` — algorithmic incremental potential implementing return-mapping check.
- `update_state(u_vec)` — call after Newton convergence each step (under `torch.no_grad()`).

#### `ContactAssembler(FacetAssembler)`
Penalty / barrier contact, surface tension, follower pressure, Robin BC.
- `energy(...)` — `∫_Γ ψ dS` (scalar; differentiable).
- `element_energy(**kwargs)` — override.

#### `const_node_assembler(c=1) → type[NodeAssembler]`
Factory: returns a subclass with `forward(self, v) = self.c * v` (uniform body load).

#### `func_node_assembler(f=lambda x: x) → type[NodeAssembler]`
Factory: returns a subclass with `forward(self, x, v) = self.f(x) * v` (spatially-varying load).

---

## 4. `tensormesh.sparse`

`SparseMatrix` is a subclass of `torch_sla.SparseTensor`. The canonical way to solve is `K.solve(b)` / `K.nonlinear_solve(residual_fn, u0)`. Free functions `spsolve` / `nonlinear_solve` are legacy.

### 4.1 `tensormesh.SparseMatrix(SparseTensor)`

```python
SparseMatrix(edata: Tensor, row: Tensor, col: Tensor, shape: Tuple[int, int])
```

**Properties**: `edata`, `row`, `col`, `edges` (`[2, nnz]`), `layout_hash` (SHA-256), `layout_mask` (dense bool), `grad`, `T`.

**Inherited solver methods** (from `torch_sla.SparseTensor`):
- `A @ B` (matmul, autograd-aware)
- `A.solve(b, *, tol=..., method=..., backend=..., preconditioner=..., is_spd=..., maxiter=..., verbose=...)` — auto-detects SPD if no hint; dispatches to `torch_sla.spsolve`.
- `A.nonlinear_solve(residual_fn, u0, *params, mode='newton'|'picard'|'anderson', line_search='armijo'|None, ...)`.

**Type-preserving overrides** (wrap result back as `SparseMatrix`): `__add__`, `__sub__`, `__mul__`, `__matmul__`, `to()`, `cuda()`, `cpu()`, `float()`, `double()`, `half()`, `detach()`.

**FEM helpers**:
- `has_same_layout(other)` — compare hash or another matrix.
- `degree(axis=0)` — nnz per row/col.
- `transpose()` / `.T`.

**Scipy interop**:
- `to_scipy_coo()` / `to_sparse_coo()`.

**Factories (static)**:
- `from_scipy_coo`, `from_sparse_coo`, `from_dense`, `from_block_coo(edata, row, col, shape)`, `random`, `random_layout`, `random_from_layout`, `eye(n, value=1.)`, `full(m, n, value=1.)`.

**Block combination**:
- `combine_vector(matrices, axis=0)`.
- `combine_matrix(matrices: List[List])` — supports `None` (zero), scalars (constant block), dense tensors.
- `combine(matrices)` — dispatcher (list-of-lists → matrix; list → vector axis 0).

### 4.2 Solver backends (`tensormesh.sparse.solve`)

`spsolve(edata, row, col, shape, b, backend='auto', method='cg', preconditioner='jacobi', tol=1e-5, max_iter=10000, x0=None, is_spd=True, verbose=False) → Tensor`

| Backend | Path | Methods | Notes |
|---|---|---|---|
| `scipy` | torch-sla | `lu, umfpack, cholesky, ldlt, cg, bicgstab, minres, gmres, lgmres` | CPU |
| `eigen` | torch-sla | iterative + direct | CPU |
| `pytorch` | torch-sla | iterative | default GPU |
| `cudss` | torch-sla | direct (NVIDIA cuDSS) | CUDA |
| `cupy` | torch-sla | direct + iterative | CUDA |
| `petsc` | fallback | BiCGSTAB + ILU | CPU |
| `native` | fallback torch | BiCGSTAB + Jacobi | CUDA when cupy missing |

Backend-specific `torch.autograd.Function`s (all auto-differentiable via `b_grad = solve(A^T, grad_output)`; `edata_grad = -b_grad[row] * u[col]`):
- `SparseSolveScipy`, `SparseLUSolveScipy` (single + batched RHS).
- `SparseSolveCupy`, `SparseLUSolveCupy` — DLPack-zero-copy.
- `SparseSolvePETSc`, `SparseLUSolvePETSc` (BiCGSTAB + ILU).
- `SparseSolveTorch` — pure PyTorch BiCGSTAB.
- `SparseSolveTorchSLA` — main path.
- `SparseSolveAMG` (`tensormesh.sparse.solve.amg_solve`) — pyAMG smoothed-aggregation preconditioner; accepts `B` near-null-space (6 rigid-body modes for 3D elasticity).
- `CuDSSSolver(row_ptr, col_idx, values, nrows, ncols, matrix_type='general')` — raw ctypes binding (`'general' | 'symmetric' | 'spd' | 'hermitian' | 'hpd'`); plus `splu_cudss`, `CuDSSBatchSolver`, `batch_solve_cudss`, `CuDSSUniformBatchSolver`.

Internal helpers: `cg_py`, `bicgstab_py`, `coo_diagonal`, `jacobi_precond`, `identity_precond`, `petscvec2tensor`, `tensor2cupy`, `cupy2tensor`.

### 4.3 `tensormesh.sparse.mm` — sparse mat-vec / mat-mat

- `spmv(edata, row, col, shape, B, backend=None)`
- `spmm(edata, row, col, shape, B, backend=None)` (`B.dim()==1` → spmv)

Backends: `'scipy'` (CPU default), `'cupy'` (CUDA default), `'torch'`. Backend-`Function`s: `SparseMMScipy/MVScipy`, `SparseMMCupy/MVCupy`, `SparseMMTorch/MVTorch` (all autograd-aware).

### 4.4 `tensormesh.sparse.nonlinear_solve` *(legacy)*
```python
nonlinear_solve(f, j, u0, params, max_iter=100, tol=1e-6, verbose=False) → Tensor
```
Forward = Newton-Raphson under `no_grad`. Backward = implicit-function theorem (adjoint solve, parameter gradients).

### 4.5 `tensormesh.sparse.utils`
- `is_petsc_available: bool`, `is_cupy_available: bool` (env-aware).
- `tensor2cupy(tensor)`, `cupy2tensor(cupy)` — zero-copy DLPack views.
- `shapeT((m, n)) → (n, m)`.

---

## 5. `tensormesh.operator`

### 5.1 `tensormesh.Condenser` *(nn.Module)*

Applies Dirichlet BCs via static condensation:
```
K_ii u_i = f_i - K_io u_o
```

```python
Condenser(dirichlet_mask: Tensor[bool, n_dof], dirichlet_value: Optional[Tensor] = None)
```

**Methods**:
- `__call__(matrix: SparseMatrix, rhs: Optional[Tensor] = None) → (K_inner, rhs_inner)` — auto-builds and caches `K_ou2in` keyed on `matrix.layout_hash`.
- `condense_rhs(rhs)` — reuse cached `K_ou2in` (after first `__call__`).
- `update_dirichlet(value)` — change BC values without rebuilding `K_ou2in`.
- `recover(u_inner) → Tensor` — lift to full DOF, writing `dirichlet_value` into the boundary slots.
- `restrict(f) → Tensor` — pure linear restriction (no Dirichlet correction); for ODE stage RHS.
- `prolong(f_inner) → Tensor` — pure linear prolongation (zeros at boundary); for ODE stage slopes.

---

## 6. `tensormesh.ode`

### 6.1 `tensormesh.ode.ExplicitRungeKutta` *(nn.Module)*
```python
ExplicitRungeKutta(a: Tensor, b: Tensor)  # a lower-triangular, b.sum()==1
```
Overrides: `forward(t, u) → Tensor` (RHS), `__post_init__()` (hook).
Method: `step(t0, u0, dt) → Tensor` — one RK step.

### 6.2 `tensormesh.ode.ImplicitLinearRungeKutta`
Implicit RK specialized to linear systems `M(t) du/dt = A(t) u + B(t)`. Override hooks:
- `forward_M(t)`, `forward_A(t)` — `SparseMatrix | Tensor | scalar`, default `1.0`.
- `forward_B(t)` — `Tensor | scalar`, default `0.0`.
- `pre_solve_lhs(K)`, `pre_solve_rhs(f)` — block transforms (for static condensation).
- `recover_stage(k_i)` — lift stage slope (e.g. `Condenser.prolong`).
- `post_solve(u)` — apply at end.

Method: `step(t0, u0, dt)` — assembles `s × s` block system, solves for stage slopes, advances `u`.

### 6.3 Built-in schemes (`tensormesh.ode.builtin`)
- `ExplicitEuler()` — `a=[[0]], b=[1]` (forward Euler).
- `ImplicitLinearEuler()` — `a=[[1]], b=[1]` (backward Euler).
- `MidPointLinearEuler()` — `a=[[1/2]], b=[1]` (implicit midpoint).

---

## 7. `tensormesh.optimizer`

### 7.1 `tensormesh.OCOptimizer`
Optimality Criteria for SIMP-style topology optimization with volume-fraction constraint.
```python
OCOptimizer(
    params: Tensor | List[Tensor],
    vf: float,
    move_limit: float = 0.2,
    rho_min: float = 1e-3,
    rho_max: float = 1.0,
    eta: float = 0.5,
    bisection_tol: float = 1e-4,
    bisection_max_iter: int = 50,
)
```
Update: `ρ ← ρ * (−∂C/∂ρ / (λ ∂V/∂ρ))^η`, with λ found by bisection so mean density = `vf`. Methods: `zero_grad()`, `step(dc=None, dv=None) → {'lambda', 'volume'}`, `get_volume()`, `get_stats()`.

(There is also an example `examples/inverse_design/mma_optimizer.py` MMA optimizer, but it is not part of the library API.)

---

## 8. `tensormesh.functional`

Re-exports everything from `ops`, `elasticity`, `plastic`.

| Function | Signature / math |
|---|---|
| `sym(a)` | `0.5*(a[..., None] + a[..., None, :])` — promotes `[..., D]` → `[..., D, D]` symmetric |
| `skew(x, sign=True, at_least2d=False)` | skew-symmetric cross-product matrix (2D or 3D) |
| `sqrt(x)` | clamp-then-sqrt (NaN-safe) |
| `divide(x, y)` | safe division (0 where `y==0`) |
| `strain(gradu)` | small strain `(∇u + ∇uᵀ)/2` |
| `isotropic_stress(strain, E=70., nu=0.3)` | Hooke's law: `λ tr(ε) I + 2μ ε` |
| `deviatoric_stress(stress)` | `σ - (tr σ / d) I` |
| `deviatoric_stress_norm(stress)` | von Mises `√(3/2 s:s)` |
| `voigt_shape_grad(gradu)` | B-matrix; `[3, 2]` (2D) or `[6, 3]` (3D) |
| `voigt_stiffness(E, nu, dim=2)` | C-matrix `[3,3]` or `[6,6]` |
| `voigt_shape_val(u, dim)` | N-matrix `[d, d]` from scalar `u` |
| `update_plastic_stress(gradu, strain, stress, E=70., yield_stress=250., strain_fn=strain, stress_fn=isotropic_stress)` | one radial-return step (perfect plasticity) |

---

## 9. `tensormesh.material`

```python
@dataclass
class IsotropicMaterial:
    name: str
    E: float
    nu: float
    rho: float
    sigma_y: float = None
    H: float = 0.0

    @property
    def lame_params(self) -> (mu, lam): ...
```

Predefined instances:
| Name | E (Pa) | ν | ρ (kg/m³) | σ_y | H |
|---|---|---|---|---|---|
| `Steel` | 210e9 | 0.3 | 7850 | 250e6 | 0.0 |
| `Aluminum` | 70e9 | 0.33 | 2700 | 100e6 | 700e6 |
| `Rubber` | 10e6 | 0.48 | 1100 | — | 0.0 |
| `Glass` | 70e9 | 0.2 | 2500 | — | 0.0 |

---

## 10. `tensormesh.dataset`

### 10.1 Mesh generators (top-level)
`gen_rectangle, gen_hollow_rectangle, gen_circle, gen_hollow_circle, gen_cube, gen_hollow_cube, gen_sphere, gen_hollow_sphere, gen_L` — see §1.1 for signatures.

### 10.2 `MeshGen` (fluent builder)
```python
MeshGen(element_type=None, dimension=2, order=1, chara_length=0.1,
        cache_path="./tmp.msh", verbose=False)
```
Mixed-element-supporting builder around gmsh OCC. Methods (return `self`): `add_rectangle`, `remove_rectangle`, `add_circle`, `remove_circle`, `add_cube`, `remove_cube`, `add_sphere`, `remove_sphere`. Finaliser: `gen(show=False) → Mesh`.

Module-level dicts:
- `abbr2element_type = {"tri":"triangle","quad":"quad","tet":"tetra","hex":"hexahedron","pri":"pyramid","pyr":"wedge"}`
- `element_type2abbr` — inverse.

### 10.3 Analytical PDE families (`tensormesh.dataset.equation`)

#### `HeatMultiFrequency(mu=None, d=2)`
2D heat equation on `[-1,1]²`, zero BC. `initial_condition(points)`, `solution(points, t)`.

#### `WaveMultiFrequency(a=None, K=2, c=1.0, r=0.5)`
2D wave equation on `[0,1]²`. `initial_condition(points)`, `solution(points, t=0.1)`.

#### `PoissonMultiFrequency(a=None, K=2, r=-0.5)`
2D Poisson on `[0,1]²`. `source_term(points, domain="rectangle")`, `solution(points)`.

#### `PoissonMultiFrequency3D` — 3D analogue.

#### `LinearElasticityMultiFrequency(a_x=None, a_y=None, K=2, r=0.5, E=1.0, nu=0.3)`
2D Navier-Cauchy manufactured solution. Methods: `solution`, `body_force`, `strain`, `stress`.

#### `LinearElasticityMultiFrequency3D(a_x=None, a_y=None, a_z=None, K=2, r=0.5, E=1.0, nu=0.3)`
3D version. Methods: `solution`, `body_force`.

#### `BatchPoissonSolver(mesh, device=None, dtype=torch.float32, solver_backend=None)` *(nn.Module)*
Batch Poisson solver (zero Dirichlet) with pre-factorized `splu` (CPU) or cupy `splu` (CUDA).
Methods: `assemble_rhs(f)`, `solve(f, tol=1e-6, max_iter=10000)`, `forward(f)`. Classmethods: `create_2d(domain, ...)`, `create_3d(...)`.

#### `solve_poisson_batch(f, mesh=None, domain="rectangle", chara_length=0.05, dim=2, ...) → (u, mesh)`

#### `BatchLinearElasticitySolver(mesh, E=1.0, nu=0.3, device=None, dtype=torch.float64, solver_backend=None, cuda_solver: Literal['bicgstab','lu']='bicgstab')`
Methods: `solve(f, tol=1e-6, max_iter=10000)`, `forward(f)`, classmethods `create_2d(domain in {"rectangle","circle","L","hollow_rectangle"}, ...)`, `create_3d(domain in {"cube","sphere","cylinder","hollow_cube"}, ...)`.

#### `solve_linear_elasticity_batch(f, mesh=None, domain="rectangle", chara_length=0.05, dim=2, E=1.0, nu=0.3, ...) → (u, mesh)`

---

## 11. `tensormesh.distributed`

### 11.1 `DistributedMesh`
```python
DistributedMesh(mesh: Mesh, num_partitions=None, method='coordinate', devices=None)
```
- Defaults: `num_partitions = cuda.device_count() or 2`; `devices = [cuda:0, cuda:1, …]` or all CPU.
- Partitioning via `partition_mesh`; each submesh has `point_data["orig_nid"]` for global mapping.
- Dunder: `__len__`, `__getitem__`, `__repr__`.

### 11.2 Assembly functions
- `distributed_element_assemble(assembler_cls, dmesh, quadrature_order=2, project='reduce', call_kwargs=None, **assembler_kwargs) → torch_sla.DSparseTensor` — three-phase strategy (sequential warm-up of `shape_val/grad/JxW` → parallel threads → sequential merge); resolves CUDA / lazy-init races.
- `distributed_element_assemble_to_sparse(...) → SparseMatrix` — same but returns tensormesh `SparseMatrix`.
- `distributed_node_assemble(assembler_cls, dmesh, quadrature_order=2, project='reduce', point_data=None, call_kwargs=None, **assembler_kwargs) → Tensor[|V| · dof]` — local node vector → global scatter_add.

---

## 12. `tensormesh.visualization`

Top-level imports (`__init__.py`):
```
draw_graph, draw_mesh, draw_point_value, update_point_value,
draw_element_value, update_element_value, draw_facet_2d,
StreamPlotter, draw_mesh_2d_stream, draw_mesh_2d_static,
animate_deformation, plot_deformation, plot_value,
mesh_to_pyvista, setup_headless
```

### 12.1 Mesh / graph wireframes
- `draw_mesh(mesh, draw_basis=True, edgecolor="blue", linewidth=3, alpha=0.3, ax=None) → Axes` — LineCollection edges (2D) / Line3DCollection (3D); optional basis-node scatter.
- `draw_graph(sparse_matrix, points, draw_points=True, point_color='orange', color="blue", linewidth=3, alpha=0.5, ax=None) → Axes | Axes3D` — adjacency-graph viz; off-diag = line segments, self-loops = arcs.

### 12.2 Nodal scalar fields
- `draw_point_value_2d_tri_gouraud(points, point_values, elements, cmap='jet', ax=None)` — Gouraud `tripcolor` (linear triangles).
- `update_point_value_2d_tri_gouraud(img, point_values)`.
- `draw_point_value_2d_interpolation(points, point_values, density=100, cmap='jet', use_scatter=False, ax=None)` — cubic `griddata` on a regular grid.
- `update_point_value_2d_interpolation(img, points, point_values)`.
- `draw_point_value_2d(points, point_values, elements, density=100, cmap='jet', use_scatter=False, ax=None)` — dispatch on element type.
- `draw_point_value_3d_interpolation(points, point_values, density=25, cmap='jet', ax=None)` — masked 3D scatter on regular grid.
- `update_point_value_3d_interpolation(img, points, point_values)`.
- `draw_point_value(mesh, point_values, density=25, cmap='jet', use_scatter=False, ax=None)` — top-level dispatch.
- `update_point_value(mesh, img, point_values)`.

### 12.3 Element-value fields
- `draw_element_value_2d_tri(points, elements, values, alpha=None, cmap='viridis', color=None, ax=None, **kwargs)`.
- `draw_element_value_2d(points, elements: Dict, values: Dict, alpha=1.0, cmap='viridis', color=None, ax=None, **kwargs)`.
- `update_element_value_2d_tri(img, values, alpha=None)`.
- `update_element_value_2d(collections, values, alpha=1.0)`.
- `draw_element_value_3d(points, elements, values, alpha=0.3, cmap='viridis', color=None, density=25, ax=None)`.
- `update_element_value_3d(collections, points, elements, values, density=25)`.
- `draw_element_value(mesh, values, alpha=None, cmap='viridis', color=None, density=25, ax=None)` — top-level.
- `update_element_value(mesh, collections, values, alpha=1.0, density=25)`.

### 12.4 Facets
- `draw_facet_2d(points, elements, draw_basis=False, point_color='orange', color="blue", alpha=0.5, linewidth=1, ax=None) → Axes` — dedupes facet edges per element type.

### 12.5 Streaming / animation
- `StreamPlotter(nrows=1, ncols=1, width=5, height=5, filename="stream_plotter.mp4")` — ffmpeg writer context manager. Methods: `__enter__/__exit__`, `grab_frame(**savefig_kwargs)`, `update()`, `draw_mesh_2d(points, elements, point_values, ax=None, cmap='jet', density=100, use_scatter=False, show_colorbar=True, title='', update=True, show_mesh=True, show_basis=True, umin=None, umax=None, linewidth=1, basiscolor='orange', linecolor='blue')`.
- `draw_mesh_2d_static(points, elements, point_values, show_colorbar=True, show_mesh=False, filename='mesh_2d_stream.jpq', umin=None, umax=None, **kwargs)` — single image (tensor or dict of tensors → multi-subplot).
- `draw_mesh_2d_stream(points, elements, point_values, dt=None, show_colorbar=True, fix_colorbar=False, show_mesh=False, filename='mesh_2d_stream.mp4', **kwargs)` — MP4 over leading time axis.

### 12.6 PyVista 3D
- `animate_deformation(mesh, displacement, file_name, frames=30, fps=10, scale_factor=1.0, scalars='displacement')` — `warp_by_vector` animation, isometric camera.
- `plot_deformation(mesh, displacement, file_name, scale_factor=1.0, camera_position='isometric', fixed_nodes=None, force_vectors=None, linearize=True)` — undeformed wireframe + deformed mesh, fixed nodes (blue cubes), force arrows (red).
- `plot_value(kwargs, mesh, save_path=None, dt=None, show_mesh=False)` — pyvista subplot per `(name, value)`; static or animated GIF.

### 12.7 Utilities
- `mesh_to_pyvista(mesh, point_data=None, cell_data=None, linearize=False) → pyvista.DataSet`.
- `setup_headless()` — `pv.start_xvfb()` if pyvista available.
- `as_sparse_matrix`, `as_tensor`, `as_ndarray`, `dim(x)`, `grid(dim, min_vals, max_vals, density=100)` (memoized).
- Flags: `HAS_PYVISTA`, `_PYVISTA_INSTALL_HINT`.

(There is also a legacy `tensormesh.visualization.matplotlib` module with an alternate `plot_value`, `plot_mesh`, `draw_mesh`, `StreamPlotter`, not re-exported.)

---

## 13. `tensormesh.nn`

PyTorch lacks a built-in container for *buffers* (non-trainable tensors). These fill the gap.

### 13.1 `BufferDict(data: Optional[Dict[str, Tensor]] = None)` *(nn.Module)*
- Stores tensors via `register_buffer`; non-identifier keys fall back to `self._data: OrderedDict`.
- `_apply(fn)` override moves both registered buffers and `_data`.
- Methods: `as_parameter(key)` / `as_buffer(key)` (promotion / demotion), `keys/items/values`, `__getitem__/__setitem__/__len__/__includes__/__hash__`, `is_floating_point()`, `is_complex()`, `to_dict()`, `clone()`.
- Properties: `dtype`, `device` (from first buffer).
- Used by `Mesh.cells`, `Mesh.point_data`, assembler buffers.

### 13.2 `BufferList(data: Optional[Iterable[Tensor]] = None)` *(nn.Module)*
- Indexed buffers (`'0', '1', ...`); list operations: `append`, `insert`, `pop`, `__setitem__`, `__delitem__`, `__len__`, `__iter__`, `__contains__`.
- `__getitem__` accepts `int`, `slice`, or 1D `Tensor` indices (returns a fresh `BufferList`).
- `as_parameter(key)`, `as_buffer(key)`, `item()` (length-1 helper), `to_list()`, `clone()`.
- Properties: `dtype`, `device`.
- Used by `FacetAssembler` for per-element-type boundary-facet masks.

---

## 14. Miscellaneous top-level modules

### 14.1 `tensormesh.vmap`
Re-exports `vmap` from `torch ≥ 2.0` (else `functorch`). Raises `ImportError` for older torch.

### 14.2 `tensormesh.zen`
`logo() → None` — prints the ASCII banner. Called at import.

### 14.3 `tensormesh._version`
`__version__ = '0.1.1'`.

### 14.4 `tensormesh.verify_install`
- `solve_poisson(device) → float` — solves `-Δu = 2π² sin(πx)sin(πy)` on the unit square; returns relative L2 error.
- `main()` — prints versions, runs CPU + (CUDA if available) Poisson smoke-test, calls `torch_sla.show_backends()`. CLI: `python -m tensormesh.verify_install`.

---

## 15. Example gallery (capabilities mapped to code)

| Category | Files | What it demonstrates |
|---|---|---|
| Basics | `examples/basics/{basis,basis_fn,element_gallery,plot_mesh}.py` | Reference-element node layout, shape functions, TensorMesh vs Gmsh/VTK ordering, mixed meshes, adjacency graphs |
| Poisson | `examples/poisson/{poisson,poisson_3d,poisson_h_adaptivity}.py` | 2D / 3D Poisson, batched RHS, h-adaptivity |
| Diffusion | `examples/diffusion/{heat,allen-cahn}/` | Heat equation; Allen-Cahn phase field with Newton iteration |
| Wave | `examples/wave/wave.py` | Explicit central-difference time integration |
| Solid | `examples/solid/{cantilever_beam,hyperelastic_beam,hertzian_contact,plasticity_strip,plasticity_3d}/` | Linear elasticity, Neo-Hookean Newton, contact, J2 plasticity |
| Fluid | `examples/fluid/{cavity,cylinder_flow,flow_obstacles,rayleigh_benard,taylor_green}/` | Incompressible Navier-Stokes (lid-driven cavity, cylinder, Rayleigh-Bénard, Taylor-Green) |
| Maxwell | `examples/maxwell/magnetostatic.py` | 3D magnetostatics, stabilized nodal curl-curl |
| Inverse design | `examples/inverse_design/{coefficient_identification,compliance_topology,thermal_topology,mma_optimizer}.py` | Autograd coefficient ID; SIMP-OC / MMA topology optimization |
| Physics-informed | `examples/physics_informed/poisson_galerkin.py` | NN minimizing assembled Galerkin residual |
| Dataset | `examples/dataset/{heat,wave,poisson}/` | Batch dataset generation for ML training |
| Distributed | `examples/distributed/{benchmark_assembly,graph_coloring,graph_partition}.py` | Multi-GPU assembly benchmarks, graph coloring, partitioning |

---

## 16. Roadmap (planned features, from `ROADMAP.md`)

1. **Mixed (multi-field / block) assembly** for Lagrange spaces (e.g. Taylor-Hood P2-P1 for Stokes).
2. **Complex-valued FEM** → Helmholtz, PML, metamaterial topology optimization (acoustic / 2D EM).
3. **New element families**: P0 (discontinuous), Raviart-Thomas (H(div)), Nédélec (H(curl)) — vector-valued bases, Piola transforms, facet-DOF + orientation/sign layer.

---

## 17. Architecture cheat-sheet

| Module | Role |
|---|---|
| `tensormesh.mesh` | `Mesh`; built-in generators; Gmsh / VTK-HDF5 I/O |
| `tensormesh.element` | Shape functions, quadrature, transformations (geom order 1–4, basis order 1–10) |
| `tensormesh.assemble` | `ElementAssembler`, `NodeAssembler`, `FacetAssembler`; built-in physics (Laplace, mass, linear elasticity, Neo-Hookean, J2, contact, const/func load) |
| `tensormesh.sparse` | `SparseMatrix` (subclass of `torch_sla.SparseTensor`); linear & nonlinear solves via scipy / Eigen / pytorch / cupy / cudss / petsc / pyamg |
| `tensormesh.operator` | `Condenser` for Dirichlet BC via static condensation |
| `tensormesh.ode` | Explicit / implicit-linear Runge–Kutta integrators |
| `tensormesh.dataset` | Parametric PDE dataset generators (Poisson / Heat / Wave / linear elasticity, 2D & 3D) |
| `tensormesh.visualization` | Matplotlib + PyVista plotting (static, streaming, animated) |
| `tensormesh.functional` | Tensor utilities for FEM (Voigt, elasticity, J2) |
| `tensormesh.material` | `IsotropicMaterial` dataclass + presets (Steel / Aluminum / Rubber / Glass) |
| `tensormesh.optimizer` | `OCOptimizer` (Optimality Criteria for topology optimization) |
| `tensormesh.distributed` | Multi-GPU element/node assembly + `DistributedMesh` |
| `tensormesh.nn` | `BufferDict`, `BufferList` — buffer-tensor containers missing from PyTorch |
| `tensormesh.vmap` / `zen` | `vmap` shim and ASCII banner |

---

## 18. Quick installation reference

```bash
pip install tensormesh-fem             # CPU only
pip install "tensormesh-fem[gpu]"      # + CuPy + cuDSS
pip install "tensormesh-fem[cupy]"     # CuPy backend only
pip install "tensormesh-fem[cudss]"    # cuDSS backend only
python -m tensormesh.verify_install    # smoke test
```

Requires Python ≥ 3.10, PyTorch ≥ 2.0. Hard dependency: `torch-sla` (sparse linear algebra). Optional: `gmsh`, `pymetis`, `pyvista`, `cupy`, `nvidia-cuDSS`, `petsc4py`, `pyamg`.

---

*Last regenerated by reading TensorMesh source at commit imported from `https://github.com/camlab-ethz/TensorMesh` into `SOLVERX/TensorMesh/`. Coverage: every Python file under `tensormesh/` (≈ 20,000 LOC).*
