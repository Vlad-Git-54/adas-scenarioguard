"""Generate project diagrams as PNG files."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle


ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "figures"


def box(ax, xy, w, h, text, fc="#eef5ff", ec="#2f5d8c", fontsize=9):
    rect = Rectangle(xy, w, h, linewidth=1.3, edgecolor=ec, facecolor=fc)
    ax.add_patch(rect)
    ax.text(xy[0] + w / 2, xy[1] + h / 2, text, ha="center", va="center", fontsize=fontsize, wrap=True)
    return rect


def arrow(ax, start, end):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="->", mutation_scale=13, linewidth=1.2, color="#333333"))


def setup(ax, title):
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    ax.set_title(title, fontsize=13, fontweight="bold")


def pipeline_diagram():
    fig, ax = plt.subplots(figsize=(10, 5.2))
    setup(ax, "ADAS ScenarioGuard pipeline")
    labels = [
        "KITTI annotations\nor JSON scene",
        "Scenario features\nclass, distance,\nocclusion",
        "Reliability proxies\ncamera + 3D geometry",
        "Trained models\nbaseline / proposed",
        "Risk score\nand threshold",
        "Critical scene\nor OK",
    ]
    xs = [0.25, 1.95, 3.65, 5.35, 7.05, 8.55]
    for x, label in zip(xs, labels):
        box(ax, (x, 2.6), 1.25, 1.15, label)
    for i in range(len(xs) - 1):
        arrow(ax, (xs[i] + 1.25, 3.18), (xs[i + 1], 3.18))
    save(fig, "pipeline_diagram.png")


def use_case_diagram():
    fig, ax = plt.subplots(figsize=(9, 5.4))
    setup(ax, "Use case diagram")
    box(ax, (0.45, 4.2), 1.4, 0.7, "Researcher", fc="#fff6e8", ec="#9b6a20")
    box(ax, (0.45, 2.7), 1.4, 0.7, "ADAS tester", fc="#fff6e8", ec="#9b6a20")
    box(ax, (0.45, 1.2), 1.4, 0.7, "Supervisor", fc="#fff6e8", ec="#9b6a20")
    use_cases = [
        ("Prepare real-data table", 3.0, 4.45),
        ("Train scenario model", 5.1, 4.45),
        ("Evaluate critical scenes", 7.2, 4.45),
        ("Inspect errors", 4.0, 2.45),
        ("Generate report figures", 6.2, 2.45),
        ("Review reproducibility", 5.1, 1.05),
    ]
    for text, x, y in use_cases:
        box(ax, (x, y), 1.55, 0.75, text, fc="#eef9f0", ec="#3a7a44")
    for start_y in [4.55, 3.05, 1.55]:
        for _, x, y in use_cases:
            arrow(ax, (1.85, start_y), (x, y + 0.38))
    save(fig, "use_case_diagram.png")


def component_diagram():
    fig, ax = plt.subplots(figsize=(10, 5.2))
    setup(ax, "Component diagram")
    components = [
        ("scripts/prepare_data.py\nKITTI parser", 0.6, 4.0),
        ("data/processed\nscenario table", 3.1, 4.0),
        ("scripts/train.py\nNumPy logreg", 5.6, 4.0),
        ("results/models.json\nweights + threshold", 8.0, 4.0),
        ("scripts/evaluate.py\nmetrics + errors", 5.6, 2.0),
        ("figures/*.png\nplots and diagrams", 8.0, 2.0),
        ("src/adas_scenarioguard\ncore + experiment", 3.1, 2.0),
        ("docs/*.md\nreproducibility", 0.6, 2.0),
    ]
    for text, x, y in components:
        box(ax, (x, y), 1.65, 0.9, text)
    arrow(ax, (2.25, 4.45), (3.1, 4.45))
    arrow(ax, (4.75, 4.45), (5.6, 4.45))
    arrow(ax, (7.25, 4.45), (8.0, 4.45))
    arrow(ax, (8.8, 4.0), (6.4, 2.9))
    arrow(ax, (6.45, 2.45), (8.0, 2.45))
    arrow(ax, (3.9, 2.9), (5.6, 2.45))
    arrow(ax, (5.6, 2.0), (2.25, 2.45))
    save(fig, "component_diagram.png")


def deployment_diagram():
    fig, ax = plt.subplots(figsize=(10, 5.2))
    setup(ax, "Deployment diagram")
    box(ax, (0.6, 3.8), 1.7, 0.9, "Dataset source\nKITTI labels", fc="#f4f6f8", ec="#555555")
    box(ax, (3.0, 3.8), 1.8, 0.9, "Windows workstation\nPython environment", fc="#eef5ff", ec="#2f5d8c")
    box(ax, (5.6, 3.8), 1.8, 0.9, "Training and evaluation\nCPU tabular model", fc="#eef9f0", ec="#3a7a44")
    box(ax, (8.0, 3.8), 1.4, 0.9, "Results\nmetrics + figures", fc="#fff6e8", ec="#9b6a20")
    box(ax, (3.0, 1.6), 1.8, 0.9, "Optional GPU path\nRX7700XT + DirectML", fc="#f7f1ff", ec="#7c4db3")
    box(ax, (5.6, 1.6), 1.8, 0.9, "Future raw-sensor model\nimages / point clouds", fc="#f7f1ff", ec="#7c4db3")
    arrow(ax, (2.3, 4.25), (3.0, 4.25))
    arrow(ax, (4.8, 4.25), (5.6, 4.25))
    arrow(ax, (7.4, 4.25), (8.0, 4.25))
    arrow(ax, (4.8, 2.05), (5.6, 2.05))
    ax.text(4.8, 0.85, "Current experiment does not require GPU. GPU use is documented as future extension.", ha="center", fontsize=9)
    save(fig, "deployment_diagram.png")


def save(fig, name: str) -> None:
    FIGURES.mkdir(exist_ok=True)
    fig.tight_layout()
    fig.savefig(FIGURES / name, dpi=180, bbox_inches="tight")
    plt.close(fig)


def main() -> int:
    pipeline_diagram()
    use_case_diagram()
    component_diagram()
    deployment_diagram()
    print(f"Saved diagrams to {FIGURES}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
