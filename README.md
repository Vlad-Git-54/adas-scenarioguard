# ADAS ScenarioGuard

ADAS ScenarioGuard - исследовательский прототип для обнаружения редких и критических сценариев в мультимодальном восприятии ADAS. Репозиторий подготовлен для ВКР по теме:

> Разработка методов обнаружения и обработки редких и критических сценариев в мультимодальном восприятии систем ADAS для повышения безопасности в сложных погодных и дорожных условиях

Прототип не управляет автомобилем и не является сертифицированной системой безопасности. Его задача - обучить и проверить scenario-level модель, которая по признакам дорожной сцены оценивает риск критического сценария.

## Что реализовано

- подготовка сценарной таблицы из реальных аннотаций KITTI Object Detection `label_2`
- обучение baseline, proposed и ablation моделей logistic regression на NumPy
- подбор порога на validation split
- оценка на test split
- расчет precision, recall, F1, accuracy, FNR, FPR, ROC AUC, PR AUC и FPS
- экспорт confusion matrix, error cases, predictions и run summary
- генерация графиков и диаграмм для ВКР
- CLI demo на JSON-сцене с camera, LiDAR и radar confidence

## Данные

Основной эксперимент использует реальные аннотации KITTI Object Detection:

- официальный бенчмарк: https://www.cvlibs.net/datasets/kitti/eval_object.php?obj_benchmark=3d
- архив разметки: `data_object_label_2.zip`
- размер таблицы после подготовки: 7481 сцена

KITTI не содержит готовую метку `critical_scene`. Поэтому целевая переменная получена фиксированным правилом из реальных аннотаций: класс объекта, 3D-дистанция, боковое положение, occlusion и truncation. Это не оригинальная метка KITTI и не ручная экспертная разметка опасности.

## Установка

```bash
git clone https://github.com/Vlad-Git-54/adas-scenarioguard.git
cd adas-scenarioguard
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m pip install -e .
```

Linux и macOS:

```bash
source .venv/bin/activate
```

Для пересборки презентации нужен Node.js 20 или новее.

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

После запуска создаются:

- `data/processed/kitti_scenarios.csv`
- `data/processed/kitti_split.json`
- `results/models.json`
- `results/metrics.json`
- `results/metrics.csv`
- `results/confusion_matrix.csv`
- `results/error_cases.csv`
- `results/predictions.json`
- `results/run_summary.md`
- `figures/*.png`

## Модели

| Модель | Смысл |
|---|---|
| `baseline_kitti_logreg` | базовые признаки сцены: число объектов, дистанция, фронтальные и уязвимые объекты |
| `proposed_reliability_logreg` | baseline + признаки окклюзии, усечения, proxy-качества камеры и 3D-геометрии, uncertainty и risk prior |
| `ablation_without_3d_geometry` | ablation без ключевых 3D-геометрических признаков |

## Пример входного JSON для CLI demo

```json
{
  "id": "scene_002_fog_pedestrian",
  "weather": "fog",
  "visibility_m": 32,
  "ego_speed_kmh": 38,
  "objects": [
    {
      "id": "ped_01",
      "class": "pedestrian",
      "distance_m": 18,
      "relative_lane": "front",
      "occlusion": 0.25,
      "camera_conf": 0.42,
      "lidar_conf": 0.72,
      "radar_conf": 0.58
    }
  ]
}
```

Запуск demo:

```bash
python scripts/run_demo.py
```

Прямой запуск CLI:

```bash
python -m adas_scenarioguard.cli data/samples/scene_002_fog_pedestrian.json --pretty
```

## Ограничения

- KITTI не содержит radar, поэтому radar используется только в JSON demo, а не в основном KITTI-эксперименте.
- KITTI не содержит готовую метку ADAS critical scene. Метка получена воспроизводимым правилом.
- Модель работает на scenario-level признаках, а не на сырых изображениях и облаках точек.
- Прототип не является сертифицированной системой безопасности.
- Для реального автомобиля нужны испытания на raw sensor data, отказоустойчивость, сертификация и юридическая проверка.
- Доступный GPU AMD Radeon RX 7700 XT может использоваться в следующем этапе для raw image/LiDAR моделей, но текущий табличный эксперимент выполняется на CPU.

## Структура

```text
adas-scenarioguard/
├── src/adas_scenarioguard/
├── scripts/
├── data/samples/
├── data/schema/
├── data/processed/
├── docs/
├── figures/
├── results/
├── tests/
├── README.md
├── CHANGELOG.md
├── LICENSE
└── requirements.txt
```

## Документы

- `docs/reproducibility.md` - команды повторения эксперимента
- `docs/error_analysis.md` - анализ ошибок
- `docs/defense_qna.md` - ответы на вопросы защиты
- `docs/teacher_review.md` - преподавательская проверка готовности
- `docs/originality_report.md` - локальная проверка оригинальности и самоповторов
- `results/run_summary.md` - краткая сводка последнего запуска

## Лицензия

MIT License. См. `LICENSE`.
