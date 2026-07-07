# Анализ ошибок

Эксперимент выполнен на test split KITTI scenario table. Primary model: `proposed_reliability_logreg`.

## Матрица ошибок

- TP: 509
- FP: 66
- FN: 34
- TN: 888
- False negative rate: 0.063
- False positive rate: 0.069

## Конкретные ошибки

- `000037`: FP, score=0.825778, distance=10.874 m, vulnerable=0, occluded=1, truncated=1.
- `000147`: FN, score=0.163414, distance=15.107 m, vulnerable=1, occluded=1, truncated=0.
- `000243`: FP, score=0.869779, distance=15.969 m, vulnerable=0, occluded=1, truncated=1.
- `000249`: FN, score=0.168456, distance=8.347 m, vulnerable=0, occluded=2, truncated=1.
- `000435`: FN, score=0.157624, distance=11.271 m, vulnerable=1, occluded=2, truncated=0.
- `000439`: FP, score=0.359672, distance=4.562 m, vulnerable=0, occluded=4, truncated=1.
- `000455`: FP, score=0.834584, distance=10.665 m, vulnerable=0, occluded=4, truncated=0.
- `000632`: FP, score=0.395049, distance=5.106 m, vulnerable=2, occluded=3, truncated=1.
- `000638`: FP, score=0.513686, distance=6.667 m, vulnerable=4, occluded=5, truncated=2.
- `000682`: FP, score=0.669881, distance=6.327 m, vulnerable=0, occluded=1, truncated=1.
- `000876`: FP, score=0.489509, distance=14.217 m, vulnerable=0, occluded=1, truncated=1.
- `000963`: FP, score=0.647849, distance=13.404 m, vulnerable=0, occluded=0, truncated=0.

## False positive

False positive возникают, когда геометрия сцены похожа на опасную: объект близко к траектории, частично перекрыт или имеет высокий risk prior. Для исследовательского прототипа это допустимая осторожная ошибка, но в реальном ADAS частые ложные предупреждения снижают доверие водителя.

## False negative

False negative означает, что опасная сцена не выделена. В текущей постановке FNR равен 0.063. Для дальнейшей проверки нужно добавить отдельный стресс-набор с плохой погодой и отказами сенсоров на реальных или симуляционных данных.

## Ограничения анализа

KITTI не содержит radar и не содержит готовой метки ADAS critical_scene. Поэтому текущая метка критичности получена фиксированным правилом из реальных аннотаций, а не из ручной экспертной разметки опасности.
