# Dataset Schema

This note defines the Task 2 canonical dataset row schema for local surrogate
and inverse workflows.

The forward physics source of truth remains the external `forward` interface.
Dataset rows store requests, output references, and emitted forward metadata;
they do not store or copy forward physics implementation details.

## Versions

- Row schema: `ar_inverse_dataset_row_v1`
- Direction-aware row schema: `ar_inverse_dataset_row_v2`
- Manifest schema: `ar_inverse_dataset_manifest_v1`

## Dataset Row

Every row must include:

- `dataset_row_schema_version`: schema version for the row.
- `row_id`: stable unique row identifier within a manifest.
- `sampling_policy_id`: identifier of the policy that produced the row.
- `split`: one of `train`, `validation`, or `test`.
- `forward_request`: the exact request payload emitted by
  `FitLayerSpectrumRequest.to_dict()`.
- `forward_output_ref`: local reference to the forward output artifact.
- `forward_metadata`: full metadata emitted by the external forward repository.

Optional but recommended:

- `controls`: local training-facing controls split into
  `fit_layer_pairing_controls`, `transport_controls`, and `bias_grid`.

Direction-aware rows use `ar_inverse_dataset_row_v2` and must also include:

- `direction`: a dedicated direction block copied from the forward request and
  forward-emitted transport metadata.

The direction block includes:

- `direction_schema_version`: currently `ar_inverse_direction_v1`.
- `direction_mode`: supported named mode when present.
- `interface_angle`: forward-emitted angle, stored as auxiliary metadata.
- `direction_support_tier`: forward-emitted support tier.
- `direction_crystal_label`: forward-emitted crystal label when available.
- `direction_dimensionality`: forward-emitted dimensionality when available.
- `directional_spread`: spread metadata when a narrow named-mode spread request
  was used; otherwise `null`.
- `direction_regime`: local evaluation bucket such as
  `inplane_100_no_spread`, `inplane_110_no_spread`, or
  `named_mode_narrow_spread`.
- `forward_direction_provenance`: request and transport-summary fields needed
  to reproduce the direction semantics.

Old `ar_inverse_dataset_row_v1` smoke manifests remain loadable when possible,
but new generation configs must write `ar_inverse_dataset_row_v2` rows with a
direction block.

## Forward Output Reference

`forward_output_ref` is a mapping:

- `storage`: currently `local_json`.
- `path`: path to the forward-output payload relative to the dataset manifest
  directory.
- `sha256`: SHA-256 digest of the referenced JSON payload.
- `payload_kind`: currently `forward_spectrum`.

The referenced payload is the direct `ForwardSpectrumResult.to_dict()` output
from the external `forward` package.

## Required Forward Metadata

Every row must copy the complete forward metadata from its referenced output.
The required keys are:

- `forward_interface_version`
- `output_schema_version`
- `pairing_convention_id`
- `formal_baseline_record`
- `formal_baseline_selection_rule`
- `projection_config`
- `git_commit`
- `git_dirty`

Datasets whose rows carry different forward metadata versions must be treated
as distinct dataset families.

Direction-aware datasets whose rows carry different direction contracts,
direction modes, or spread semantics must also be treated as distinct dataset
families.

## Manifest

The dataset manifest is a compact JSON object:

- `dataset_manifest_schema_version`
- `dataset_id`
- `description`
- `sampling_policy`
- `sampling_policy_id`
- `rows`

## Resumable Manifest

The legacy Task 3 orchestration and the current Task 8 directional smoke
generator both use resumable orchestration fields:

- `resumable_manifest_schema_version`: currently
  `ar_inverse_resumable_manifest_v1`.
- `source_config`: JSON config used by the dataset generation CLI.
- `plan`: one entry per requested row.

Every plan entry includes:

- `row_id`
- `split`
- `sampling_policy_id`
- `status`: one of `pending`, `completed`, or `failed`
- `forward_output_path`
- `reused_existing_output`

Completed plan entries must have matching completed dataset rows in `rows`.
When a previous manifest exists, the generator reuses a completed row only if
its referenced forward-output file exists and its SHA-256 digest still matches
the row's `forward_output_ref`.

Retries, scheduling, parallel workers, and large-scale policy expansion remain
outside these smoke orchestration paths.
