from __future__ import annotations

from pathlib import Path


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def relative_markdown_path(from_file: Path, to_file: Path) -> str:
    rel = (
        to_file.relative_to(from_file.parent) if to_file.is_relative_to(from_file.parent) else None
    )
    if rel is None:
        import os

        rel = Path(os.path.relpath(to_file, start=from_file.parent))
    return rel.as_posix()


def safe_join(root: Path, *parts: str) -> Path:
    candidate = root.joinpath(*parts).resolve()
    root_resolved = root.resolve()
    if not candidate.is_relative_to(root_resolved):
        raise ValueError(f"path escapes root: {candidate}")
    return candidate
