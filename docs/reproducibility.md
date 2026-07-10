# Воспроизводимость эксперимента

Эксперимент обучает легкие scenario-level модели на реальных аннотациях KITTI Object Detection. Сырой архив разметки скачивается автоматически в `data/external` и не добавляется в Git.

## Окружение

- Python: 3.10 или новее
- Node.js: 20 или новее для вспомогательных графических скриптов
- ОС проверки: Windows
- Вычислительный контур: CPU-friendly табличная модель

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

- Model: `proposed_reliability_logreg`
- Test examples: 1497
- Precision: 0.885
- Recall: 0.937
- F1: 0.911
- Accuracy: 0.933
- ROC AUC: 0.981
- PR AUC: 0.970
- TP/FP/FN/TN: 509/66/34/888

## Проверка на Windows

Все команды выше выполняются из корня репозитория. Если PowerShell не видит локальный пакет, выполните `python -m pip install -e .` повторно после активации окружения.
