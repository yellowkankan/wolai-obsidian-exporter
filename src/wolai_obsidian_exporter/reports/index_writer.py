from __future__ import annotations

import json
from pathlib import Path


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_markdown_table(
    path: Path, title: str, headers: list[str], rows: list[list[object]]
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [f"# {title}", ""]
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join("---" for _ in headers) + " |")
    for row in rows:
        lines.append("| " + " | ".join(_cell(cell) for cell in row) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _cell(value: object) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")
