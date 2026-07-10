"""Evaluate trained models and export reproducible result files."""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adas_scenarioguard.experiment import (  # noqa: E402
    evaluate_named_model,
    grouped_metrics,
    pr_points,
    read_csv,
    roc_points,
    write_json,
)


PRIMARY_MODEL = "proposed_reliability_logreg"


def write_metrics_csv(path: Path, model_metrics: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["model", "metric", "value"])
        for model_name, metrics in model_metrics.items():
            for key, value in metrics.items():
                writer.writerow([model_name, key, value])


def write_confusion_matrix(path: Path, metrics: dict) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["", "predicted_critical", "predicted_ok"])
        writer.writerow(["actual_critical", metrics["tp"], metrics["fn"]])
        writer.writerow(["actual_ok", metrics["fp"], metrics["tn"]])


def write_error_cases(path: Path, predictions: list[dict]) -> None:
    errors = [row for row in predictions if row["error_type"] in {"FP", "FN"}]
    with path.open("w", encoding="utf-8", newline="") as f:
        fieldnames = [
            "scene_id",
            "error_type",
            "y_true",
            "y_pred",
            "score",
            "min_distance_m",
            "vulnerable_count",
            "occluded_count",
            "truncated_count",
            "risk_prior",
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in errors:
            writer.writerow({key: row[key] for key in fieldnames})


def write_curve_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> int:
    results_dir = ROOT / "results"
    dataset_path = ROOT / "data" / "processed" / "kitti_scenarios.csv"
    models_path = results_dir / "models.json"
    if not dataset_path.exists():
        raise SystemExit("Missing data/processed/kitti_scenarios.csv. Run scripts/prepare_data.py first.")
    if not models_path.exists():
        raise SystemExit("Missing results/models.json. Run scripts/train.py first.")

    rows = read_csv(dataset_path)
    model_bundle = json.loads(models_path.read_text(encoding="utf-8"))
    metrics_by_model = {}
    predictions_by_model = {}

    for name, spec in model_bundle["models"].items():
        metrics, predictions = evaluate_named_model(rows, spec, split="test")
        metrics_by_model[name] = metrics
        predictions_by_model[name] = predictions

    primary_predictions = predictions_by_model[PRIMARY_MODEL]
    primary_metrics = metrics_by_model[PRIMARY_MODEL]
    grouped = grouped_metrics(rows, primary_predictions)
    y_true = [int(row["y_true"]) for row in primary_predictions]
    scores = [float(row["score"]) for row in primary_predictions]

    result = {
        "dataset": "KITTI Object Detection training annotations",
        "dataset_source": "https://www.cvlibs.net/datasets/kitti/eval_object.php?obj_benchmark=3d",
        "raw_label_archive": "https://s3.eu-central-1.amazonaws.com/avg-kitti/data_object_label_2.zip",
        "target_note": (
            "critical_scene is a deterministic label derived from real KITTI annotations. "
            "It is not an original KITTI benchmark target."
        ),
        "primary_model": PRIMARY_MODEL,
        "models": metrics_by_model,
        "grouped_metrics": grouped,
    }

    write_json(results_dir / "metrics.json", result)
    write_json(results_dir / "predictions.json", predictions_by_model)
    write_metrics_csv(results_dir / "metrics.csv", metrics_by_model)
    write_confusion_matrix(results_dir / "confusion_matrix.csv", primary_metrics)
    write_error_cases(results_dir / "error_cases.csv", primary_predictions)

    roc = roc_points(y_true, scores)
    pr = pr_points(y_true, scores)
    write_json(results_dir / "roc_points.json", roc)
    write_json(results_dir / "pr_points.json", pr)
    write_curve_csv(results_dir / "roc_points.csv", roc)
    write_curve_csv(results_dir / "pr_points.csv", pr)

    summary = [
        "# Run summary",
        "",
        "Experiment: scenario-level logistic models trained on KITTI Object Detection annotations.",
        "",
        f"Primary model: `{PRIMARY_MODEL}`",
        f"Test examples: {primary_metrics['num_examples']}",
        f"Precision: {primary_metrics['precision']}",
        f"Recall: {primary_metrics['recall']}",
        f"F1: {primary_metrics['f1']}",
        f"Accuracy: {primary_metrics['accuracy']}",
        f"ROC AUC: {primary_metrics['roc_auc']}",
        f"PR AUC: {primary_metrics['pr_auc']:.3f}",
        f"Confusion matrix: TP={primary_metrics['tp']}, FP={primary_metrics['fp']}, "
        f"FN={primary_metrics['fn']}, TN={primary_metrics['tn']}",
        "",
        "The target label is derived from real KITTI object annotations by a fixed rule.",
    ]
    (results_dir / "run_summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
