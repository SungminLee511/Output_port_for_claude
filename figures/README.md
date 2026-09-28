# TMLR figure drafts (evaluation only)

No retraining, no `ckpt/*/results.json` touched, nothing written into
`iasbs_tmlr`. Every panel is recorded in `manifest.json` with its checkpoint
dir, seed, weights (live for annealed-temperature runs, EMA otherwise), sample
RNG seed and selection rule. Sample RNG seed is 0 everywhere; no cherry-picking.

## F3 — Cu–Au 2×2×4, the four most probable configurations

![F3](F3_cuau_2x2x4_top4/F3_cuau_2x2x4_top4_t20260928.png)

16 fcc sites at x_Au = ½, so the canonical law is **enumerable**:
C(16,8) = 12870 states, p_exact = softmax(−E/τ) over the whole space. The
learned law is the empirical frequency of 500 000 draws (seed 0) matched to the
enumeration by an exact bit code — no binning, no kernel.

Top row 1200 K (τ = 0.1034), bottom row 680 K (τ = 0.0586); columns are the
four most probable states, which are four of the L1₀ variants and are exactly
degenerate. Under each cell: dark-grey bar = p_exact, coloured bar = p_learned,
**one common scale for both rows**, so the 5× mass concentration at 680 K is
the visible difference.

| row | τ | p_exact (each of 4) | p_learned | TV over all 12870 states |
|---|---|---|---|---|
| 1200 K | 0.1034 | 0.02723 | 0.02711 – 0.02774 | 0.0578 |
| 680 K | 0.0586 | 0.14846 | 0.14672 – 0.15036 | 0.0555 |

Au gold, Cu copper; cell outline colours the L1₀ variant (6 colours), outline
centred on the atom set. Raw: `top4.json`, `top4.csv`,
`<row>/top{0..3}.extxyz` (p_exact, p_learned, LRO, variant in `at.info`).

## F4 — sphere samples, E = 6(1 − x₃²), τ = 1, Haar source, 500 steps

![F4](F4_sphere/F4_sphere_t20260928.png)

Left: reflection-trained (`sphere_haar_I_refl` seed 0), P(x₃>0) = 0.4988.
Right: no reflection, seed 2 — the largest |P(x₃>0) − ½| of the three seeds,
P(x₃>0) = 0.5574. Points coloured by x₃ (diverging PuOr), camera along −e₁ so
both poles are visible; front hemisphere drawn, all 5000 samples in the CSVs.

## F7 — 16×16 lattice snapshots

![F7](F7_lattice_snapshots/F7_lattice_snapshots_t20260928.png)

Learned (left 4) beside Swendsen–Wang reference (right 4). Rows: canonical
Ising β = 0.4407; free Ising β = 0.28 / 0.4407 / 0.6; free 3-state Potts
β = 0.5 / 1.005 / 1.2. Greyscale for Ising, three colours for Potts.
Raw: `samples.json`, `samples.csv`.
