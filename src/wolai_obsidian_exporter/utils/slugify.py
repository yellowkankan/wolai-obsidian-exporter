from __future__ import annotations

import re
import unicodedata
from typing import Optional

UNSAFE_FILENAME = re.compile(r'[/\\:*?"<>|\x00-\x1f]')
WHITESPACE = re.compile(r"\s+")


def slugify_filename(
    value: Optional[str], fallback: str = "untitled", max_length: int = 120
) -> str:
    text = unicodedata.normalize("NFKC", value or "").strip()
    text = UNSAFE_FILENAME.sub("_", text)
    text = WHITESPACE.sub(" ", text).strip(" .")
    if not text:
        text = fallback
    if len(text) > max_length:
        text = text[:max_length].rstrip(" ._")
    return text or fallback


def split_wolai_path(path: Optional[str]) -> list[str]:
    if not path:
        return []
    delimiter = " / " if " / " in path else "/"
    return [slugify_filename(part) for part in path.split(delimiter) if part.strip()]
