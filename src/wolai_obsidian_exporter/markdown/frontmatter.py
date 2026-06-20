from __future__ import annotations

from collections.abc import Mapping


def frontmatter(fields: Mapping[str, object]) -> str:
    lines = ["---"]
    for key, value in fields.items():
        lines.append(f"{key}: {format_value(value)}")
    lines.append("---")
    return "\n".join(lines)


def format_value(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value).replace('"', "'")
    if any(ch in text for ch in [":", "#", "[", "]", "{", "}", "\n"]):
        return f'"{text}"'
    return text
