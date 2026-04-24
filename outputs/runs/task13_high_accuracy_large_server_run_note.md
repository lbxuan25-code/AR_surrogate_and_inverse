# Task 13 High-Accuracy Large Server Run Note

- Date: 2026-04-24T10:01:49+00:00
- Forward repository commit used: b85a5cb304acbfd5d51133251ef57293bd0abd2b
- Training repository commit used: 7f05597fbbbfce61f071ce3219ec60118e4dd0b2

## Exact Commands Run

python scripts/surrogate/train_surrogate.py --config configs/surrogate/task13_directional_high_accuracy_large.json
python scripts/surrogate/evaluate_surrogate.py --config configs/surrogate/task13_directional_high_accuracy_evaluation_large.json

## Existing Dataset Reused

- outputs/datasets/task13_directional_large_accuracy/dataset.json
- outputs/runs/task13_directional_large_accuracy_dataset_run_metadata.json

## Launch Addendum Used

- docs/task13_high_accuracy_large_launch_addendum.md
- mean_std = 0.005
- max_std = 0.025

## Output Directories Used

- outputs/checkpoints/task13_directional_high_accuracy_large
- outputs/runs/task13_directional_high_accuracy_evaluation_large

## Heavy Artifacts Kept On Server

- outputs/datasets/task13_directional_large_accuracy/forward_outputs/
- outputs/checkpoints/task13_directional_high_accuracy_large/members/
