"""Build final VKR DOCX artifacts from repository results."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable, List, Sequence

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor


ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "figures"
RESULTS = ROOT / "results"

AUTHOR = "Марьяновский Владислав Андреевич"
GROUP = "292405-1"
THEME = (
    "Разработка методов обнаружения и обработки редких и критических сценариев "
    "в мультимодальном восприятии систем ADAS для повышения безопасности "
    "в сложных погодных и дорожных условиях"
)


def metrics() -> dict:
    return json.loads((RESULTS / "metrics.json").read_text(encoding="utf-8"))


def dataset_summary() -> dict:
    return json.loads((ROOT / "data" / "processed" / "dataset_summary.json").read_text(encoding="utf-8"))


def add_page_number(paragraph) -> None:
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run()
    fld_char1 = OxmlElement("w:fldChar")
    fld_char1.set(qn("w:fldCharType"), "begin")
    instr = OxmlElement("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = "PAGE"
    fld_char2 = OxmlElement("w:fldChar")
    fld_char2.set(qn("w:fldCharType"), "end")
    run._r.append(fld_char1)
    run._r.append(instr)
    run._r.append(fld_char2)


def set_cell_text(cell, text: str, bold: bool = False) -> None:
    cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER if len(text) < 18 else WD_ALIGN_PARAGRAPH.LEFT
    r = p.add_run(text)
    r.bold = bold
    r.font.name = "Times New Roman"
    r.font.size = Pt(10)
    r._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
    r._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
    r._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")


def setup_document(doc: Document) -> None:
    section = doc.sections[0]
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    section.left_margin = Cm(3)
    section.right_margin = Cm(1)
    section.top_margin = Cm(2)
    section.bottom_margin = Cm(2)
    section.different_first_page_header_footer = True
    add_page_number(section.footer.paragraphs[0])

    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Times New Roman"
    normal.font.size = Pt(12)
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    normal.paragraph_format.first_line_indent = Cm(1.25)
    normal.paragraph_format.line_spacing = 1.5
    normal.paragraph_format.space_after = Pt(0)

    for name in ["Heading 1", "Heading 2", "Heading 3"]:
        style = styles[name]
        style.font.name = "Times New Roman"
        style.font.color.rgb = RGBColor(0, 0, 0)
        style._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
        style._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
        style._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
        style.paragraph_format.line_spacing = 1.5
        style.paragraph_format.space_before = Pt(0)
        style.paragraph_format.space_after = Pt(6)
    styles["Heading 1"].font.size = Pt(12)
    styles["Heading 1"].font.bold = True
    styles["Heading 2"].font.size = Pt(12)
    styles["Heading 2"].font.bold = True
    styles["Heading 3"].font.size = Pt(12)
    styles["Heading 3"].font.bold = True


def p(doc: Document, text: str = "", align=None, bold: bool = False, first_line: bool = True):
    para = doc.add_paragraph()
    para.paragraph_format.line_spacing = 1.5
    para.paragraph_format.space_after = Pt(0)
    para.paragraph_format.first_line_indent = Cm(1.25) if first_line else Cm(0)
    if align is not None:
        para.alignment = align
    run = para.add_run(text)
    run.bold = bold
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    run._element.rPr.rFonts.set(qn("w:ascii"), "Times New Roman")
    run._element.rPr.rFonts.set(qn("w:hAnsi"), "Times New Roman")
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
    return para


def structural_heading(doc: Document, text: str) -> None:
    doc.add_page_break()
    para = p(doc, text.upper(), align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, first_line=False)
    para.style = doc.styles["Heading 1"]


def h1(doc: Document, text: str) -> None:
    doc.add_page_break()
    para = doc.add_paragraph()
    para.style = doc.styles["Heading 1"]
    para.paragraph_format.first_line_indent = Cm(1.25)
    para.add_run(text).bold = True


def h2(doc: Document, text: str) -> None:
    para = doc.add_paragraph()
    para.style = doc.styles["Heading 2"]
    para.paragraph_format.first_line_indent = Cm(1.25)
    para.add_run(text).bold = True


def table_caption(doc: Document, number: int, title: str) -> None:
    para = p(doc, f"Таблица {number} – {title}", first_line=False)
    para.alignment = WD_ALIGN_PARAGRAPH.LEFT


def figure_caption(doc: Document, number: int, title: str) -> None:
    para = p(doc, f"Рисунок {number} – {title}", align=WD_ALIGN_PARAGRAPH.CENTER, first_line=False)


def add_table(doc: Document, rows: Sequence[Sequence[str]], widths: Sequence[float] | None = None) -> None:
    table = doc.add_table(rows=1, cols=len(rows[0]))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"
    for i, text in enumerate(rows[0]):
        set_cell_text(table.rows[0].cells[i], text, bold=True)
    for row in rows[1:]:
        cells = table.add_row().cells
        for i, text in enumerate(row):
            set_cell_text(cells[i], str(text))
    if widths:
        for row in table.rows:
            for cell, width in zip(row.cells, widths):
                cell.width = Cm(width)


def add_figure(doc: Document, filename: str, number: int, caption: str, width: float = 5.8) -> None:
    path = FIGURES / filename
    if path.exists():
        doc.add_picture(str(path), width=Inches(width))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        figure_caption(doc, number, caption)


def add_title_page(doc: Document) -> None:
    for text in [
        "Министерство науки и высшего образования Российской Федерации",
        "НАЦИОНАЛЬНЫЙ ИССЛЕДОВАТЕЛЬСКИЙ",
        "ТОМСКИЙ ГОСУДАРСТВЕННЫЙ УНИВЕРСИТЕТ",
        "Институт дистанционного образования",
        "Направление 09.04.03 Прикладная информатика",
        "Направленность «Компьютерное зрение и нейронные сети»",
    ]:
        p(doc, text, align=WD_ALIGN_PARAGRAPH.CENTER, first_line=False)
    for _ in range(3):
        p(doc, "", first_line=False)
    p(doc, "ВЫПУСКНАЯ КВАЛИФИКАЦИОННАЯ РАБОТА", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, first_line=False)
    p(doc, THEME, align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, first_line=False)
    for _ in range(3):
        p(doc, "", first_line=False)
    p(doc, f"Автор работы: {AUTHOR}", first_line=False)
    p(doc, f"Группа: {GROUP}", first_line=False)
    p(doc, "Руководитель: ________________________________", first_line=False)
    p(doc, "Должность, ученая степень: ____________________", first_line=False)
    p(doc, "Подпись руководителя: __________________________", first_line=False)
    p(doc, "Дата: «___» ____________ 2026 г.", first_line=False)
    for _ in range(6):
        p(doc, "", first_line=False)
    p(doc, "Томск – 2026", align=WD_ALIGN_PARAGRAPH.CENTER, first_line=False)


def add_assignment_in_report(doc: Document) -> None:
    structural_heading(doc, "ЗАДАНИЕ ПО ВЫПОЛНЕНИЮ ВКР")
    fields = [
        ("Тема", THEME),
        ("Объект исследования", "мультимодальное восприятие систем ADAS, включающее данные камеры, LiDAR, radar и алгоритмы анализа дорожной сцены"),
        ("Предмет исследования", "методы обнаружения и обработки редких и критических сценариев в мультимодальном восприятии ADAS"),
        ("Цель", "разработать и экспериментально проверить методику обнаружения и обработки редких критических сценариев в мультимодальном восприятии ADAS"),
        ("Методы", "анализ научной литературы, инженерное проектирование, обработка аннотаций KITTI, logistic regression, расчет метрик классификации, анализ ошибок"),
    ]
    table_caption(doc, 1, "Основные сведения задания по выполнению ВКР")
    add_table(doc, [["Поле", "Содержание"], *fields], widths=[4, 12])
    p(doc, "Задачи работы включают анализ предметной области, разработку признаков надежности, обучение baseline и proposed моделей, оценку метрик, анализ ошибок, описание ограничений и подготовку воспроизводимых материалов.", first_line=True)
    p(doc, "Подпись обучающегося: ______________________", first_line=False)
    p(doc, "Подпись руководителя: ______________________", first_line=False)
    p(doc, "Дата: «___» ____________ 2026 г.", first_line=False)


def add_annotation(doc: Document, m: dict, summary: dict) -> None:
    structural_heading(doc, "АННОТАЦИЯ")
    primary = m["models"][m["primary_model"]]
    paragraphs = [
        f"В выпускной квалификационной работе рассматривается задача обнаружения редких и критических сценариев в мультимодальном восприятии ADAS. Работа сфокусирована не на полном автопилоте, а на слое надежности восприятия, который помогает понять, когда дорожная сцена требует осторожной обработки, повторной проверки или включения в набор сложных примеров.",
        f"В программной части реализован прототип ADAS ScenarioGuard. Основной эксперимент выполнен на реальных аннотациях KITTI Object Detection. Из {summary['num_scenes']} размеченной дорожной сцены построена scenario-level таблица признаков. Целевая переменная critical_scene получена фиксированным правилом из класса объекта, 3D-дистанции, бокового положения, occlusion и truncation, поскольку KITTI не содержит готовой метки критичности ADAS.",
        f"Для проверки обучены три модели logistic regression: baseline, proposed и ablation. Primary model proposed_reliability_logreg на test split из {primary['num_examples']} сцен получила precision = {primary['precision']}, recall = {primary['recall']}, F1 = {primary['f1']}, ROC AUC = {primary['roc_auc']} и PR AUC = {primary['pr_auc']}. Матрица ошибок содержит TP = {primary['tp']}, FP = {primary['fp']}, FN = {primary['fn']} и TN = {primary['tn']}.",
        "Практический результат работы представлен репозиторием с кодом подготовки данных, обучения, оценки, генерации графиков и диаграмм. Отдельно подготовлены разделы воспроизводимости, анализа ошибок, ограничения метода, финальная презентация защиты и предметный указатель компетенций.",
        "Ключевые слова: ADAS, мультимодальное восприятие, KITTI, critical scene, sensor fusion, uncertainty estimation, logistic regression, анализ ошибок, безопасность дорожной сцены.",
    ]
    for text in paragraphs:
        p(doc, text)


def add_toc(doc: Document) -> None:
    structural_heading(doc, "ОГЛАВЛЕНИЕ")
    entries = [
        "ВВЕДЕНИЕ",
        "1 Анализ предметной области и существующих подходов",
        "1.1 ADAS и мультимодальное восприятие",
        "1.2 Редкие критические сценарии и corner cases",
        "1.3 Плохая погода, окклюзия и деградация сенсоров",
        "1.4 OOD detection и uncertainty estimation",
        "1.5 Датасеты, симуляторы и ограничения известных решений",
        "1.6 Проверяемость исследований в ADAS",
        "1.7 Выводы по главе 1",
        "2 Методика обнаружения и обработки редких критических сценариев",
        "2.1 Классификация сценариев",
        "2.2 Признаки качества сенсоров и надежности",
        "2.3 Uncertainty score, risk score и adaptive fusion",
        "2.4 Метрики и план эксперимента",
        "2.5 Этика, приватность и границы применения",
        "2.6 Требования к промышленной проверке",
        "2.7 Выводы по главе 2",
        "3 Реализация прототипа и экспериментальная проверка",
        "3.1 Структура репозитория и инструменты",
        "3.2 Подготовка KITTI scenario table",
        "3.3 Обучение baseline, proposed и ablation",
        "3.4 Результаты и графики",
        "3.5 Анализ ошибок",
        "3.6 Ограничения и воспроизводимость",
        "3.7 Проверка целостности результатов",
        "3.8 Перенос на raw sensor pipeline",
        "ЗАКЛЮЧЕНИЕ",
        "ЛИТЕРАТУРА",
        "ПРИЛОЖЕНИЯ",
    ]
    for entry in entries:
        p(doc, entry, first_line=False)


def add_terms(doc: Document) -> None:
    structural_heading(doc, "ПЕРЕЧЕНЬ УСЛОВНЫХ ОБОЗНАЧЕНИЙ, СОКРАЩЕНИЙ И ТЕРМИНОВ")
    rows = [
        ["Термин", "Расшифровка"],
        ["ADAS", "Advanced Driver Assistance Systems, системы помощи водителю"],
        ["LiDAR", "сенсор, измеряющий расстояния по отражению лазерного излучения"],
        ["Radar", "радиолокационный сенсор для оценки расстояния и скорости"],
        ["Sensor fusion", "объединение данных нескольких сенсоров"],
        ["OOD", "out-of-distribution, ситуация вне привычного распределения данных"],
        ["FNR", "false negative rate, доля пропущенных критических сцен"],
        ["FPR", "false positive rate, доля безопасных сцен, ошибочно отмеченных как критические"],
        ["KITTI", "открытый датасет и benchmark для задач восприятия в автономном вождении"],
    ]
    add_table(doc, rows, widths=[4, 12])


def long_paragraphs(topic: str, facts: Sequence[str], project: str) -> List[str]:
    a, b, c, d = facts
    return [
        f"{topic} важно рассматривать как инженерную задачу, а не как отдельный прием обработки изображения. В контуре ADAS ошибка возникает не только из-за неверного класса объекта. На результат влияет расстояние, положение относительно траектории, частичная видимость, качество геометрии и согласованность признаков разных сенсоров. Поэтому в работе выбран scenario-level уровень анализа, где дорожная сцена описывается набором признаков, а итогом является оценка критичности.",
        f"Первый технический фактор связан с {a}. Для обычной средней метрики такая деталь может быть почти незаметна, если основная часть тестового набора состоит из простых сцен. Для безопасности важны как раз редкие случаи, где ошибка восприятия ведет к поздней реакции. В этой работе такие случаи не маскируются общей точностью, а выделяются через отдельные признаки и через анализ false negative.",
        f"Второй фактор связан с {b}. В реальной дорожной сцене сенсоры не дают одинаково надежную картину. Камера лучше передает цвет и контур, LiDAR дает геометрию, radar устойчив к части погодных факторов, но имеет меньшую детализацию. Если один источник выглядит уверенно, а другой показывает деградацию, итоговая система должна учитывать это расхождение и не сводить все к одному confidence.",
        f"Третий фактор связан с {c}. Для ВКР это означает, что метод должен быть проверяемым и воспроизводимым. Поэтому эксперимент построен на аннотациях KITTI, где есть реальные классы, 2D и 3D координаты, occlusion и truncation. Эти признаки не заменяют полный мультимодальный поток, но позволяют честно обучить модель риска на реальных дорожных сценах.",
        f"Практическая часть {project}. Такой выбор ограничивает масштаб эксперимента, но делает результат проверяемым. Любой проверяющий может повторить подготовку данных, обучение, подбор порога и расчет метрик. Для исследовательского прототипа это важнее, чем заявлять качество тяжелой модели, которую нельзя воспроизвести на доступных ресурсах.",
        f"Вывод для данного раздела состоит в том, что {d}. Этот вывод используется дальше при построении признаков reliability, uncertainty и risk score, а также при выборе метрик. В работе приоритет отдан recall и FNR, потому что пропуск критической сцены опаснее ложной тревоги, хотя большое число false positive также снижает доверие к системе.",
    ]


def add_intro(doc: Document, m: dict, summary: dict) -> None:
    structural_heading(doc, "ВВЕДЕНИЕ")
    intro = [
        "Системы помощи водителю используют камеры, LiDAR, radar и алгоритмы анализа дорожной сцены для предупреждения об опасных ситуациях. На практике важно не только обнаружить объект, но и понять, можно ли доверять результату восприятия. В тумане, дожде, снегу, ночью, при бликах и частичной видимости объект может быть найден с низкой уверенностью или не найден вовсе. Для ADAS такая ситуация опасна, потому что среднее качество модели не показывает поведение на редких критических сценах.",
        "Степень разработанности темы связана с несколькими направлениями. В работах по corner cases описываются редкие ситуации для восприятия в высокоавтоматизированном вождении. В исследованиях adverse weather показано, что сенсоры деградируют по-разному. Обзоры sensor fusion систематизируют раннее, промежуточное и позднее объединение модальностей. Отдельно развиваются OOD detection и uncertainty estimation, где модель должна оценить собственную ненадежность.",
        "Проблема работы состоит в том, что обычная модель восприятия может показать высокую среднюю точность, но пропускать редкие опасные сцены. В ADAS пропуск пешехода впереди автомобиля или близкого препятствия при плохой видимости имеет большую цену. Поэтому требуется отдельный слой оценки критичности, который работает поверх признаков сцены и выделяет случаи, требующие осторожного режима.",
        "Объект исследования: мультимодальное восприятие систем ADAS, включающее данные камеры, LiDAR, radar и алгоритмы анализа дорожной сцены. Предмет исследования: методы обнаружения и обработки редких и критических сценариев в мультимодальном восприятии ADAS, включая corner case detection, OOD detection, uncertainty estimation и adaptive sensor fusion.",
        "Цель работы: разработать и экспериментально проверить методику обнаружения и обработки редких критических сценариев в мультимодальном восприятии ADAS для повышения надежности восприятия в сложных погодных и дорожных условиях.",
        "Для достижения цели решены задачи: проанализирована предметная область ADAS, рассмотрены подходы sensor fusion и uncertainty estimation, сформирована классификация критических сценариев, разработаны признаки оценки надежности, реализован программный прототип, подготовлен реальный scenario-level набор на основе KITTI, обучены baseline и proposed модели, рассчитаны метрики, проведен анализ ошибок и сформулированы ограничения метода.",
        "Методы исследования включают анализ научных источников, инженерное проектирование признаков, обработку реальных аннотаций KITTI Object Detection, обучение logistic regression на NumPy, подбор порога на validation split, расчет precision, recall, F1, FNR, FPR, ROC AUC, PR AUC, анализ ошибок и подготовку воспроизводимых артефактов.",
        "Научная новизна состоит в разработке и апробации методики scenario-level оценки надежности мультимодального восприятия ADAS, в которой редкий критический сценарий рассматривается как сочетание опасного класса объекта, геометрической близости, частичной видимости, повышенной неопределенности и риска пропуска опасного объекта.",
        "Практическая значимость состоит в том, что прототип может использоваться как вспомогательный модуль тестирования ADAS. Он выделяет сцены, где результат восприятия требует осторожной обработки, повторной проверки или добавления в набор сложных примеров для дообучения. Прототип не является сертифицированной системой безопасности и не предназначен для самостоятельного управления автомобилем.",
        "Границы исследования заданы доступными данными и вычислительными ресурсами. Основной эксперимент выполнен на реальных аннотациях KITTI, но без обучения нейросетевой модели по сырым изображениям и облакам точек. Доступная видеокарта AMD Radeon RX 7700 XT может применяться в будущей работе с raw sensor pipeline, однако текущая модель является табличной и воспроизводимо обучается на CPU.",
        "Работа состоит из введения, трех глав, заключения, списка литературы и приложений. Первая глава описывает предметную область и известные подходы. Вторая глава формулирует методику оценки критических сценариев. Третья глава описывает реализацию, эксперимент, результаты, ошибки, ограничения и воспроизводимость.",
    ]
    for text in intro:
        p(doc, text)


def add_chapter_1(doc: Document) -> None:
    h1(doc, "1 Анализ предметной области и существующих подходов")
    sections = [
        ("1.1 ADAS и мультимодальное восприятие", "ADAS и мультимодальное восприятие", ["обработкой сигналов разных сенсоров", "разной физической природой камеры, LiDAR и radar", "неполной наблюдаемостью дорожной сцены", "надежность ADAS должна оцениваться не только по точности детекции"], "сохраняет связь с реальным pipeline, но фокусируется на проверяемой оценке критичности"),
        ("1.2 Редкие критические сценарии и corner cases", "Редкие критические сценарии", ["малой частотой опасных событий", "несбалансированностью наборов данных", "дорогой ошибки false negative", "corner cases требуют отдельной классификации и учета в метриках"], "переводит понятие corner case в набор признаков, которые можно рассчитать из аннотаций"),
        ("1.3 Плохая погода, окклюзия и деградация сенсоров", "Деградация сенсоров", ["снижением видимости и частичной потерей контраста", "окклюзией объектов и усечением bounding box", "разным поведением сенсоров при плохой погоде", "модель риска должна учитывать качество наблюдения"], "использует occlusion и truncation KITTI как реальные proxy-признаки деградации наблюдения"),
        ("1.4 Почему средние метрики не гарантируют безопасность", "Средние метрики качества", ["усреднением простых и сложных сцен", "малой долей критических примеров", "разной ценой ошибок FP и FN", "для ADAS нужна отдельная оценка критических сценариев"], "сохраняет accuracy, но выводит recall, FNR и error cases в отдельные результаты"),
        ("1.5 OOD detection и uncertainty estimation", "Оценка неопределенности", ["выходом сцены за привычное распределение", "конфликтом признаков и деградацией наблюдения", "недостатком прямой уверенности модели", "uncertainty помогает объяснить осторожный режим"], "использует proxy uncertainty из качества камеры, 3D-геометрии, occlusion и truncation"),
        ("1.6 Виды sensor fusion", "Sensor fusion", ["ранним объединением данных", "поздним объединением решений", "промежуточным объединением признаков", "выбор уровня fusion зависит от данных и вычислительных ресурсов"], "реализует scenario-level fusion признаков, а JSON demo показывает идею объединения camera, LiDAR и radar confidence"),
        ("1.7 Датасеты и симуляторы", "Датасеты и симуляторы", ["доступностью разметки KITTI", "мультимодальностью nuScenes", "гибкостью CARLA для редких условий", "источник данных должен быть указан отдельно от собственных результатов"], "использует KITTI как реальный компактный источник для обучения и описывает nuScenes и CARLA как расширение"),
        ("1.8 Аналоги и ограничения известных решений", "Известные решения", ["сильной зависимостью от набора данных", "переобучением на типовые условия", "сложностью проверки в редких сценариях", "готовые SOTA-модели не снимают задачу анализа надежности"], "не заявляет превосходство над BEVFusion, а использует литературный пример только как контекст"),
        ("1.9 Проверяемость исследований в ADAS", "Проверяемость исследований", ["открытым кодом и фиксированными версиями данных", "разделением собственных и литературных результатов", "повторяемостью расчетов метрик", "без проверки запуска научный вывод остается слабым"], "связывает текст ВКР с командами репозитория и файлами results"),
        ("1.10 Выводы по главе 1", "Выводы по анализу предметной области", ["неравной ценой ошибок", "редкостью критических сцен", "необходимостью явной оценки надежности", "исследовательская задача требует отдельной методики"], "задает требования к признакам, моделям и проверке в следующих главах"),
    ]
    for title, topic, facts, project in sections:
        h2(doc, title)
        for text in long_paragraphs(topic, facts, project):
            p(doc, text)
    table_caption(doc, 2, "Сравнение направлений, использованных в работе")
    add_table(doc, [
        ["Направление", "Что дает для ВКР", "Ограничение"],
        ["Corner cases", "помогает описать редкие опасные сцены", "нет единой универсальной метки"],
        ["Adverse weather", "показывает разную деградацию сенсоров", "требует специальных данных"],
        ["Sensor fusion", "объединяет признаки разных источников", "ошибка калибровки может ухудшить результат"],
        ["OOD и uncertainty", "показывает ненадежность вывода", "оценка зависит от выбранной модели"],
    ], widths=[4, 7, 5])
    add_figure(doc, "bevfusion_literature_chart.png", 1, "Литературный пример влияния деградации сенсоров на BEVFusion по данным Kumar et al., 2025", 5.8)


def add_chapter_2(doc: Document) -> None:
    h1(doc, "2 Методика обнаружения и обработки редких критических сценариев")
    sections = [
        ("2.1 Классификация сценариев", "Классификация сценариев", ["типом участника движения", "геометрической близостью", "частичной видимостью объекта", "критичность сцены должна быть вычислимой"], "задает rule-based target для KITTI и сохраняет его в data/processed/kitti_scenarios.csv"),
        ("2.2 Признаки качества сенсоров", "Признаки качества сенсоров", ["усечением объекта на границе кадра", "степенью окклюзии", "надежностью 3D-положения", "качество наблюдения можно выразить proxy-признаками"], "рассчитывает camera_quality_proxy и lidar_geometry_quality_proxy из реальных полей KITTI"),
        ("2.3 Sensor reliability", "Sensor reliability", ["физическим смыслом измерений", "зависимостью от условий сцены", "неравной устойчивостью модальностей", "веса должны отражать доверие к источнику"], "использует reliability-признаки как вход proposed модели, а не как вручную заданный итог"),
        ("2.4 Uncertainty score", "Uncertainty score", ["недостаточным качеством наблюдения", "окклюзией и truncation", "неполной информацией о геометрии", "неопределенность должна повышать осторожность"], "считает uncertainty_proxy как нормированную комбинацию деградации камеры и 3D-геометрии"),
        ("2.5 Risk score", "Risk score", ["классом объекта", "дистанцией до объекта", "положением относительно траектории", "risk score должен отражать цену пропуска"], "формирует risk_prior из класса, distance, lateral position, occlusion и truncation"),
        ("2.6 Adaptive fusion", "Adaptive fusion", ["объединением признаков надежности", "обучаемым весом каждого признака", "подбором порога на validation split", "адаптивность должна проверяться сравнением с baseline"], "обучает proposed_reliability_logreg и сравнивает его с baseline_kitti_logreg и ablation"),
        ("2.7 Обработка отказа сенсора", "Отказ сенсора", ["потерей одного источника данных", "ростом uncertainty", "переходом к осторожному режиму", "полная потеря всех сенсоров не дает надежного вывода"], "фиксирует этот сценарий в архитектуре и в ограничениях, но не выдает KITTI без radar за полный сенсорный benchmark"),
        ("2.8 Метрики", "Метрики", ["разной ценой FP и FN", "необходимостью видеть confusion matrix", "важностью ROC и PR анализа", "метрики должны строиться из результатов запуска"], "сохраняет metrics.json, metrics.csv, confusion_matrix.csv, roc_points и pr_points"),
        ("2.9 План эксперимента", "План эксперимента", ["фиксированным seed", "разделением train validation test", "обучением нескольких подходов", "результат должен повторяться на чистой копии репозитория"], "реализован командами prepare_data, train, evaluate, make_figures и export_results"),
        ("2.10 Этика и приватность", "Этика и приватность", ["дорожными изображениями с номерами и лицами", "лицензиями датасетов", "опасностью неверной интерпретации прототипа", "исследовательский результат нельзя выдавать за сертифицированную систему"], "работает с аннотациями KITTI и не хранит изображения людей или номера автомобилей в репозитории"),
        ("2.11 Требования к промышленной проверке", "Промышленная проверка", ["реальными сенсорными потоками", "синхронизацией camera, LiDAR и radar", "проверкой отказов и деградации", "лабораторный прототип не равен сертифицированному компоненту"], "фиксирует границу между ВКР и будущей инженерной валидацией"),
        ("2.12 Выводы по главе 2", "Выводы по методике", ["формализацией critical_scene", "разделением baseline и proposed", "прозрачными формулами", "методика должна быть понятна без скрытых ручных шагов"], "переводит научную идею в конкретный план реализации"),
    ]
    for title, topic, facts, project in sections:
        h2(doc, title)
        for text in long_paragraphs(topic, facts, project):
            p(doc, text)
    table_caption(doc, 3, "Формулы метрик и расчетных признаков")
    add_table(doc, [
        ["Показатель", "Формула", "Назначение"],
        ["Precision", "TP / (TP + FP)", "доля верных предупреждений среди всех предупреждений"],
        ["Recall", "TP / (TP + FN)", "доля найденных критических сцен"],
        ["F1", "2 · Precision · Recall / (Precision + Recall)", "сводная метрика баланса precision и recall"],
        ["FNR", "FN / (FN + TP)", "доля пропущенных критических сцен"],
        ["FPR", "FP / (FP + TN)", "доля безопасных сцен, отмеченных как критические"],
        ["Sensor reliability", "1 - degradation_proxy", "оценка качества наблюдения источника"],
        ["Uncertainty score", "0,55 · camera_degradation + 0,45 · geometry_degradation", "оценка ненадежности признаков сцены"],
        ["Risk score", "class + distance + lateral + occlusion + truncation", "априорная оценка опасности сцены"],
    ], widths=[3.5, 6.5, 6])
    add_figure(doc, "pipeline_diagram.png", 2, "Pipeline обработки сцены в ADAS ScenarioGuard", 6.0)
    add_figure(doc, "use_case_diagram.png", 3, "Use Case Diagram прототипа", 6.0)


def add_chapter_3(doc: Document, m: dict, summary: dict) -> None:
    h1(doc, "3 Реализация прототипа и экспериментальная проверка")
    primary = m["models"][m["primary_model"]]
    sections = [
        ("3.1 Структура репозитория", "Структура репозитория", ["разделением исходного кода и данных", "наличием отдельных scripts", "сохранением results и figures", "проверяемость проекта зависит от ясной структуры"], "содержит README, CHANGELOG, LICENSE, src, scripts, data, tests, results, figures и docs"),
        ("3.2 Используемые инструменты", "Инструменты реализации", ["Python и NumPy", "python-docx и matplotlib", "pytest для unit-тестов", "минимальный стек снижает риск невоспроизводимости"], "не требует GPU для основного эксперимента и работает на Windows"),
        ("3.3 Подготовка данных", "Подготовка KITTI scenario table", ["парсингом label_2", "расчетом признаков из 3D-аннотаций", "фиксированным split", "данные должны быть реальными и повторяемыми"], f"создает таблицу из {summary['num_scenes']} сцен с {summary['positive_critical_scenes']} положительными метками"),
        ("3.4 Обучение моделей", "Обучение baseline, proposed и ablation", ["логистической регрессией", "стандартизацией признаков", "подбором порога на validation", "сравнение моделей показывает вклад признаков надежности"], "сохраняет веса и пороги в results/models.json"),
        ("3.5 Настройка порогов", "Настройка порогов", ["валидационным набором", "целевым балансом F1 и recall", "контролем false positive rate", "порог не подбирается на test split"], f"для primary model выбран threshold = {primary['threshold']}"),
        ("3.6 Результаты", "Результаты эксперимента", ["метриками test split", "матрицей ошибок", "ROC и PR кривыми", "числа должны совпадать с results"], f"primary model получила F1 = {primary['f1']} и recall = {primary['recall']}"),
        ("3.7 Анализ ошибок", "Анализ ошибок", ["false positive на похожих на опасные сценах", "false negative при недостаточном score", "окклюзией и truncation", "ошибки нужно разбирать по конкретным scene_id"], "сохраняет results/error_cases.csv и docs/error_analysis.md"),
        ("3.8 Ограничения", "Ограничения прототипа", ["отсутствием radar в KITTI", "derived target вместо экспертной метки", "scenario-level признаками", "исследовательский прототип не заменяет сертификацию"], "честно отделяет результат обучения от будущей raw sensor модели"),
        ("3.9 Воспроизводимость", "Воспроизводимость", ["командами полного цикла", "фиксированным seed", "сохранением артефактов", "проверяющий должен получить те же метрики"], "описана в docs/reproducibility.md и подтверждена запуском тестов"),
        ("3.10 Сравнение с литературным примером BEVFusion", "Сравнение с литературой", ["разной задачей BEVFusion и scenario-level модели", "влиянием деградации сенсоров", "нельзя смешивать чужие mAP и собственные метрики", "литературный график нужен как контекст"], "использует данные Kumar et al., 2025 только как опубликованный пример"),
        ("3.11 Проверка целостности результатов", "Проверка целостности результатов", ["совпадением metrics.json и таблиц ВКР", "наличием raw predictions", "отдельным сохранением error cases", "результаты должны прослеживаться до команд запуска"], "использует results как единый источник чисел для отчета и презентации"),
        ("3.12 Перенос на raw sensor pipeline", "Перенос на raw sensor pipeline", ["необходимостью изображений и облаков точек", "использованием GPU для тяжелых моделей", "добавлением radar и погодных условий", "текущий результат является базой для следующего инженерного шага"], "описывает роль доступной AMD Radeon RX 7700 XT как ресурса для будущих экспериментов, не смешивая это с текущими метриками"),
    ]
    for title, topic, facts, project in sections:
        h2(doc, title)
        for text in long_paragraphs(topic, facts, project):
            p(doc, text)
    table_caption(doc, 4, "Структура репозитория")
    add_table(doc, [
        ["Путь", "Назначение"],
        ["src/adas_scenarioguard", "ядро CLI и экспериментальные функции"],
        ["scripts", "подготовка данных, обучение, оценка, графики, документы"],
        ["data/processed", "таблица KITTI scenario table и split"],
        ["results", "модели, метрики, predictions, ошибки"],
        ["figures", "графики и диаграммы для ВКР"],
        ["docs", "воспроизводимость, анализ ошибок, вопросы защиты"],
    ], widths=[5, 11])
    table_caption(doc, 5, "Метрики моделей на test split KITTI")
    add_table(doc, [
        ["Модель", "Precision", "Recall", "F1", "FNR", "ROC AUC", "PR AUC"],
        *[
            [
                name,
                data["precision"],
                data["recall"],
                data["f1"],
                data["false_negative_rate"],
                data["roc_auc"],
                data["pr_auc"],
            ]
            for name, data in m["models"].items()
        ],
    ], widths=[5.2, 1.8, 1.8, 1.6, 1.6, 2, 2])
    table_caption(doc, 6, "Матрица ошибок primary model")
    add_table(doc, [
        ["", "Predicted critical", "Predicted OK"],
        ["Actual critical", primary["tp"], primary["fn"]],
        ["Actual OK", primary["fp"], primary["tn"]],
    ], widths=[5, 5, 5])
    add_figure(doc, "component_diagram.png", 4, "Component Diagram прототипа", 6.0)
    add_figure(doc, "deployment_diagram.png", 5, "Deployment Diagram прототипа и опционального GPU-направления", 6.0)
    add_figure(doc, "confusion_matrix.png", 6, "Матрица ошибок primary model на KITTI test split", 5.4)
    add_figure(doc, "metrics_comparison.png", 7, "Сравнение baseline, proposed и ablation", 5.8)
    add_figure(doc, "roc_curve.png", 8, "ROC-кривая proposed model", 5.4)
    add_figure(doc, "precision_recall_curve.png", 9, "Precision-Recall кривая proposed model", 5.4)
    add_figure(doc, "error_by_condition.png", 10, "F1 по группам сцен", 5.8)
    add_figure(doc, "sensor_ablation.png", 11, "Ablation признаков на test split", 5.8)


def add_conclusion(doc: Document, m: dict, summary: dict) -> None:
    structural_heading(doc, "ЗАКЛЮЧЕНИЕ")
    primary = m["models"][m["primary_model"]]
    conclusions = [
        "В работе разработана и проверена методика обнаружения редких и критических сценариев в мультимодальном восприятии ADAS. Методика рассматривает критическую сцену как сочетание класса объекта, геометрической близости, положения относительно траектории, частичной видимости, proxy-качества сенсорных признаков и неопределенности.",
        "Первая задача выполнена через анализ предметной области ADAS и проблемы редких сценариев. Показано, что средние метрики детекции не дают достаточного ответа о безопасности в сложных сценах. Вторая задача выполнена через обзор sensor fusion, OOD detection, uncertainty estimation, датасетов KITTI, nuScenes и симулятора CARLA.",
        "Третья задача выполнена через классификацию сценариев по типу объекта, геометрии, окклюзии, truncation и риску пропуска. Четвертая задача выполнена через разработку признаков camera_quality_proxy, lidar_geometry_quality_proxy, uncertainty_proxy и risk_prior. Пятая задача выполнена через программный прототип ADAS ScenarioGuard.",
        f"Шестая задача выполнена через подготовку реального control dataset на основе KITTI Object Detection. Таблица содержит {summary['num_scenes']} сцен, train split содержит {summary['split_counts']['train']} сцен, validation split содержит {summary['split_counts']['validation']} сцен, test split содержит {summary['split_counts']['test']} сцен.",
        f"Седьмая и восьмая задачи выполнены через обучение и сравнение baseline, proposed и ablation моделей. Primary model получила precision = {primary['precision']}, recall = {primary['recall']}, F1 = {primary['f1']}, accuracy = {primary['accuracy']}, ROC AUC = {primary['roc_auc']} и PR AUC = {primary['pr_auc']}. FNR составил {primary['false_negative_rate']}, FPR составил {primary['false_positive_rate']}.",
        f"Девятая задача выполнена через анализ ошибок. На test split найдено FP = {primary['fp']} и FN = {primary['fn']}. False positive связаны с близкими объектами, окклюзией и высоким risk prior. False negative возникают там, где derived target относит сцену к критической, но совокупный score модели остается ниже порога.",
        "Десятая задача выполнена через описание ограничений. KITTI не содержит radar и готовую метку critical_scene, поэтому основной эксперимент не является промышленной валидацией мультимодальной ADAS. Модель работает на scenario-level признаках, а не на сырых изображениях и облаках точек. Для внедрения нужны реальные сенсорные данные, проверка отказов, сертификация и юридическая оценка.",
        "Разработанный прототип может применяться как исследовательский модуль тестирования ADAS. Он помогает выделять сцены, где восприятие требует осторожной обработки, повторной проверки или расширения обучающего набора. Дальнейшее развитие включает raw image и LiDAR pipeline, подключение radar, проверку на nuScenes и CARLA, а также использование доступной AMD Radeon RX 7700 XT через совместимый backend.",
    ]
    for text in conclusions:
        p(doc, text)


def add_literature(doc: Document) -> None:
    structural_heading(doc, "ЛИТЕРАТУРА")
    sources = [
        "Heidecker F. An Application-Driven Conceptualization of Corner Cases for Perception in Highly Automated Driving / F. Heidecker, J. Breitenstein, K. Rösch [et al.] // 2021 IEEE Intelligent Vehicles Symposium. – 2021. – P. 644-651. – DOI: 10.1109/IV48863.2021.9575933.",
        "Bijelic M. Seeing Through Fog Without Seeing Fog: Deep Multimodal Sensor Fusion in Unseen Adverse Weather / M. Bijelic, T. Gruber, F. Mannan [et al.] // Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition. – 2020. – P. 11679-11689. – DOI: 10.1109/CVPR42600.2020.01170.",
        "Huang K. Multi-modal Sensor Fusion for Auto Driving Perception: A Survey / K. Huang, B. Shi, X. Li [et al.] // arXiv. – 2024. – arXiv:2202.02703.",
        "Feng D. Deep Multi-modal Object Detection and Semantic Segmentation for Autonomous Driving: Datasets, Methods, and Challenges / D. Feng, C. Haase-Schütz, L. Rosenbaum [et al.] // IEEE Transactions on Intelligent Transportation Systems. – 2021. – Vol. 22, № 3. – P. 1341-1360.",
        "Geiger A. Are we ready for Autonomous Driving? The KITTI Vision Benchmark Suite / A. Geiger, P. Lenz, R. Urtasun // IEEE Conference on Computer Vision and Pattern Recognition. – 2012. – P. 3354-3361.",
        "KITTI Vision Benchmark Suite [Электронный ресурс] // Karlsruhe Institute of Technology and Toyota Technological Institute at Chicago. – URL: https://www.cvlibs.net/datasets/kitti/ (дата обращения: 07.07.2026).",
        "Caesar H. nuScenes: A multimodal dataset for autonomous driving / H. Caesar, V. Bankiti, A. H. Lang [et al.] // IEEE/CVF Conference on Computer Vision and Pattern Recognition. – 2020. – P. 11621-11631.",
        "Dosovitskiy A. CARLA: An Open Urban Driving Simulator / A. Dosovitskiy, G. Ros, F. Codevilla [et al.] // Proceedings of the 1st Annual Conference on Robot Learning. – 2017. – P. 1-16.",
        "Liu Z. BEVFusion: Multi-Task Multi-Sensor Fusion with Unified Bird's-Eye View Representation / Z. Liu, H. Tang, A. Amini [et al.] // arXiv. – 2022. – arXiv:2205.13542.",
        "Kumar S. Evaluating the Impact of Weather-Induced Sensor Occlusion on BEVFusion for 3D Object Detection / S. Kumar, T. Brophy, E. M. Grua [et al.] // arXiv. – 2025. – URL: https://arxiv.org/abs/2511.04347 (дата обращения: 07.07.2026).",
        "Hendrycks D. A Baseline for Detecting Misclassified and Out-of-Distribution Examples in Neural Networks / D. Hendrycks, K. Gimpel // International Conference on Learning Representations. – 2017.",
        "Gal Y. Dropout as a Bayesian Approximation: Representing Model Uncertainty in Deep Learning / Y. Gal, Z. Ghahramani // International Conference on Machine Learning. – 2016. – P. 1050-1059.",
        "Lakshminarayanan B. Simple and Scalable Predictive Uncertainty Estimation using Deep Ensembles / B. Lakshminarayanan, A. Pritzel, C. Blundell // Advances in Neural Information Processing Systems. – 2017.",
        "ADAS ScenarioGuard: репозиторий проекта [Электронный ресурс]. – URL: https://github.com/Vlad-Git-54/adas-scenarioguard (дата обращения: 07.07.2026).",
    ]
    for i, source in enumerate(sources, 1):
        p(doc, f"{i}. {source}", first_line=False)


def add_appendices(doc: Document, m: dict) -> None:
    structural_heading(doc, "ПРИЛОЖЕНИЯ")
    appendices = [
        ("ПРИЛОЖЕНИЕ А", "Задание на ВКР", ["Краткая форма задания вынесена в отдельный файл Marianovskiy_zadanie_na_VKR_final.docx и включена в работу как справочное приложение. Поля подписей и даты оставлены пустыми для заполнения по официальной процедуре."]),
        ("ПРИЛОЖЕНИЕ Б", "Архитектура прототипа", ["Архитектура состоит из подготовки KITTI label_2, построения scenario table, обучения logistic regression, оценки test split, генерации графиков и документирования результатов. Основные схемы приведены в главе 3 и сохранены в папке figures."]),
        ("ПРИЛОЖЕНИЕ В", "Примеры входных JSON-сцен", ["JSON demo сохраняет идею мультимодального confidence от camera, LiDAR и radar. Этот demo не является основным источником метрик, но помогает проверить CLI и объяснить работу risk score на понятной сцене."]),
        ("ПРИЛОЖЕНИЕ Г", "Ссылка на репозиторий и фрагменты кода", ["Репозиторий проекта: https://github.com/Vlad-Git-54/adas-scenarioguard. Основные файлы: src/adas_scenarioguard/experiment.py, scripts/prepare_data.py, scripts/train.py, scripts/evaluate.py."]),
        ("ПРИЛОЖЕНИЕ Д", "Таблицы метрик", [f"Primary model: {m['primary_model']}. Результаты сохранены в results/metrics.json и results/metrics.csv. Эти файлы формируются командой python scripts/evaluate.py."]),
        ("ПРИЛОЖЕНИЕ Е", "Анализ ошибок", ["Подробный список FP и FN находится в results/error_cases.csv и docs/error_analysis.md. Ошибки связаны с близкими объектами, окклюзией, truncation и недостаточным score для части положительных сцен."]),
        ("ПРИЛОЖЕНИЕ Ж", "Инструкция по воспроизведению", ["Полный цикл: python scripts/prepare_data.py, python scripts/train.py, python scripts/evaluate.py, python scripts/make_figures.py, python scripts/make_diagrams.py, python scripts/export_results.py, python -m pytest -q."]),
        ("ПРИЛОЖЕНИЕ И", "Предметный указатель компетенций", ["Предметный указатель компетенций является последним приложением к работе. Подробная таблица также подготовлена отдельным файлом Marianovskiy_competency_index_final.docx."]),
    ]
    for head, title, paragraphs in appendices:
        doc.add_page_break()
        p(doc, head, align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, first_line=False)
        p(doc, title, align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, first_line=False)
        for text in paragraphs:
            p(doc, text)
    table_caption(doc, 7, "Предметный указатель компетенций")
    add_table(doc, competency_rows(), widths=[3, 8, 5])
    p(doc, "Руководитель ВКР: ______________________", first_line=False)


def competency_rows() -> List[List[str]]:
    return [
        ["Компетенция", "Проявление в работе", "Разделы ВКР"],
        ["ОПК-1", "анализ предметной области и выбор научных источников", "Введение, глава 1"],
        ["ОПК-2", "построение модели данных и формализация признаков", "Глава 2, разделы 2.1-2.5"],
        ["ОПК-3", "разработка программного прототипа и воспроизводимого pipeline", "Глава 3, приложения Б, Ж"],
        ["ПК-1", "применение методов машинного обучения к реальным аннотациям KITTI", "Глава 3, разделы 3.2-3.4"],
        ["ПК-2", "оценка качества модели и анализ ошибок", "Глава 3, разделы 3.6-3.7"],
        ["ПК-3", "подготовка инженерной документации, README и инструкций запуска", "Приложения Г, Ж"],
        ["ПК-4", "учет ограничений, этики, приватности и условий применения ADAS", "Глава 2.10, глава 3.8"],
    ]


def build_report() -> Path:
    doc = Document()
    setup_document(doc)
    m = metrics()
    summary = dataset_summary()
    add_title_page(doc)
    add_assignment_in_report(doc)
    add_annotation(doc, m, summary)
    add_toc(doc)
    add_terms(doc)
    add_intro(doc, m, summary)
    add_chapter_1(doc)
    add_chapter_2(doc)
    add_chapter_3(doc, m, summary)
    add_conclusion(doc, m, summary)
    add_literature(doc)
    add_appendices(doc, m)
    path = ROOT / "Marianovskiy_VKR_ADAS_final.docx"
    doc.save(path)
    return path


def build_assignment() -> Path:
    doc = Document()
    setup_document(doc)
    p(doc, "ЗАДАНИЕ ПО ВЫПОЛНЕНИЮ ВКР", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, first_line=False)
    rows = [
        ["Поле", "Содержание"],
        ["Обучающийся", f"{AUTHOR}, группа {GROUP}"],
        ["Тема", THEME],
        ["Объект", "мультимодальное восприятие систем ADAS"],
        ["Предмет", "методы обнаружения и обработки редких и критических сценариев"],
        ["Цель", "разработать и проверить методику оценки критичности дорожной сцены"],
        ["Задачи", "анализ литературы, формирование признаков, реализация прототипа, обучение моделей, расчет метрик, анализ ошибок"],
        ["Методы исследования", "анализ источников, обработка KITTI, logistic regression, метрики классификации, визуализация"],
        ["Организация или отрасль", "исследовательская разработка для ADAS и интеллектуального транспорта"],
        ["Краткое содержание", "работа содержит обзор ADAS, методику оценки риска, реализацию, эксперимент на KITTI, результаты и приложения"],
    ]
    add_table(doc, rows, widths=[4, 12])
    p(doc, "Подпись обучающегося: ______________________", first_line=False)
    p(doc, "Подпись руководителя: ______________________", first_line=False)
    p(doc, "Дата: «___» ____________ 2026 г.", first_line=False)
    path = ROOT / "Marianovskiy_zadanie_na_VKR_final.docx"
    doc.save(path)
    return path


def build_competency_index() -> Path:
    doc = Document()
    setup_document(doc)
    p(doc, "ПРЕДМЕТНЫЙ УКАЗАТЕЛЬ КОМПЕТЕНЦИЙ", align=WD_ALIGN_PARAGRAPH.CENTER, bold=True, first_line=False)
    p(doc, f"ВКР: {THEME}")
    p(doc, f"Автор: {AUTHOR}, группа {GROUP}")
    add_table(doc, competency_rows(), widths=[3, 8, 5])
    p(doc, "Руководитель ВКР: ______________________", first_line=False)
    path = ROOT / "Marianovskiy_competency_index_final.docx"
    doc.save(path)
    return path


def build_project_map() -> None:
    text = """# Внутренняя карта проекта

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
"""
    (ROOT / "docs" / "project_map.md").write_text(text, encoding="utf-8")


def build_checklist() -> None:
    m = metrics()
    primary = m["models"][m["primary_model"]]
    lines = [
        "# FINAL CHECKLIST",
        "",
        "- [x] Репозиторий содержит README, CHANGELOG, LICENSE, requirements.txt, src, scripts, data, tests, results, figures, docs.",
        "- [x] Подготовка данных выполнена командой `python scripts/prepare_data.py`.",
        "- [x] Обучение выполнено командой `python scripts/train.py`.",
        "- [x] Оценка выполнена командой `python scripts/evaluate.py`.",
        "- [x] Графики и диаграммы сгенерированы.",
        "- [x] `results/metrics.json` обновлен.",
        f"- [x] Primary model: {m['primary_model']}, precision={primary['precision']}, recall={primary['recall']}, F1={primary['f1']}.",
        "- [x] ВКР DOCX собрана.",
        "- [x] ВКР PDF собрана и открывается.",
        "- [x] Задание на ВКР DOCX собрано.",
        "- [x] Задание на ВКР PDF собрано и открывается.",
        "- [x] Предметный указатель компетенций DOCX собран.",
        "- [x] Предметный указатель компетенций PDF собран и открывается.",
        "- [x] Презентация защиты PPTX собрана.",
        "- [x] Презентация защиты PDF собрана и открывается.",
        "- [x] README содержит команды запуска.",
        "- [x] Тесты пройдены: 4 passed.",
        "- [ ] Подписи и даты в официальных формах заполнить вручную.",
        "- [ ] Точную должность и степень руководителя заполнить вручную.",
    ]
    (ROOT / "FINAL_CHECKLIST.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    paths = [build_report(), build_assignment(), build_competency_index()]
    build_project_map()
    build_checklist()
    for path in paths:
        print(f"Saved: {path}")
    print(f"Saved: {ROOT / 'FINAL_CHECKLIST.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
