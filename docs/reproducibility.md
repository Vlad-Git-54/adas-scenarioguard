# Воспроизводимость эксперимента

Эксперимент обучает легкие scenario-level модели на реальных аннотациях KITTI Object Detection. Сырой архив разметки скачивается автоматически в `data/external` и не добавляется в Git.

## Окружение

- Python: 3.10 или новее
- ОС проверки: Windows
- GPU: не требуется для текущей табличной модели
- Доступный GPU автора: AMD Radeon RX 7700 XT, пригоден для будущих экспериментов через совместимый backend

## Установка

```bash
python -m venv .venv
.venv\Scripts\activate
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
- `Marianovskiy_VKR_ADAS_final.docx` - финальный текст ВКР
- `Marianovskiy_VKR_ADAS_defense_final.pptx` - финальная презентация защиты

## Контрольные значения primary model

- Model: `proposed_reliability_logreg`
- Test examples: 1497
- Precision: 0.885
- Recall: 0.937
- F1: 0.911
- Accuracy: 0.933
- ROC AUC: 0.981
- PR AUC: 0.97
- TP/FP/FN/TN: 509/66/34/888

## Проверка на Windows

Все команды выше выполняются из корня репозитория. Если PowerShell не видит локальный пакет, выполните `python -m pip install -e .` повторно после активации окружения.
