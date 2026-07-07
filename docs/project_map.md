# Внутренняя карта проекта

## Что уже есть

- Реальный pipeline на KITTI Object Detection annotations.
- CLI demo для JSON-сцен с camera, LiDAR и radar confidence.
- Скрипты подготовки данных, обучения, оценки, графиков, диаграмм и экспорта docs.
- Метрики, матрица ошибок, predictions, error cases и run summary.

## Что можно использовать

- `data/processed/kitti_scenarios.csv` как основной воспроизводимый набор.
- `results/metrics.json` как источник чисел для ВКР и презентации.
- `figures/*.png` как рисунки для ВКР и защиты.
- `docs/reproducibility.md`, `docs/error_analysis.md`, `docs/defense_qna.md` как вспомогательные материалы.

## Что нужно переписать вручную только перед сдачей

- ФИО и точную должность руководителя, если университет требует точное заполнение.
- Подписи и даты в официальных формах.

## Что проверено запуском

- Подготовка KITTI scenario table.
- Обучение трех моделей.
- Оценка test split.
- Генерация графиков и диаграмм.
- Unit-тесты.

## Рисунки

- confusion matrix, ROC, PR curve, metrics comparison, condition analysis, ablation, BEVFusion literature chart.
- pipeline, use case, component, deployment diagrams.

## Документы

- Финальная ВКР, презентация, задание, предметный указатель, checklist.
