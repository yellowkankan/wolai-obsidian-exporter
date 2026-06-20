from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

PATTERNS = {
    "api_key": re.compile(r"(?i)(api[_-]?key|apikey)\s*[:=]\s*['\"]?[A-Za-z0-9._\-]{12,}"),
    "bearer": re.compile(r"(?i)Bearer\s+[A-Za-z0-9._\-]{12,}"),
    "sk_token": re.compile(r"sk-[A-Za-z0-9._\-]{8,}"),
    "auth_query": re.compile(r"(?i)(auth_key|access_token|token|session|cookie)=([^&\s]+)"),
    "private_path": re.compile(r"/Users/[^\s)\]}]+"),
}


@dataclass(frozen=True)
class SensitiveHit:
    file: str
    line: int
    kind: str


def scan_path(path: Path) -> list[SensitiveHit]:
    hits: list[SensitiveHit] = []
    files = [path] if path.is_file() else [p for p in path.rglob("*") if p.is_file()]
    for file in files:
        if any(part in {".git", ".venv", "__pycache__"} for part in file.parts):
            continue
        try:
            text = file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_no, line in enumerate(text.splitlines(), 1):
            for kind, pattern in PATTERNS.items():
                if pattern.search(line):
                    hits.append(SensitiveHit(str(file), line_no, kind))
    return hits
