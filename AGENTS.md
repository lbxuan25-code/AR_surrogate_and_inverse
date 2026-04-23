# AGENTS.md

## Purpose

This repository hosts AR surrogate training, inverse search, experiment-fitting,
and experiment-side data handling.

It is not the source of truth for forward physics.
The forward truth chain lives in the external LNO327 AR forward repository and
must be consumed only through its stable public `forward` interface.

The current development cycle is focused on direction-aware surrogate
preparation, pilot validation, and production-handoff preparation under a split
local-edit / server-run workflow.

Current stage note:
- Task 9 completed the canonical direction-aware surrogate smoke loop.
- Task 10A completed the canonical non-smoke pilot preparation: configs,
  runbook, and lightweight validation are now in the repository.
- Task 10B completed: the server-run pilot artifacts were returned, reviewed
  locally, and accepted.
- Task 11A completed: the canonical production dataset/training/evaluation
  configs, frozen forward-family contract, handoff note, and lightweight
  validation are now in the repository.
- The current `TODO.md` task is Task 11B: run the first production server job
  and return compact review artifacts for local validation.
- Heavy execution remains deferred to explicit server-run tasks reviewed only
  after compact artifacts are returned to GitHub.

## Source Of Truth

Priority order:

1. this repository's `TODO.md`
2. committed configs, docs, and lightweight validation tests in this repository
3. dataset metadata, run metadata, and forward-interface version metadata
4. the external forward repository's public `forward` API contract
5. the external forward repository's published directional capability contract
6. local code and tests
7. returned server artifacts committed back to GitHub for review

If local assumptions conflict with forward-interface metadata or the external
direction contract, the external forward metadata and contract win.

## Workflow Model

This repository now uses a split execution workflow.

### Local Codex workspace responsibilities
Local Codex may:
- edit source code;
- edit configs;
- edit docs and runbooks;
- add or update lightweight validation tests;
- prepare server commands and output expectations;
- review compact server-returned artifacts after they are committed back.

Local Codex must not:
- silently run heavy pilot dataset generation;
- silently run heavy surrogate training;
- silently run heavy evaluation;
- pretend a server-run task completed before returned artifacts are reviewed.

### GitHub handoff responsibilities
GitHub is the handoff boundary between:
- local Codex preparation, and
- manual server execution.

Committed configs and runbooks are the authoritative instructions for the
server-side run.

### Server responsibilities
The server is where heavy execution happens:
- dataset generation
- surrogate training
- evaluation
- large output creation

The server may keep heavyweight artifacts locally. Only compact review artifacts
should normally be brought back to GitHub.

## Repository Boundary

This repository owns:
- dataset orchestration;
- sampling policies for fit-layer, transport, and supported directional regimes;
- surrogate model training code;
- surrogate evaluation and calibration code;
- inverse search;
- experiment-fitting reports;
- experiment-side ingest and preprocessing metadata;
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

## Execution Protocol

At any moment, only the single task in `TODO.md -> Current Task` may be
executed.

Do not start backlog tasks early.
Do not combine dataset generation, surrogate training, inverse search,
experiment preprocessing, and reporting into one unverified mega-step.

### For local Codex tasks
Before marking a preparation task complete:
- run only the lightweight tests or checks explicitly allowed by the task;
- verify config paths and docs are consistent;
- verify no heavy output has been fabricated;
- update `TODO.md` only after the preparation stage is genuinely complete.

### For server-run tasks
A server-run task must not be marked complete until compact returned artifacts
have been committed back to GitHub and reviewed locally.

Returned artifacts should include only compact validation evidence unless the
task explicitly requests a larger canonical artifact.

## Dataset And Sampling Rules

Primary training datasets must be built from supported truth-grade directional
regimes first.

Use this hierarchy unless the current task explicitly changes it:
1. supported named in-plane modes without spread
2. supported named in-plane modes with narrow spread
3. diagnostic-only raw-angle extensions, if explicitly enabled

Do not mix all regimes into one undifferentiated pool by default.

Sampling policy documents, configs, and returned manifests must make it clear:
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

## Server Handoff Rules

Every server-run task should have a committed runbook note that states:
- exact commands to run;
- exact config files to use;
- expected output directories;
- which artifacts must be returned to GitHub for review;
- which heavy artifacts should stay only on the server.

Heavy outputs such as:
- full forward-output directories
- large raw pilot or production datasets
- large checkpoints
- bulky spectrum collections

should stay on the server unless the task explicitly promotes a small canonical
example into the repository.

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
