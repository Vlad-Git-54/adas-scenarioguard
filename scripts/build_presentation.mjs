import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, "..");
const FINAL = path.join(ROOT, "final");
const OUT = path.join(FINAL, "Marianovskiy_VKR_ADAS_defense_final.pptx");
const QA_DIR = path.join(ROOT, "work", "presentation_qa");

const metrics = JSON.parse(await fs.readFile(path.join(ROOT, "results", "metrics.json"), "utf8"));
const summary = JSON.parse(await fs.readFile(path.join(ROOT, "data", "processed", "dataset_summary.json"), "utf8"));
const primary = metrics.models[metrics.primary_model];

const TGU_BLUE = "#2730b6";
const TGU_BLUE_DARK = "#171d72";
const TGU_BLUE_SOFT = "#eef2ff";
const TGU_ACCENT = "#36d2cf";

async function imageBytes(relPath) {
  const bytes = await fs.readFile(path.join(ROOT, relPath));
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength);
}

async function writeBlob(filePath, blob) {
  await fs.writeFile(filePath, new Uint8Array(await blob.arrayBuffer()));
}

function addText(slide, text, x, y, w, h, style = {}) {
  const shape = slide.shapes.add({
    geometry: "textbox",
    position: { left: x, top: y, width: w, height: h },
    fill: "none",
    line: { style: "solid", fill: "none", width: 0 },
  });
  shape.text = text;
  shape.text.style = {
    fontSize: style.fontSize ?? 22,
    bold: style.bold ?? false,
    color: style.color ?? "#1f2937",
    alignment: style.alignment ?? "left",
  };
  return shape;
}

function addBox(slide, text, x, y, w, h, fill = "#f8fafc", line = "#cbd5e1", fontSize = 20) {
  const rect = slide.shapes.add({
    geometry: "roundRect",
    position: { left: x, top: y, width: w, height: h },
    fill,
    line: { style: "solid", fill: line, width: 1.2 },
    borderRadius: 8,
  });
  rect.text = text;
  rect.text.style = { fontSize, color: "#111827", alignment: "center", bold: true };
  return rect;
}

function addArrowText(slide, x, y, w = 36, h = 34, color = "#334155") {
  addText(slide, "→", x, y, w, h, { fontSize: 28, bold: true, color, alignment: "center" });
}

function addSlideChrome(slide, n) {
  slide.shapes.add({
    geometry: "rect",
    position: { left: 0, top: 0, width: 1280, height: 18 },
    fill: TGU_BLUE,
    line: { style: "solid", fill: TGU_BLUE, width: 0 },
  });
  slide.shapes.add({
    geometry: "rect",
    position: { left: 0, top: 0, width: 18, height: 720 },
    fill: TGU_BLUE,
    line: { style: "solid", fill: TGU_BLUE, width: 0 },
  });
  addText(slide, "НИ ТГУ · ИДО", 1030, 42, 150, 24, { fontSize: 13, bold: true, color: TGU_BLUE });
  addText(slide, String(n), 1195, 42, 38, 24, { fontSize: 13, color: TGU_BLUE, alignment: "right" });
}

function addTitle(slide, title, subtitle = "") {
  addText(slide, title, 60, 42, 980, 58, { fontSize: 35, bold: true, color: "#0f172a" });
  slide.shapes.add({
    geometry: "rect",
    position: { left: 60, top: 104, width: 640, height: 3 },
    fill: TGU_ACCENT,
    line: { style: "solid", fill: TGU_ACCENT, width: 0 },
  });
  if (subtitle) addText(slide, subtitle, 60, 114, 1040, 34, { fontSize: 18, color: "#475569" });
}

function addFooter(slide, n) {
  const cover = n === 1;
  const color = cover ? "#dbeafe" : TGU_BLUE;
  addText(slide, "ADAS ScenarioGuard · ВКР · 2026", 60, 680, 420, 24, { fontSize: 13, color });
  addText(slide, String(n), 1180, 680, 40, 24, { fontSize: 13, color, alignment: "right" });
}

function addBulletList(slide, items, x, y, w, lineHeight = 42, fontSize = 22) {
  items.forEach((item, index) => {
    addText(slide, "•", x, y + index * lineHeight, 24, 30, { fontSize, color: TGU_BLUE, bold: true });
    addText(slide, item, x + 32, y + index * lineHeight, w - 32, 36, { fontSize, color: "#1f2937" });
  });
}

async function addImage(slide, relPath, x, y, w, h, alt, options = {}) {
  slide.images.add({
    blob: await imageBytes(relPath),
    contentType: "image/png",
    alt,
    fit: options.fit ?? "contain",
    position: { left: x, top: y, width: w, height: h },
  });
}

function notes(slide, lines) {
  slide.speakerNotes.textFrame.setText(lines);
  slide.speakerNotes.setVisible(true);
}

const deck = Presentation.create({ slideSize: { width: 1280, height: 720 } });

for (let i = 1; i <= 10; i++) {
  const slide = deck.slides.add();
  slide.background.fill = "#ffffff";
  if (i !== 1) {
    addSlideChrome(slide, i);
  }
}

{
  const slide = deck.slides.items[0];
  await addImage(slide, "figures/title_cover.png", 0, 0, 1280, 720, "Титульный слайд", { fit: "cover" });
}

{
  const slide = deck.slides.items[1];
  addTitle(slide, "Ошибка восприятия опасна именно в редких сценах");
  addBulletList(slide, [
    "Средняя точность скрывает поведение модели в тумане, ночью, при окклюзии и усечении объекта",
    "Для ADAS пропуск критической сцены опаснее лишней тревоги",
    "Нужен слой, который оценивает надежность восприятия и риск сцены",
  ], 70, 170, 670, 58, 24);
  addBox(slide, `FNR primary model\n${primary.false_negative_rate}`, 820, 160, 260, 110, "#fff7ed", "#f97316", 28);
  addBox(slide, `FN на test split\n${primary.fn}`, 820, 310, 260, 110, "#fef2f2", "#ef4444", 28);
  addBox(slide, `Recall\n${primary.recall}`, 820, 460, 260, 110, "#ecfdf5", "#10b981", 28);
  addFooter(slide, 2);
  notes(slide, [
    "Пояснить цену ошибки: false negative означает, что сцена опасна по разметке, но модель не выделила ее.",
    "Подчеркнуть, что recall выбран важной метрикой не случайно.",
  ]);
}

{
  const slide = deck.slides.items[2];
  addTitle(slide, "Объект, предмет и цель задают узкую инженерную границу");
  addBox(slide, "Объект\nмультимодальное восприятие ADAS", 70, 165, 330, 180, "#eff6ff", "#2563eb", 24);
  addBox(slide, "Предмет\nредкие и критические сценарии, uncertainty, reliability", 475, 165, 330, 180, "#f0fdf4", "#16a34a", 22);
  addBox(slide, "Цель\nметодика оценки critical scene и проверка на реальных данных", 880, 165, 330, 180, "#fff7ed", "#ea580c", 22);
  addBulletList(slide, [
    "Разработаны признаки качества наблюдения и risk prior",
    "Обучены baseline, proposed и ablation модели",
    "Собран воспроизводимый pipeline с результатами и графиками",
  ], 120, 430, 940, 44, 23);
  addFooter(slide, 3);
  notes(slide, [
    "Сказать, что работа осознанно не претендует на управление автомобилем.",
    "Цель проверяется через код, данные и метрики, а не только через литературный обзор.",
  ]);
}

{
  const slide = deck.slides.items[3];
  addTitle(slide, "Литература показывает, что деградация сенсоров измерима");
  await addImage(slide, "figures/bevfusion_literature_chart.png", 70, 150, 610, 430, "BEVFusion literature chart");
  addText(slide, "По данным Kumar et al., 2025. Не является собственным экспериментом", 86, 585, 575, 28, { fontSize: 15, color: "#475569", alignment: "center" });
  addBulletList(slide, [
    "Corner cases требуют отдельного анализа вне средней точности",
    "Плохая погода влияет на сенсоры по-разному",
    "Fusion устойчивее camera-only, но LiDAR degradation все равно заметна",
    "График справа не является собственным экспериментом",
  ], 730, 170, 470, 50, 21);
  addFooter(slide, 4);
  notes(slide, [
    "Указать источники: Heidecker по corner cases, Bijelic по погоде, Huang по sensor fusion, BEVFusion и Kumar как пример деградации.",
    "Отделить чужие опубликованные числа от собственных метрик KITTI.",
  ]);
}

{
  const slide = deck.slides.items[4];
  addTitle(slide, "Методика связывает наблюдение, надежность и риск");
  addBox(slide, "Входные наблюдения\nclass, bbox, 3D position,\nocclusion, truncation", 64, 166, 205, 130, "#eff6ff", "#2563eb", 19);
  addArrowText(slide, 280, 214);
  addBox(slide, "Признаки качества\ncamera proxy\ngeometry proxy", 330, 166, 190, 130, "#f0fdf4", "#16a34a", 19);
  addArrowText(slide, 531, 214);
  addBox(slide, "Reliability\nкачество наблюдения\nкак вход модели", 580, 166, 190, 130, "#ecfeff", "#0891b2", 19);
  addArrowText(slide, 781, 214);
  addBox(slide, "Uncertainty\n0,55 camera\n0,45 geometry", 830, 166, 175, 130, "#fff7ed", "#ea580c", 19);
  addArrowText(slide, 1014, 214);
  addBox(slide, "Risk score\nclass, distance,\nlateral, occlusion", 1055, 166, 165, 130, "#fef2f2", "#dc2626", 18);
  addBox(slide, "Фиксированное правило critical_scene\nуязвимый участник впереди, близкий транспорт, сильная окклюзия или truncation", 95, 350, 430, 120, "#f8fafc", "#64748b", 20);
  addBox(slide, "Logistic regression\nbaseline, proposed, ablation\nпорог выбирается на validation", 565, 350, 300, 120, "#f5f3ff", "#7c3aed", 20);
  addBox(slide, "Итог\ncritical scene или OK\nошибки сохраняются", 905, 350, 245, 120, "#fff7ed", "#d97706", 20);
  addArrowText(slide, 525, 392);
  addArrowText(slide, 866, 392);
  addText(slide, "Обучение и метрики строятся на реальных аннотациях KITTI. JSON demo не влияет на test split.", 135, 535, 1010, 36, { fontSize: 20, color: "#334155", alignment: "center" });
  addFooter(slide, 5);
  notes(slide, [
    "Пояснить, что признаки считаются из класса объекта, расстояния, lateral position, occlusion и truncation.",
    "Порог выбирается на validation split, test split остается для финальной оценки.",
  ]);
}

{
  const slide = deck.slides.items[5];
  addTitle(slide, "Архитектура разделяет подготовку, обучение и отчетность");
  addBox(slide, "1\nprepare_data.py\nKITTI label_2", 72, 155, 180, 110, "#eff6ff", "#2563eb", 19);
  addArrowText(slide, 260, 195);
  addBox(slide, "2\nscenario table\nfeatures + split", 305, 155, 180, 110, "#f0fdf4", "#16a34a", 19);
  addArrowText(slide, 494, 195);
  addBox(slide, "3\ntrain.py\nmodel weights", 538, 155, 180, 110, "#f5f3ff", "#7c3aed", 19);
  addArrowText(slide, 727, 195);
  addBox(slide, "4\nevaluate.py\nmetrics + errors", 770, 155, 180, 110, "#fff7ed", "#d97706", 19);
  addArrowText(slide, 959, 195);
  addBox(slide, "5\nresults / figures\nJSON, PNG, CSV", 1002, 155, 180, 110, "#fef2f2", "#dc2626", 19);
  addBox(slide, "Документы\nВКР, приложение, презентация\nберут числа из results/metrics.json", 125, 360, 305, 118, "#f8fafc", "#64748b", 20);
  addBox(slide, "Контроль качества\nметрики, графики, pytest\nподтверждают результат", 485, 360, 305, 118, "#ecfeff", "#0891b2", 20);
  addBox(slide, "Граница эксперимента\nтекущая модель scenario-level\nraw sensor pipeline вынесен дальше", 845, 360, 305, 118, "#fff7ed", "#ea580c", 20);
  addText(slide, "Архитектура оставляет проверяемый след: от исходной разметки до финальных PDF и графиков.", 125, 548, 980, 42, { fontSize: 22, color: "#334155", alignment: "center" });
  addFooter(slide, 6);
  notes(slide, [
    "Развести текущий воспроизводимый эксперимент и будущий более тяжелый raw sensor pipeline.",
    "Текущие метрики получены на табличной модели и не зависят от будущего raw sensor контура.",
  ]);
}

{
  const slide = deck.slides.items[6];
  addTitle(slide, "Эксперимент обучен на реальных аннотациях KITTI");
  addBox(slide, `Сцен всего\n${summary.num_scenes}`, 80, 170, 230, 120, "#eff6ff", "#2563eb", 28);
  addBox(slide, `Train\n${summary.split_counts.train}`, 350, 170, 230, 120, "#f8fafc", "#64748b", 28);
  addBox(slide, `Validation\n${summary.split_counts.validation}`, 620, 170, 230, 120, "#f8fafc", "#64748b", 28);
  addBox(slide, `Test\n${summary.split_counts.test}`, 890, 170, 230, 120, "#f8fafc", "#64748b", 28);
  addBulletList(slide, [
    "KITTI не содержит готовую метку critical_scene",
    "Метка получена фиксированным правилом из реальных class, distance, occlusion и truncation",
    "Обучены три logistic regression модели на NumPy",
  ], 120, 370, 960, 52, 23);
  addFooter(slide, 7);
  notes(slide, [
    "Честно проговорить, что целевая метка derived, потому что KITTI не размечает ADAS criticality.",
    "Это реальные аннотации дорожных сцен KITTI. Целевая метка получена фиксированным правилом из наблюдаемых признаков.",
  ]);
}

{
  const slide = deck.slides.items[7];
  addTitle(slide, "Proposed model снижает пропуски критических сцен");
  await addImage(slide, "figures/metrics_comparison.png", 60, 145, 520, 360, "Metrics comparison");
  await addImage(slide, "figures/confusion_matrix.png", 650, 135, 430, 380, "Confusion matrix");
  addText(slide, `Primary: precision ${primary.precision}, recall ${primary.recall}, F1 ${primary.f1}, ROC AUC ${primary.roc_auc}`, 90, 565, 1040, 46, { fontSize: 24, bold: true, color: "#0f172a", alignment: "center" });
  addFooter(slide, 8);
  notes(slide, [
    "Пройти по основным числам. Подчеркнуть, что proposed выше baseline по recall и F1 на test split.",
    "Матрица ошибок показывает 509 TP и 34 FN.",
  ]);
}

{
  const slide = deck.slides.items[8];
  addTitle(slide, "Близкие и частично видимые объекты объясняют ошибки");
  await addImage(slide, "figures/error_by_condition.png", 70, 145, 540, 360, "Error by condition");
  await addImage(slide, "figures/sensor_ablation.png", 660, 145, 520, 360, "Sensor ablation");
  addBulletList(slide, [
    "FP: сцена похожа на опасную из-за близкого объекта или высокого risk prior",
    "FN: score ниже порога при derived critical label",
    "Главное ограничение: KITTI не содержит radar и готовую ADAS critical label",
  ], 110, 555, 980, 36, 20);
  addFooter(slide, 9);
  notes(slide, [
    "Сказать, что ошибки не скрыты: они сохранены в results/error_cases.csv.",
    "Ограничение radar важно, поэтому результат не называется промышленной мультимодальной валидацией.",
  ]);
}

{
  const slide = deck.slides.items[9];
  addTitle(slide, "Итог: воспроизводимый слой оценки критичности ADAS-сцен");
  addBox(slide, "Разработано\nscenario-level методика риска", 80, 165, 310, 130, "#eff6ff", "#2563eb", 24);
  addBox(slide, "Реализовано\nкод, обучение, метрики, графики", 485, 165, 310, 130, "#f0fdf4", "#16a34a", 24);
  addBox(slide, "Проверено\nKITTI test split и unit tests", 890, 165, 310, 130, "#fff7ed", "#ea580c", 24);
  addBulletList(slide, [
    "Прототип пригоден как исследовательский модуль тестирования ADAS",
    "Не является сертифицированной системой безопасности",
    "Дальше: raw image/LiDAR/radar pipeline, nuScenes, CARLA, стресс-тесты, сертификация",
  ], 125, 380, 950, 48, 23);
  addFooter(slide, 10);
  notes(slide, [
    "Закрыть доклад по задачам: методика, реализация, реальные данные, метрики, ошибки, ограничения.",
    "Финальная фраза: работа дает проверяемую основу для дальнейшей промышленной валидации, но не заменяет ее.",
  ]);
}

await fs.mkdir(QA_DIR, { recursive: true });
for (const [index, slide] of deck.slides.items.entries()) {
  const stem = `slide-${String(index + 1).padStart(2, "0")}`;
  await writeBlob(path.join(QA_DIR, `${stem}.png`), await deck.export({ slide, format: "png", scale: 1 }));
  await fs.writeFile(path.join(QA_DIR, `${stem}.layout.json`), await (await slide.export({ format: "layout" })).text());
}
await writeBlob(path.join(QA_DIR, "montage.webp"), await deck.export({ format: "webp", montage: true, scale: 1 }));

await fs.mkdir(FINAL, { recursive: true });
const pptx = await PresentationFile.exportPptx(deck);
await pptx.save(OUT);
console.log(`Saved: ${OUT}`);
