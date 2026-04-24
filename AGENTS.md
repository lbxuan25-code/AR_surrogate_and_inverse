# AGENTS.md

## Purpose

This repository hosts AR surrogate training, inverse search, experiment-fitting,
and experiment-side data handling.

It is not the source of truth for forward physics.
The forward truth chain lives in the external LNO327 AR forward repository and
must be consumed only through its stable public `forward` interface.

Task 13B is complete.
The next development cycle is no longer centered on improving the already
accepted local-surrogate accuracy inside the old baseline-neighborhood 5-control
pairing box.

The new development cycle is centered on:
- replacing the old 5-control pairing-input contract;
- moving to the full projected complex 7+1 pairing representation;
- removing only the globally redundant phase degree of freedom;
- avoiding any further latent compression;
- expanding the bias window beyond `[-20, 20] meV`;
- expanding nuisance-domain coverage;
- introducing a first TB-variation pilot;
- and preparing an inverse-ready medium-scale contract.

## Source Of Truth

Priority order:

1. `TODO.md`
2. committed configs, docs, and lightweight validation tests in this repository
3. dataset metadata, run metadata, checkpoint metadata, and forward-interface
   version metadata
4. the external forward repository's public `forward` API contract
5. the external forward repository's published directional capability contract
6. local code and tests
7. returned server artifacts committed back to GitHub for review

If local assumptions conflict with forward-interface metadata or the external
direction contract, the external forward metadata and contract win.

## Split Workflow Model

This repository uses a strict split workflow.

### Local Codex responsibilities
Local Codex may:
- edit source code;
- edit configs;
- edit docs and handoff notes;
- add or update lightweight tests;
- wire new schema fields and representation helpers;
- prepare exact server commands and returned-artifact expectations;
- review compact returned artifacts after the user has run the server task and
  committed those compact artifacts back to GitHub.

Local Codex must not:
- run medium-scale or large-scale dataset generation;
- run surrogate training beyond tiny smoke-level local validation explicitly
  allowed by `TODO.md`;
- run surrogate evaluation beyond tiny smoke-level local validation explicitly
  allowed by `TODO.md`;
- fabricate heavy outputs under `outputs/`;
- mark a server-run task complete before returned artifacts are reviewed.

### Manual server responsibilities
The user manually executes all heavy tasks on the server.

Heavy tasks include:
- dataset generation;
- surrogate training;
- surrogate evaluation;
- synthetic inverse benchmarks at medium or larger scale;
- any run that produces large datasets, large checkpoints, or bulky spectrum
  collections.

### GitHub handoff boundary
GitHub is the handoff boundary between:
- local Codex preparation, and
- the user's manual server execution.

Committed configs and handoff notes are authoritative.
Codex must prepare them locally.
The user must execute them manually on the server.

## Repository Boundary

This repository owns:
- dataset orchestration;
- sampling policies for pairing, transport, TB pilot coordinates, and supported
  directional regimes;
- surrogate model training code;
- surrogate evaluation and calibration code;
- inverse search;
- experiment-fitting reports;
- checkpoint and run metadata schema management;
- server handoff notes and returned-artifact review logic.

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

## Pairing Representation Rules

The canonical future-facing pairing representation is no longer the old
baseline-neighborhood 5-control local perturbation path.

### Canonical pairing input contract
The canonical pairing input contract must be:
- the full projected complex 7+1 pairing channels;
- gauge-fixed only to remove the single globally redundant phase degree of
  freedom;
- otherwise left uncompressed.

### Explicit prohibition
Do not introduce:
- PCA compression;
- latent manifold compression;
- learned low-dimensional pairing coordinates;
- any other extra lossy dimensionality reduction after the projected 7+1 pairing
  representation has already been formed.

### Gauge-fixing rule
Gauge-fixing is allowed and required only for the physically redundant global
phase.
It must:
- use a deterministic anchor selection policy;
- rotate all channels by one common phase only;
- preserve all relative phase information between channels.

Do not remove relative phase information.

## RMFT Data-Source Rules

Canonical future datasets must not be built primarily from the old
`delta_from_baseline_meV` 5-control local box.

Canonical future pairing samples must come primarily from:
1. projected RMFT anchor points,
2. local neighborhood perturbations around projected RMFT anchor points,
3. a small number of bridge samples between sparse nearby anchors.

Do not replace RMFT-driven pairing coverage with unconstrained random sampling
over the full 7+1 complex hypercube.

## Bias-Window Rules

The old accepted Task 13 high-accuracy surrogate remains valid for its own
contract, but future inverse-ready work must probe a wider bias window.

The canonical next probe target is:
- `bias_min_mev = -40.0`
- `bias_max_mev = 40.0`
- `num_bias = 241`

Do not silently choose a different bias-window probe unless `TODO.md`
explicitly changes it.

## Nuisance-Domain Rules

Future inverse-ready work must expand nuisance-domain coverage beyond the old
structured low/high sweep.

The fixed initial target ranges are:
- `barrier_z` in `[0.10, 1.50]`
- `gamma` in `[0.40, 1.80]`
- `temperature_kelvin` in `[1.0, 15.0]`

Use a two-tier policy:
- dense core region;
- sparse guard-band region.

Do not silently narrow those ranges without an explicit `TODO.md` change.

## TB Pilot Rules

Future inverse-ready work must no longer freeze the normal state completely, but
the first TB expansion stage must remain simple and controlled.

### Fixed TB pilot coordinates
Use exactly these five pilot coordinates:
- `mu_shift`
- `bandwidth_scale`
- `interlayer_scale`
- `orbital_splitting_shift`
- `hybridization_scale`

### Explicit prohibition
Do not add more TB pilot coordinates before `TODO.md` explicitly promotes such a
task.
Do not add heavy hard band-topology filters in the first TB pilot stage.
Only basic solver-stability and schema-validity guards may be used.

## Execution Protocol

At any moment, only the single task in `TODO.md -> Current Task` may be
executed.

Do not start backlog tasks early.
Do not merge multiple tasks into one mega-step.

### For local Codex tasks
Before marking a local-preparation task complete:
- run only the exact lightweight tests allowed by `TODO.md`;
- verify config paths and docs are consistent;
- verify no heavy output has been fabricated;
- verify schema, checkpoint, and report wiring remain consistent;
- update `TODO.md` only after the preparation stage is genuinely complete.

### For manual server tasks
A manual server task must not be marked complete until:
- the user has executed the run on the server,
- compact returned artifacts are committed back to GitHub,
- and local review has accepted those artifacts.

## Dataset And Sampling Rules

Primary future training datasets must be built from:
- projected RMFT anchor samples,
- local RMFT-neighborhood samples,
- sparse bridge samples.

Do not default back to the old baseline-neighborhood local 5-control path as
the main pairing source.

Do not use unsupported direction regimes in the primary truth-grade pool.

## Feature Intake Rules

Direction must not be represented only as a raw continuous `interface_angle`.

When direction-aware training is implemented, feature intake must distinguish:
- discrete directional semantics,
- continuous transport controls,
- continuous spread controls,
- raw angle as auxiliary metadata when applicable.

Pairing input must now distinguish:
- full projected gauge-fixed 7+1 complex channels,
- gauge metadata,
- weak-channel activation metadata.

Do not collapse supported named modes, diagnostic-only angles, and unsupported
modes into one ambiguous feature path.

## Evaluation Rules

Future inverse-ready surrogate promotion must be judged against:
- the committed ridge baseline,
- the committed Task 12B plain neural baseline,
- and the committed Task 13B high-accuracy heavy surrogate family.

Do not claim a later inverse-ready surrogate is validated merely because it
trained successfully.
It must remain accurate under the wider pairing domain, wider bias window,
expanded nuisance domain, and TB pilot variation.

Evaluation for future inverse-ready tasks must be reported by:
- bias sub-window,
- nuisance sub-range,
- direction regime,
- and TB pilot regime when applicable.

## Scientific Reporting Rules

Inverse outputs must be candidate parameter families, not unique microscopic
truth claims.

Reports should say:
- "the AR data are compatible with these parameter families"

They should not say:
- "the order parameter is uniquely this RMFT point"

Always separate:
- projected pairing-channel structure;
- transport nuisance controls;
- TB pilot coordinates;
- experimental preprocessing;
- directional priors or directional regime assumptions;
- surrogate uncertainty;
- final direct-forward recheck results.

Do not present unsupported directional interpretations as established physical
results.

## Server Handoff Rules

Every manual server task should have a committed handoff note that states:
- exact commands to run;
- exact config files to use;
- expected output directories;
- which artifacts must be returned to GitHub for review;
- which heavy artifacts should stay only on the server.

Heavy outputs such as:
- full forward-output directories;
- large raw datasets;
- large checkpoints;
- bulky spectrum collections

should stay on the server unless `TODO.md` explicitly promotes a compact example
into the repository.

## Storage Rules

Large artifacts belong only in explicit output directories:
- datasets under `outputs/datasets/`
- checkpoints under `outputs/checkpoints/`
- training logs under `outputs/runs/`
- inverse results under `outputs/inverse/`
- experiment fits under `outputs/experiments/`

Do not commit heavyweight generated artifacts unless explicitly requested by
`TODO.md`.

## Cleanliness Rules

Do not leave behind obsolete configs, stale manifests, or ambiguous dual paths
that can contaminate later inverse-ready tasks.

When replacing the old baseline-neighborhood pairing-input path:
- update the docs;
- update the config examples;
- update tests;
- clearly mark the old path as legacy where necessary.

No silent dual-standard behavior is allowed for:
- direction semantics;
- pairing representation semantics;
- baseline-vs-neural checkpoint/report semantics;
- local Codex vs manual server execution responsibilities.
