# Active Learning Plan

Task S8 freezes the active-learning roadmap for later surrogate work.

This task does not execute active learning.
It defines the future loop only.

## Scope

Active learning is a later extension to the surrogate roadmap, not a
replacement for the rectified representation, sampling, observability, and
review standards already frozen by Tasks S1-S7.

Any future active-learning round must continue to obey:

- the forward repository public `forward` interface;
- the frozen direction contract;
- the pairing-representation contract;
- the grouped-error and observability standards;
- the local-Codex / manual-server split workflow.

## Initial Training Stage

The initial stage is a standard supervised surrogate-training stage on the
current accepted dataset family.

That stage must:

1. start from a committed dataset contract and committed training config;
2. train a surrogate under the current accepted architecture and loss contract;
3. emit the full observability artifact set from Task S5;
4. emit held-out grouped error reports and representative spectrum plots;
5. freeze one reviewable checkpoint family before any difficulty-driven point
   selection begins.

Active learning must not begin from an unreviewed or observability-poor run.

## Uncertainty / Difficulty Trigger

New points are selected only when the current accepted surrogate shows explicit
difficulty evidence.

The trigger is a union of three allowed difficulty sources:

1. uncertainty trigger:
   ensemble disagreement or another committed uncertainty proxy exceeds its
   accepted threshold;
2. grouped-regime trigger:
   grouped error reports show a regime that remains a repeated outlier across
   accepted reviews;
3. representative-spectrum trigger:
   best / median / worst review plots show persistent shape failure in a regime
   that matters to the accepted target scope.

The trigger must be written as a compact returned artifact for each round.
It must identify:

- which rows or candidate regions were flagged;
- why they were flagged;
- which trigger category fired;
- which regime labels were involved.

No active-learning round may add points merely because "more data is probably
better."

## Forward Relabel Path

When difficult points are identified, they must be sent back through the
external forward truth chain, not labeled locally by imitation.

The relabel path is:

1. produce a compact candidate-selection artifact listing the difficult points
   or candidate regions;
2. commit the exact server handoff note and exact forward-generation command;
3. run the true forward labeling on the server through the external `forward`
   repository interface;
4. return compact artifacts proving which new rows were generated and under
   which forward metadata family;
5. review those returned artifacts locally before the new rows are promoted.

The active-learning loop must never fabricate true labels inside this
repository.

## Merge-Back Rule

New true-labeled rows are merged back only as a new dataset version or explicit
dataset-family extension.

The merge must record:

- parent dataset family;
- newly added rows;
- trigger provenance for those rows;
- forward metadata family for the new labels;
- whether the round is pure append or requires a family split.

Rows generated under incompatible forward metadata or direction contracts must
remain a distinct dataset family rather than being silently merged.

## Retrain Stage

After the merge, the surrogate is retrained on the expanded accepted dataset.

The retrain stage must:

1. use a committed training config for the new round;
2. emit the same observability artifact family as the initial stage;
3. emit grouped error reports that can be compared with the prior round;
4. emit representative best / median / worst spectrum comparisons;
5. produce a compact round-comparison artifact summarizing whether the newly
   added data improved the flagged failure modes.

Active learning is successful only if the round improves the targeted difficult
regimes without breaking accepted behavior elsewhere.

## Required Returned Compact Artifacts

Each active-learning round must return compact artifacts sufficient for local
review.

At minimum, the returned compact artifact set must include:

1. `difficulty_trigger_report.json`
   Contains the uncertainty / difficulty trigger, flagged regimes, and selected
   candidate rows or regions.
2. `forward_relabel_round_metadata.json`
   Records the exact forward labeling run, dataset family, and forward metadata
   family for the newly labeled rows.
3. `dataset_merge_report.json`
   Records how the new rows were appended or split into a new dataset family.
4. `training_round_metrics.json`
   Summarizes retraining metrics for the new round.
5. `training_round_observability_manifest.json`
   Points to the required training curves, optimization summaries, grouped error
   reports, and representative spectrum plots.
6. `round_comparison_report.json`
   Compares the new round against the previous accepted round and states whether
   the targeted difficult regimes improved.

## Promotion Rule

A later active-learning round may be accepted only if local review confirms all
of the following:

- the difficulty trigger was explicit;
- the forward relabel path used true forward labels;
- the dataset merge preserved provenance and family boundaries;
- the retrained surrogate emitted full observability artifacts;
- the round comparison shows improvement or at least a justified tradeoff.

Without those conditions, the round is not accepted as a valid roadmap step.
