"""Train lightweight scenario-level models on the KITTI scenario table."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adas_scenarioguard.experiment import model_registry, read_csv, train_named_model, write_json  # noqa: E402


def main() -> int:
    dataset_path = ROOT / "data" / "processed" / "kitti_scenarios.csv"
    if not dataset_path.exists():
        raise SystemExit("Missing data/processed/kitti_scenarios.csv. Run scripts/prepare_data.py first.")

    rows = read_csv(dataset_path)
    trained = {
        "dataset": "KITTI Object Detection training annotations",
        "target": "derived critical_scene label",
        "models": {},
    }
    for name, features in model_registry().items():
        trained["models"][name] = train_named_model(rows, features)

    out_path = ROOT / "results" / "models.json"
    write_json(out_path, trained)
    print(json.dumps({name: spec["validation_metrics"] for name, spec in trained["models"].items()}, indent=2))
    print(f"Saved: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
