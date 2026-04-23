# Task 10 Pilot Server Run Note

- Date: 2026-04-23T10:42:56+00:00
- Forward repository commit used: `b85a5cb304acbfd5d51133251ef57293bd0abd2b`
- Training repository commit used: `247d5825826bb121d17738a770b3d1e6bfc23286`

## Exact Commands Run

```bash
python scripts/datasets/build_dataset.py --config configs/datasets/task10_directional_pilot_dataset.json
python scripts/surrogate/train_surrogate.py --config configs/surrogate/task10_directional_surrogate_pilot.json
python scripts/surrogate/evaluate_surrogate.py --config configs/surrogate/task10_directional_evaluation_pilot.json
```

## Output Directories Used

- `outputs/datasets/task10_directional_pilot`
- `outputs/checkpoints/task10_directional_surrogate_pilot`
- `outputs/runs/task10_directional_evaluation_pilot`

## Returned Artifact Choice

- Returning dataset manifest: `outputs/datasets/task10_directional_pilot/dataset.json`
- Heavy artifacts kept on server:
  - `outputs/datasets/task10_directional_pilot/forward_outputs/`
  - `outputs/checkpoints/task10_directional_surrogate_pilot/model.npz`
