# AGENTS.md

## Start Here For Any Fresh Codex Conversation

The user has reset the task authority.

Do not continue Codex-invented S9/S10 tasks.
Do not invent new mainline task numbers.
Do not promote a new Current Task unless the user explicitly approves it.

The active user-approved roadmap is:

1. P1 — prepare the first production-scale rectified surrogate run contract;
2. P2 — execute that production run locally and review compact artifacts;
3. P3 — review the run and decide the next user-approved action.

The repository has completed the surrogate rectification sequence S1-S8. S9/S10 were Codex-invented and are superseded.

## Purpose

This repository hosts AR surrogate dataset orchestration, surrogate training, evaluation, observability, and production-run review.

It is not the source of truth for forward physics. The forward truth chain lives in the external LNO327 AR forward repository and must be consumed only through its stable public `forward` interface.

The current mission is to prepare and run the first user-approved production-scale rectified surrogate training pipeline on the user's local machine.

## Task Authority Rules

The user owns task definition.

Codex may:
- execute the Current Task in `TODO.md`;
- suggest possible future tasks in prose;
- create files required by the Current Task;
- run only the lightweight or heavy actions explicitly allowed by the Current Task.

Codex must not:
- invent new mainline tasks;
- promote backlog items to Current Task;
- add S-number, P-number, or other numbered tasks by itself;
- reinterpret a draft contract as canonical;
- silently continue S9/S10;
- start heavy training unless the Current Task explicitly allows it.

If Codex believes a new task is needed, it must state it as a proposal for the user, not edit it into the mainline task chain.

## Current User-Approved Roadmap

### P1
Prepare the first production-scale rectified surrogate run contract.

P1 is local preparation only. It creates the production dataset, training, evaluation configs, and runbook. It does not run heavy generation or training.

### P2
Execute the first production-scale surrogate run locally and review compact artifacts.

P2 is the first heavy task. It may run dataset generation, training, and evaluation on the user's local machine, using only P1 configs.

### P3
Review the production run and decide the next action.

P3 is observation-dependent. It chooses whether to accept, rerun, scale, revise sampling, revise training, start active learning, or revisit capacity.

## Current Scientific / Engineering Baseline

The repository previously completed S1-S8:

- full projected complex 7+1 pairing representation with only global-phase gauge fixing;
- no PCA or latent compression of the pairing representation;
- TB representation caution: low-dimensional TB pilot is not automatically canonical;
- sampling quality comes before fixed row budgets;
- joint sampling contract exists;
- training observability standards exist;
- repository layout and naming standards exist;
- model-capacity decision rules say not to expand the residual MLP architecture yet;
- active learning is a future roadmap item, not the first production run.

## Source Of Truth

Priority order:

1. `TODO.md`
2. committed user-approved contracts, configs, runbooks, and tests
3. dataset metadata, run metadata, checkpoint metadata, and forward-interface metadata
4. the external forward repository's public `forward` API contract
5. the external forward repository's directional capability contract
6. local code and tests
7. compact returned artifacts committed back to GitHub for review

If local assumptions conflict with the external forward interface or directional contract, the forward repository wins.

## Local Execution Policy

The user intends to run production training locally unless a later user-approved task says otherwise.

Local execution assumptions:
- use WSL2;
- use CUDA GPU for training when available;
- do not silently fall back to CPU for training;
- begin CPU data generation with a conservative worker count, normally 8 workers;
- do not run multiple large ensemble members concurrently unless memory has been checked;
- keep heavy generated artifacts local and uncommitted unless explicitly promoted.

## Repository Boundary

This repository owns:
- dataset orchestration;
- sampling policy implementation;
- surrogate model training;
- evaluation and calibration;
- observability tooling;
- run metadata;
- model cards and review reports;
- production runbooks.

This repository must not copy, fork, or silently reimplement:
- authoritative normal-state Hamiltonian code;
- authoritative pairing-matrix code;
- RMFT source projection code;
- interface matching code;
- BTK solver code;
- formal baseline files;
- forward-side directional truth logic.

Use the external forward repository as the forward engine and metadata authority.

## Direction Contract Rules

Supported truth-grade regimes:
- `inplane_100`
- `inplane_110`

Supported spread regime:
- narrow named-mode-centered spread only, within the forward contract.

Unsupported:
- `c_axis` is not supported;
- do not train on it;
- do not expose it as a valid target.

Diagnostic-only:
- generic raw in-plane angles must not be silently promoted into the primary truth-grade pool.

## Pairing Representation Rules

Canonical pairing representation:
- full projected complex 7+1 pairing channels;
- gauge-fixed only to remove the single globally redundant phase;
- otherwise uncompressed.

Forbidden:
- PCA compression;
- latent manifold compression;
- learned low-dimensional pairing coordinates;
- any other lossy compression after the projected 7+1 representation.

Gauge fixing must preserve all relative phase information.

## TB Representation Rules

The old five-coordinate TB pilot is not automatically canonical.

Future production configs must preserve original-parameter provenance and any grouped training-facing TB controls required by the S2 decision. Do not treat a reduced TB representation as valid merely because it is convenient.

## Sampling Rules

Sampling-policy design comes before row-budget freezing.

Production configs should use the S3/S4 rectified sampling rules:
- RMFT anchor coverage;
- neighborhood density rules;
- bridge triggering rules;
- explicit continuous-subspace sampler;
- physically sensitive-region densification;
- joint sampling across pairing, nuisance, and TB spaces.

Do not replace sampling strategy with arbitrary fixed quotas.

## Observability Rules

A serious production training run must emit:

- train and validation loss curves;
- reconstruction and shape loss curves;
- learning-rate curve;
- gradient norm summary;
- parameter update summary;
- grouped error report;
- representative best / median / worst spectrum comparisons;
- metrics and run metadata;
- model card or run summary.

A single metrics file is not sufficient.

## Model Capacity Rules

Do not widen or deepen the model by intuition.

The current conclusion from S7 is:
- no sufficient evidence yet supports immediate expansion of model capacity;
- keep the residual architecture unchanged for the first production-scale rectified run.

Capacity changes require P3-style evidence from production observability artifacts.

## Active Learning Rules

Active learning is a future roadmap item, not part of the first production run.

Do not start active learning until a production baseline has been run and reviewed.

## File / Layout Rules

Prefer content-based names over task-number names.

For the first production contract, use:

- `docs/runbooks/production_surrogate_v1_handoff.md`
- `configs/datasets/production_surrogate_v1.dataset.json`
- `configs/training/production_surrogate_v1.training.json`
- `configs/evaluation/production_surrogate_v1.evaluation.json`
- `tests/test_production_surrogate_v1_contract.py`

Do not create new task-number-first files unless the user explicitly asks.

## Heavy Artifact Policy

Heavy artifacts should stay local and uncommitted unless explicitly promoted.

Usually do not commit:
- full forward outputs;
- bulky intermediate spectra;
- large checkpoints;
- scratch files;
- CUDA caches;
- profiling outputs.

Commit or review only compact artifacts specified by the active task.

## Review Rules

After a production run, do not silently accept it.

Review must check:
- held-out metrics;
- grouped errors;
- observability plots;
- worst-spectrum behavior;
- gradient and update summaries;
- dataset/run metadata consistency;
- forward metadata consistency.

The next task after P2 must be explicitly user-approved based on P3 review.
