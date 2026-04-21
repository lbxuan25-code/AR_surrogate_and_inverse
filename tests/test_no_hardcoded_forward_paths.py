from __future__ import annotations

from pathlib import Path


def test_source_files_do_not_hardcode_local_forward_paths() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    checked_suffixes = {".md", ".py", ".toml"}
    forbidden = (
        "/" + "home" + "/",
        ".." + "/" + "AR" + "/" + "src",
        "parent / " + '"' + "AR" + '"',
        "file://" + "/" + "home",
    )

    offenders: list[str] = []
    for path in repo_root.rglob("*"):
        if ".git" in path.parts or ".pytest_cache" in path.parts or "__pycache__" in path.parts:
            continue
        if path.suffix not in checked_suffixes:
            continue
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            if token in text:
                offenders.append(f"{path.relative_to(repo_root)} contains {token!r}")

    assert offenders == []
