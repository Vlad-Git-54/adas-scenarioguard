"""Generate readable project diagrams as PNG files."""
from __future__ import annotations

from pathlib import Path
from textwrap import fill

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "figures"

BLUE = "#2563eb"
BLUE_SOFT = "#eff6ff"
GREEN = "#16a34a"
GREEN_SOFT = "#ecfdf5"
AMBER = "#d97706"
AMBER_SOFT = "#fff7ed"
RED = "#dc2626"
RED_SOFT = "#fef2f2"
PURPLE = "#7c3aed"
PURPLE_SOFT = "#f5f3ff"
INK = "#111827"
MUTED = "#64748b"
LINE = "#334155"


def setup(ax, title: str, xlim=(0, 12), ylim=(0, 7)) -> None:
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.axis("off")
    ax.set_title(title, fontsize=18, fontweight="bold", color=INK, pad=14)


def round_box(
    ax,
    x: float,
    y: float,
    w: float,
    h: float,
    title: str,
    subtitle: str = "",
    fc: str = BLUE_SOFT,
    ec: str = BLUE,
    fontsize: int = 10,
    title_size: int = 11,
    wrap: int = 24,
) -> FancyBboxPatch:
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.02,rounding_size=0.12",
        linewidth=1.6,
        edgecolor=ec,
        facecolor=fc,
    )
    ax.add_patch(patch)
    if subtitle:
        ax.text(
            x + w / 2,
            y + h * 0.73,
            fill(title, wrap),
            ha="center",
            va="center",
            fontsize=title_size,
            color=INK,
            fontweight="bold",
            linespacing=1.05,
        )
        ax.text(
            x + w / 2,
            y + h * 0.28,
            fill(subtitle, wrap),
            ha="center",
            va="center",
            fontsize=fontsize,
            color=INK,
            linespacing=1.12,
        )
    else:
        ax.text(
            x + w / 2,
            y + h / 2,
            fill(title, wrap),
            ha="center",
            va="center",
            fontsize=fontsize,
            color=INK,
            linespacing=1.15,
            fontweight="bold",
        )
    return patch


def group_box(ax, x: float, y: float, w: float, h: float, label: str, color: str) -> None:
    patch = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle="round,pad=0.04,rounding_size=0.18",
        linewidth=1.2,
        edgecolor=color,
        facecolor="#ffffff",
        alpha=0.9,
        linestyle="--",
    )
    ax.add_patch(patch)
    ax.text(x + 0.18, y + h + 0.08, label, ha="left", va="bottom", fontsize=10, color=color, fontweight="bold")


def arrow(ax, start, end, color: str = LINE, curved: float = 0.0, dashed: bool = False) -> None:
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=15,
            linewidth=1.5,
            color=color,
            connectionstyle=f"arc3,rad={curved}",
            linestyle="--" if dashed else "-",
        )
    )


def step_badge(ax, x: float, y: float, number: int, color: str = BLUE) -> None:
    circle = FancyBboxPatch(
        (x, y),
        0.42,
        0.42,
        boxstyle="circle,pad=0.03",
        linewidth=0,
        facecolor=color,
    )
    ax.add_patch(circle)
    ax.text(x + 0.21, y + 0.21, str(number), ha="center", va="center", fontsize=10, color="white", fontweight="bold")


def pipeline_diagram() -> None:
    fig, ax = plt.subplots(figsize=(12, 6.2))
    setup(ax, "Pipeline обработки ADAS-сцен")
    steps = [
        ("Данные", "KITTI label_2 или JSON-сцена", BLUE_SOFT, BLUE),
        ("Scenario table", "класс, дистанция, lateral, occlusion", GREEN_SOFT, GREEN),
        ("Признаки", "reliability, uncertainty, risk prior", AMBER_SOFT, AMBER),
        ("Обучение", "baseline, proposed, ablation", PURPLE_SOFT, PURPLE),
        ("Оценка", "threshold, F1, recall, FNR", BLUE_SOFT, BLUE),
        ("Решение", "critical scene или OK", RED_SOFT, RED),
    ]
    xs = [0.35, 2.25, 4.15, 6.05, 7.95, 9.85]
    y = 3.2
    for i, (title, subtitle, fc, ec) in enumerate(steps, 1):
        round_box(ax, xs[i - 1], y, 1.55, 1.25, title, subtitle, fc, ec, fontsize=9, wrap=18)
        step_badge(ax, xs[i - 1] + 0.08, y + 1.08, i, ec)
    for i in range(len(xs) - 1):
        arrow(ax, (xs[i] + 1.55, y + 0.62), (xs[i + 1], y + 0.62))
    notes = [
        ("реальные аннотации", 0.45, 2.25, BLUE),
        ("фиксированный split", 2.55, 2.25, GREEN),
        ("без ручной подгонки", 4.35, 2.25, AMBER),
        ("validation -> test", 7.75, 2.25, BLUE),
        ("ошибки сохраняются", 9.55, 2.25, RED),
    ]
    for text, x, yy, color in notes:
        ax.text(x, yy, text, ha="left", va="center", fontsize=9, color=color, fontweight="bold")
    ax.text(
        6,
        1.15,
        "Смысл схемы: от реальной разметки KITTI строится таблица сценариев, затем модель оценивает риск и сохраняет проверяемые метрики.",
        ha="center",
        va="center",
        fontsize=10,
        color=MUTED,
    )
    save(fig, "pipeline_diagram.png")


def use_case_diagram() -> None:
    fig, ax = plt.subplots(figsize=(11.5, 6.4))
    setup(ax, "Сценарии использования прототипа", xlim=(0, 12), ylim=(0, 7.2))
    actors = [
        ("Исследователь", 0.35, 5.0, BLUE),
        ("Тестировщик ADAS", 0.35, 3.05, GREEN),
        ("Руководитель", 0.35, 1.1, AMBER),
    ]
    for name, x, y, color in actors:
        round_box(ax, x, y, 1.85, 0.82, name, fc="#ffffff", ec=color, fontsize=10, wrap=18)
    researcher = [
        ("Подготовить\nреальную таблицу", 3.0, 5.0, BLUE_SOFT, BLUE),
        ("Обучить\nмодель сценариев", 5.3, 5.0, PURPLE_SOFT, PURPLE),
        ("Оценить\ncritical scenes", 7.6, 5.0, RED_SOFT, RED),
        ("Собрать\nграфики и отчет", 9.85, 5.0, AMBER_SOFT, AMBER),
    ]
    tester = [
        ("Запустить\nJSON demo", 3.0, 3.05, GREEN_SOFT, GREEN),
        ("Разобрать\nFP/FN ошибки", 5.3, 3.05, RED_SOFT, RED),
        ("Проверить\nограничения", 7.6, 3.05, AMBER_SOFT, AMBER),
    ]
    supervisor = [
        ("Проверить\nвоспроизводимость", 3.0, 1.1, BLUE_SOFT, BLUE),
        ("Оценить\nаргументацию", 5.3, 1.1, GREEN_SOFT, GREEN),
        ("Подготовить\nвопросы защиты", 7.6, 1.1, PURPLE_SOFT, PURPLE),
    ]
    lanes = [researcher, tester, supervisor]
    for lane in lanes:
        for text, x, y, fc, ec in lane:
            round_box(ax, x, y, 1.75, 0.82, text, fc=fc, ec=ec, fontsize=9, wrap=15)
        for left, right in zip(lane, lane[1:]):
            arrow(ax, (left[1] + 1.75, left[2] + 0.41), (right[1], right[2] + 0.41))
    for actor, lane in zip(actors, lanes):
        arrow(ax, (actor[1] + 1.85, actor[2] + 0.41), (lane[0][1], lane[0][2] + 0.41), color=actor[3])
    arrow(ax, (8.48, 3.87), (9.85, 5.0), color=AMBER, curved=0.15, dashed=True)
    arrow(ax, (8.48, 1.92), (9.85, 5.0), color=PURPLE, curved=0.22, dashed=True)
    ax.text(6, 0.45, "Связи показаны по ролям, чтобы не перегружать схему пересекающимися линиями.", ha="center", fontsize=9, color=MUTED)
    save(fig, "use_case_diagram.png")


def component_diagram() -> None:
    fig, ax = plt.subplots(figsize=(12, 6.4))
    setup(ax, "Компонентная схема прототипа", xlim=(0, 12), ylim=(0, 7.2))
    group_box(ax, 0.25, 3.95, 3.1, 2.05, "Data layer", BLUE)
    group_box(ax, 4.05, 3.95, 3.6, 2.05, "Experiment layer", GREEN)
    group_box(ax, 8.3, 3.95, 3.35, 2.05, "Result layer", AMBER)
    group_box(ax, 0.25, 1.05, 11.4, 1.85, "Documentation and QA", PURPLE)
    nodes = {
        "parser": ("prepare_data.py", "KITTI parser", 0.55, 4.55, BLUE_SOFT, BLUE),
        "table": ("scenario table", "data/processed + split", 2.05, 4.55, BLUE_SOFT, BLUE),
        "core": ("experiment.py", "features + CLI", 4.35, 4.55, GREEN_SOFT, GREEN),
        "train": ("train.py", "logistic regression", 6.0, 4.55, GREEN_SOFT, GREEN),
        "models": ("models.json", "weights + thresholds", 8.6, 4.55, AMBER_SOFT, AMBER),
        "eval": ("evaluate.py", "metrics + errors", 10.0, 4.55, RED_SOFT, RED),
        "fig": ("figures", "plots + diagrams", 8.55, 1.55, AMBER_SOFT, AMBER),
        "docs": ("docs", "reproducibility + Q&A", 5.0, 1.55, PURPLE_SOFT, PURPLE),
        "final": ("final files", "DOCX, PDF, PPTX", 1.0, 1.55, BLUE_SOFT, BLUE),
    }
    for title, subtitle, x, y, fc, ec in nodes.values():
        round_box(ax, x, y, 1.35, 0.88, title, subtitle, fc, ec, fontsize=8, title_size=9, wrap=16)
    arrow(ax, (1.9, 5.0), (2.05, 5.0))
    arrow(ax, (3.4, 5.0), (4.35, 5.0))
    arrow(ax, (5.7, 5.0), (6.0, 5.0))
    arrow(ax, (7.35, 5.0), (8.6, 5.0))
    arrow(ax, (9.95, 5.0), (10.0, 5.0))
    arrow(ax, (10.68, 4.55), (9.22, 2.43), curved=-0.12)
    arrow(ax, (10.25, 4.55), (5.68, 2.43), curved=-0.18)
    arrow(ax, (5.0, 1.55), (2.35, 1.55), curved=0.0, dashed=True)
    arrow(ax, (8.55, 1.55), (2.35, 1.55), curved=0.12, dashed=True)
    save(fig, "component_diagram.png")


def deployment_diagram() -> None:
    fig, ax = plt.subplots(figsize=(12, 6.4))
    setup(ax, "Схема развертывания", xlim=(0, 12), ylim=(0, 7.2))
    ax.text(0.6, 6.0, "Текущий воспроизводимый контур", fontsize=12, color=GREEN, fontweight="bold")
    ax.text(0.6, 3.05, "Будущее расширение под raw-sensor обучение", fontsize=12, color=PURPLE, fontweight="bold")
    current = [
        ("KITTI labels", "источник реальных аннотаций", 0.65, 4.95, "#f8fafc", MUTED),
        ("Windows workstation", "Python, NumPy, matplotlib", 3.05, 4.95, BLUE_SOFT, BLUE),
        ("CPU experiment", "табличная модель сценариев", 5.55, 4.95, GREEN_SOFT, GREEN),
        ("Results", "metrics, figures, DOCX/PPTX", 8.05, 4.95, AMBER_SOFT, AMBER),
    ]
    future = [
        ("RX 7700 XT", "доступный GPU-ресурс", 3.05, 1.65, PURPLE_SOFT, PURPLE),
        ("DirectML / ROCm path", "зависит от выбранного backend", 5.55, 1.65, PURPLE_SOFT, PURPLE),
        ("Raw sensor model", "images, LiDAR, radar, stress tests", 8.05, 1.65, RED_SOFT, RED),
    ]
    for title, subtitle, x, y, fc, ec in current + future:
        round_box(ax, x, y, 1.85, 0.95, title, subtitle, fc, ec, fontsize=8, title_size=9, wrap=18)
    for left, right in zip(current, current[1:]):
        arrow(ax, (left[2] + 1.85, left[3] + 0.48), (right[2], right[3] + 0.48))
    for left, right in zip(future, future[1:]):
        arrow(ax, (left[2] + 1.85, left[3] + 0.48), (right[2], right[3] + 0.48), color=PURPLE)
    arrow(ax, (6.45, 4.95), (6.45, 2.9), color=PURPLE, curved=0.05, dashed=True)
    ax.text(
        6.1,
        3.58,
        "не влияет на текущие метрики",
        ha="left",
        va="center",
        fontsize=9,
        color=PURPLE,
        fontweight="bold",
    )
    ax.text(
        6,
        0.75,
        "Текущий эксперимент не требует GPU: он проверяет scenario-level методику на CPU. GPU указан только как ресурс следующего этапа.",
        ha="center",
        va="center",
        fontsize=10,
        color=MUTED,
    )
    save(fig, "deployment_diagram.png")


def save(fig, name: str) -> None:
    FIGURES.mkdir(exist_ok=True)
    fig.subplots_adjust(left=0.025, right=0.975, top=0.86, bottom=0.08)
    fig.savefig(FIGURES / name, dpi=220, facecolor="white", bbox_inches="tight")
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
