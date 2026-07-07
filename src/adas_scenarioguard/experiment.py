"""Real-data experiment utilities for ADAS ScenarioGuard.

The experiment uses KITTI Object Detection annotations. It trains lightweight
scenario-level logistic models on real annotated road scenes and reports
test-set metrics. The critical-scene label is derived by a documented rule from
KITTI object class, 3D distance, truncation, occlusion, and lateral position.
"""
from __future__ import annotations

from dataclasses import dataclass
import csv
import json
import math
import random
import urllib.request
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple
from zipfile import ZipFile

import numpy as np


SEED = 54
KITTI_LABEL_URL = "https://s3.eu-central-1.amazonaws.com/avg-kitti/data_object_label_2.zip"
KITTI_LABEL_ZIP = "data_object_label_2.zip"
VULNERABLE_CLASSES = {"Pedestrian", "Cyclist", "Person_sitting"}
VEHICLE_CLASSES = {"Car", "Van", "Truck", "Tram"}


BASELINE_FEATURES = [
    "object_count",
    "min_distance_m",
    "front_object_count",
    "vulnerable_count",
    "close_object_count",
    "max_bbox_area_norm",
]

PROPOSED_FEATURES = BASELINE_FEATURES + [
    "occluded_count",
    "truncated_count",
    "mean_occlusion",
    "mean_truncation",
    "camera_quality_proxy",
    "lidar_geometry_quality_proxy",
    "uncertainty_proxy",
    "risk_prior",
    "max_abs_alpha",
    "min_lateral_abs_m",
]

ABLATION_FEATURES = [
    "object_count",
    "front_object_count",
    "vulnerable_count",
    "close_object_count",
    "occluded_count",
    "truncated_count",
    "camera_quality_proxy",
    "uncertainty_proxy",
    "max_bbox_area_norm",
]


@dataclass
class KittiObject:
    label: str
    truncation: float
    occlusion: int
    alpha: float
    bbox_left: float
    bbox_top: float
    bbox_right: float
    bbox_bottom: float
    height_m: float
    width_m: float
    length_m: float
    x_m: float
    y_m: float
    z_m: float
    rotation_y: float

    @property
    def distance_m(self) -> float:
        return math.sqrt(self.x_m * self.x_m + self.z_m * self.z_m)

    @property
    def bbox_area_norm(self) -> float:
        area = max(0.0, self.bbox_right - self.bbox_left) * max(0.0, self.bbox_bottom - self.bbox_top)
        return area / (1242.0 * 375.0)

    @property
    def is_front(self) -> bool:
        return self.z_m > 0 and abs(self.x_m) <= 3.5

    @property
    def is_vulnerable(self) -> bool:
        return self.label in VULNERABLE_CLASSES


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def safe_div(num: float, den: float) -> float:
    return num / den if den else 0.0


def download_kitti_labels(zip_path: Path) -> None:
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    if zip_path.exists() and zip_path.stat().st_size > 1_000_000:
        return
    urllib.request.urlretrieve(KITTI_LABEL_URL, zip_path)


def ensure_kitti_labels(data_dir: Path) -> Path:
    external_dir = data_dir / "external"
    zip_path = external_dir / KITTI_LABEL_ZIP
    download_kitti_labels(zip_path)
    label_dir = external_dir / "training" / "label_2"
    if not label_dir.exists():
        with ZipFile(zip_path) as archive:
            archive.extractall(external_dir)
    return label_dir


def parse_kitti_label_line(line: str) -> KittiObject | None:
    parts = line.strip().split()
    if len(parts) < 15 or parts[0] == "DontCare":
        return None
    return KittiObject(
        label=parts[0],
        truncation=float(parts[1]),
        occlusion=int(float(parts[2])),
        alpha=float(parts[3]),
        bbox_left=float(parts[4]),
        bbox_top=float(parts[5]),
        bbox_right=float(parts[6]),
        bbox_bottom=float(parts[7]),
        height_m=float(parts[8]),
        width_m=float(parts[9]),
        length_m=float(parts[10]),
        x_m=float(parts[11]),
        y_m=float(parts[12]),
        z_m=float(parts[13]),
        rotation_y=float(parts[14]),
    )


def read_kitti_label_file(path: Path) -> List[KittiObject]:
    objects: List[KittiObject] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            obj = parse_kitti_label_line(line)
            if obj is not None:
                objects.append(obj)
    return objects


def object_risk_prior(obj: KittiObject) -> float:
    class_risk = 0.42 if obj.is_vulnerable else 0.28 if obj.label in VEHICLE_CLASSES else 0.20
    distance_risk = clamp((45.0 - obj.distance_m) / 45.0) * 0.30
    lateral_risk = clamp((3.5 - abs(obj.x_m)) / 3.5) * 0.16 if obj.z_m > 0 else 0.0
    occlusion_risk = min(obj.occlusion, 3) / 3.0 * 0.08
    truncation_risk = clamp(obj.truncation) * 0.08
    return clamp(class_risk + distance_risk + lateral_risk + occlusion_risk + truncation_risk)


def derived_critical_label(objects: Sequence[KittiObject]) -> bool:
    """Derive a critical-scene label from real KITTI annotations.

    KITTI does not contain an ADAS criticality label. The rule is intentionally
    explicit so the experiment is reproducible and not hand-labeled after the
    fact.
    """
    for obj in objects:
        if obj.is_vulnerable and obj.is_front and obj.distance_m <= 35.0:
            return True
        if obj.label in VEHICLE_CLASSES and obj.is_front and obj.distance_m <= 12.0:
            return True
        if obj.occlusion >= 2 and obj.is_front and obj.distance_m <= 24.0:
            return True
        if obj.truncation >= 0.55 and obj.is_front and obj.distance_m <= 28.0:
            return True
    return False


def scenario_features(scene_id: str, objects: Sequence[KittiObject]) -> Dict[str, Any]:
    if not objects:
        return {
            "scene_id": scene_id,
            "object_count": 0,
            "front_object_count": 0,
            "vulnerable_count": 0,
            "vehicle_count": 0,
            "close_object_count": 0,
            "occluded_count": 0,
            "truncated_count": 0,
            "min_distance_m": 120.0,
            "mean_distance_m": 120.0,
            "min_lateral_abs_m": 20.0,
            "max_bbox_area_norm": 0.0,
            "mean_occlusion": 0.0,
            "mean_truncation": 0.0,
            "camera_quality_proxy": 1.0,
            "lidar_geometry_quality_proxy": 1.0,
            "uncertainty_proxy": 0.0,
            "risk_prior": 0.0,
            "max_abs_alpha": 0.0,
            "critical_scene": 0,
        }

    distances = [obj.distance_m for obj in objects]
    occlusions = [min(obj.occlusion, 3) / 3.0 for obj in objects]
    truncations = [clamp(obj.truncation) for obj in objects]
    camera_quality = 1.0 - clamp(0.65 * max(truncations) + 0.35 * max(occlusions))
    lidar_quality = 1.0 - clamp((min(distances) / 85.0) * 0.45 + max(occlusions) * 0.25)
    uncertainty = clamp((1.0 - camera_quality) * 0.55 + (1.0 - lidar_quality) * 0.45)
    risk_values = [object_risk_prior(obj) for obj in objects]

    return {
        "scene_id": scene_id,
        "object_count": len(objects),
        "front_object_count": sum(1 for obj in objects if obj.is_front),
        "vulnerable_count": sum(1 for obj in objects if obj.is_vulnerable),
        "vehicle_count": sum(1 for obj in objects if obj.label in VEHICLE_CLASSES),
        "close_object_count": sum(1 for obj in objects if obj.distance_m <= 25.0 and obj.is_front),
        "occluded_count": sum(1 for obj in objects if obj.occlusion >= 2),
        "truncated_count": sum(1 for obj in objects if obj.truncation >= 0.35),
        "min_distance_m": round(min(distances), 3),
        "mean_distance_m": round(sum(distances) / len(distances), 3),
        "min_lateral_abs_m": round(min(abs(obj.x_m) for obj in objects), 3),
        "max_bbox_area_norm": round(max(obj.bbox_area_norm for obj in objects), 6),
        "mean_occlusion": round(sum(occlusions) / len(occlusions), 3),
        "mean_truncation": round(sum(truncations) / len(truncations), 3),
        "camera_quality_proxy": round(camera_quality, 3),
        "lidar_geometry_quality_proxy": round(lidar_quality, 3),
        "uncertainty_proxy": round(uncertainty, 3),
        "risk_prior": round(max(risk_values), 3),
        "max_abs_alpha": round(max(abs(obj.alpha) for obj in objects), 3),
        "critical_scene": int(derived_critical_label(objects)),
    }


def build_kitti_scenario_table(label_dir: Path) -> List[Dict[str, Any]]:
    rows = []
    for path in sorted(label_dir.glob("*.txt")):
        rows.append(scenario_features(path.stem, read_kitti_label_file(path)))
    return rows


def stratified_split(rows: Sequence[Dict[str, Any]], seed: int = SEED) -> Dict[str, List[str]]:
    rng = random.Random(seed)
    positives = [row["scene_id"] for row in rows if int(row["critical_scene"]) == 1]
    negatives = [row["scene_id"] for row in rows if int(row["critical_scene"]) == 0]
    rng.shuffle(positives)
    rng.shuffle(negatives)

    def split(ids: List[str]) -> Tuple[List[str], List[str], List[str]]:
        n = len(ids)
        train_n = int(n * 0.60)
        val_n = int(n * 0.20)
        return ids[:train_n], ids[train_n : train_n + val_n], ids[train_n + val_n :]

    train_p, val_p, test_p = split(positives)
    train_n, val_n, test_n = split(negatives)
    return {
        "train": sorted(train_p + train_n),
        "validation": sorted(val_p + val_n),
        "test": sorted(test_p + test_n),
    }


def mark_splits(rows: List[Dict[str, Any]], split_ids: Dict[str, List[str]]) -> None:
    lookup = {scene_id: split for split, ids in split_ids.items() for scene_id in ids}
    for row in rows:
        row["split"] = lookup[row["scene_id"]]


def write_csv(path: Path, rows: Sequence[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(rows[0].keys()) if rows else []
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def read_csv(path: Path) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_rows_by_split(rows: Sequence[Dict[str, Any]], split: str) -> List[Dict[str, Any]]:
    return [row for row in rows if row["split"] == split]


def matrix_from_rows(rows: Sequence[Dict[str, Any]], features: Sequence[str]) -> Tuple[np.ndarray, np.ndarray, List[str]]:
    x = np.array([[float(row[name]) for name in features] for row in rows], dtype=float)
    y = np.array([int(float(row["critical_scene"])) for row in rows], dtype=float)
    ids = [row["scene_id"] for row in rows]
    return x, y, ids


def standardize_train(x_train: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    mean = x_train.mean(axis=0)
    std = x_train.std(axis=0)
    std[std == 0.0] = 1.0
    return mean, std


def sigmoid(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-np.clip(z, -35, 35)))


def train_logistic_regression(
    x_train: np.ndarray,
    y_train: np.ndarray,
    learning_rate: float = 0.08,
    epochs: int = 2500,
    l2: float = 0.001,
) -> Dict[str, Any]:
    mean, std = standardize_train(x_train)
    x = (x_train - mean) / std
    x = np.c_[np.ones((x.shape[0], 1)), x]
    weights = np.zeros(x.shape[1], dtype=float)

    for _ in range(epochs):
        pred = sigmoid(x @ weights)
        grad = (x.T @ (pred - y_train)) / len(y_train)
        grad[1:] += l2 * weights[1:]
        weights -= learning_rate * grad

    return {
        "weights": weights.tolist(),
        "mean": mean.tolist(),
        "std": std.tolist(),
        "epochs": epochs,
        "learning_rate": learning_rate,
        "l2": l2,
    }


def predict_proba(model: Dict[str, Any], x: np.ndarray) -> np.ndarray:
    mean = np.array(model["mean"], dtype=float)
    std = np.array(model["std"], dtype=float)
    weights = np.array(model["weights"], dtype=float)
    x_scaled = (x - mean) / std
    x_scaled = np.c_[np.ones((x_scaled.shape[0], 1)), x_scaled]
    return sigmoid(x_scaled @ weights)


def confusion(y_true: Sequence[int], y_pred: Sequence[int]) -> Dict[str, int]:
    return {
        "tp": sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 1),
        "fp": sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 1),
        "fn": sum(1 for t, p in zip(y_true, y_pred) if t == 1 and p == 0),
        "tn": sum(1 for t, p in zip(y_true, y_pred) if t == 0 and p == 0),
    }


def roc_points(y_true: Sequence[int], scores: Sequence[float]) -> List[Dict[str, float]]:
    thresholds = sorted(set([0.0, 1.0, *[float(s) for s in scores]]), reverse=True)
    points = []
    for threshold in thresholds:
        pred = [int(score >= threshold) for score in scores]
        cm = confusion(y_true, pred)
        points.append(
            {
                "threshold": round(threshold, 6),
                "fpr": safe_div(cm["fp"], cm["fp"] + cm["tn"]),
                "tpr": safe_div(cm["tp"], cm["tp"] + cm["fn"]),
            }
        )
    return sorted(points, key=lambda row: row["fpr"])


def pr_points(y_true: Sequence[int], scores: Sequence[float]) -> List[Dict[str, float]]:
    thresholds = sorted(set([0.0, 1.0, *[float(s) for s in scores]]), reverse=True)
    points = []
    for threshold in thresholds:
        pred = [int(score >= threshold) for score in scores]
        cm = confusion(y_true, pred)
        points.append(
            {
                "threshold": round(threshold, 6),
                "recall": safe_div(cm["tp"], cm["tp"] + cm["fn"]),
                "precision": safe_div(cm["tp"], cm["tp"] + cm["fp"]),
            }
        )
    return sorted(points, key=lambda row: row["recall"])


def trapezoid(points: Sequence[Tuple[float, float]]) -> float:
    if len(points) < 2:
        return 0.0
    area = 0.0
    last_x, last_y = points[0]
    for x, y in points[1:]:
        area += (x - last_x) * (last_y + y) / 2.0
        last_x, last_y = x, y
    return abs(area)


def auc_roc(y_true: Sequence[int], scores: Sequence[float]) -> float:
    points = roc_points(y_true, scores)
    return clamp(trapezoid([(p["fpr"], p["tpr"]) for p in points]))


def auc_pr(y_true: Sequence[int], scores: Sequence[float]) -> float:
    points = pr_points(y_true, scores)
    return clamp(trapezoid([(p["recall"], p["precision"]) for p in points]))


def metrics_from_scores(y_true: Sequence[int], scores: Sequence[float], threshold: float) -> Dict[str, Any]:
    pred = [int(score >= threshold) for score in scores]
    cm = confusion(y_true, pred)
    precision = safe_div(cm["tp"], cm["tp"] + cm["fp"])
    recall = safe_div(cm["tp"], cm["tp"] + cm["fn"])
    f1 = safe_div(2.0 * precision * recall, precision + recall)
    accuracy = safe_div(cm["tp"] + cm["tn"], len(y_true))
    fpr = safe_div(cm["fp"], cm["fp"] + cm["tn"])
    fnr = safe_div(cm["fn"], cm["fn"] + cm["tp"])
    return {
        **cm,
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1": round(f1, 3),
        "accuracy": round(accuracy, 3),
        "false_positive_rate": round(fpr, 3),
        "false_negative_rate": round(fnr, 3),
        "roc_auc": round(auc_roc(y_true, scores), 3),
        "pr_auc": round(auc_pr(y_true, scores), 3),
        "threshold": round(threshold, 3),
    }


def tune_threshold(y_true: Sequence[int], scores: Sequence[float]) -> float:
    best_threshold = 0.5
    best_key = (-1.0, -1.0, 0.0)
    for i in range(5, 96):
        threshold = i / 100.0
        metrics = metrics_from_scores(y_true, scores, threshold)
        key = (metrics["f1"], metrics["recall"], -metrics["false_positive_rate"])
        if key > best_key:
            best_key = key
            best_threshold = threshold
    return best_threshold


def train_named_model(rows: Sequence[Dict[str, Any]], feature_names: Sequence[str]) -> Dict[str, Any]:
    train_rows = load_rows_by_split(rows, "train")
    val_rows = load_rows_by_split(rows, "validation")
    x_train, y_train, _ = matrix_from_rows(train_rows, feature_names)
    x_val, y_val, _ = matrix_from_rows(val_rows, feature_names)
    model = train_logistic_regression(x_train, y_train)
    val_scores = predict_proba(model, x_val)
    threshold = tune_threshold([int(v) for v in y_val], [float(v) for v in val_scores])
    return {
        "feature_names": list(feature_names),
        "threshold": threshold,
        "model": model,
        "validation_metrics": metrics_from_scores([int(v) for v in y_val], [float(v) for v in val_scores], threshold),
    }


def evaluate_named_model(
    rows: Sequence[Dict[str, Any]],
    model_spec: Dict[str, Any],
    split: str = "test",
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    eval_rows = load_rows_by_split(rows, split)
    x, y, ids = matrix_from_rows(eval_rows, model_spec["feature_names"])
    scores = predict_proba(model_spec["model"], x)
    y_int = [int(v) for v in y]
    score_list = [float(v) for v in scores]
    metrics = metrics_from_scores(y_int, score_list, float(model_spec["threshold"]))
    metrics["num_examples"] = len(eval_rows)
    predictions = []
    for row, scene_id, true_value, score in zip(eval_rows, ids, y_int, score_list):
        pred = int(score >= float(model_spec["threshold"]))
        predictions.append(
            {
                "scene_id": scene_id,
                "split": split,
                "y_true": true_value,
                "y_pred": pred,
                "score": round(score, 6),
                "error_type": "TP" if true_value and pred else "FP" if pred else "FN" if true_value else "TN",
                "min_distance_m": float(row["min_distance_m"]),
                "vulnerable_count": int(float(row["vulnerable_count"])),
                "occluded_count": int(float(row["occluded_count"])),
                "truncated_count": int(float(row["truncated_count"])),
                "risk_prior": float(row["risk_prior"]),
            }
        )
    return metrics, predictions


def grouped_metrics(rows: Sequence[Dict[str, Any]], predictions: Sequence[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    row_by_id = {row["scene_id"]: row for row in rows}
    groups: Dict[str, List[Dict[str, Any]]] = {
        "close_objects": [],
        "vulnerable_road_users": [],
        "occluded_objects": [],
        "truncated_objects": [],
        "vehicle_scenes": [],
    }
    for pred in predictions:
        row = row_by_id[pred["scene_id"]]
        if float(row["min_distance_m"]) <= 25.0:
            groups["close_objects"].append(pred)
        if int(float(row["vulnerable_count"])) > 0:
            groups["vulnerable_road_users"].append(pred)
        if int(float(row["occluded_count"])) > 0:
            groups["occluded_objects"].append(pred)
        if int(float(row["truncated_count"])) > 0:
            groups["truncated_objects"].append(pred)
        if int(float(row["vehicle_count"])) > 0:
            groups["vehicle_scenes"].append(pred)

    output: Dict[str, Dict[str, Any]] = {}
    for name, group in groups.items():
        if not group:
            continue
        y_true = [int(row["y_true"]) for row in group]
        y_pred = [int(row["y_pred"]) for row in group]
        cm = confusion(y_true, y_pred)
        precision = safe_div(cm["tp"], cm["tp"] + cm["fp"])
        recall = safe_div(cm["tp"], cm["tp"] + cm["fn"])
        f1 = safe_div(2.0 * precision * recall, precision + recall)
        output[name] = {
            "num_examples": len(group),
            **cm,
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1": round(f1, 3),
        }
    return output


def model_registry() -> Dict[str, Sequence[str]]:
    return {
        "baseline_kitti_logreg": BASELINE_FEATURES,
        "proposed_reliability_logreg": PROPOSED_FEATURES,
        "ablation_without_3d_geometry": ABLATION_FEATURES,
    }
