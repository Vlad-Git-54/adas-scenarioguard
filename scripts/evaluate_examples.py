"""Evaluate ADAS ScenarioGuard on control JSON examples."""
from __future__ import annotations

import csv
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adas_scenarioguard.core import evaluate_scene_prediction  # noqa: E402


def safe_div(num: float, den: float) -> float:
    return num / den if den else 0.0


def main() -> int:
    data_dir = ROOT / "data" / "samples"
    result_dir = ROOT / "results"
    result_dir.mkdir(exist_ok=True)

    files = sorted(data_dir.glob("*.json"))
    rows = []
    start = time.perf_counter()
    for path in files:
        with path.open("r", encoding="utf-8") as f:
            scene = json.load(f)
        rows.append(evaluate_scene_prediction(scene))
    elapsed = time.perf_counter() - start

    tp = sum(1 for r in rows if r["y_true"] and r["y_pred"])
    fp = sum(1 for r in rows if not r["y_true"] and r["y_pred"])
    fn = sum(1 for r in rows if r["y_true"] and not r["y_pred"])
    tn = sum(1 for r in rows if not r["y_true"] and not r["y_pred"])

    precision = safe_div(tp, tp + fp)
    recall = safe_div(tp, tp + fn)
    f1 = safe_div(2 * precision * recall, precision + recall)
    fps = safe_div(len(rows), elapsed)
    avg_ms = safe_div(elapsed * 1000.0, len(rows))

    metrics = {
        "note": "Demo counters are calculated on sample JSON scenarios. They illustrate CLI behavior and are separate from the KITTI experiment.",
        "num_examples": len(rows),
        "tp": tp,
        "fp": fp,
        "fn": fn,
        "tn": tn,
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
        "fps_json_pipeline": round(fps, 1),
        "avg_ms_per_scene": round(avg_ms, 4),
    }

    with (result_dir / "demo_metrics.json").open("w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    with (result_dir / "demo_predictions.json").open("w", encoding="utf-8") as f:
        json.dump(rows, f, ensure_ascii=False, indent=2)

    with (result_dir / "demo_metrics.csv").open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["metric", "value"])
        for key, value in metrics.items():
            writer.writerow([key, value])

    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
