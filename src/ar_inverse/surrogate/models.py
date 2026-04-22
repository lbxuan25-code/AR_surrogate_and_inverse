"""Lightweight surrogate model baselines."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True, slots=True)
class FeatureSpec:
    """Feature order used by the first surrogate baseline."""

    names: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return {"names": list(self.names)}


DEFAULT_FEATURE_SPEC = FeatureSpec(
    names=(
        "delta_zz_s",
        "delta_xx_s",
        "delta_zx_d",
        "delta_perp_z",
        "delta_perp_x",
        "delta_zz_d",
        "delta_xx_d",
        "delta_zx_s",
        "direction_inplane_100",
        "direction_inplane_110",
        "direction_named_mode",
        "direction_diagnostic_raw_angle",
        "direction_has_spread",
        "direction_spread_half_width",
        "direction_spread_num_samples",
        "direction_raw_interface_angle",
        "barrier_z",
        "gamma",
        "temperature_kelvin",
        "nk",
    )
)


@dataclass(slots=True)
class RidgeLinearSpectrumSurrogate:
    """Ridge-linear map from controls to full conductance spectrum."""

    feature_spec: FeatureSpec
    weights: np.ndarray
    feature_mean: np.ndarray
    feature_scale: np.ndarray
    target_mean: np.ndarray
    ridge_alpha: float

    @classmethod
    def fit(
        cls,
        features: np.ndarray,
        targets: np.ndarray,
        *,
        feature_spec: FeatureSpec = DEFAULT_FEATURE_SPEC,
        ridge_alpha: float = 1.0e-6,
    ) -> "RidgeLinearSpectrumSurrogate":
        """Fit a ridge-linear model with standardized input features."""

        x = np.asarray(features, dtype=np.float64)
        y = np.asarray(targets, dtype=np.float64)
        if x.ndim != 2:
            raise ValueError("features must be a 2D array.")
        if y.ndim != 2:
            raise ValueError("targets must be a 2D array.")
        if x.shape[0] != y.shape[0]:
            raise ValueError("features and targets must have the same row count.")
        if x.shape[1] != len(feature_spec.names):
            raise ValueError("feature column count does not match feature_spec.")

        feature_mean = x.mean(axis=0)
        feature_scale = x.std(axis=0)
        feature_scale = np.where(feature_scale > 0.0, feature_scale, 1.0)
        x_scaled = (x - feature_mean) / feature_scale
        target_mean = y.mean(axis=0)
        y_centered = y - target_mean

        design = np.concatenate([np.ones((x_scaled.shape[0], 1), dtype=np.float64), x_scaled], axis=1)
        penalty = np.eye(design.shape[1], dtype=np.float64) * float(ridge_alpha)
        penalty[0, 0] = 0.0
        weights = np.linalg.pinv(design.T @ design + penalty) @ design.T @ y_centered

        return cls(
            feature_spec=feature_spec,
            weights=weights,
            feature_mean=feature_mean,
            feature_scale=feature_scale,
            target_mean=target_mean,
            ridge_alpha=float(ridge_alpha),
        )

    def predict(self, features: np.ndarray) -> np.ndarray:
        """Predict spectra for feature rows."""

        x = np.asarray(features, dtype=np.float64)
        if x.ndim == 1:
            x = x.reshape(1, -1)
        if x.shape[1] != len(self.feature_spec.names):
            raise ValueError("feature column count does not match feature_spec.")
        x_scaled = (x - self.feature_mean) / self.feature_scale
        design = np.concatenate([np.ones((x_scaled.shape[0], 1), dtype=np.float64), x_scaled], axis=1)
        return design @ self.weights + self.target_mean

    def save(self, path: Path | str) -> Path:
        """Save the model checkpoint as a compact npz file."""

        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        np.savez(
            output_path,
            weights=self.weights,
            feature_mean=self.feature_mean,
            feature_scale=self.feature_scale,
            target_mean=self.target_mean,
            ridge_alpha=np.asarray([self.ridge_alpha], dtype=np.float64),
            feature_names=np.asarray(self.feature_spec.names, dtype=str),
        )
        return output_path

    @classmethod
    def load(cls, path: Path | str) -> "RidgeLinearSpectrumSurrogate":
        """Load a model checkpoint saved by `save`."""

        data = np.load(Path(path), allow_pickle=False)
        return cls(
            feature_spec=FeatureSpec(names=tuple(str(value) for value in data["feature_names"].tolist())),
            weights=np.asarray(data["weights"], dtype=np.float64),
            feature_mean=np.asarray(data["feature_mean"], dtype=np.float64),
            feature_scale=np.asarray(data["feature_scale"], dtype=np.float64),
            target_mean=np.asarray(data["target_mean"], dtype=np.float64),
            ridge_alpha=float(np.asarray(data["ridge_alpha"], dtype=np.float64)[0]),
        )
