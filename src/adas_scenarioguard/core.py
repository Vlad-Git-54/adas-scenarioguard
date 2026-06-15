"""Core logic for ADAS ScenarioGuard MVP.

The MVP works with simplified scene JSON files. It does not replace a real ADAS model.
It demonstrates the project logic: multimodal confidence fusion, uncertainty estimate,
and critical scenario flagging.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from math import sqrt
from typing import Any, Dict, Iterable, List, Optional


BAD_WEATHER = {"fog", "rain", "snow", "night_rain", "heavy_rain"}
VULNERABLE_CLASSES = {"pedestrian", "cyclist", "motorcyclist"}


@dataclass
class FusedObject:
    object_id: str
    label: str
    distance_m: float
    lane: str
    fused_confidence: float
    uncertainty: float
    risk_score: float
    is_critical: bool
    reason: str


@dataclass
class SceneResult:
    scene_id: str
    weather: str
    visibility_m: float
    objects: List[FusedObject]
    scene_is_critical: bool
    max_risk_score: float

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        return data


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def _sensor_reliability(sensor: str, weather: str, visibility_m: float, occlusion: float) -> float:
    """Return reliability weight for a sensor in a given scene.

    The constants are simple engineering assumptions for MVP. They are not claimed
    as trained model parameters.
    """
    visibility_factor = clamp(visibility_m / 80.0, 0.25, 1.0)

    if sensor == "camera":
        weight = 0.92
        if weather in {"fog", "snow", "heavy_rain", "night_rain"}:
            weight -= 0.32
        elif weather == "rain":
            weight -= 0.18
        weight *= visibility_factor
        weight *= 1.0 - 0.55 * occlusion
        return clamp(weight, 0.05, 1.0)

    if sensor == "lidar":
        weight = 0.88
        if weather in {"fog", "snow", "heavy_rain"}:
            weight -= 0.18
        elif weather == "rain":
            weight -= 0.08
        weight *= clamp(0.75 + 0.25 * visibility_factor, 0.65, 1.0)
        weight *= 1.0 - 0.25 * occlusion
        return clamp(weight, 0.05, 1.0)

    if sensor == "radar":
        weight = 0.76
        if weather in BAD_WEATHER:
            weight += 0.08
        weight *= 1.0 - 0.10 * occlusion
        return clamp(weight, 0.05, 1.0)

    return 0.1


def _weighted_average(values: Iterable[float], weights: Iterable[float]) -> float:
    pairs = [(v, w) for v, w in zip(values, weights) if v is not None and w > 0]
    if not pairs:
        return 0.0
    total_weight = sum(w for _, w in pairs)
    return sum(v * w for v, w in pairs) / total_weight


def _std(values: List[float]) -> float:
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    return sqrt(sum((v - mean) ** 2 for v in values) / len(values))


def _object_risk(label: str, distance_m: float, lane: str, weather: str, visibility_m: float, uncertainty: float) -> float:
    if label in VULNERABLE_CLASSES:
        class_risk = 0.42
    elif label in {"car", "truck", "bus"}:
        class_risk = 0.27
    elif label in {"unknown", "obstacle"}:
        class_risk = 0.38
    else:
        class_risk = 0.18

    distance_risk = clamp((55.0 - distance_m) / 55.0) * 0.30
    lane_risk = {"front": 0.23, "adjacent": 0.12, "side": 0.05, "far": 0.02}.get(lane, 0.07)
    weather_risk = 0.10 if weather in BAD_WEATHER or visibility_m < 45 else 0.02
    uncertainty_risk = 0.16 * uncertainty

    return clamp(class_risk + distance_risk + lane_risk + weather_risk + uncertainty_risk)


def fuse_object(obj: Dict[str, Any], weather: str, visibility_m: float) -> FusedObject:
    label = str(obj.get("class", "unknown"))
    distance_m = float(obj.get("distance_m", 999.0))
    lane = str(obj.get("relative_lane", "unknown"))
    occlusion = float(obj.get("occlusion", 0.0))

    sensor_conf = {
        "camera": obj.get("camera_conf"),
        "lidar": obj.get("lidar_conf"),
        "radar": obj.get("radar_conf"),
    }
    values: List[float] = []
    weights: List[float] = []
    for sensor, conf in sensor_conf.items():
        if conf is None:
            continue
        values.append(float(conf))
        weights.append(_sensor_reliability(sensor, weather, visibility_m, occlusion))

    fused_confidence = clamp(_weighted_average(values, weights))
    disagreement = _std(values)
    missing_penalty = (3 - len(values)) * 0.06
    bad_weather_penalty = 0.08 if weather in BAD_WEATHER or visibility_m < 45 else 0.02
    uncertainty = clamp((1.0 - fused_confidence) + 0.35 * disagreement + missing_penalty + bad_weather_penalty)
    risk_score = _object_risk(label, distance_m, lane, weather, visibility_m, uncertainty)

    is_critical = risk_score >= 0.75 or (
        label in VULNERABLE_CLASSES and lane == "front" and distance_m <= 30 and uncertainty >= 0.25
    )

    reasons = []
    if label in VULNERABLE_CLASSES:
        reasons.append("уязвимый участник движения")
    if lane == "front":
        reasons.append("объект находится впереди")
    if distance_m <= 30:
        reasons.append("малая дистанция")
    if weather in BAD_WEATHER or visibility_m < 45:
        reasons.append("сложные погодные условия")
    if uncertainty >= 0.35:
        reasons.append("повышенная неопределенность")
    if not reasons:
        reasons.append("низкий риск")

    return FusedObject(
        object_id=str(obj.get("id", "object")),
        label=label,
        distance_m=round(distance_m, 2),
        lane=lane,
        fused_confidence=round(fused_confidence, 3),
        uncertainty=round(uncertainty, 3),
        risk_score=round(risk_score, 3),
        is_critical=bool(is_critical),
        reason=", ".join(reasons),
    )


def analyze_scene(scene: Dict[str, Any]) -> SceneResult:
    scene_id = str(scene.get("id", "unknown_scene"))
    weather = str(scene.get("weather", "clear"))
    visibility_m = float(scene.get("visibility_m", 80.0))

    fused_objects = [fuse_object(obj, weather, visibility_m) for obj in scene.get("objects", [])]
    max_risk_score = max((obj.risk_score for obj in fused_objects), default=0.0)
    scene_is_critical = any(obj.is_critical for obj in fused_objects)

    return SceneResult(
        scene_id=scene_id,
        weather=weather,
        visibility_m=round(visibility_m, 2),
        objects=fused_objects,
        scene_is_critical=bool(scene_is_critical),
        max_risk_score=round(max_risk_score, 3),
    )


def evaluate_scene_prediction(scene: Dict[str, Any]) -> Dict[str, Any]:
    result = analyze_scene(scene)
    y_true = bool(scene.get("ground_truth_critical_scene", False))
    y_pred = bool(result.scene_is_critical)
    return {
        "scene_id": result.scene_id,
        "weather": result.weather,
        "y_true": y_true,
        "y_pred": y_pred,
        "max_risk_score": result.max_risk_score,
        "result": result.to_dict(),
    }
