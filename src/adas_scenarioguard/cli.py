"""Command line interface for ADAS ScenarioGuard."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict

from .core import analyze_scene


def load_scene(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def main() -> int:
    parser = argparse.ArgumentParser(description="ADAS ScenarioGuard MVP")
    parser.add_argument("scene", type=Path, help="Path to input scene JSON")
    parser.add_argument("--output", type=Path, default=None, help="Optional output JSON path")
    parser.add_argument("--pretty", action="store_true", help="Print human-readable summary")
    args = parser.parse_args()

    scene = load_scene(args.scene)
    result = analyze_scene(scene)
    result_dict = result.to_dict()

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8") as f:
            json.dump(result_dict, f, ensure_ascii=False, indent=2)

    if args.pretty:
        status = "CRITICAL" if result.scene_is_critical else "OK"
        print(f"Scene: {result.scene_id}")
        print(f"Weather: {result.weather}, visibility: {result.visibility_m} m")
        print(f"Status: {status}, max risk: {result.max_risk_score}")
        for obj in result.objects:
            print(
                f"- {obj.object_id}: {obj.label}, dist={obj.distance_m} m, "
                f"risk={obj.risk_score}, conf={obj.fused_confidence}, "
                f"uncertainty={obj.uncertainty}, critical={obj.is_critical}"
            )
            print(f"  reason: {obj.reason}")
    else:
        print(json.dumps(result_dict, ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
