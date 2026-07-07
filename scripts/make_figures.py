"""Generate publication-ready figures from experiment results."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
FIGURES = ROOT / "figures"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def save_fig(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(path, dpi=180, bbox_inches="tight")
    plt.close()


def confusion_matrix(metrics: dict) -> None:
    primary = metrics["models"][metrics["primary_model"]]
    values = [[primary["tp"], primary["fn"]], [primary["fp"], primary["tn"]]]
    fig, ax = plt.subplots(figsize=(5.6, 4.6))
    im = ax.imshow(values, cmap="Blues")
    ax.set_xticks([0, 1], labels=["Critical", "OK"])
    ax.set_yticks([0, 1], labels=["Critical", "OK"])
    ax.set_xlabel("Predicted class")
    ax.set_ylabel("Actual class")
    ax.set_title("Confusion matrix on KITTI test split")
    for y, row in enumerate(values):
        for x, value in enumerate(row):
            ax.text(x, y, str(value), ha="center", va="center", fontsize=16, fontweight="bold")
    fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    save_fig(FIGURES / "confusion_matrix.png")


def roc_curve() -> None:
    rows = load_json(RESULTS / "roc_points.json")
    plt.figure(figsize=(5.8, 4.4))
    plt.plot([row["fpr"] for row in rows], [row["tpr"] for row in rows], color="#1f77b4", linewidth=2)
    plt.plot([0, 1], [0, 1], color="#777777", linestyle="--", linewidth=1)
    plt.xlabel("False positive rate")
    plt.ylabel("True positive rate")
    plt.title("ROC curve for proposed model")
    plt.grid(True, alpha=0.25)
    save_fig(FIGURES / "roc_curve.png")


def precision_recall_curve() -> None:
    rows = load_json(RESULTS / "pr_points.json")
    plt.figure(figsize=(5.8, 4.4))
    plt.plot([row["recall"] for row in rows], [row["precision"] for row in rows], color="#2ca02c", linewidth=2)
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall curve for proposed model")
    plt.ylim(0, 1.05)
    plt.grid(True, alpha=0.25)
    save_fig(FIGURES / "precision_recall_curve.png")


def metrics_comparison(metrics: dict) -> None:
    model_order = ["baseline_kitti_logreg", "proposed_reliability_logreg", "ablation_without_3d_geometry"]
    labels = ["Baseline", "Proposed", "Ablation"]
    metric_names = ["precision", "recall", "f1"]
    x = range(len(labels))
    width = 0.22
    plt.figure(figsize=(7.2, 4.4))
    for i, metric in enumerate(metric_names):
        values = [metrics["models"][name][metric] for name in model_order]
        positions = [p + (i - 1) * width for p in x]
        plt.bar(positions, values, width=width, label=metric)
    plt.xticks(list(x), labels)
    plt.ylim(0, 1.05)
    plt.ylabel("Metric value")
    plt.title("Model comparison on KITTI test split")
    plt.legend()
    plt.grid(axis="y", alpha=0.25)
    save_fig(FIGURES / "metrics_comparison.png")


def error_by_condition(metrics: dict) -> None:
    grouped = metrics.get("grouped_metrics", {})
    labels = list(grouped.keys())
    values = [grouped[name]["f1"] for name in labels]
    counts = [grouped[name]["num_examples"] for name in labels]
    readable = [name.replace("_", "\n") for name in labels]
    plt.figure(figsize=(7.4, 4.6))
    bars = plt.bar(readable, values, color="#9467bd")
    for bar, count in zip(bars, counts):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.015, f"n={count}", ha="center", fontsize=9)
    plt.ylim(0, 1.05)
    plt.ylabel("F1")
    plt.title("F1 by scene condition on KITTI test split")
    plt.grid(axis="y", alpha=0.25)
    save_fig(FIGURES / "error_by_condition.png")


def sensor_ablation(metrics: dict) -> None:
    model_order = ["baseline_kitti_logreg", "proposed_reliability_logreg", "ablation_without_3d_geometry"]
    labels = ["Baseline\nbasic features", "Proposed\nquality + geometry", "Ablation\nwithout 3D geometry"]
    f1_values = [metrics["models"][name]["f1"] for name in model_order]
    fnr_values = [metrics["models"][name]["false_negative_rate"] for name in model_order]
    x = range(len(labels))
    plt.figure(figsize=(7.2, 4.6))
    plt.bar([i - 0.18 for i in x], f1_values, width=0.34, label="F1", color="#1f77b4")
    plt.bar([i + 0.18 for i in x], fnr_values, width=0.34, label="FNR", color="#d62728")
    plt.xticks(list(x), labels)
    plt.ylim(0, 1.05)
    plt.title("Feature ablation on KITTI test split")
    plt.ylabel("Metric value")
    plt.legend()
    plt.grid(axis="y", alpha=0.25)
    save_fig(FIGURES / "sensor_ablation.png")


def bevfusion_literature_chart() -> None:
    categories = ["Camera-only\ncamera occlusion", "Fusion\ncamera occlusion", "Fusion\nLiDAR degradation"]
    before = [35.6, 68.5, 68.5]
    after = [20.9, 65.7, 50.1]
    x = range(len(categories))
    plt.figure(figsize=(7.2, 4.6))
    plt.bar([i - 0.18 for i in x], before, width=0.34, label="Before degradation", color="#4c78a8")
    plt.bar([i + 0.18 for i in x], after, width=0.34, label="After degradation", color="#f58518")
    plt.xticks(list(x), categories)
    plt.ylabel("mAP")
    plt.title("Literature example: BEVFusion under sensor degradation")
    plt.figtext(
        0.5,
        -0.02,
        "Data from Kumar et al., 2025. This chart is not an own experiment.",
        ha="center",
        fontsize=9,
    )
    plt.legend()
    plt.grid(axis="y", alpha=0.25)
    save_fig(FIGURES / "bevfusion_literature_chart.png")


def predictions_error_table() -> None:
    predictions = load_json(RESULTS / "predictions.json")["proposed_reliability_logreg"]
    errors = [row for row in predictions if row["error_type"] in {"FP", "FN"}]
    with (RESULTS / "error_cases.csv").open("w", encoding="utf-8", newline="") as f:
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
            writer.writerow({name: row[name] for name in fieldnames})


def main() -> int:
    metrics = load_json(RESULTS / "metrics.json")
    FIGURES.mkdir(exist_ok=True)
    confusion_matrix(metrics)
    roc_curve()
    precision_recall_curve()
    metrics_comparison(metrics)
    error_by_condition(metrics)
    sensor_ablation(metrics)
    bevfusion_literature_chart()
    predictions_error_table()
    print(f"Saved figures to {FIGURES}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
