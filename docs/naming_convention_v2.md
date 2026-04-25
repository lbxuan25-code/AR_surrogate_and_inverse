# Naming Convention V2

Task S6 freezes the repository naming convention standard.

The naming rule is:
file names must describe content and role first.
Task numbers may appear only as compatibility labels, migration aliases, or
historical archive markers.

## Core Rule

Prefer:

- content-based name;
- role-based suffix;
- optional stage label.

Avoid:

- task number as the primary identifier;
- names whose meaning is only "this came from Task N";
- names that mix multiple roles such as contract plus audit plus runbook
  without saying so explicitly.

## Canonical Patterns

### Docs

Preferred patterns:

- `<topic>_contract.md`
- `<topic>_audit.md`
- `<topic>_runbook.md`
- `<topic>_standard.md`
- `<topic>_template.md`
- `<topic>_decision.md`

Examples:

- `pairing_representation_contract.md`
- `joint_sampling_contract.md`
- `training_observability_standard.md`
- `tb_parameterization_decision.md`

Avoid as primary names:

- `task14_*.md`
- `task15_*.md`
- bare stage numbers with no content label.

### Configs

Preferred patterns:

- `<content>_<stage>_dataset.json`
- `<content>_<stage>_training.json`
- `<content>_<stage>_evaluation.json`
- `<content>_<stage>_search.json`
- `<content>_<stage>_experiment.json`

Examples:

- `directional_smoke_dataset.json`
- `directional_production_training.json`
- `bias40_probe_evaluation.json`

If a task-number alias must remain, the content-based name is the primary name
and the task-number form becomes the compatibility alias.

### Outputs

Preferred directory names:

- `<content>_<stage>/`

Preferred files inside those directories:

- `dataset.json`
- `metrics.json`
- `model_card.md`
- `evaluation_report.json`
- `evaluation_report.md`
- `run_metadata.json`

Avoid embedding the task number in every nested output path once a stable
content-based stage label exists.

### Tests

Preferred patterns:

- `test_<topic>_contract.py`
- `test_<topic>_standard.py`
- `test_<topic>_decision.py`
- `test_<topic>_smoke.py`

Examples:

- `test_joint_sampling_contract.py`
- `test_training_observability_standard.py`

## Stage Labels

Allowed stage labels are content labels such as:

- `smoke`
- `pilot`
- `production`
- `high_accuracy`
- `bias40_probe`

These are preferable to raw task numbers because they communicate meaning.

## Legacy Labeling Rule

When an old task-number file is kept for compatibility, its status must be
explicitly one of:

- `legacy`
- `archive`
- `compatibility alias`
- `draft reference`

No silent dual-standard naming is allowed.

## Path Naming Style

Use:

- lowercase;
- underscores;
- short, role-specific suffixes.

Avoid:

- CamelCase filenames;
- spaces;
- opaque abbreviations that hide the file's role.

## Examples Of Good Renames

Examples of the desired direction:

- `task14_pairing_representation_contract.md` ->
  `pairing_representation_contract.md`
- `task15_inverse_ready_medium_handoff.md` ->
  `inverse_ready_medium_runbook.md`
- `task10_directional_pilot_dataset.json` ->
  `directional_pilot_dataset.json`
- `task13_directional_high_accuracy_large.json` ->
  `directional_high_accuracy_training.json`

## Task S6 Boundary

Task S6 freezes naming rules only.

It does not yet require immediate renaming of every legacy file in the
repository.
