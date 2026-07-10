# Run summary

Experiment: scenario-level logistic models trained on KITTI Object Detection annotations.

Dataset examples: 7481
Train examples: 4488
Validation examples: 1496
Test examples: 1497
Positive critical scenes: 2715
Negative scenes: 4766
Seed: 54

Primary model: `proposed_reliability_logreg`
Precision: 0.885
Recall: 0.937
F1: 0.911
Accuracy: 0.933
ROC AUC: 0.981
PR AUC: 0.970
Confusion matrix: TP=509, FP=66, FN=34, TN=888

The target label is derived from real KITTI object annotations by a fixed rule. It is not an original KITTI benchmark target.
