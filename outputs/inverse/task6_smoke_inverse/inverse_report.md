# Task 6 Smoke Inverse Search Report

The AR data are compatible with these feature families. This report does not
claim a unique microscopic truth.

## Target

- Dataset: `outputs/datasets/task8_directional_smoke/dataset.json`
- Row id: `task8_direction_train_inplane_100`

## Search Policy

- Objective: `spectrum_rmse`
- Surrogate used: `False`
- Surrogate reason: Task 5 fallback policy requires direct forward for unsafe or unseen regimes.
- Direction prior: `direction_biased`

## Candidate Families

### compatible_train_like_000

- Objective score: `0`
- Pairing controls: `{'delta_zz_s': 0.18, 'delta_perp_x': -0.08}`
- Transport nuisance controls: `{'barrier_z': 0.5, 'gamma': 1.0, 'temperature_kelvin': 3.0, 'nk': 11}`
- Direction regime: `inplane_100_no_spread`
- Forward recheck git commit: `b85a5cb304acbfd5d51133251ef57293bd0abd2b`

### nearby_barrier_shift_001

- Objective score: `0.036554209`
- Pairing controls: `{'delta_zz_s': 0.16, 'delta_perp_x': -0.06}`
- Transport nuisance controls: `{'barrier_z': 0.55, 'gamma': 1.0, 'temperature_kelvin': 3.0, 'nk': 11}`
- Direction regime: `inplane_100_no_spread`
- Forward recheck git commit: `b85a5cb304acbfd5d51133251ef57293bd0abd2b`
