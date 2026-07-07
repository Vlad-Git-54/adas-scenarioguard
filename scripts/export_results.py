"""Export human-readable markdown docs from the latest experiment results."""
from __future__ import annotations

import csv
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
DOCS = ROOT / "docs"


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_error_cases() -> list[dict]:
    path = RESULTS / "error_cases.csv"
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_reproducibility(metrics: dict) -> None:
    primary = metrics["models"][metrics["primary_model"]]
    text = f"""# Воспроизводимость эксперимента

Эксперимент обучает легкие scenario-level модели на реальных аннотациях KITTI Object Detection. Сырой архив разметки скачивается автоматически в `data/external` и не добавляется в Git.

## Окружение

- Python: 3.10 или новее
- Node.js: 20 или новее для сборки презентации
- ОС проверки: Windows
- GPU: не требуется для текущей табличной модели
- Доступный GPU автора: AMD Radeon RX 7700 XT, пригоден для будущих экспериментов через совместимый backend

## Установка

```bash
python -m venv .venv
.venv\\Scripts\\activate
python -m pip install -r requirements.txt
python -m pip install -e .
```

## Полный цикл

```bash
python scripts/prepare_data.py
python scripts/train.py
python scripts/evaluate.py
python scripts/make_figures.py
python scripts/make_diagrams.py
python scripts/export_results.py
python scripts/build_documents.py
node scripts/build_presentation.mjs
python -m pytest -q
```

## Где лежат результаты

- `data/processed/kitti_scenarios.csv` - сценарная таблица из KITTI label_2
- `results/models.json` - веса logistic regression и пороги
- `results/metrics.json` - итоговые метрики
- `results/confusion_matrix.csv` - матрица ошибок
- `results/error_cases.csv` - ошибки test split
- `figures/` - графики и схемы
- `submission/Marianovskiy_VKR_ADAS_final_submission.docx` / `.pdf` - финальный текст ВКР
- `submission/Marianovskiy_VKR_ADAS_defense_final_submission.pptx` / `.pdf` - презентация защиты
- `submission/Marianovskiy_zadanie_na_VKR_final_submission.docx` / `.pdf` - задание на ВКР
- `submission/Marianovskiy_competency_index_final_submission.docx` / `.pdf` - предметный указатель компетенций

## Контрольные значения primary model

- Model: `{metrics["primary_model"]}`
- Test examples: {primary["num_examples"]}
- Precision: {primary["precision"]}
- Recall: {primary["recall"]}
- F1: {primary["f1"]}
- Accuracy: {primary["accuracy"]}
- ROC AUC: {primary["roc_auc"]}
- PR AUC: {primary["pr_auc"]}
- TP/FP/FN/TN: {primary["tp"]}/{primary["fp"]}/{primary["fn"]}/{primary["tn"]}

## Проверка на Windows

Все команды выше выполняются из корня репозитория. Если PowerShell не видит локальный пакет, выполните `python -m pip install -e .` повторно после активации окружения.
"""
    (DOCS / "reproducibility.md").write_text(text, encoding="utf-8")


def write_error_analysis(metrics: dict) -> None:
    primary = metrics["models"][metrics["primary_model"]]
    errors = read_error_cases()
    if errors:
        error_lines = [
            f"- `{row['scene_id']}`: {row['error_type']}, score={row['score']}, "
            f"distance={row['min_distance_m']} m, vulnerable={row['vulnerable_count']}, "
            f"occluded={row['occluded_count']}, truncated={row['truncated_count']}."
            for row in errors[:12]
        ]
    else:
        error_lines = ["- На test split ошибок FP/FN не найдено. Для анализа устойчивости нужен отдельный stress split."]

    text = f"""# Анализ ошибок

Эксперимент выполнен на test split KITTI scenario table. Primary model: `{metrics["primary_model"]}`.

## Матрица ошибок

- TP: {primary["tp"]}
- FP: {primary["fp"]}
- FN: {primary["fn"]}
- TN: {primary["tn"]}
- False negative rate: {primary["false_negative_rate"]}
- False positive rate: {primary["false_positive_rate"]}

## Конкретные ошибки

{chr(10).join(error_lines)}

## False positive

False positive возникают, когда геометрия сцены похожа на опасную: объект близко к траектории, частично перекрыт или имеет высокий risk prior. Для исследовательского прототипа это допустимая осторожная ошибка, но в реальном ADAS частые ложные предупреждения снижают доверие водителя.

## False negative

False negative означает, что опасная сцена не выделена. В текущей постановке FNR равен {primary["false_negative_rate"]}. Для дальнейшей проверки нужно добавить отдельный стресс-набор с плохой погодой и отказами сенсоров на реальных или симуляционных данных.

## Ограничения анализа

KITTI не содержит radar и не содержит готовой метки ADAS critical_scene. Поэтому текущая метка критичности получена фиксированным правилом из реальных аннотаций, а не из ручной экспертной разметки опасности.
"""
    (DOCS / "error_analysis.md").write_text(text, encoding="utf-8")


def write_defense_qna(metrics: dict) -> None:
    primary = metrics["models"][metrics["primary_model"]]
    text = f"""# Вопросы и ответы к защите

## 1. Почему это не классическое CV

Классическое CV обычно отвечает на вопрос, где находится объект и к какому классу он относится. В этой работе рассматривается следующий слой: насколько результату восприятия можно доверять и нужно ли пометить сцену как критическую.

## 2. Почему это не полный автопилот

Прототип не управляет автомобилем. Он оценивает риск сцены и может быть использован как вспомогательный модуль тестирования ADAS.

## 3. Почему использованы KITTI-аннотации

KITTI дает реальные дорожные сцены с 2D/3D-разметкой объектов. Это позволяет честно обучить и проверить scenario-level модель без GPU и без скачивания тяжелых изображений.

## 4. Что будет при отказе камеры

В текущем KITTI-эксперименте отказ камеры не измеряется напрямую. В архитектуре прототипа качество камеры учитывается через отдельный reliability-признак, а при отказе система должна повышать uncertainty и переходить к осторожной классификации.

## 5. Что будет при отказе LiDAR

Для реального автомобиля отказ LiDAR снижает надежность 3D-геометрии. В прототипе это отражается через geometry quality и uncertainty. Для промышленного варианта нужна отдельная проверка на датасете с LiDAR dropout.

## 6. Почему важнее recall и false negative rate

Пропуск критической сцены опаснее лишней тревоги. Поэтому для ADAS важен высокий recall и низкий FNR. В текущем test split FNR = {primary["false_negative_rate"]}.

## 7. Чем работа отличается от обычного sensor fusion

Обычный fusion объединяет сигналы для повышения точности детекции. Здесь fusion рассматривается вместе с надежностью, неопределенностью и критичностью сцены.

## 8. Где научная новизна

Новизна состоит в методике scenario-level оценки критичности, где опасная сцена рассматривается как сочетание класса объекта, геометрии, окклюзии, усечения, качества сенсорных признаков и неопределенности.

## 9. Какие ограничения у прототипа

KITTI не содержит radar и не содержит готовой метки critical_scene. Модель проверена как исследовательский прототип и не является сертифицированной системой безопасности.

## 10. Как довести до промышленной проверки

Нужно перейти к raw sensor pipeline, добавить реальные погодные сценарии, radar, LiDAR dropout, калибровку fusion, проверку на nuScenes или собственном полигоне, затем выполнить независимую валидацию и сертификацию.
"""
    (DOCS / "defense_qna.md").write_text(text, encoding="utf-8")


def main() -> int:
    DOCS.mkdir(exist_ok=True)
    metrics = load_json(RESULTS / "metrics.json")
    write_reproducibility(metrics)
    write_error_analysis(metrics)
    write_defense_qna(metrics)
    print(f"Saved markdown docs to {DOCS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
