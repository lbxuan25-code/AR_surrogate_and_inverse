"""Training observability standard helpers for later surrogate runs."""

from __future__ import annotations


def required_training_curves() -> dict[str, dict[str, object]]:
    """Return the mandatory training-curve contract."""

    return {
        "train_loss": {"x_axis": "epoch", "required": True},
        "validation_loss": {"x_axis": "epoch", "required": True},
        "reconstruction_loss": {"x_axis": "epoch", "required": True},
        "shape_loss": {"x_axis": "epoch", "required": True},
        "learning_rate": {"x_axis": "epoch", "required": True},
    }


def optimization_diagnostics_contract() -> dict[str, object]:
    """Return the mandatory optimization-diagnostics contract."""

    return {
        "per_layer_gradient_norm_summary": {
            "required": True,
            "statistics": ["median", "max"],
        },
        "parameter_update_summary": {
            "required": True,
            "statistics": ["median_update_ratio", "max_update_ratio"],
        },
        "gradient_warnings": {
            "required": True,
            "explosion_threshold": 100.0,
            "vanishing_threshold": 1e-8,
            "consecutive_checkpoints_for_warning": 3,
        },
    }


def sensitivity_diagnostics_contract() -> dict[str, object]:
    """Return the mandatory feature-block sensitivity contract."""

    return {
        "blocks": [
            "pairing",
            "direction",
            "nuisance",
            "tb",
        ],
        "required_outputs": [
            "relative_sensitivity_score",
            "block_rank_order",
            "imbalance_warning",
        ],
        "imbalance_warning_ratio": 3.0,
    }


def grouped_error_report_contract() -> dict[str, object]:
    """Return the mandatory grouped-error reporting contract."""

    return {
        "required_axes": [
            "bias_sub_window",
            "pairing_source_role",
            "nuisance_sub_range",
            "tb_regime",
            "direction_regime",
        ],
        "bias_sub_windows": [
            "central_window",
            "inner_shoulder",
            "outer_shoulder",
            "edge_guard",
        ],
        "required_statistics": [
            "row_count",
            "mean_rmse",
            "max_rmse",
            "mean_max_abs_error",
            "representative_row_ids",
            "warning_flags",
        ],
    }


def observability_standard_spec() -> dict[str, object]:
    """Return the full frozen S5 observability standard."""

    return {
        "standard_id": "training_observability_standard_v1",
        "metrics_only_is_sufficient": False,
        "required_training_curves": required_training_curves(),
        "optimization_diagnostics": optimization_diagnostics_contract(),
        "sensitivity_diagnostics": sensitivity_diagnostics_contract(),
        "grouped_error_reports": grouped_error_report_contract(),
    }
