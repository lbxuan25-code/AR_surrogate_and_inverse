"""Surrogate model implementations and checkpoint loading helpers."""

from __future__ import annotations

import copy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset

RIDGE_MODEL_TYPE = "ridge_linear_spectrum_surrogate"
NEURAL_MLP_MODEL_TYPE = "neural_mlp_spectrum_surrogate"


@dataclass(frozen=True, slots=True)
class FeatureSpec:
    """Feature order used by surrogate models."""

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


def normalize_model_type(model_type: str | None) -> str:
    """Normalize config aliases into canonical model type ids."""

    normalized = str(model_type or RIDGE_MODEL_TYPE).strip().lower()
    aliases = {
        "ridge": RIDGE_MODEL_TYPE,
        "ridge_linear": RIDGE_MODEL_TYPE,
        RIDGE_MODEL_TYPE: RIDGE_MODEL_TYPE,
        "neural": NEURAL_MLP_MODEL_TYPE,
        "neural_mlp": NEURAL_MLP_MODEL_TYPE,
        "mlp": NEURAL_MLP_MODEL_TYPE,
        NEURAL_MLP_MODEL_TYPE: NEURAL_MLP_MODEL_TYPE,
    }
    if normalized not in aliases:
        raise ValueError(f"Unsupported model_type {model_type!r}.")
    return aliases[normalized]


def checkpoint_filename_for_model_type(model_type: str) -> str:
    """Return the default checkpoint filename for the given model type."""

    canonical = normalize_model_type(model_type)
    return "model.pt" if canonical == NEURAL_MLP_MODEL_TYPE else "model.npz"


def resolve_device(device: str | None) -> str:
    """Resolve a requested torch device into a concrete device string."""

    requested = str(device or "auto").strip().lower()
    if requested == "auto":
        return "cuda" if torch.cuda.is_available() else "cpu"
    if requested.startswith("cuda") and not torch.cuda.is_available():
        raise ValueError("CUDA device requested but torch.cuda.is_available() is false.")
    if requested not in {"cpu", "mps"} and not requested.startswith("cuda"):
        raise ValueError(f"Unsupported device selection {device!r}.")
    return requested


def activation_module(name: str) -> nn.Module:
    """Construct a supported activation module."""

    normalized = str(name).strip().lower()
    if normalized == "relu":
        return nn.ReLU()
    if normalized == "gelu":
        return nn.GELU()
    if normalized == "tanh":
        return nn.Tanh()
    if normalized == "silu":
        return nn.SiLU()
    raise ValueError(f"Unsupported activation {name!r}.")


def optimizer_factory(
    optimizer_name: str,
    parameters: Any,
    *,
    learning_rate: float,
) -> torch.optim.Optimizer:
    """Construct a supported optimizer."""

    normalized = str(optimizer_name).strip().lower()
    if normalized == "adam":
        return torch.optim.Adam(parameters, lr=learning_rate)
    if normalized == "adamw":
        return torch.optim.AdamW(parameters, lr=learning_rate)
    if normalized == "sgd":
        return torch.optim.SGD(parameters, lr=learning_rate, momentum=0.9)
    raise ValueError(f"Unsupported optimizer {optimizer_name!r}.")


def _as_float_array(values: np.ndarray) -> np.ndarray:
    return np.asarray(values, dtype=np.float64)


def _standardize(values: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    mean = values.mean(axis=0)
    scale = values.std(axis=0)
    scale = np.where(scale > 0.0, scale, 1.0)
    standardized = (values - mean) / scale
    return standardized, mean, scale


def _build_mlp(
    *,
    input_dim: int,
    output_dim: int,
    hidden_layer_widths: tuple[int, ...],
    activation_name: str,
) -> nn.Sequential:
    layers: list[nn.Module] = []
    last_width = input_dim
    for width in hidden_layer_widths:
        layers.append(nn.Linear(last_width, int(width)))
        layers.append(activation_module(activation_name))
        last_width = int(width)
    layers.append(nn.Linear(last_width, output_dim))
    return nn.Sequential(*layers)


@dataclass(slots=True)
class RidgeLinearSpectrumSurrogate:
    """Ridge-linear map from controls to full conductance spectrum."""

    feature_spec: FeatureSpec
    weights: np.ndarray
    feature_mean: np.ndarray
    feature_scale: np.ndarray
    target_mean: np.ndarray
    ridge_alpha: float

    @property
    def model_type(self) -> str:
        return RIDGE_MODEL_TYPE

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

        x = _as_float_array(features)
        y = _as_float_array(targets)
        if x.ndim != 2:
            raise ValueError("features must be a 2D array.")
        if y.ndim != 2:
            raise ValueError("targets must be a 2D array.")
        if x.shape[0] != y.shape[0]:
            raise ValueError("features and targets must have the same row count.")
        if x.shape[1] != len(feature_spec.names):
            raise ValueError("feature column count does not match feature_spec.")

        x_scaled, feature_mean, feature_scale = _standardize(x)
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

    def predict(self, features: np.ndarray, *, device: str | None = None) -> np.ndarray:
        """Predict spectra for feature rows."""

        del device
        x = _as_float_array(features)
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
            model_type=np.asarray([self.model_type], dtype=str),
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
        """Load a ridge checkpoint saved by `save`."""

        data = np.load(Path(path), allow_pickle=False)
        if "model_type" in data:
            model_type = str(np.asarray(data["model_type"]).reshape(-1)[0])
            if normalize_model_type(model_type) != RIDGE_MODEL_TYPE:
                raise ValueError(f"Checkpoint {path} is not a ridge surrogate checkpoint.")
        return cls(
            feature_spec=FeatureSpec(names=tuple(str(value) for value in data["feature_names"].tolist())),
            weights=_as_float_array(data["weights"]),
            feature_mean=_as_float_array(data["feature_mean"]),
            feature_scale=_as_float_array(data["feature_scale"]),
            target_mean=_as_float_array(data["target_mean"]),
            ridge_alpha=float(_as_float_array(data["ridge_alpha"])[0]),
        )


@dataclass(slots=True)
class NeuralMLPSpectrumSurrogate:
    """Simple feed-forward neural surrogate for full-spectrum prediction."""

    feature_spec: FeatureSpec
    module: nn.Module
    feature_mean: np.ndarray
    feature_scale: np.ndarray
    target_mean: np.ndarray
    target_scale: np.ndarray
    hidden_layer_widths: tuple[int, ...]
    activation_name: str

    @property
    def model_type(self) -> str:
        return NEURAL_MLP_MODEL_TYPE

    @classmethod
    def fit(
        cls,
        features: np.ndarray,
        targets: np.ndarray,
        *,
        validation_features: np.ndarray | None = None,
        validation_targets: np.ndarray | None = None,
        feature_spec: FeatureSpec = DEFAULT_FEATURE_SPEC,
        hidden_layer_widths: tuple[int, ...] = (128, 128),
        activation_name: str = "relu",
        optimizer_name: str = "adam",
        learning_rate: float = 1.0e-3,
        batch_size: int = 32,
        max_epochs: int = 100,
        early_stopping_patience: int = 10,
        random_seed: int = 0,
        device: str = "auto",
    ) -> tuple["NeuralMLPSpectrumSurrogate", dict[str, Any]]:
        """Fit a simple MLP surrogate and return training summary metadata."""

        x_train = _as_float_array(features)
        y_train = _as_float_array(targets)
        if x_train.ndim != 2:
            raise ValueError("features must be a 2D array.")
        if y_train.ndim != 2:
            raise ValueError("targets must be a 2D array.")
        if x_train.shape[0] != y_train.shape[0]:
            raise ValueError("features and targets must have the same row count.")
        if x_train.shape[1] != len(feature_spec.names):
            raise ValueError("feature column count does not match feature_spec.")
        if not hidden_layer_widths or any(int(width) < 1 for width in hidden_layer_widths):
            raise ValueError("hidden_layer_widths must contain positive integers.")
        if int(batch_size) < 1:
            raise ValueError("batch_size must be at least 1.")
        if int(max_epochs) < 1:
            raise ValueError("max_epochs must be at least 1.")
        if int(early_stopping_patience) < 1:
            raise ValueError("early_stopping_patience must be at least 1.")

        torch.manual_seed(int(random_seed))
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(int(random_seed))

        x_train_scaled, feature_mean, feature_scale = _standardize(x_train)
        y_train_scaled, target_mean, target_scale = _standardize(y_train)

        has_validation = validation_features is not None and validation_targets is not None
        x_validation_scaled: np.ndarray | None = None
        y_validation_scaled: np.ndarray | None = None
        if has_validation:
            x_validation = _as_float_array(validation_features)
            y_validation = _as_float_array(validation_targets)
            x_validation_scaled = (x_validation - feature_mean) / feature_scale
            y_validation_scaled = (y_validation - target_mean) / target_scale

        resolved_device = resolve_device(device)
        torch_device = torch.device(resolved_device)

        module = _build_mlp(
            input_dim=x_train.shape[1],
            output_dim=y_train.shape[1],
            hidden_layer_widths=tuple(int(width) for width in hidden_layer_widths),
            activation_name=activation_name,
        ).to(torch_device)

        optimizer = optimizer_factory(
            optimizer_name,
            module.parameters(),
            learning_rate=float(learning_rate),
        )
        criterion = nn.MSELoss()

        train_dataset = TensorDataset(
            torch.from_numpy(x_train_scaled.astype(np.float32)),
            torch.from_numpy(y_train_scaled.astype(np.float32)),
        )
        train_loader = DataLoader(
            train_dataset,
            batch_size=min(int(batch_size), len(train_dataset)),
            shuffle=True,
        )
        validation_tensors: tuple[torch.Tensor, torch.Tensor] | None = None
        if has_validation and x_validation_scaled is not None and y_validation_scaled is not None:
            validation_tensors = (
                torch.from_numpy(x_validation_scaled.astype(np.float32)).to(torch_device),
                torch.from_numpy(y_validation_scaled.astype(np.float32)).to(torch_device),
            )

        best_state = copy.deepcopy(module.state_dict())
        best_monitored_loss = float("inf")
        best_epoch = 0
        best_train_loss = float("inf")
        best_validation_loss: float | None = None
        patience = 0

        epochs_completed = 0
        for epoch in range(1, int(max_epochs) + 1):
            epochs_completed = epoch
            module.train()
            total_loss = 0.0
            total_rows = 0
            for batch_features, batch_targets in train_loader:
                batch_features = batch_features.to(torch_device)
                batch_targets = batch_targets.to(torch_device)
                optimizer.zero_grad(set_to_none=True)
                predictions = module(batch_features)
                loss = criterion(predictions, batch_targets)
                loss.backward()
                optimizer.step()
                total_rows += int(batch_features.shape[0])
                total_loss += float(loss.item()) * int(batch_features.shape[0])
            train_loss = total_loss / max(total_rows, 1)

            validation_loss: float | None = None
            monitored_loss = train_loss
            if validation_tensors is not None:
                module.eval()
                with torch.no_grad():
                    predictions = module(validation_tensors[0])
                    validation_loss = float(criterion(predictions, validation_tensors[1]).item())
                monitored_loss = validation_loss

            if monitored_loss < best_monitored_loss:
                best_monitored_loss = monitored_loss
                best_epoch = epoch
                best_state = copy.deepcopy(module.state_dict())
                best_train_loss = train_loss
                best_validation_loss = validation_loss
                patience = 0
            else:
                patience += 1
                if patience >= int(early_stopping_patience):
                    break

        module.load_state_dict(best_state)
        module = module.to("cpu").eval()

        surrogate = cls(
            feature_spec=feature_spec,
            module=module,
            feature_mean=feature_mean,
            feature_scale=feature_scale,
            target_mean=target_mean,
            target_scale=target_scale,
            hidden_layer_widths=tuple(int(width) for width in hidden_layer_widths),
            activation_name=str(activation_name),
        )
        summary = {
            "optimizer": str(optimizer_name),
            "learning_rate": float(learning_rate),
            "batch_size": int(batch_size),
            "epoch_limit": int(max_epochs),
            "epochs_completed": int(epochs_completed),
            "best_epoch": int(best_epoch),
            "best_monitored_loss": float(best_monitored_loss),
            "best_train_loss": float(best_train_loss),
            "best_validation_loss": None if best_validation_loss is None else float(best_validation_loss),
            "early_stopping_patience": int(early_stopping_patience),
            "random_seed": int(random_seed),
            "requested_device": str(device),
            "resolved_device": resolved_device,
            "hidden_layer_widths": list(int(width) for width in hidden_layer_widths),
            "depth": len(hidden_layer_widths),
            "activation": str(activation_name),
        }
        return surrogate, summary

    def predict(self, features: np.ndarray, *, device: str | None = None) -> np.ndarray:
        """Predict spectra for feature rows."""

        x = _as_float_array(features)
        if x.ndim == 1:
            x = x.reshape(1, -1)
        if x.shape[1] != len(self.feature_spec.names):
            raise ValueError("feature column count does not match feature_spec.")
        resolved_device = resolve_device(device) if device is not None else "cpu"
        torch_device = torch.device(resolved_device)
        x_scaled = (x - self.feature_mean) / self.feature_scale
        self.module = self.module.to(torch_device).eval()
        with torch.no_grad():
            prediction = self.module(torch.from_numpy(x_scaled.astype(np.float32)).to(torch_device)).cpu().numpy()
        self.module = self.module.to("cpu")
        return prediction.astype(np.float64) * self.target_scale + self.target_mean

    def save(self, path: Path | str) -> Path:
        """Save the neural checkpoint in torch format."""

        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "model_type": self.model_type,
            "feature_names": list(self.feature_spec.names),
            "feature_mean": self.feature_mean.tolist(),
            "feature_scale": self.feature_scale.tolist(),
            "target_mean": self.target_mean.tolist(),
            "target_scale": self.target_scale.tolist(),
            "hidden_layer_widths": list(self.hidden_layer_widths),
            "activation": self.activation_name,
            "state_dict": {key: value.detach().cpu() for key, value in self.module.state_dict().items()},
        }
        torch.save(payload, output_path)
        return output_path

    @classmethod
    def load(cls, path: Path | str) -> "NeuralMLPSpectrumSurrogate":
        """Load a neural checkpoint saved by `save`."""

        payload = torch.load(Path(path), map_location="cpu")
        model_type = normalize_model_type(str(payload["model_type"]))
        if model_type != NEURAL_MLP_MODEL_TYPE:
            raise ValueError(f"Checkpoint {path} is not a neural MLP checkpoint.")
        feature_spec = FeatureSpec(names=tuple(str(value) for value in payload["feature_names"]))
        hidden_layer_widths = tuple(int(width) for width in payload["hidden_layer_widths"])
        module = _build_mlp(
            input_dim=len(feature_spec.names),
            output_dim=len(payload["target_mean"]),
            hidden_layer_widths=hidden_layer_widths,
            activation_name=str(payload["activation"]),
        )
        module.load_state_dict(payload["state_dict"])
        module = module.to("cpu").eval()
        return cls(
            feature_spec=feature_spec,
            module=module,
            feature_mean=np.asarray(payload["feature_mean"], dtype=np.float64),
            feature_scale=np.asarray(payload["feature_scale"], dtype=np.float64),
            target_mean=np.asarray(payload["target_mean"], dtype=np.float64),
            target_scale=np.asarray(payload["target_scale"], dtype=np.float64),
            hidden_layer_widths=hidden_layer_widths,
            activation_name=str(payload["activation"]),
        )


def load_surrogate_checkpoint(path: Path | str) -> RidgeLinearSpectrumSurrogate | NeuralMLPSpectrumSurrogate:
    """Load either a ridge or neural checkpoint."""

    checkpoint_path = Path(path)
    if checkpoint_path.suffix == ".pt":
        return NeuralMLPSpectrumSurrogate.load(checkpoint_path)
    if checkpoint_path.suffix == ".npz":
        return RidgeLinearSpectrumSurrogate.load(checkpoint_path)
    raise ValueError(f"Unsupported checkpoint extension for {checkpoint_path}.")
