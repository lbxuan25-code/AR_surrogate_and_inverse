from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

import pytest

from ar_inverse.datasets.build import load_dataset_config, materialize_dataset_samples
from ar_inverse.surrogate.evaluate import _grouped_error_report
from ar_inverse.surrogate.models import checkpoint_filename_for_model_type
from ar_inverse.surrogate.train import _feature_from_row, feature_spec_from_config


DATASET_CONFIG_PATH = Path("configs/datasets/production_surrogate_v1.dataset.json")
TRAINING_CONFIG_PATH = Path("configs/training/production_surrogate_v1.training.json")
EVALUATION_CONFIG_PATH = Path("configs/evaluation/production_surrogate_v1.evaluation.json")


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_minimal_rmft_projection_source(root: Path) -> None:
    source_dir = root / "outputs/source"
    source_dir.mkdir(parents=True)
    (source_dir / "round2_projection_examples.csv").write_text(
        "\n".join(
            [
                "sample_id,delta_zz_s,delta_zz_d,delta_xx_s,delta_xx_d,delta_zx_d,delta_perp_z,delta_perp_x,delta_zx_s",
                "s0,1+0j,0.1+0.2j,0.3+0j,0.4+0.1j,0.5+0j,0.6+0j,0.7+0j,0+0j",
                "s1,2+0j,0.2+0.1j,0.4+0j,0.5+0.1j,0.6+0j,0.7+0j,0.8+0j,0.01+0j",
                "s2,3+0j,0.3+0.1j,0.5+0j,0.6+0.1j,0.7+0j,0.8+0j,0.9+0j,0+0j",
                "s3,4+0j,0.4+0.1j,0.6+0j,0.7+0.1j,0.8+0j,0.9+0j,1.0+0j,0+0j",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _materialized_samples(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    _write_minimal_rmft_projection_source(tmp_path)
    monkeypatch.setenv("LNO327_FORWARD_REPO", str(tmp_path))
    return materialize_dataset_samples(load_dataset_config(DATASET_CONFIG_PATH))


def test_production_v1_materializer_enforces_exact_contract_quotas(tmp_path, monkeypatch) -> None:
    samples = _materialized_samples(tmp_path, monkeypatch)

    assert len(samples) == 8192
    assert Counter(sample.split for sample in samples) == {
        "train": 6144,
        "validation": 1024,
        "test": 1024,
    }
    assert Counter(sample.group_labels["pairing_source_role"] for sample in samples) == {
        "anchor": 3072,
        "neighborhood": 3072,
        "bridge": 2048,
    }
    assert Counter(sample.group_labels["tb_regime"] for sample in samples) == {
        "near_baseline": 6144,
        "edge_probe": 2048,
    }
    direction_regimes = Counter(
        "named_mode_narrow_spread"
        if sample.direction and sample.direction.get("directional_spread")
        else f"{sample.direction['direction_mode']}_no_spread"
        for sample in samples
    )
    assert direction_regimes == {
        "inplane_100_no_spread": 2048,
        "inplane_110_no_spread": 2048,
        "named_mode_narrow_spread": 4096,
    }


def test_production_v1_samples_carry_pairing_representation_and_rmft_provenance(tmp_path, monkeypatch) -> None:
    samples = _materialized_samples(tmp_path, monkeypatch)

    for sample in (samples[0], samples[3072], samples[6144]):
        assert sample.pairing_control_mode == "absolute_meV"
        assert sample.pairing_representation is not None
        assert sample.pairing_representation["pairing_representation_version"] == "projected_7plus1_gauge_fixed_v1"
        provenance = sample.source_provenance
        assert provenance is not None
        assert provenance["pairing_source_role"] == sample.group_labels["pairing_source_role"]
        assert provenance["source_sample_ids"]
        assert provenance["source_indices"]
        assert provenance["forward_request_mode"] == "fit_layer_absolute_meV_real_channels"
        assert provenance["dataset_training_representation"] == "projected_7plus1_complex_gauge_fixed_v1"
        assert provenance["full_complex_7plus1_forward_truth_input"] is False
    bridge = next(sample for sample in samples if sample.group_labels["pairing_source_role"] == "bridge")
    assert len(bridge.source_provenance["bridge_endpoint_source_sample_ids"]) == 2


def test_projected_complex_feature_spec_reads_pairing_representation(tmp_path, monkeypatch) -> None:
    sample = _materialized_samples(tmp_path, monkeypatch)[0]
    training = _load_json(TRAINING_CONFIG_PATH)
    feature_spec = feature_spec_from_config(training)

    row = {
        "row_id": sample.row_id,
        "direction": sample.direction,
        "controls": {
            "pairing_representation": sample.pairing_representation,
            "fit_layer_pairing_controls": sample.pairing_controls,
            "transport_controls": sample.transport_controls,
        },
    }
    features = _feature_from_row(row, feature_spec=feature_spec)

    assert training["feature_spec_id"] == "projected_7plus1_complex_v1"
    assert "delta_zz_s_re" in feature_spec.names
    assert "delta_zx_s_im" in feature_spec.names
    assert len(features) == len(feature_spec.names)

    bad_row = {**row, "controls": {"transport_controls": sample.transport_controls}}
    with pytest.raises(ValueError, match="missing controls.pairing_representation"):
        _feature_from_row(bad_row, feature_spec=feature_spec)


def test_evaluation_checkpoint_matches_training_output_filename() -> None:
    training = _load_json(TRAINING_CONFIG_PATH)
    evaluation = _load_json(EVALUATION_CONFIG_PATH)

    expected_checkpoint = Path(str(training["checkpoint_dir"])) / checkpoint_filename_for_model_type(
        str(training["model_type"])
    )
    assert evaluation["checkpoint"] == expected_checkpoint.as_posix()


def test_grouped_error_axis_names_match_config() -> None:
    evaluation = _load_json(EVALUATION_CONFIG_PATH)
    row_records = [
        {
            "row_id": "r0",
            "metrics": {"rmse": 0.1, "max_abs_error": 0.2},
            "pairing_source_role": "anchor",
            "nuisance_regime": "core_sharp",
            "tb_regime": "near_baseline",
            "direction_regime": "inplane_100_no_spread",
        }
    ]
    report = _grouped_error_report(
        row_records=row_records,
        held_out_examples=[{"row_id": "r0", "prediction": [0.0, 1.0], "target": [0.1, 1.1]}],
        bias_mev=[-1.0, 1.0],
    )

    assert report["required_axes"] == evaluation["grouped_error_axes"]
    assert set(report["axes"]) == set(evaluation["grouped_error_axes"])
    assert "nuisance_regime" in report["axes"]
    assert "nuisance_sub_range" not in report["axes"]


def test_rmft_source_missing_fails_fast(monkeypatch) -> None:
    monkeypatch.delenv("LNO327_FORWARD_REPO", raising=False)
    monkeypatch.delenv("LNO327_FORWARD_SRC", raising=False)

    with pytest.raises(ValueError, match="requires an explicit forward repository root"):
        materialize_dataset_samples(load_dataset_config(DATASET_CONFIG_PATH))
