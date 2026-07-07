"""Export report-ready result assets from the latest experiment run."""
from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
DATA = ROOT / "data" / "processed"


FEATURE_DESCRIPTIONS = {
    "object_count": "number of annotated objects in the scene",
    "min_distance_m": "minimum 3D distance to an annotated object",
    "front_object_count": "number of objects in the front corridor",
    "vulnerable_count": "number of pedestrians, cyclists and sitting persons",
    "close_object_count": "number of front objects within 25 m",
    "max_bbox_area_norm": "largest normalized 2D bounding box area",
    "occluded_count": "number of objects with occlusion level at least 2",
    "truncated_count": "number of objects with truncation at least 0.35",
    "mean_occlusion": "mean normalized occlusion level",
    "mean_truncation": "mean truncation value",
    "camera_quality_proxy": "proxy estimate of camera observation quality",
    "lidar_geometry_quality_proxy": "proxy estimate of 3D geometry quality",
    "uncertainty_proxy": "proxy uncertainty from camera and geometry quality",
    "risk_prior": "rule-based object risk prior",
    "max_abs_alpha": "maximum absolute KITTI alpha angle",
    "min_lateral_abs_m": "minimum absolute lateral distance",
}


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_model_comparison(metrics: dict, models: dict) -> None:
    path = RESULTS / "model_comparison.csv"
    fieldnames = [
        "model",
        "threshold",
        "precision",
        "recall",
        "f1",
        "accuracy",
        "false_positive_rate",
        "false_negative_rate",
        "roc_auc",
        "pr_auc",
        "tp",
        "fp",
        "fn",
        "tn",
        "num_examples",
        "num_features",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for name, values in metrics["models"].items():
            writer.writerow(
                {
                    "model": name,
                    "threshold": values["threshold"],
                    "precision": values["precision"],
                    "recall": values["recall"],
                    "f1": values["f1"],
                    "accuracy": values["accuracy"],
                    "false_positive_rate": values["false_positive_rate"],
                    "false_negative_rate": values["false_negative_rate"],
                    "roc_auc": values["roc_auc"],
                    "pr_auc": values["pr_auc"],
                    "tp": values["tp"],
                    "fp": values["fp"],
                    "fn": values["fn"],
                    "tn": values["tn"],
                    "num_examples": values["num_examples"],
                    "num_features": len(models["models"][name]["feature_names"]),
                }
            )


def write_feature_list(models: dict) -> None:
    payload = {
        "note": "Feature values are derived from real KITTI object annotations. They are not synthetic training data.",
        "models": {},
    }
    for name, spec in models["models"].items():
        payload["models"][name] = [
            {"name": feature, "description": FEATURE_DESCRIPTIONS.get(feature, "feature from scenario table")}
            for feature in spec["feature_names"]
        ]
    (RESULTS / "feature_list.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_threshold_selection(metrics: dict, models: dict) -> None:
    lines = [
        "# Threshold selection",
        "",
        "The threshold is selected on the validation split. The search maximizes F1, then recall, then lower false positive rate. Test metrics are calculated after threshold selection and are not used for tuning.",
        "",
        "| Model | Validation threshold | Validation F1 | Validation recall | Test F1 | Test recall | Test FNR |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for name, spec in models["models"].items():
        validation = spec["validation_metrics"]
        test = metrics["models"][name]
        lines.append(
            "| "
            + " | ".join(
                [
                    name,
                    str(round(float(spec["threshold"]), 3)),
                    str(validation["f1"]),
                    str(validation["recall"]),
                    str(test["f1"]),
                    str(test["recall"]),
                    str(test["false_negative_rate"]),
                ]
            )
            + " |"
        )
    lines.extend(
        [
            "",
            "For ADAS-oriented critical-scene screening, recall and false negative rate are treated as priority metrics. A missed critical scene is more dangerous than an extra warning, although false positives still matter for driver trust.",
        ]
    )
    (RESULTS / "threshold_selection.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_run_summary(metrics: dict, summary: dict) -> None:
    primary = metrics["models"][metrics["primary_model"]]
    lines = [
        "# Run summary",
        "",
        "Experiment: scenario-level logistic models trained on KITTI Object Detection annotations.",
        "",
        f"Dataset examples: {summary['num_scenes']}",
        f"Train examples: {summary['split_counts']['train']}",
        f"Validation examples: {summary['split_counts']['validation']}",
        f"Test examples: {summary['split_counts']['test']}",
        f"Positive critical scenes: {summary['positive_critical_scenes']}",
        f"Negative scenes: {summary['negative_scenes']}",
        f"Seed: {summary['seed']}",
        "",
        f"Primary model: `{metrics['primary_model']}`",
        f"Precision: {primary['precision']}",
        f"Recall: {primary['recall']}",
        f"F1: {primary['f1']}",
        f"Accuracy: {primary['accuracy']}",
        f"ROC AUC: {primary['roc_auc']}",
        f"PR AUC: {primary['pr_auc']}",
        f"Confusion matrix: TP={primary['tp']}, FP={primary['fp']}, FN={primary['fn']}, TN={primary['tn']}",
        "",
        "The target label is derived from real KITTI object annotations by a fixed rule. It is not an original KITTI benchmark target.",
    ]
    (RESULTS / "run_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    metrics = load_json(RESULTS / "metrics.json")
    models = load_json(RESULTS / "models.json")
    summary = load_json(DATA / "dataset_summary.json")
    write_model_comparison(metrics, models)
    write_feature_list(models)
    write_threshold_selection(metrics, models)
    write_run_summary(metrics, summary)
    print("Saved report assets to results/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
