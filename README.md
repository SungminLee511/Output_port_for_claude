# LG-VS Jig Dataset Analysis

This repo contains analysis and visualization code for the downloaded Hugging Face dataset:

`TRASHCAN/data_port/huggingface_datasets/solverx/lg-vs_JIG`

Run:

```bash
/home/sky/miniconda3/bin/conda run -n SML_env python -u analyze_lgvs.py
```

Outputs are written to `results/`.

Per-case pointcloud visualizations:

```bash
/home/sky/miniconda3/bin/conda run -n SML_env python -u pointcloud_case_visuals.py
```

Outputs are written to `results/pointclouds/`.

## Modal solver — GT vs computed mode-shape comparison

Computed with `SOLVERX/modal_solvers` (QLoRA-free FEA modal eigensolver: CTETRA10 + CBAR + RBE2/RBE3 + SPC + penalty contact, GPU cuDSS + ARPACK eigsh), compared against the ground-truth Nastran modes embedded in each H5 (`frequency_hz`, `eigvec`).

- `lgvs_g1_01_mode1_t20260617.png` — g1_01 (GT 1st freq 1464.3 Hz)
- `lgvs_g2_0001_mode1_t20260617.png` — g2_0001 (GT 1st freq 1071.0 Hz, 23 disconnected blobs held only by contact)

Note: out-of-box accuracy is limited (30–300% freq error, low MAC) because these jigs are disconnected solid bodies whose modes are entirely contact-stiffness-driven; matching GT needs OptiStruct `.CPR`/`.out` contact-stiffness references (not in the H5).
