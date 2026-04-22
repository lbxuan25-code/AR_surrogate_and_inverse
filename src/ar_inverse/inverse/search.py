"""Smoke inverse-search prototype with direct forward rechecks."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ar_inverse.direction import (
    SUPPORTED_DIRECTION_MODES,
    direction_block_from_forward_payload,
    normalize_direction_prior,
    validate_direction_config,
)
from ar_inverse.datasets.schema import file_sha256, forward_output_ref
from ar_inverse.forward_dependency import import_forward_module
from ar_inverse.inverse.candidates import (
    control_ranges,
    make_candidate_family,
    validate_inverse_report,
)
from ar_inverse.inverse.objectives import spectrum_objective

DEFAULT_TASK6_CONFIG_PATH = Path("configs/inverse/task6_smoke_inverse.json")
DEFAULT_TASK6_OUTPUT_DIR = Path("outputs/inverse/task6_smoke_inverse")
DEFAULT_TASK6_RUN_METADATA_PATH = Path("outputs/runs/task6_smoke_inverse_run_metadata.json")


def load_inverse_config(path: Path | str) -> dict[str, Any]:
    """Load an inverse-search config from JSON."""

    config = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError("Inverse config must be a JSON object.")
    required = ("target_dataset_manifest", "target_row_id", "candidate_specs", "output_dir")
    missing = [key for key in required if key not in config]
    if missing:
        raise ValueError(f"Inverse config is missing required key(s): {', '.join(missing)}.")
    if not isinstance(config["candidate_specs"], list) or not config["candidate_specs"]:
        raise ValueError("Inverse config must contain a non-empty candidate_specs list.")
    direction_prior = normalize_direction_prior(config.get("direction_prior"))
    config["direction_prior"] = direction_prior
    for spec in config["candidate_specs"]:
        direction = spec.get("direction")
        validate_direction_config(direction)
        if direction_prior["kind"] == "direction_resolved":
            mode = direction.get("direction_mode") if isinstance(direction, dict) else None
            if mode not in direction_prior["allowed_direction_modes"]:
                raise ValueError("Direction-resolved inverse candidates must use an allowed supported direction mode.")
    return config


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _load_target_payload(manifest_path: Path, target_row_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    manifest = _load_json(manifest_path)
    row = next((row for row in manifest["rows"] if row["row_id"] == target_row_id), None)
    if row is None:
        raise ValueError(f"No target row_id {target_row_id!r} in {manifest_path}.")
    output_ref = row["forward_output_ref"]
    output_path = manifest_path.parent / output_ref["path"]
    if not output_path.exists():
        raise ValueError(f"Target forward output does not exist: {output_path}.")
    if output_ref["sha256"] != file_sha256(output_path):
        raise ValueError(f"Target forward output hash mismatch: {output_path}.")
    return row, _load_json(output_path)


def _request_from_spec(spec: dict[str, Any], target_payload: dict[str, Any]):
    forward = import_forward_module("forward")
    request_payload = target_payload["request"]
    bias_grid = dict(request_payload["bias_grid"])
    transport_controls = dict(spec["transport_controls"])
    direction = spec.get("direction")
    if isinstance(direction, dict) and direction.get("direction_mode") in SUPPORTED_DIRECTION_MODES:
        transport_controls.pop("interface_angle", None)
        transport_controls.pop("direction_mode", None)
        transport = forward.transport_with_direction_mode(str(direction["direction_mode"]), **transport_controls)
    else:
        transport = forward.TransportControls(**transport_controls)
    return forward.FitLayerSpectrumRequest(
        pairing_controls=dict(spec.get("pairing_controls", {})),
        pairing_control_mode="delta_from_baseline_meV",
        allow_weak_delta_zx_s=bool(spec.get("allow_weak_delta_zx_s", False)),
        transport=transport,
        bias_grid=forward.BiasGrid(**bias_grid),
        request_label=str(spec["candidate_family_id"]),
    )


def _transport_range_widths(transport_controls: dict[str, float | int]) -> dict[str, float]:
    widths: dict[str, float] = {}
    for key, value in transport_controls.items():
        if key == "nk":
            widths[key] = 0.0
        else:
            widths[key] = max(abs(float(value)) * 0.05, 0.02)
    return widths


def run_inverse_search_from_config(config_path: Path | str = DEFAULT_TASK6_CONFIG_PATH) -> tuple[Path, Path]:
    """Run the Task 6 smoke inverse search and write report artifacts."""

    forward = import_forward_module("forward")
    config_file = Path(config_path)
    config = load_inverse_config(config_file)
    output_dir = Path(config.get("output_dir", DEFAULT_TASK6_OUTPUT_DIR))
    recheck_dir = output_dir / "forward_rechecks"
    output_dir.mkdir(parents=True, exist_ok=True)
    recheck_dir.mkdir(parents=True, exist_ok=True)

    target_manifest_path = Path(config["target_dataset_manifest"])
    target_row, target_payload = _load_target_payload(target_manifest_path, str(config["target_row_id"]))
    target_conductance = list(target_payload["conductance"])
    fallback_policy_report = _load_json(Path(config["fallback_policy_report"])) if config.get("fallback_policy_report") else {}
    fallback_policy = dict(fallback_policy_report.get("fallback_policy", {}))
    direction_prior = normalize_direction_prior(config.get("direction_prior"))
    surrogate_usage = {
        "used": False,
        "reason": "Task 5 fallback policy requires direct forward for unsafe or unseen regimes.",
        "fallback_policy_id": fallback_policy.get("policy_id"),
    }

    candidates: list[dict[str, Any]] = []
    for spec in config["candidate_specs"]:
        request = _request_from_spec(spec, target_payload)
        result = forward.generate_spectrum_from_fit_layer(request)
        payload = result.to_dict()
        objective = spectrum_objective(payload["conductance"], target_conductance)
        recheck_path = recheck_dir / f"{spec['candidate_family_id']}.json"
        recheck_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

        pairing_controls = {str(key): float(value) for key, value in dict(spec.get("pairing_controls", {})).items()}
        transport_controls = dict(spec["transport_controls"])
        direction = (
            direction_block_from_forward_payload(payload, configured_direction=dict(spec["direction"]))
            if isinstance(spec.get("direction"), dict)
            else None
        )
        pairing_half_width = spec.get("pairing_half_width", 0.05)
        transport_half_width = spec.get("transport_half_width", _transport_range_widths(transport_controls))
        forward_recheck = {
            "request": payload["request"],
            "metadata": payload["metadata"],
            "output_ref": forward_output_ref(recheck_path, base_dir=output_dir),
            "objective": objective,
        }
        candidate = make_candidate_family(
            candidate_family_id=str(spec["candidate_family_id"]),
            pairing_center=pairing_controls,
            pairing_ranges=control_ranges(pairing_controls, pairing_half_width),
            transport_center=transport_controls,
            transport_ranges=control_ranges({key: float(value) for key, value in transport_controls.items()}, transport_half_width),
            objective=objective,
            forward_recheck=forward_recheck,
            surrogate_usage=surrogate_usage,
            direction=direction,
            direction_prior=direction_prior,
        )
        candidates.append(candidate)

    candidates.sort(key=lambda candidate: float(candidate["objective"]["score"]))
    top_k = int(config.get("top_k", len(candidates)))
    candidate_families = candidates[:top_k]
    report = {
        "run_kind": "task6_inverse_search_prototype",
        "report_schema_version": "ar_inverse_smoke_inverse_report_v1",
        "interpretation": "the AR data are compatible with these feature families",
        "target": {
            "dataset_manifest": target_manifest_path.as_posix(),
            "row_id": target_row["row_id"],
            "forward_output_ref": target_row["forward_output_ref"],
            "forward_metadata": target_row["forward_metadata"],
            "direction": target_row.get("direction"),
        },
        "search": {
            "candidate_count": len(config["candidate_specs"]),
            "reported_candidate_count": len(candidate_families),
            "objective": "spectrum_rmse",
            "surrogate_usage": surrogate_usage,
            "fallback_policy": fallback_policy,
            "direction_prior": direction_prior,
        },
        "candidate_families": candidate_families,
    }
    validate_inverse_report(report)

    report_path = output_dir / "inverse_report.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_path = output_dir / "inverse_report.md"
    _write_markdown_report(markdown_path, report)

    run_metadata_path = Path(config.get("run_metadata_path", DEFAULT_TASK6_RUN_METADATA_PATH))
    run_metadata_path.parent.mkdir(parents=True, exist_ok=True)
    run_metadata = {
        "run_kind": "task6_inverse_search_prototype",
        "config": config_file.as_posix(),
        "report": report_path.as_posix(),
        "markdown_report": markdown_path.as_posix(),
        "target_row_id": target_row["row_id"],
        "reported_candidate_count": len(candidate_families),
        "best_objective_score": candidate_families[0]["objective"]["score"],
        "forward_recheck_metadata": [candidate["forward_recheck"]["metadata"] for candidate in candidate_families],
        "direction_prior": direction_prior,
    }
    run_metadata_path.write_text(json.dumps(run_metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report_path, markdown_path


def _write_markdown_report(path: Path, report: dict[str, Any]) -> None:
    lines = [
        "# Task 6 Smoke Inverse Search Report",
        "",
        "The AR data are compatible with these feature families. This report does not",
        "claim a unique microscopic truth.",
        "",
        "## Target",
        "",
        f"- Dataset: `{report['target']['dataset_manifest']}`",
        f"- Row id: `{report['target']['row_id']}`",
        "",
        "## Search Policy",
        "",
        f"- Objective: `{report['search']['objective']}`",
        f"- Surrogate used: `{report['search']['surrogate_usage']['used']}`",
        f"- Surrogate reason: {report['search']['surrogate_usage']['reason']}",
        f"- Direction prior: `{report['search']['direction_prior']['kind']}`",
        "",
        "## Candidate Families",
        "",
    ]
    for candidate in report["candidate_families"]:
        lines.extend(
            [
                f"### {candidate['candidate_family_id']}",
                "",
                f"- Objective score: `{candidate['objective']['score']:.8g}`",
                f"- Pairing controls: `{candidate['pairing_controls']['center']}`",
                f"- Transport nuisance controls: `{candidate['transport_nuisance_controls']['center']}`",
                f"- Direction regime: `{candidate.get('direction', {}).get('direction_regime', 'unspecified')}`",
                f"- Forward recheck git commit: `{candidate['forward_recheck']['metadata']['git_commit']}`",
                "",
            ]
        )
    path.write_text("\n".join(lines), encoding="utf-8")
