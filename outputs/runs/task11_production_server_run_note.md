# Task 11 Production Server Run Note

- Date: 2026-04-23T12:07:55+00:00
- Forward repository commit used: b85a5cb304acbfd5d51133251ef57293bd0abd2b
- Training repository commit used: af232257cd6d0a392716325d176cfd9d44c94e84

## Exact Commands Run

python scripts/datasets/build_dataset.py --config configs/datasets/task11_directional_production_dataset.json
python scripts/surrogate/train_surrogate.py --config configs/surrogate/task11_directional_surrogate_production.json
python scripts/surrogate/evaluate_surrogate.py --config configs/surrogate/task11_directional_evaluation_production.json

## Output Directories Used

- outputs/datasets/task11_directional_production
- outputs/checkpoints/task11_directional_surrogate_production
- outputs/runs/task11_directional_evaluation_production

## Returned Artifact Choice

- Returned full dataset manifest: outputs/datasets/task11_directional_production/dataset.json
- Heavy artifacts kept on server:
  - outputs/datasets/task11_directional_production/forward_outputs/
  - outputs/checkpoints/task11_directional_surrogate_production/model.npz
