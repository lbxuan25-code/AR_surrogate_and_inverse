from __future__ import annotations

import importlib.util
from pathlib import Path


DOC_PATH = Path("docs/training_observability_standard.md")
MONITORING_PATH = Path("src/ar_inverse/training/monitoring.py")
PLOTS_PATH = Path("src/ar_inverse/training/plots.py")


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Could not load module from {path}.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_training_observability_doc_freezes_required_curves_and_diagnostics() -> None:
    doc = DOC_PATH.read_text(encoding="utf-8")

    assert "one `metrics.json`" in doc
    assert "one `evaluation_report.json`" in doc
    assert "train loss versus epoch" in doc
    assert "validation loss versus epoch" in doc
    assert "reconstruction loss versus epoch" in doc
    assert "shape loss versus epoch" in doc
    assert "learning-rate curve versus epoch" in doc
    assert "per-layer gradient norm summary" in doc
    assert "parameter update magnitude summary" in doc
    assert "gradient explosion warning logic" in doc
    assert "gradient vanishing warning logic" in doc


def test_training_observability_contract_freezes_sensitivity_and_grouped_error_axes() -> None:
    monitoring = _load_module("monitoring_contract", MONITORING_PATH)
    spec = monitoring.observability_standard_spec()

    assert spec["standard_id"] == "training_observability_standard_v1"
    assert spec["metrics_only_is_sufficient"] is False
    assert list(spec["required_training_curves"]) == [
        "train_loss",
        "validation_loss",
        "reconstruction_loss",
        "shape_loss",
        "learning_rate",
    ]
    assert spec["sensitivity_diagnostics"]["blocks"] == [
        "pairing",
        "direction",
        "nuisance",
        "tb",
    ]
    assert spec["grouped_error_reports"]["required_axes"] == [
        "bias_sub_window",
        "pairing_source_role",
        "nuisance_sub_range",
        "tb_regime",
        "direction_regime",
    ]


def test_training_observability_plot_suite_requires_representative_spectrum_figures() -> None:
    plots = _load_module("plot_contract", PLOTS_PATH)
    plot_spec = plots.observability_plot_suite_spec()

    assert plot_spec["plot_suite_id"] == "training_observability_plots_v1"
    assert plot_spec["training_curves"]["required_figures"] == [
        "train_vs_validation_loss",
        "reconstruction_vs_shape_loss",
        "learning_rate_curve",
    ]
    assert plot_spec["representative_predictions"]["required_groups"] == [
        "best",
        "median",
        "worst",
    ]
    assert plot_spec["representative_predictions"]["required_layers"] == [
        "direct_forward_conductance",
        "surrogate_prediction",
        "absolute_error_curve",
    ]
    assert plot_spec["representative_predictions"]["required_metadata_labels"] == [
        "bias_sub_window",
        "pairing_source_role",
        "nuisance_sub_range",
        "tb_regime",
        "direction_regime",
    ]
