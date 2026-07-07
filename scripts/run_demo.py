"""Run a small CLI demo on the JSON sample scene."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    scene = ROOT / "data" / "samples" / "scene_002_fog_pedestrian.json"
    output = ROOT / "results" / "example_output.json"
    command = [
        sys.executable,
        "-m",
        "adas_scenarioguard.cli",
        str(scene),
        "--pretty",
        "--output",
        str(output),
    ]
    completed = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=True)
    demo_dir = ROOT / "demo"
    demo_dir.mkdir(exist_ok=True)
    (demo_dir / "cli_demo.txt").write_text(completed.stdout, encoding="utf-8")
    print(completed.stdout)
    print(f"Saved: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
