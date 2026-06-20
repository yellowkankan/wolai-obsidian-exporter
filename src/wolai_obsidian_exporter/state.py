from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


@dataclass
class ExportState:
    root_pages: list[str] = field(default_factory=list)
    completed_pages: dict[str, Any] = field(default_factory=dict)
    failed_pages: dict[str, Any] = field(default_factory=dict)
    completed_assets: dict[str, Any] = field(default_factory=dict)
    failed_assets: dict[str, Any] = field(default_factory=dict)
    last_updated: str = ""

    @classmethod
    def load(cls, path: Path) -> "ExportState":
        if not path.exists():
            return cls()
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls(**data)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.last_updated = datetime.now(timezone.utc).isoformat()
        path.write_text(
            json.dumps(self.__dict__, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    def page_done(self, page_id: str) -> bool:
        return page_id in self.completed_pages

    def asset_done(self, block_id: str) -> bool:
        return block_id in self.completed_assets

    def mark_page_done(self, page_id: str, payload: dict[str, Any]) -> None:
        self.completed_pages[page_id] = payload
        self.failed_pages.pop(page_id, None)

    def mark_page_failed(self, page_id: str, payload: dict[str, Any]) -> None:
        self.failed_pages[page_id] = payload

    def mark_asset_done(self, block_id: str, payload: dict[str, Any]) -> None:
        self.completed_assets[block_id] = payload
        self.failed_assets.pop(block_id, None)

    def mark_asset_failed(self, block_id: str, payload: dict[str, Any]) -> None:
        self.failed_assets[block_id] = payload
