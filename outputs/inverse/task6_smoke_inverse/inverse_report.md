# Task 6 Smoke Inverse Search Report

The AR data are compatible with these feature families. This report does not
claim a unique microscopic truth.

## Target

- Dataset: `outputs/datasets/task3_orchestration_smoke/dataset.json`
- Row id: `task3_smoke_train_000`

## Search Policy

- Objective: `spectrum_rmse`
- Surrogate used: `False`
- Surrogate reason: Task 5 fallback policy requires direct forward for unsafe or unseen regimes.

## Candidate Families

### compatible_train_like_000

- Objective score: `0`
- Pairing controls: `{'delta_zz_s': 0.18, 'delta_perp_x': -0.08}`
- Transport nuisance controls: `{'interface_angle': 0.0, 'barrier_z': 0.5, 'gamma': 1.0, 'temperature_kelvin': 3.0, 'nk': 11}`
- Forward recheck git commit: `4e4c935d1f123c03ee2250f8624d5df3c2c7ebe3`

### nearby_barrier_shift_001

- Objective score: `0.038377394`
- Pairing controls: `{'delta_zz_s': 0.16, 'delta_perp_x': -0.06}`
- Transport nuisance controls: `{'interface_angle': 0.02, 'barrier_z': 0.55, 'gamma': 1.0, 'temperature_kelvin': 3.0, 'nk': 11}`
- Forward recheck git commit: `4e4c935d1f123c03ee2250f8624d5df3c2c7ebe3`
