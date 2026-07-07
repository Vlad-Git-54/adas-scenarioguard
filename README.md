# ADAS ScenarioGuard

Исследовательский прототип для выпускной квалификационной работы по теме:

> Разработка методов обнаружения и обработки редких и критических сценариев в мультимодальном восприятии систем ADAS для повышения безопасности в сложных погодных и дорожных условиях.

Проект проверяет не полный автопилот, а отдельный scenario-level слой оценки критичности дорожной сцены. Модель обучается на признаках, рассчитанных из реальных аннотаций KITTI Object Detection: классы объектов, 2D/3D-геометрия, расстояния, боковое положение, occlusion и truncation. Синтетические сцены для обучения и расчета метрик не используются.

## Данные

Основной эксперимент использует KITTI Object Detection:

- официальный benchmark: <https://www.cvlibs.net/datasets/kitti/eval_object.php?obj_benchmark=3d>
- исходная разметка: `data_object_label_2.zip`
- подготовленная таблица: 7481 сцена
- train/validation/test: 4488 / 1496 / 1497 сцен

В KITTI нет готовой ADAS-метки `critical_scene`. В этой работе она получена воспроизводимым правилом из реальных аннотаций: учитываются класс объекта, расстояние, положение относительно траектории, occlusion и truncation. Поэтому результат следует читать как проверку инженерной методики оценки риска, а не как официальную разметку опасности от авторов KITTI.

## Воспроизведение

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m pip install -e .
```

Полный цикл:

```bash
python scripts/prepare_data.py
python scripts/train.py
python scripts/evaluate.py
python scripts/make_figures.py
python scripts/make_diagrams.py
python scripts/export_report_assets.py
python scripts/export_results.py
python scripts/build_documents.py
node scripts/build_presentation.mjs
python -m pytest -q
```

После запуска формируются таблицы в `data/processed/`, метрики и ошибки в `results/`, графики в `figures/`, а финальный комплект для сдачи в `final/`.

## Модель и метрики

Primary model: `proposed_reliability_logreg`.

| Split | Scenes |
|---|---:|
| Train | 4488 |
| Validation | 1496 |
| Test | 1497 |

| Metric | Value |
|---|---:|
| Precision | 0.885 |
| Recall | 0.937 |
| F1 | 0.911 |
| Accuracy | 0.933 |
| ROC AUC | 0.981 |
| PR AUC | 0.970 |

Confusion matrix on test split: TP = 509, FP = 66, FN = 34, TN = 888.

## Структура

```text
src/adas_scenarioguard/   код прототипа и CLI
scripts/                  подготовка данных, обучение, оценка, графики, документы
data/processed/           подготовленная таблица KITTI и split
data/samples/             небольшие JSON-примеры для CLI
results/                  метрики, predictions, error cases, summaries
figures/                  графики и диаграммы для отчета и презентации
docs/                     воспроизводимость, ограничения, анализ ошибок, вопросы к докладу
tests/                    unit-тесты
final/                    финальные файлы для сдачи
```

## Ограничения

- KITTI не содержит radar, поэтому radar используется только в демонстрационных JSON-примерах, а не в основном KITTI-эксперименте.
- Модель работает с табличными scenario-level признаками, а не с raw image/LiDAR pipeline.
- `critical_scene` является derived target по фиксированному правилу, а не экспертной меткой датасета.
- Прототип не является сертифицированной системой безопасности автомобиля.
- Доступная GPU AMD Radeon RX 7700 XT может быть использована на следующем этапе для тяжелых raw sensor моделей, но текущий воспроизводимый эксперимент не требует GPU.

## Финальные материалы

Файлы для сдачи формируются в `final/`:

- `Marianovskiy_VKR_ADAS_final.docx`
- `Marianovskiy_VKR_ADAS_final.pdf`
- `Marianovskiy_zadanie_na_VKR_final.docx`
- `Marianovskiy_zadanie_na_VKR_final.pdf`
- `Marianovskiy_competency_index_final.docx`
- `Marianovskiy_competency_index_final.pdf`
- `Marianovskiy_VKR_ADAS_defense_final.pptx`
- `Marianovskiy_VKR_ADAS_defense_final.pdf`

## Лицензия

MIT License. См. `LICENSE`.
