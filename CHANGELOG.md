# Changelog

## v0.1.0 - MVP

- Добавлен CLI для анализа JSON-сцен.
- Реализовано простое объединение оценок camera, LiDAR и radar.
- Добавлен расчет uncertainty и risk score.
- Добавлены 10 контрольных сценариев для проверки логики.
- Добавлен скрипт оценки precision, recall, F1 и FPS.
- Подготовлены README, LICENSE и demo-скриншот.

## v0.2.0 - планируемые улучшения

- Подключение реальных выходов модели 3D-детекции.
- Поддержка формата nuScenes.
- Экспорт результатов в COCO-style или nuScenes-style JSON.
- Подготовка Dockerfile для edge-запуска.
- Сравнение camera-only, simple fusion и adaptive fusion.
