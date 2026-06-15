from adas_scenarioguard.core import analyze_scene


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
