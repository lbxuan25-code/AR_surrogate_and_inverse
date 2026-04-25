"""Runtime helpers for rendering observability artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def _plt():
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as pyplot

    return pyplot


def write_training_curve_figures(history: dict[str, list[float | None]], output_dir: Path | str) -> dict[str, str]:
    """Render the required training-curve figures and return artifact paths."""

    plt = _plt()
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)

    epochs = list(range(1, len(history.get("train_loss", [])) + 1))
    validation = [float(value) if value is not None else float("nan") for value in history.get("validation_loss", [])]

    train_validation_path = directory / "train_vs_validation_loss.png"
    figure = plt.figure(figsize=(8, 5))
    plt.plot(epochs, history.get("train_loss", []), label="train_loss")
    plt.plot(epochs, validation, label="validation_loss")
    plt.xlabel("epoch")
    plt.ylabel("loss")
    plt.title("Train vs Validation Loss")
    plt.legend()
    plt.tight_layout()
    figure.savefig(train_validation_path, dpi=160)
    plt.close(figure)

    reconstruction_shape_path = directory / "reconstruction_vs_shape_loss.png"
    figure = plt.figure(figsize=(8, 5))
    plt.plot(epochs, history.get("reconstruction_loss", []), label="reconstruction_loss")
    plt.plot(epochs, history.get("shape_loss", []), label="shape_loss")
    plt.xlabel("epoch")
    plt.ylabel("loss")
    plt.title("Reconstruction vs Shape Loss")
    plt.legend()
    plt.tight_layout()
    figure.savefig(reconstruction_shape_path, dpi=160)
    plt.close(figure)

    learning_rate_path = directory / "learning_rate_curve.png"
    figure = plt.figure(figsize=(8, 5))
    plt.plot(epochs, history.get("learning_rate", []), label="learning_rate")
    plt.xlabel("epoch")
    plt.ylabel("lr")
    plt.title("Learning Rate")
    plt.legend()
    plt.tight_layout()
    figure.savefig(learning_rate_path, dpi=160)
    plt.close(figure)

    return {
        "train_vs_validation_loss": train_validation_path.as_posix(),
        "reconstruction_vs_shape_loss": reconstruction_shape_path.as_posix(),
        "learning_rate_curve": learning_rate_path.as_posix(),
    }


def write_spectrum_comparison_figure(
    *,
    bias_mev: list[float],
    target: list[float],
    prediction: list[float],
    label: str,
    metadata_labels: dict[str, Any],
    output_path: Path | str,
) -> str:
    """Render one direct-forward versus surrogate spectrum comparison figure."""

    plt = _plt()
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    absolute_error = [abs(pred - truth) for pred, truth in zip(prediction, target, strict=True)]
    subtitle = ", ".join(f"{key}={value}" for key, value in metadata_labels.items())

    figure = plt.figure(figsize=(9, 6))
    plt.plot(bias_mev, target, label="direct_forward_conductance")
    plt.plot(bias_mev, prediction, label="surrogate_prediction")
    plt.plot(bias_mev, absolute_error, label="absolute_error_curve")
    plt.xlabel("bias_meV")
    plt.ylabel("conductance / error")
    plt.title(label if not subtitle else f"{label}\n{subtitle}")
    plt.legend()
    plt.tight_layout()
    figure.savefig(path, dpi=160)
    plt.close(figure)
    return path.as_posix()
