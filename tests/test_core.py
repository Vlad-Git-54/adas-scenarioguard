from adas_scenarioguard.core import analyze_scene
from adas_scenarioguard.experiment import derived_critical_label, parse_kitti_label_line


def test_fog_pedestrian_is_critical():
    scene = {
        "id": "test_scene",
        "weather": "fog",
        "visibility_m": 30,
        "objects": [
            {
                "id": "ped",
                "class": "pedestrian",
                "distance_m": 18,
                "relative_lane": "front",
                "occlusion": 0.2,
                "camera_conf": 0.4,
                "lidar_conf": 0.7,
                "radar_conf": 0.6,
            }
        ],
    }
    result = analyze_scene(scene)
    assert result.scene_is_critical is True
    assert result.objects[0].risk_score >= 0.62


def test_far_car_is_not_critical():
    scene = {
        "id": "test_scene_ok",
        "weather": "clear",
        "visibility_m": 90,
        "objects": [
            {
                "id": "car",
                "class": "car",
                "distance_m": 70,
                "relative_lane": "front",
                "occlusion": 0,
                "camera_conf": 0.9,
                "lidar_conf": 0.85,
                "radar_conf": 0.8,
            }
        ],
    }
    result = analyze_scene(scene)
    assert result.scene_is_critical is False


def test_kitti_parser_reads_real_label_line():
    line = "Car 0.00 0 -1.57 712.40 143.00 810.73 307.92 1.89 1.64 4.47 1.84 1.47 8.41 -1.56"
    obj = parse_kitti_label_line(line)
    assert obj is not None
    assert obj.label == "Car"
    assert round(obj.distance_m, 1) == 8.6


def test_derived_critical_label_for_front_pedestrian():
    line = "Pedestrian 0.10 1 0.10 600.00 150.00 650.00 300.00 1.70 0.60 0.80 0.30 1.50 18.00 0.00"
    obj = parse_kitti_label_line(line)
    assert obj is not None
    assert derived_critical_label([obj]) is True
