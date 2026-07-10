# Changelog

## v1.0.0 - Final VKR release

- Добавлен полный воспроизводимый цикл работы с реальными аннотациями KITTI Object Detection.
- Реализованы `scripts/prepare_data.py`, `scripts/train.py`, `scripts/evaluate.py`, `scripts/make_figures.py`, `scripts/make_diagrams.py`, `scripts/export_results.py` и `scripts/run_demo.py`.
- Добавлено обучение трех scenario-level моделей logistic regression на признаках из KITTI `label_2`.
- Добавлены train, validation и test split с фиксированным seed.
- Добавлены метрики precision, recall, F1, accuracy, FNR, FPR, ROC AUC, PR AUC, FPS и матрица ошибок.
- Добавлены графики confusion matrix, ROC, Precision-Recall, сравнение моделей, анализ условий, ablation и литературный пример BEVFusion.
- Добавлены pipeline, use case, component и deployment diagrams.
- Добавлены документы `docs/reproducibility.md`, `docs/error_analysis.md` и `docs/defense_qna_final.md`.
- Обновлены README, структура проекта и тесты.

## v0.1.0 - Initial JSON demo

- Добавлен CLI для анализа JSON-сцен.
- Реализовано простое объединение оценок camera, LiDAR и radar.
- Добавлен расчет uncertainty и risk score.
- Добавлены 10 контрольных JSON-сцен для демонстрации логики.
- Добавлен скрипт оценки демонстрационных примеров.
