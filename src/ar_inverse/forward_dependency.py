"""Portable loading helpers for the external forward interface."""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path
from types import ModuleType

FORWARD_SRC_ENV = "LNO327_FORWARD_SRC"
FORWARD_REPO_ENV = "LNO327_FORWARD_REPO"


class ForwardDependencyError(RuntimeError):
    """Raised when the external forward package cannot be loaded."""


def _setup_message() -> str:
    return (
        "Missing external forward interface package `forward`. "
        "Install the forward truth-chain repository in editable mode, for example "
        "`python -m pip install -e /path/to/forward-repo`, or set "
        f"`{FORWARD_SRC_ENV}` to its source directory containing the `forward` package. "
        f"You may also set `{FORWARD_REPO_ENV}` to the forward repository root. "
        "This repository will not copy or reimplement forward physics code."
    )


def _forward_src_from_env() -> Path | None:
    explicit_src = os.environ.get(FORWARD_SRC_ENV)
    if explicit_src:
        return Path(explicit_src).expanduser().resolve()

    explicit_repo = os.environ.get(FORWARD_REPO_ENV)
    if explicit_repo:
        return (Path(explicit_repo).expanduser().resolve() / "src").resolve()

    return None


def configure_forward_import_path() -> Path | None:
    """Add an explicitly configured forward source path to `sys.path`."""

    source_path = _forward_src_from_env()
    if source_path is None:
        return None

    forward_package = source_path / "forward" / "__init__.py"
    if not forward_package.exists():
        raise ForwardDependencyError(
            f"Invalid forward source path: {source_path}. Expected to find "
            f"`forward/__init__.py` below that directory. {_setup_message()}"
        )

    source_path_text = str(source_path)
    if source_path_text not in sys.path:
        sys.path.insert(0, source_path_text)
    return source_path


def import_forward_module(module_name: str = "forward") -> ModuleType:
    """Import a module from the external forward interface with clear errors."""

    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        missing_name = exc.name or ""
        if missing_name != "forward":
            raise
        source_path = configure_forward_import_path()
        if source_path is None:
            raise ForwardDependencyError(_setup_message()) from exc

    try:
        return importlib.import_module(module_name)
    except ModuleNotFoundError as exc:
        missing_name = exc.name or ""
        if missing_name == "forward":
            raise ForwardDependencyError(_setup_message()) from exc
        raise
