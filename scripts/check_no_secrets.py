#!/usr/bin/env python3
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    ".ruff_cache",
    "dist",
    "build",
    "exports",
    "output",
    "tmp",
    ".wolai-export-state",
}
SKIP_FILES = {".env"}
PATTERNS = {
    "private_path": re.compile(r"/Users/kkll"),
    "bearer_token": re.compile(r"Bearer\s+[A-Za-z0-9._\-]{12,}", re.I),
    "sk_token": re.compile(r"sk-[A-Za-z0-9._\-]{8,}", re.I),
    "auth_key_url": re.compile(r"auth_key=[^&\s]+", re.I),
}
ALLOWLIST = {
    "scripts/check_no_secrets.py",
}


def iter_files():
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(ROOT).as_posix()
        if rel in ALLOWLIST or path.name in SKIP_FILES:
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        yield path, rel


def main() -> int:
    failures = []
    for path, rel in iter_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for name, pattern in PATTERNS.items():
            if pattern.search(text):
                failures.append((rel, name))
    for rel, name in failures:
        print(f"{rel}: {name}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
