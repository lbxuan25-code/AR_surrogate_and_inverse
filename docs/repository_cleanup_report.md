# Repository Cleanup Report

This report records the real cleanup performed after the S1–S6 standards were
frozen.

The goal of this cleanup was to reduce active ambiguity in `docs/`, `configs/`,
`tests/`, and `outputs/` without touching heavy training or dataset workflows.

## Kept

Kept without relocation:

- the task-numbered server contract configs for Tasks 10–13 under `configs/`
  because they are still tied to existing returned server artifacts and
  historical runbook references;
- all real datasets, checkpoints, evaluation reports, and run metadata under
  `outputs/`;
- the legacy Task 3/4/5 config family as compatibility-kept baseline aliases.

Why:

- these paths still anchor existing artifacts and historical review trails;
- moving them now would create more churn than value for this minimal cleanup.

## Renamed Or Moved

Moved into content-based `docs/` homes:

- contracts:
  `docs/contracts/`
- audits:
  `docs/audits/`
- runbooks:
  `docs/runbooks/`
- standards:
  `docs/standards/`
- templates:
  `docs/templates/`
- setup:
  `docs/setup/`
- archive:
  `docs/archive/`

Examples:

- `docs/task10_pilot_server_runbook.md` ->
  `docs/runbooks/directional_pilot_runbook.md`
- `docs/task15_inverse_ready_medium_handoff.md` ->
  `docs/runbooks/inverse_ready_medium_draft_runbook.md`
- `docs/task14_pairing_representation_contract.md` ->
  `docs/contracts/pairing_representation_contract.md`
- `docs/task14_rmft_projection_audit.md` ->
  `docs/audits/rmft_projection_audit.md`
- `docs/training_observability_standard.md` ->
  `docs/standards/training_observability_standard.md`

Moved current canonical lightweight configs into content-based homes:

- `configs/datasets/smoke/directional_smoke_dataset.json`
- `configs/datasets/contracts/rmft_anchor_dataset_contract.json`
- `configs/datasets/contracts/bias40_probe_dataset_contract.json`
- `configs/datasets/drafts/tb_pilot_dataset_draft.json`
- `configs/datasets/drafts/inverse_ready_medium_dataset_draft.json`
- `configs/surrogate/smoke/directional_smoke_training.json`
- `configs/surrogate/smoke/directional_smoke_evaluation.json`
- `configs/surrogate/contracts/bias40_probe_training_contract.json`
- `configs/surrogate/contracts/bias40_probe_evaluation_contract.json`
- `configs/surrogate/drafts/inverse_ready_medium_training_draft.json`
- `configs/surrogate/drafts/inverse_ready_medium_evaluation_draft.json`

Renamed path-heavy tests to role-first names:

- `tests/test_task10_pilot_handoff.py` ->
  `tests/test_directional_pilot_runbook.py`
- `tests/test_task11_production_contract.py` ->
  `tests/test_directional_production_contract.py`
- `tests/test_task12_neural_contract.py` ->
  `tests/test_directional_medium_neural_contract.py`
- `tests/test_task13_high_accuracy_contract.py` ->
  `tests/test_directional_high_accuracy_contract.py`
- `tests/test_task14_bias40_probe_contract.py` ->
  `tests/test_bias40_probe_contract.py`
- `tests/test_task14_pairing_representation.py` ->
  `tests/test_pairing_representation_contract.py`
- `tests/test_task14_rmft_anchor_contract.py` ->
  `tests/test_rmft_anchor_contract.py`
- `tests/test_task14_tb_pilot_contract.py` ->
  `tests/test_legacy_tb_pilot_contract.py`
- `tests/test_task14_transport_domain_contract.py` ->
  `tests/test_transport_domain_contract.py`
- `tests/test_task15_inverse_ready_medium_contract.py` ->
  `tests/test_inverse_ready_medium_draft_contract.py`

## Migrated

Migrated path references across:

- `README.md`
- `AGENTS.md`
- active contract docs and runbooks
- config cross-references
- code default config paths for the smoke dataset/training/evaluation entry
  points
- path-assertion tests

Outputs structure was also made more explicit by creating:

- `outputs/figures/`
- `outputs/audits/`

Why:

- S5/S6 had already frozen those homes, but the repository tree had not yet
  reflected them.

## Marked As Legacy

Explicitly archived and labeled as legacy:

- `docs/archive/legacy_sampling_policy_smoke.md`
- `docs/archive/legacy_directional_smoke_training_note.md`
- `docs/archive/legacy_tb_pilot_contract.md`

Implicitly retained as compatibility-kept paths for now:

- Task 10–13 task-numbered server config files
- Task 3/4/5 legacy baseline config files

Why:

- these still map directly to historical run artifacts or compatibility entry
  points, so they were not moved in this minimal cleanup pass.

## Deleted

Deleted lightweight generated or stale files:

- `src/ar_surrogate_and_inverse.egg-info/`
- `tests/__pycache__/`

Why:

- they were generated metadata or bytecode caches;
- they contained stale path references;
- they were not source-of-truth files;
- and they can be regenerated locally when needed.

## Not Deleted

Explicitly not deleted:

- any dataset manifest under `outputs/datasets/`
- any checkpoint or model card under `outputs/checkpoints/`
- any run metadata or evaluation report under `outputs/runs/`
- any inverse or experiment artifact under `outputs/inverse/` or
  `outputs/experiments/`

Why:

- these are user-relevant outputs and part of the repository's review trail.

## Why This Cleanup Was Minimal

This cleanup intentionally stopped short of a full config/output renaming sweep.

It prioritized:

- removing the most active ambiguity at the top level;
- moving the current canonical rectification docs/configs into content-based
  homes;
- keeping historical run-linked paths stable where risk was higher;
- and making remaining task-number-heavy paths clearly legible as compatibility
  paths rather than the new naming standard.
