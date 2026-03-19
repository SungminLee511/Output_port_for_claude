# Output Port for Claude

This repo is used to share result images from Claude Code.

**Timezone: KST (UTC+9)** — Server time is 9 hours behind KST.

## Results

### SolverAI Trainer — March 18 Inference (2026-03-19 13:40 KST)

**Model**: GNN Baseline (GATv2, 124K params) — Epoch 405, Step 103,275
**Dataset**: HD Mobis Laplacian (processed_260318)

---

#### Validation Samples (60 C_L_SPFH590 samples)

**Error Distribution** — Per-sample Rel MSE/MAE + node-level error histogram
![error_dist](inference_mar18_error_dist.png)

**Predicted vs GT** — Sample C_L_SPFH590_16T_v1_1 (reconstructed via line integral)
![compare](inference_mar18_C_L_SPFH590_16T_v1_1.png)

**Predicted Field Magnitude**
![pred_field](inference_mar18_pred_field.png)

**GT Field Magnitude**
![gt_field](inference_mar18_gt_field.png)

---

#### Train Samples (9 samples: A_E_STEEL, B_H_SPFH590, D_E_STEEL)
- Avg Rel MSE: 113.16% | Avg Rel MAE: 121.95%

**Error Distribution** — Per-sample Rel MSE/MAE + node-level error histogram
![train_error_dist](inference_mar18_train_error_dist.png)

**Predicted vs GT** — Sample A_E_STEEL_16T_v1_1 (reconstructed via line integral)
![train_compare](inference_mar18_train_A_E_STEEL_16T_v1_1.png)

**Predicted Field Magnitude**
![train_pred_field](inference_mar18_train_pred_field.png)

**GT Field Magnitude**
![train_gt_field](inference_mar18_train_gt_field.png)
