"""Prepare the real-data KITTI scenario table."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from adas_scenarioguard.experiment import (  # noqa: E402
    SEED,
    build_kitti_scenario_table,
    ensure_kitti_labels,
    mark_splits,
    stratified_split,
    write_csv,
    write_json,
)


def main() -> int:
    data_dir = ROOT / "data"
    processed_dir = data_dir / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)

    label_dir = ensure_kitti_labels(data_dir)
    rows = build_kitti_scenario_table(label_dir)
    split_ids = stratified_split(rows, seed=SEED)
    mark_splits(rows, split_ids)

    csv_path = processed_dir / "kitti_scenarios.csv"
    split_path = processed_dir / "kitti_split.json"
    summary_path = processed_dir / "dataset_summary.json"

    write_csv(csv_path, rows)
    write_json(split_path, split_ids)

    summary = {
        "dataset": "KITTI Object Detection training annotations",
        "source_url": "https://s3.eu-central-1.amazonaws.com/avg-kitti/data_object_label_2.zip",
        "num_scenes": len(rows),
        "positive_critical_scenes": sum(int(row["critical_scene"]) for row in rows),
        "negative_scenes": sum(1 for row in rows if int(row["critical_scene"]) == 0),
        "split_counts": {name: len(ids) for name, ids in split_ids.items()},
        "seed": SEED,
        "label_note": (
            "KITTI does not provide a critical_scene target. The target is derived "
            "by a fixed rule from real KITTI class, distance, lateral position, "
            "occlusion, and truncation annotations."
        ),
    }
    write_json(summary_path, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Saved: {csv_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
