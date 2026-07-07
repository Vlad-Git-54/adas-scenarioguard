# Data Card

## Dataset

Primary dataset: KITTI Object Detection annotations.

Official page: <https://www.cvlibs.net/datasets/kitti/eval_object.php?obj_benchmark=3d>

The repository stores prepared derived tables and small JSON examples. Raw KITTI archives are not committed.

## Prepared Table

| Field | Value |
|---|---:|
| Scenes | 7481 |
| Train | 4488 |
| Validation | 1496 |
| Test | 1497 |

The split is fixed and stored in `data/processed/kitti_split.json`.

## Target

KITTI does not provide an official `critical_scene` label. The target is derived from real annotations by a deterministic rule using object class, 3D distance, lateral position, occlusion and truncation.

This target is suitable for a reproducible research prototype. It should not be interpreted as a certified safety label.

## Synthetic Data

Synthetic scenes are not used for training the primary model or for reporting final metrics. Demonstration JSON files are small examples for CLI behavior and are separate from the KITTI experiment.

## Known Gaps

- No radar channel in KITTI Object Detection.
- No direct weather label in the prepared table.
- No raw image or point-cloud model in the current experiment.
- No expert ADAS hazard annotation beyond the deterministic derived target.
