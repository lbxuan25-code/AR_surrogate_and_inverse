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
NEURAL_RESIDUAL_MLP_MODEL_TYPE = "neural_residual_mlp_spectrum_surrogate"


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
        "residual_mlp": NEURAL_RESIDUAL_MLP_MODEL_TYPE,
        "neural_residual_mlp": NEURAL_RESIDUAL_MLP_MODEL_TYPE,
        "high_accuracy_residual_mlp": NEURAL_RESIDUAL_MLP_MODEL_TYPE,
        NEURAL_RESIDUAL_MLP_MODEL_TYPE: NEURAL_RESIDUAL_MLP_MODEL_TYPE,
    }
    if normalized not in aliases:
        raise ValueError(f"Unsupported model_type {model_type!r}.")
    return aliases[normalized]


def checkpoint_filename_for_model_type(model_type: str) -> str:
    """Return the default checkpoint filename for the given model type."""

    canonical = normalize_model_type(model_type)
    return "model.pt" if canonical != RIDGE_MODEL_TYPE else "model.npz"


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


def normalization_module(name: str, width: int) -> nn.Module:
    """Construct a supported normalization layer."""

    normalized = str(name or "none").strip().lower()
    if normalized == "none":
        return nn.Identity()
    if normalized == "layernorm":
        return nn.LayerNorm(int(width))
    raise ValueError(f"Unsupported normalization {name!r}.")


def optimizer_factory(
    optimizer_name: str,
    parameters: Any,
    *,
    learning_rate: float,
    weight_decay: float = 0.0,
) -> torch.optim.Optimizer:
    """Construct a supported optimizer."""

    normalized = str(optimizer_name).strip().lower()
    if normalized == "adam":
        return torch.optim.Adam(parameters, lr=learning_rate, weight_decay=weight_decay)
    if normalized == "adamw":
        return torch.optim.AdamW(parameters, lr=learning_rate, weight_decay=weight_decay)
    if normalized == "sgd":
        return torch.optim.SGD(parameters, lr=learning_rate, momentum=0.9, weight_decay=weight_decay)
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


class ResidualMLPBlock(nn.Module):
    """Simple pre-norm residual block for feed-forward spectrum prediction."""

    def __init__(self, width: int, *, activation_name: str, normalization_name: str) -> None:
        super().__init__()
        self.norm = normalization_module(normalization_name, width)
        self.linear_in = nn.Linear(width, width)
        self.activation = activation_module(activation_name)
        self.linear_out = nn.Linear(width, width)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        residual = inputs
        outputs = self.norm(inputs)
        outputs = self.linear_in(outputs)
        outputs = self.activation(outputs)
        outputs = self.linear_out(outputs)
        return residual + outputs


class ResidualSpectrumMLP(nn.Module):
    """Residual MLP head that preserves the fixed feature and spectrum contracts."""

    def __init__(
        self,
        *,
        input_dim: int,
        output_dim: int,
        hidden_width: int,
        num_blocks: int,
        activation_name: str,
        normalization_name: str,
    ) -> None:
        super().__init__()
        if hidden_width < 1:
            raise ValueError("hidden_width must be at least 1.")
        if num_blocks < 1:
            raise ValueError("num_blocks must be at least 1.")
        self.input_projection = nn.Linear(input_dim, hidden_width)
        self.input_activation = activation_module(activation_name)
        self.blocks = nn.ModuleList(
            [
                ResidualMLPBlock(
                    hidden_width,
                    activation_name=activation_name,
                    normalization_name=normalization_name,
                )
                for _ in range(num_blocks)
            ]
        )
        self.output_norm = normalization_module(normalization_name, hidden_width)
        self.output_head = nn.Linear(hidden_width, output_dim)

    def forward(self, inputs: torch.Tensor) -> torch.Tensor:
        outputs = self.input_projection(inputs)
        outputs = self.input_activation(outputs)
        for block in self.blocks:
            outputs = block(outputs)
        outputs = self.output_norm(outputs)
        return self.output_head(outputs)


def _build_torch_module(
    *,
    model_type: str,
    input_dim: int,
    output_dim: int,
    hidden_layer_widths: tuple[int, ...],
    residual_hidden_width: int,
    residual_num_blocks: int,
    activation_name: str,
    normalization_name: str,
) -> tuple[nn.Module, dict[str, Any]]:
    canonical = normalize_model_type(model_type)
    if canonical == NEURAL_MLP_MODEL_TYPE:
        widths = tuple(int(width) for width in hidden_layer_widths)
        module = _build_mlp(
            input_dim=input_dim,
            output_dim=output_dim,
            hidden_layer_widths=widths,
            activation_name=activation_name,
        )
        return module, {
            "architecture_kind": "mlp",
            "hidden_layer_widths": list(widths),
            "activation": str(activation_name),
        }
    if canonical == NEURAL_RESIDUAL_MLP_MODEL_TYPE:
        hidden_width = int(residual_hidden_width)
        num_blocks = int(residual_num_blocks)
        module = ResidualSpectrumMLP(
            input_dim=input_dim,
            output_dim=output_dim,
            hidden_width=hidden_width,
            num_blocks=num_blocks,
            activation_name=activation_name,
            normalization_name=normalization_name,
        )
        return module, {
            "architecture_kind": "residual_mlp",
            "hidden_width": hidden_width,
            "num_blocks": num_blocks,
            "activation": str(activation_name),
            "normalization": str(normalization_name),
        }
    raise ValueError(f"Unsupported torch model_type {model_type!r}.")


def _module_from_architecture(
    *,
    model_type: str,
    feature_count: int,
    output_dim: int,
    architecture_config: dict[str, Any],
) -> nn.Module:
    canonical = normalize_model_type(model_type)
    if canonical == NEURAL_MLP_MODEL_TYPE:
        return _build_mlp(
            input_dim=feature_count,
            output_dim=output_dim,
            hidden_layer_widths=tuple(int(width) for width in architecture_config["hidden_layer_widths"]),
            activation_name=str(architecture_config["activation"]),
        )
    if canonical == NEURAL_RESIDUAL_MLP_MODEL_TYPE:
        return ResidualSpectrumMLP(
            input_dim=feature_count,
            output_dim=output_dim,
            hidden_width=int(architecture_config["hidden_width"]),
            num_blocks=int(architecture_config["num_blocks"]),
            activation_name=str(architecture_config["activation"]),
            normalization_name=str(architecture_config["normalization"]),
        )
    raise ValueError(f"Unsupported torch model_type {model_type!r}.")


def _uniform_loss_contract() -> dict[str, Any]:
    return {
        "kind": "plain_mse",
        "reconstruction_weight": 1.0,
        "shape_weight": 0.0,
        "bias_weighting": {
            "kind": "uniform",
            "outer_weight": 1.0,
            "central_weight": 1.0,
            "central_bias_half_width_mev": 0.0,
        },
    }


def normalize_loss_contract(loss_config: dict[str, Any] | None) -> dict[str, Any]:
    """Normalize the training loss contract into an explicit serializable mapping."""

    if loss_config is None:
        return _uniform_loss_contract()
    if not isinstance(loss_config, dict):
        raise ValueError("loss must be a mapping when provided.")

    kind = str(loss_config.get("kind", "plain_mse")).strip().lower()
    if kind in {"plain_mse", "mse"}:
        return _uniform_loss_contract()
    if kind not in {"weighted_mse_plus_first_difference", "weighted_spectrum_plus_shape"}:
        raise ValueError(f"Unsupported loss kind {kind!r}.")

    bias_weighting = dict(loss_config.get("bias_weighting", {}))
    weighting_kind = str(bias_weighting.get("kind", "center_window")).strip().lower()
    if weighting_kind != "center_window":
        raise ValueError("Only center_window bias weighting is currently supported for composite loss.")

    outer_weight = float(bias_weighting.get("outer_weight", 1.0))
    central_weight = float(bias_weighting.get("central_weight", 1.0))
    central_half_width = float(bias_weighting.get("central_bias_half_width_mev", 0.0))
    if outer_weight <= 0.0 or central_weight <= 0.0:
        raise ValueError("Bias weighting coefficients must be positive.")
    if central_half_width < 0.0:
        raise ValueError("central_bias_half_width_mev must be non-negative.")

    reconstruction_weight = float(loss_config.get("reconstruction_weight", 1.0))
    shape_weight = float(loss_config.get("shape_weight", 0.0))
    if reconstruction_weight <= 0.0:
        raise ValueError("reconstruction_weight must be positive.")
    if shape_weight < 0.0:
        raise ValueError("shape_weight must be non-negative.")

    return {
        "kind": "weighted_mse_plus_first_difference",
        "reconstruction_weight": reconstruction_weight,
        "shape_weight": shape_weight,
        "bias_weighting": {
            "kind": "center_window",
            "outer_weight": outer_weight,
            "central_weight": central_weight,
            "central_bias_half_width_mev": central_half_width,
        },
    }


def _bias_weights_from_contract(bias_mev: list[float], loss_contract: dict[str, Any]) -> np.ndarray:
    bias_array = np.asarray(bias_mev, dtype=np.float64)
    if bias_array.ndim != 1 or bias_array.size == 0:
        raise ValueError("bias_mev must contain a non-empty 1D bias grid.")

    if loss_contract["kind"] == "plain_mse":
        return np.ones_like(bias_array, dtype=np.float64)

    weighting = dict(loss_contract["bias_weighting"])
    half_width = float(weighting["central_bias_half_width_mev"])
    outer_weight = float(weighting["outer_weight"])
    central_weight = float(weighting["central_weight"])

    weights = np.full_like(bias_array, outer_weight, dtype=np.float64)
    weights[np.abs(bias_array) <= half_width] = central_weight
    mean_weight = float(np.mean(weights))
    if mean_weight <= 0.0:
        raise ValueError("Computed bias weights must have positive mean.")
    return weights / mean_weight


class CompositeSpectrumLoss(nn.Module):
    """Composite spectrum loss with low-bias weighting and slope consistency."""

    def __init__(self, *, loss_contract: dict[str, Any], bias_mev: list[float]) -> None:
        super().__init__()
        normalized_contract = normalize_loss_contract(loss_contract)
        bias_weights = _bias_weights_from_contract(bias_mev, normalized_contract)
        self.loss_contract = normalized_contract
        self.register_buffer("bias_weights", torch.from_numpy(bias_weights.astype(np.float32)))

    def forward(self, prediction: torch.Tensor, target: torch.Tensor) -> tuple[torch.Tensor, dict[str, float]]:
        weights = self.bias_weights.unsqueeze(0)
        reconstruction_loss = torch.mean(((prediction - target) ** 2) * weights)
        shape_loss = torch.zeros((), device=prediction.device, dtype=prediction.dtype)
        if float(self.loss_contract["shape_weight"]) > 0.0 and prediction.shape[-1] > 1:
            diff_weights = 0.5 * (weights[:, 1:] + weights[:, :-1])
            prediction_diff = prediction[:, 1:] - prediction[:, :-1]
            target_diff = target[:, 1:] - target[:, :-1]
            shape_loss = torch.mean(((prediction_diff - target_diff) ** 2) * diff_weights)

        total_loss = (
            float(self.loss_contract["reconstruction_weight"]) * reconstruction_loss
            + float(self.loss_contract["shape_weight"]) * shape_loss
        )
        breakdown = {
            "total_loss": float(total_loss.detach().cpu().item()),
            "reconstruction_loss": float(reconstruction_loss.detach().cpu().item()),
            "shape_loss": float(shape_loss.detach().cpu().item()),
            "bias_weight_min": float(self.bias_weights.min().detach().cpu().item()),
            "bias_weight_max": float(self.bias_weights.max().detach().cpu().item()),
        }
        return total_loss, breakdown


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
    """Torch-based surrogate that preserves the fixed spectrum output contract."""

    feature_spec: FeatureSpec
    model_type_id: str
    module: nn.Module
    feature_mean: np.ndarray
    feature_scale: np.ndarray
    target_mean: np.ndarray
    target_scale: np.ndarray
    architecture_config: dict[str, Any]
    loss_contract: dict[str, Any]

    @property
    def model_type(self) -> str:
        return normalize_model_type(self.model_type_id)

    @classmethod
    def fit(
        cls,
        features: np.ndarray,
        targets: np.ndarray,
        *,
        validation_features: np.ndarray | None = None,
        validation_targets: np.ndarray | None = None,
        feature_spec: FeatureSpec = DEFAULT_FEATURE_SPEC,
        model_type: str = NEURAL_MLP_MODEL_TYPE,
        hidden_layer_widths: tuple[int, ...] = (128, 128),
        residual_hidden_width: int = 256,
        residual_num_blocks: int = 4,
        activation_name: str = "relu",
        normalization_name: str = "none",
        optimizer_name: str = "adam",
        learning_rate: float = 1.0e-3,
        weight_decay: float = 0.0,
        batch_size: int = 32,
        max_epochs: int = 100,
        early_stopping_patience: int = 10,
        random_seed: int = 0,
        device: str = "auto",
        loss_config: dict[str, Any] | None = None,
        bias_mev: list[float] | None = None,
    ) -> tuple["NeuralMLPSpectrumSurrogate", dict[str, Any]]:
        """Fit a torch surrogate and return training summary metadata."""

        canonical_model_type = normalize_model_type(model_type)
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
        if int(batch_size) < 1:
            raise ValueError("batch_size must be at least 1.")
        if int(max_epochs) < 1:
            raise ValueError("max_epochs must be at least 1.")
        if int(early_stopping_patience) < 1:
            raise ValueError("early_stopping_patience must be at least 1.")
        if bias_mev is None:
            raise ValueError("bias_mev must be provided for torch surrogate training.")

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

        module, architecture_config = _build_torch_module(
            model_type=canonical_model_type,
            input_dim=x_train.shape[1],
            output_dim=y_train.shape[1],
            hidden_layer_widths=tuple(int(width) for width in hidden_layer_widths),
            residual_hidden_width=int(residual_hidden_width),
            residual_num_blocks=int(residual_num_blocks),
            activation_name=activation_name,
            normalization_name=normalization_name,
        )
        module = module.to(torch_device)

        optimizer = optimizer_factory(
            optimizer_name,
            module.parameters(),
            learning_rate=float(learning_rate),
            weight_decay=float(weight_decay),
        )
        criterion = CompositeSpectrumLoss(
            loss_contract=normalize_loss_contract(loss_config),
            bias_mev=list(bias_mev),
        ).to(torch_device)

        train_dataset = TensorDataset(
            torch.from_numpy(x_train_scaled.astype(np.float32)),
            torch.from_numpy(y_train_scaled.astype(np.float32)),
        )
        data_loader_generator = torch.Generator()
        data_loader_generator.manual_seed(int(random_seed))
        train_loader = DataLoader(
            train_dataset,
            batch_size=min(int(batch_size), len(train_dataset)),
            shuffle=True,
            generator=data_loader_generator,
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
        best_reconstruction_loss = float("inf")
        best_shape_loss = float("inf")
        patience = 0

        epochs_completed = 0
        for epoch in range(1, int(max_epochs) + 1):
            epochs_completed = epoch
            module.train()
            total_loss = 0.0
            total_reconstruction = 0.0
            total_shape = 0.0
            total_rows = 0
            for batch_features, batch_targets in train_loader:
                batch_features = batch_features.to(torch_device)
                batch_targets = batch_targets.to(torch_device)
                optimizer.zero_grad(set_to_none=True)
                predictions = module(batch_features)
                loss, breakdown = criterion(predictions, batch_targets)
                loss.backward()
                optimizer.step()
                total_rows += int(batch_features.shape[0])
                total_loss += float(loss.item()) * int(batch_features.shape[0])
                total_reconstruction += float(breakdown["reconstruction_loss"]) * int(batch_features.shape[0])
                total_shape += float(breakdown["shape_loss"]) * int(batch_features.shape[0])
            train_loss = total_loss / max(total_rows, 1)
            reconstruction_loss = total_reconstruction / max(total_rows, 1)
            shape_loss = total_shape / max(total_rows, 1)

            validation_loss: float | None = None
            monitored_loss = train_loss
            if validation_tensors is not None:
                module.eval()
                with torch.no_grad():
                    predictions = module(validation_tensors[0])
                    validation_total, _ = criterion(predictions, validation_tensors[1])
                    validation_loss = float(validation_total.item())
                monitored_loss = validation_loss

            if monitored_loss < best_monitored_loss:
                best_monitored_loss = monitored_loss
                best_epoch = epoch
                best_state = copy.deepcopy(module.state_dict())
                best_train_loss = train_loss
                best_validation_loss = validation_loss
                best_reconstruction_loss = reconstruction_loss
                best_shape_loss = shape_loss
                patience = 0
            else:
                patience += 1
                if patience >= int(early_stopping_patience):
                    break

        module.load_state_dict(best_state)
        module = module.to("cpu").eval()

        surrogate = cls(
            feature_spec=feature_spec,
            model_type_id=canonical_model_type,
            module=module,
            feature_mean=feature_mean,
            feature_scale=feature_scale,
            target_mean=target_mean,
            target_scale=target_scale,
            architecture_config=architecture_config,
            loss_contract=criterion.loss_contract,
        )
        summary = {
            "optimizer": str(optimizer_name),
            "learning_rate": float(learning_rate),
            "weight_decay": float(weight_decay),
            "batch_size": int(batch_size),
            "epoch_limit": int(max_epochs),
            "epochs_completed": int(epochs_completed),
            "best_epoch": int(best_epoch),
            "best_monitored_loss": float(best_monitored_loss),
            "best_train_loss": float(best_train_loss),
            "best_validation_loss": None if best_validation_loss is None else float(best_validation_loss),
            "best_reconstruction_loss": float(best_reconstruction_loss),
            "best_shape_loss": float(best_shape_loss),
            "early_stopping_patience": int(early_stopping_patience),
            "random_seed": int(random_seed),
            "requested_device": str(device),
            "resolved_device": resolved_device,
            "activation": str(activation_name),
            "model_type": canonical_model_type,
            "loss_contract": criterion.loss_contract,
        }
        summary.update(architecture_config)
        if "hidden_layer_widths" in architecture_config:
            summary["depth"] = len(architecture_config["hidden_layer_widths"])
        if "num_blocks" in architecture_config:
            summary["depth"] = int(architecture_config["num_blocks"])
            summary["residual_num_blocks"] = int(architecture_config["num_blocks"])
            summary["residual_hidden_width"] = int(architecture_config["hidden_width"])
            summary["normalization"] = str(architecture_config["normalization"])
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
        """Save the torch surrogate checkpoint in torch format."""

        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "model_type": self.model_type,
            "feature_names": list(self.feature_spec.names),
            "feature_mean": self.feature_mean.tolist(),
            "feature_scale": self.feature_scale.tolist(),
            "target_mean": self.target_mean.tolist(),
            "target_scale": self.target_scale.tolist(),
            "architecture_config": self.architecture_config,
            "loss_contract": self.loss_contract,
            "state_dict": {key: value.detach().cpu() for key, value in self.module.state_dict().items()},
        }
        torch.save(payload, output_path)
        return output_path

    @classmethod
    def load(cls, path: Path | str) -> "NeuralMLPSpectrumSurrogate":
        """Load a torch surrogate checkpoint saved by `save`."""

        payload = torch.load(Path(path), map_location="cpu")
        model_type = normalize_model_type(str(payload["model_type"]))
        feature_spec = FeatureSpec(names=tuple(str(value) for value in payload["feature_names"]))
        architecture_config = dict(payload.get("architecture_config", {}))
        target_mean = np.asarray(payload["target_mean"], dtype=np.float64)
        module = _module_from_architecture(
            model_type=model_type,
            feature_count=len(feature_spec.names),
            output_dim=len(target_mean),
            architecture_config=architecture_config,
        )
        module.load_state_dict(payload["state_dict"])
        module = module.to("cpu").eval()
        return cls(
            feature_spec=feature_spec,
            model_type_id=model_type,
            module=module,
            feature_mean=np.asarray(payload["feature_mean"], dtype=np.float64),
            feature_scale=np.asarray(payload["feature_scale"], dtype=np.float64),
            target_mean=target_mean,
            target_scale=np.asarray(payload["target_scale"], dtype=np.float64),
            architecture_config=architecture_config,
            loss_contract=normalize_loss_contract(dict(payload.get("loss_contract", _uniform_loss_contract()))),
        )


def load_surrogate_checkpoint(path: Path | str) -> RidgeLinearSpectrumSurrogate | NeuralMLPSpectrumSurrogate:
    """Load either a ridge or torch surrogate checkpoint."""

    checkpoint_path = Path(path)
    if checkpoint_path.suffix == ".pt":
        return NeuralMLPSpectrumSurrogate.load(checkpoint_path)
    if checkpoint_path.suffix == ".npz":
        return RidgeLinearSpectrumSurrogate.load(checkpoint_path)
    raise ValueError(f"Unsupported checkpoint extension for {checkpoint_path}.")
