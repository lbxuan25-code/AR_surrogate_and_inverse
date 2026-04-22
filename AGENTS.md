# AGENTS.md

## Purpose

This repository hosts AR surrogate training, inverse search, experiment-fitting,
and experiment-side data handling.

It is not the source of truth for forward physics.
The forward truth chain lives in the external LNO327 AR forward repository and
must be consumed only through its stable public `forward` interface.

The current development cycle is focused on integrating the forward repository's
directional capability contract into this repository's dataset, surrogate,
inverse, and experiment-fitting layers.

## Source Of Truth

Priority order:

1. this repository's `TODO.md`
2. dataset metadata, run metadata, and forward-interface version metadata
3. the external forward repository's public `forward` API contract
4. the external forward repository's published directional capability contract
5. local training / inverse / experiment code and tests
6. local reports and checkpoints

If local assumptions conflict with forward-interface metadata or the external
direction contract, the external forward metadata and contract win.

## Repository Boundary

This repository owns:

- dataset orchestration;
- sampling policies for fit-layer, transport, and supported directional regimes;
- surrogate model training;
- surrogate evaluation and calibration;
- inverse search;
- experiment-fitting reports;
- experiment-side ingest and preprocessing metadata;
- checkpoint and run metadata management.

This repository must not copy, fork, or silently reimplement:

- normal-state Hamiltonian code;
- round-2 pairing matrix code;
- RMFT source projection code;
- interface matching code;
- BTK transport solver code;
- authoritative formal baseline files;
- forward-side directional truth logic.

Use the external forward repository as the forward engine and as the authority
for what directional modes are physically supported.

## Required Forward Dependency

All generated data must record the forward metadata emitted by the external
forward repository, including:

- `forward_interface_version`
- `output_schema_version`
- `pairing_convention_id`
- `formal_baseline_record`
- `formal_baseline_selection_rule`
- `projection_config`
- `git_commit`
- `git_dirty`

Direction-aware datasets must additionally preserve forward-emitted directional
metadata whenever available, including:

- `direction_mode`
- `interface_angle`
- `direction_support_tier`
- `direction_crystal_label`
- `direction_dimensionality`
- `directional_spread`
- any other forward-side provenance fields required to reproduce the spectrum

Datasets generated under different forward metadata or different direction
contracts must be treated as distinct dataset families.

## Direction Contract Rules

This repository must follow the forward repository's current directional rules.

### Supported truth-grade directional regimes
- `inplane_100`
- `inplane_110`

### Supported spread regime
- narrow directional spread centered on supported named in-plane modes only
- spread settings must stay within the forward contract
- do not invent wider or arbitrary spread semantics

### Unsupported regime
- `c_axis` is not currently supported
- do not train on it
- do not expose it as a valid inverse target
- do not silently map any 2D in-plane angle to `c_axis`

### Diagnostic-only regime
- generic raw in-plane angles are caution-only / diagnostic-only
- they must not be silently promoted into the primary truth-grade training pool
- if included, they must be explicitly labeled, documented, and separated or
  down-weighted

## Execution Protocol

At any moment, only the single task in `TODO.md -> Current Task` may be
executed.

Do not start backlog tasks early.
Do not combine dataset generation, surrogate training, inverse search,
experiment preprocessing, and reporting into one unverified mega-step.

Before marking a task complete:

- run relevant unit tests;
- verify generated artifacts exist;
- write or update run metadata;
- confirm forward-interface metadata is recorded;
- confirm directional metadata is recorded where required;
- update `TODO.md` only after completion.

If a task introduces a new supported directional feature, update docs, configs,
schema notes, and evaluation outputs in the same task before marking it done.

## Dataset And Sampling Rules

Primary training datasets must be built from supported truth-grade directional
regimes first.

Use this hierarchy unless the current task explicitly changes it:

1. supported named in-plane modes without spread
2. supported named in-plane modes with narrow spread
3. diagnostic-only raw-angle extensions, if explicitly enabled

Do not mix all regimes into one undifferentiated pool by default.

Sampling policy documents and manifests must make it clear:

- which regimes are primary
- which are secondary
- which are diagnostic-only
- which are unsupported and therefore rejected

## Feature Intake Rules

Direction must not be represented only as a raw continuous `interface_angle`.

When direction-aware training is implemented, feature intake must distinguish:

- discrete directional semantics
- continuous transport controls
- continuous spread controls
- raw angle as auxiliary metadata when applicable

Do not let model code collapse supported named modes, diagnostic-only angles,
and unsupported modes into one ambiguous feature path.

## Scientific Reporting Rules

Inverse outputs must be candidate families, not unique microscopic truth claims.

Reports should say:
- "the AR data are compatible with these feature families"

They should not say:
- "the order parameter is uniquely this RMFT point"

Always separate:

- fit-layer pairing controls;
- transport nuisance controls;
- experimental preprocessing;
- directional priors or directional regime assumptions;
- surrogate uncertainty;
- final forward recheck results.

Do not present unsupported directional interpretations as established physical
results.

## Experiment-Side Rules

Experiment ingest and preprocessing belong in this repository, not in the
forward truth-chain repository.

Experiment-side handling must preserve:

- the raw experimental spectrum;
- the declared preprocessing metadata;
- any direction prior supplied by the experiment;
- whether the experiment is direction-resolved, direction-biased, or
  mixed/unknown.

Do not let experiment preprocessing silently rewrite the physical meaning of the
forward-side directional contract.

## Storage Rules

Large artifacts belong in explicit output directories, not in source code paths:

- datasets under `outputs/datasets/`
- checkpoints under `outputs/checkpoints/`
- training logs under `outputs/runs/`
- inverse results under `outputs/inverse/`
- experiment fits under `outputs/experiments/`

Do not commit heavyweight generated artifacts unless the project explicitly
decides they are small canonical examples.

## Cleanliness Rules

Do not leave behind obsolete configs, stale manifests, or legacy angle-only
assumptions that can contaminate later tasks.

When replacing an old schema or feature assumption:

- update the docs;
- update the config examples;
- update tests;
- remove or clearly deprecate the obsolete path.

No silent dual-standard behavior is allowed for direction semantics.
