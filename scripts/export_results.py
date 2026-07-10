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
- Node.js: 20 или новее для вспомогательных графических скриптов
- ОС проверки: Windows
- Вычислительный контур: CPU-friendly табличная модель

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
python -m pytest -q
```

## Где лежат результаты

- `data/processed/kitti_scenarios.csv` - сценарная таблица из KITTI label_2
- `results/models.json` - веса logistic regression и пороги
- `results/metrics.json` - итоговые метрики
- `results/confusion_matrix.csv` - матрица ошибок
- `results/error_cases.csv` - ошибки test split
- `figures/` - графики и схемы
- `final/Marianovskiy_VKR_ADAS_final.docx` / `.pdf` - финальный текст ВКР
- `final/Marianovskiy_VKR_ADAS_defense_final.pptx` / `.pdf` - финальная презентация
- `final/Marianovskiy_zadanie_na_VKR_final.docx` / `.pdf` - задание на ВКР
- `final/Marianovskiy_competency_index_final.docx` / `.pdf` - предметный указатель компетенций

## Контрольные значения primary model

- Model: `{metrics["primary_model"]}`
- Test examples: {primary["num_examples"]}
- Precision: {primary["precision"]}
- Recall: {primary["recall"]}
- F1: {primary["f1"]}
- Accuracy: {primary["accuracy"]}
- ROC AUC: {primary["roc_auc"]}
- PR AUC: {primary["pr_auc"]:.3f}
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
    text = """# Короткие ответы к защите ВКР

## 1. Почему не классическое CV?

Классическое CV обычно отвечает на вопрос, где находится объект и к какому классу он относится. В этой работе рассматривается следующий слой: насколько сцену нужно считать критической для ADAS с учетом риска, частичной видимости и ненадежности наблюдения.

## 2. Почему logistic regression, а не нейросеть?

Цель эксперимента состояла в проверке scenario-level методики на табличных признаках из аннотаций KITTI. Logistic regression дает интерпретируемые веса, быстро повторяется и не смешивает текущий результат с отдельной задачей обучения raw image detector.

## 3. Почему KITTI, если тема про мультимодальность?

KITTI содержит реальные дорожные сцены, 2D/3D-аннотации и признаки видимости объектов. Этого достаточно для проверки слоя оценки критичности сцены. Полная sensor fusion проверка с radar и временными рядами вынесена в следующий этап.

## 4. Что значит derived critical_scene label?

Это не исходная метка KITTI. Метка построена фиксированным правилом из класса объекта, 3D distance, lateral position, occlusion и truncation. Правило зафиксировано до обучения и одинаково применяется ко всем split.

## 5. Как защищались от утечки данных?

Сначала строится единая таблица сцен, затем выполняется фиксированное разделение на train, validation и test. Стандартизация признаков, обучение модели и выбор порога опираются на train и validation. Test split используется только для финального расчета.

## 6. Почему recall важнее accuracy?

Accuracy может выглядеть высокой даже при пропусках опасных сцен. Для ADAS важнее не пропустить критический случай, поэтому recall и FNR показывают более важную сторону результата.

## 7. Что означает FN в этой задаче?

FN означает сцену, которую fixed rule относит к critical_scene, но модель не подняла флаг риска. В прикладной интерпретации это опаснее лишнего предупреждения.

## 8. Что будет при отказе камеры?

В текущем эксперименте отказ камеры не моделируется как raw sensor failure. На уровне признаков ухудшение наблюдения отражается через occlusion, truncation и reliability proxy. Для промышленной версии нужен отдельный набор данных с отказами.

## 9. Что будет при деградации LiDAR?

В работе используется геометрия из KITTI-аннотаций, а не поток LiDAR. Деградация LiDAR в реальной системе должна снижать надежность 3D-оценки и повышать uncertainty. Это направление нужно проверять в отдельном raw sensor pipeline.

## 10. Почему нет radar в эксперименте?

KITTI Object Detection не содержит radar-канал. Поэтому radar не входит в основной эксперимент и не влияет на метрики. Его можно добавить только при переходе на датасет с соответствующей модальностью, например nuScenes.

## 11. Где научная новизна?

Новизна состоит в scenario-level постановке: критичность сцены оценивается через сочетание класса объекта, геометрии, частичной видимости, reliability, uncertainty и risk prior. Это проверено на реальных KITTI-аннотациях.

## 12. Что является практическим результатом?

Практический результат: воспроизводимый pipeline, который строит таблицу сцен, обучает baseline, proposed и ablation модели, сохраняет метрики, графики и случаи ошибок. Его можно использовать как исследовательский модуль для поиска сложных сцен.

## 13. Что нужно сделать для промышленной версии?

Нужны raw image, LiDAR и radar pipeline, проверка на погодных условиях, отказах сенсоров, временных последовательностях, независимых test sets и инженерная валидация перед применением.

## 14. Можно ли использовать прототип в реальном автомобиле?

Нет. Прототип не управляет автомобилем и не является сертифицированной системой безопасности. Его корректная роль: анализ, тестирование и подготовка сложных сцен для дальнейшей проверки.

## 15. Какие ограничения у работы?

Главные ограничения: derived label вместо экспертной ADAS-разметки, отсутствие radar в KITTI, работа на scenario-level признаках, а не на raw sensor потоках, и отсутствие промышленной safety validation.
"""
    (DOCS / "defense_qna_final.md").write_text(text, encoding="utf-8")


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
