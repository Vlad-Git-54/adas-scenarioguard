# Threshold selection

The threshold is selected on the validation split. The search maximizes F1, then recall, then lower false positive rate. Test metrics are calculated after threshold selection and are not used for tuning.

| Model | Validation threshold | Validation F1 | Validation recall | Test F1 | Test recall | Test FNR |
|---|---:|---:|---:|---:|---:|---:|
| baseline_kitti_logreg | 0.38 | 0.902 | 0.917 | 0.894 | 0.913 | 0.087 |
| proposed_reliability_logreg | 0.35 | 0.902 | 0.921 | 0.911 | 0.937 | 0.063 |
| ablation_without_3d_geometry | 0.43 | 0.882 | 0.871 | 0.875 | 0.869 | 0.131 |

For ADAS-oriented critical-scene screening, recall and false negative rate are treated as priority metrics. A missed critical scene is more dangerous than an extra warning, although false positives still matter for driver trust.
