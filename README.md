# Output Port for Claude

This repo is used to share result images from Claude Code.

**Timezone: KST (UTC+9)** — Server time is 9 hours behind KST.

## Results

### SolverAI Trainer — March 18 Inference (2026-03-19 13:30 KST)

**Model**: GNN Baseline (GATv2, 124K params) — Epoch 405, Step 103,275
**Dataset**: HD Mobis Laplacian (processed_260318)
**Validation**: 60 samples (C_L_SPFH590, 16T/23T/26T)

**Error Distribution** — Per-sample Rel MSE/MAE + node-level error histogram
![error_dist](inference_mar18_error_dist.png)

**Predicted vs GT** — Sample C_L_SPFH590_16T_v1_1 (reconstructed via line integral)
![compare](inference_mar18_C_L_SPFH590_16T_v1_1.png)

**Predicted Field Magnitude**
![pred_field](inference_mar18_pred_field.png)

**GT Field Magnitude**
![gt_field](inference_mar18_gt_field.png)
