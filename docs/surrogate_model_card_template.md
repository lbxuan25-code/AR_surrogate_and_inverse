# Surrogate Model Card Template

Every surrogate checkpoint should include a model card with these sections:

## Purpose

State the workflow scope. For early baselines, say clearly when a model is only
a smoke-scale training check and not a calibrated inverse-search surrogate.

## Model

- model type;
- training objective;
- feature order;
- target spectrum shape;
- checkpoint path.

## Dataset

- dataset id;
- dataset manifest path;
- sampling policy id;
- split counts;
- forward-output references used for training and held-out evaluation.

## Forward Metadata Family

Record the forward-interface metadata family from the dataset:

- `forward_interface_version`
- `output_schema_version`
- `pairing_convention_id`
- `formal_baseline_record`
- `formal_baseline_selection_rule`
- `projection_config`
- `git_commit`
- `git_dirty`

## Metrics

Report at least train and held-out validation metrics. If a test split exists,
include it as held-out forward-generated spectra.

## Limitations

Separate baseline training limitations from future calibration or inverse-search
claims. Do not make microscopic truth claims from surrogate metrics.
