# TODO

## Current Task

### Awaiting User Decision After P3 Review

#### Task type
Manual rerun gate after approved local repairs.

#### Goal
Let the user rerun the repaired production v1 heavy pipeline from the terminal.

P3 reviewed `production_surrogate_v1` and selected:

> revise sampling and metadata before acceptance.

Reason:

- training and held-out evaluation quality are strong;
- no S7 model-capacity trigger was observed;
- the materialized P2 sampling composition does not match the P1 targets;
- the original Luo RMFT source point cloud and source-to-anchor mapping are not
  present in P2 artifacts, so RMFT source coverage cannot be proven.

#### Decision evidence

- review:
  `docs/reviews/production_surrogate_v1_review.md`
- RMFT coverage audit:
  `outputs/audits/production_surrogate_v1/rmft_source_coverage_audit.json`
- required 2D figure:
  `outputs/figures/production_surrogate_v1/luo_rmft_sampling_2d.png`

#### Repair status

The user approved fixing the problems found in P3 before rerunning heavy work.
Local code/config/doc/test repairs are complete:

- production v1 materialization now enforces P1 role, direction, and TB quotas
  exactly;
- production v1 materialization now consumes the external forward repository's
  compact round-2 Luo/RMFT projection CSV;
- production rows now carry source provenance and
  `controls.pairing_representation`;
- production training now uses `feature_spec_id =
  projected_7plus1_complex_v1`;
- evaluation now uses the checkpoint feature spec when rebuilding features.

#### Next step

The user should rerun data generation, training, and evaluation manually from
the terminal to monitor progress.

Do not automatically promote active learning, model expansion, or a new
numbered task before the repaired run is reviewed.

---

## Backlog

No backlog task is currently promoted.

---

## Archive

### Task P3 — Review production run, audit Luo-RMFT coverage, and decide next action

Completed.

#### Task type
Observation-dependent review task.

#### Goal
Use P2 outputs to decide what to do next.

P3 must not only review surrogate training quality. It must also audit whether
the production v1 sampling distribution broadly covers the original Luo RMFT
parameter space.

The key additional question is:

> In the original Luo RMFT parameter space, does production_surrogate_v1 cover
> most of the physically relevant region, or does it concentrate in only a small
> subset of the Luo RMFT distribution?

#### Required precondition
P2 must be complete.

The following P2 artifacts must exist before P3 can begin:

- production v1 dataset manifest and metadata;
- production v1 training observability artifacts;
- production v1 evaluation report;
- production v1 grouped error report;
- production v1 best / median / worst spectrum comparison plots.

#### Required review evidence
The decision must be based on:

- train / validation curves;
- reconstruction / shape loss curves;
- grouped error report;
- worst spectrum comparisons;
- gradient and parameter update summaries;
- held-out metrics;
- uncertainty / ensemble diagnostics if available;
- RMFT source coverage audit;
- two-dimensional visualization of production samples inside Luo's original
  RMFT parameter space.

#### Required RMFT source coverage audit
P3 must include a dedicated RMFT coverage audit section.

The audit must compare:

1. the original Luo RMFT parameter dataset;
2. the RMFT anchors used by production_surrogate_v1;
3. production_surrogate_v1 neighborhood samples;
4. production_surrogate_v1 bridge samples.

The audit must report at minimum:

- total number of original Luo RMFT points available;
- number and fraction of Luo RMFT anchor points used by production_surrogate_v1;
- whether production samples cover the high-density body of the Luo RMFT point cloud;
- whether production samples cover sparse / edge / boundary regions;
- whether any obvious Luo RMFT clusters are missing;
- whether anchor / neighborhood / bridge samples occupy distinct useful regions
  or mostly collapse onto the same area;
- nearest-neighbor distance statistics from Luo RMFT points to production samples;
- marginal coverage for the main projected 7+1 gauge-fixed pairing channels;
- a clear pass / warning / fail judgment for RMFT coverage.

#### Required 2D Luo-parameter-space visualization
P3 must generate at least one clear two-dimensional figure showing the production
sampling distribution inside Luo's original RMFT parameter space.

The preferred figure is:

- background: all original Luo RMFT points, plotted in light gray;
- overlay 1: production v1 anchor samples;
- overlay 2: production v1 neighborhood samples;
- overlay 3: production v1 bridge samples;
- axes: two physically meaningful Luo RMFT coordinates if available;
- otherwise axes: the first two principal components of the original Luo RMFT
  parameter vectors or the full projected 7+1 gauge-fixed pairing representation.

The figure must be saved as:

- `outputs/figures/production_surrogate_v1/luo_rmft_sampling_2d.png`

and referenced from:

- `docs/reviews/production_surrogate_v1_review.md`

If PCA is used for the 2D visualization, the review must also report:

- which input vector was used for PCA;
- explained variance ratio of PC1 and PC2;
- whether the 2D projection is only a visualization aid, not a replacement for
  the full high-dimensional coverage audit.

#### Required optional diagnostic figures
If implementation is straightforward, P3 should also generate:

- `outputs/figures/production_surrogate_v1/luo_rmft_sampling_density_2d.png`
- `outputs/figures/production_surrogate_v1/luo_rmft_nearest_neighbor_distance.png`
- `outputs/figures/production_surrogate_v1/luo_rmft_channel_marginal_coverage.png`

These optional figures are not required to complete P3, but should be generated
if the necessary metadata are already available.

#### Fixed output files
P3 must create or update:

- `docs/reviews/production_surrogate_v1_review.md`
- `outputs/figures/production_surrogate_v1/luo_rmft_sampling_2d.png`

If a separate machine-readable audit artifact is useful, create:

- `outputs/audits/production_surrogate_v1/rmft_source_coverage_audit.json`

#### Possible outcomes
Exactly one primary outcome should be chosen:

1. accept production_surrogate_v1 as the current baseline;
2. revise sampling and rerun because Luo RMFT coverage is insufficient;
3. revise training settings and rerun;
4. scale dataset size using the same sampling policy;
5. start an active-learning round;
6. revisit model capacity only if S7 decision rules are triggered.

#### Decision rules
P3 must prioritize decisions in this order:

1. If Luo RMFT coverage is clearly insufficient, revise sampling before active
   learning, model expansion, or acceptance.
2. If Luo RMFT coverage is broad but certain regimes still fail, consider
   active learning or targeted densification.
3. If coverage is broad and errors are acceptable, accept production_surrogate_v1
   as the current baseline.
4. If train / validation curves or gradient diagnostics show instability, revise
   training settings before changing the model architecture.
5. Revisit model capacity only if the S7 capacity decision rules are clearly
   triggered.

#### Completion summary

P3 reviewed P2 compact artifacts and generated:

- `docs/reviews/production_surrogate_v1_review.md`
- `outputs/audits/production_surrogate_v1/rmft_source_coverage_audit.json`
- `outputs/figures/production_surrogate_v1/luo_rmft_sampling_2d.png`
- `outputs/figures/production_surrogate_v1/luo_rmft_sampling_density_2d.png`
- `outputs/figures/production_surrogate_v1/luo_rmft_nearest_neighbor_distance.png`
- `outputs/figures/production_surrogate_v1/luo_rmft_channel_marginal_coverage.png`

Decision:

- training/evaluation quality: acceptable under the materialized dataset;
- model capacity: do not change;
- active learning: do not start yet;
- RMFT coverage: warning, because original Luo source artifacts are missing;
- sampling contract: warning, because P2 materialized composition does not match
  P1 targets;
- primary outcome: revise sampling and metadata before accepting v1 as the
  current baseline.

Validation completed:

- `pytest tests/test_production_surrogate_v1_review.py tests/test_production_surrogate_v1_contract.py tests/test_repository_cleanup_paths.py -q`

### Task P2 — Execute the first production-scale surrogate run locally

Completed.

P2 executed the first user-approved production-scale rectified surrogate run on
the local machine using the P1 configs.

Completion summary:

- dataset generation completed under P1 contract;
- training completed under P1 contract;
- evaluation completed under P1 contract;
- observability artifacts exist;
- compact artifacts are reviewable;
- heavy outputs remain local and uncommitted;
- explicit accept/reject decision was deferred to P3.

### Task P1 — User-approved first production-scale surrogate run contract

Completed.

P1 froze the first user-approved production-scale dataset-generation, training,
and evaluation contract for the rectified surrogate pipeline. It produced the
content-based P1 runbook, dataset config, training config, evaluation config,
and lightweight contract test. It did not run heavy generation, training, or
evaluation.

Validation completed:

- `pytest tests/test_production_surrogate_v1_contract.py -q`

### Tasks S1-S8 — Surrogate rectification sequence

Completed previously.

Summary:
- S1 stopped direct promotion of the old Task 15B route.
- S2 audited TB representation and demoted the five-coordinate TB pilot from automatic canonical status.
- S3 froze sampling-quality-first policy.
- S4 froze joint sampling policy.
- S5 froze training observability standards.
- S6 froze repository layout and naming standards.
- S7 concluded that current evidence does not justify immediate model expansion.
- S8 froze active learning as a future roadmap item.

### Codex-proposed S9/S10

Superseded.

S9/S10 were introduced by Codex after S8 and are not user-owned canonical task definitions. They must not be treated as the active execution path. This TODO replaces them with the user-approved P1/P2/P3 production sequence.

### Earlier historical tasks

Task 13B, Task 14A-14E, Task 15A, and earlier tasks remain historical references. Task 15A is a draft reference contract only and is not the active production contract.
