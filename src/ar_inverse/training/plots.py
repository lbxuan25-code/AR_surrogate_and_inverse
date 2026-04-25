"""Plot-spec helpers for the frozen training observability standard."""

from __future__ import annotations


def training_curve_plot_suite() -> dict[str, object]:
    """Return the required training-curve figure suite."""

    return {
        "required_figures": [
            "train_vs_validation_loss",
            "reconstruction_vs_shape_loss",
            "learning_rate_curve",
        ],
        "x_axis": "epoch",
        "artifact_kind": "curve_figure",
    }


def representative_prediction_plot_suite() -> dict[str, object]:
    """Return the required direct-forward versus surrogate review plots."""

    return {
        "required_groups": [
            "best",
            "median",
            "worst",
        ],
        "required_layers": [
            "direct_forward_conductance",
            "surrogate_prediction",
            "absolute_error_curve",
        ],
        "required_metadata_labels": [
            "bias_sub_window",
            "pairing_source_role",
            "nuisance_sub_range",
            "tb_regime",
            "direction_regime",
        ],
        "artifact_kind": "spectrum_comparison_figure",
    }


def observability_plot_suite_spec() -> dict[str, object]:
    """Return the full frozen plot-suite contract."""

    return {
        "plot_suite_id": "training_observability_plots_v1",
        "training_curves": training_curve_plot_suite(),
        "representative_predictions": representative_prediction_plot_suite(),
    }
