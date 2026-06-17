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
