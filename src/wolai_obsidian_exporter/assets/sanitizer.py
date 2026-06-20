from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional

SECRET_PATTERNS = [
    re.compile(r"Authorization\s*:\s*Bearer\s+[^\s\]})\",]+", re.I),
    re.compile(r"Bearer\s+[A-Za-z0-9._\-]{12,}", re.I),
    re.compile(r"sk-[A-Za-z0-9._\-]{8,}", re.I),
    re.compile(
        r"([?&](?:auth_key|token|access_token|api_key|apikey|secret|session|cookie)=)[^&\s]+", re.I
    ),
]


@dataclass(frozen=True)
class SanitizedUrl:
    value: str
    redacted: bool


def redact_secrets(text: str) -> str:
    redacted = text
    for pattern in SECRET_PATTERNS:
        redacted = pattern.sub(lambda m: _replacement(m), redacted)
    return redacted


def _replacement(match: re.Match[str]) -> str:
    value = match.group(0)
    if value.startswith("?") or value.startswith("&"):
        return value.split("=", 1)[0] + "=[REDACTED]"
    if value.lower().startswith("authorization"):
        return "Authorization: Bearer [REDACTED]"
    if value.lower().startswith("bearer"):
        return "Bearer [REDACTED]"
    if value.startswith("sk-"):
        return "sk-[REDACTED]"
    return "[REDACTED]"


def sanitize_url_for_reports(url: Optional[str]) -> SanitizedUrl:
    if not url:
        return SanitizedUrl("", False)
    redacted = redact_secrets(url)
    return SanitizedUrl(redacted, redacted != url)
