# Task 14 RMFT Projection Audit

This document is the canonical audit skeleton for the later Task 14
server-side RMFT projection audit run.

The later audit metadata JSON must be written to:

- `outputs/runs/task14_rmft_projection_audit.json`

Task 14B does not generate that JSON locally.
It only freezes what the later server-side audit must report.

## Audit Purpose

The audit must prove that the canonical future pairing source is no longer the
old local `delta_from_baseline_meV` 5-control box.

It must instead show that the dataset family is built primarily from:

- projected RMFT anchor points;
- local neighborhoods around projected anchors;
- sparse bridge samples between nearby projected anchors.

## Required Audit Summary

The later audit must report:

- dataset id;
- sampling policy id;
- audit metadata output path;
- direction contract used;
- pairing representation version used;
- gauge-anchor priority used;
- forward metadata family used for the generated rows.

## Required Pairing Coverage Report

The later audit must include counts for:

- `anchor` rows;
- `neighborhood` rows;
- `bridge` rows;
- total rows;
- rows by split if splits are already assigned;
- rows by direction regime.

It must also describe:

- the projected RMFT source family used for anchor extraction;
- how neighborhoods were defined around anchors;
- how nearby-anchor pairs were selected for bridge samples;
- which bridge provenance fields were stored in the dataset rows or audit
  metadata.

## Required Representation Report

The later audit must verify:

- the full gauge-fixed 7+1 channels are stored;
- only one global phase rotation was removed;
- no PCA or latent compression was used;
- `weak_channel_active` was preserved;
- the dataset rows use `controls.pairing_representation`;
- the dataset rows use schema version `ar_inverse_dataset_row_v3`.

## Required Legacy-Replacement Check

The later audit must explicitly state:

- the old `delta_from_baseline_meV` path is not the canonical main source of
  pairing samples for this dataset family;
- symmetry labels are not used as training labels;
- no unsupported direction regime was promoted into the primary truth-grade
  pool.

## Required Returned Artifact Shape

The later compact returned audit artifacts should include:

- this audit document updated with concrete run results;
- `outputs/runs/task14_rmft_projection_audit.json`;
- the committed dataset contract file
  `configs/datasets/task14_rmft_anchor_dataset.json`;
- any compact manifest-family summary needed to review anchor, neighborhood,
  and bridge counts without returning heavy raw data.
