from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from wolai_obsidian_exporter.assets.downloader import download_asset
from wolai_obsidian_exporter.assets.resolver import build_asset_links
from wolai_obsidian_exporter.config import Settings
from wolai_obsidian_exporter.markdown.blocks import collect_media_blocks
from wolai_obsidian_exporter.markdown.renderer import MarkdownRenderer
from wolai_obsidian_exporter.reports.index_writer import write_json, write_markdown_table
from wolai_obsidian_exporter.state import ExportState
from wolai_obsidian_exporter.wolai_client import WolaiClient, unwrap_mcp_data


@dataclass(frozen=True)
class ExportOptions:
    root_pages: list[str]
    output_dir: Path
    resume: bool = True
    force: bool = False
    max_depth: int = 10
    link_style: str = "markdown"
    download_assets: bool = True


class WolaiExporter:
    def __init__(self, settings: Settings, options: ExportOptions) -> None:
        self.settings = settings
        self.options = options
        self.pages_root = options.output_dir / "pages"
        self.json_pages_root = options.output_dir / "json" / "pages"
        self.assets_root = options.output_dir / "assets"
        self.reports_root = options.output_dir / "reports"
        self.state_path = options.output_dir / ".wolai-export-state" / "state.json"
        self.renderer = MarkdownRenderer(link_style=options.link_style)

    def export(self) -> dict[str, int]:
        state = ExportState.load(self.state_path) if self.options.resume else ExportState()
        state.root_pages = self.options.root_pages
        queue: list[tuple[str, str, str, int]] = [
            (page_id, "", "", 0) for page_id in self.options.root_pages
        ]
        seen = {page_id for page_id in self.options.root_pages}
        exported = partial = failed = assets_downloaded = 0
        page_rows: list[list[object]] = []
        failure_rows: list[list[object]] = []
        asset_rows: list[list[object]] = []

        with WolaiClient(
            token=self.settings.token,
            base_url=self.settings.api_base_url,
            timeout_seconds=self.settings.timeout_seconds,
            max_retries=self.settings.max_retries,
        ) as client:
            while queue:
                page_id, path, parent_id, depth = queue.pop(0)
                if depth > self.options.max_depth:
                    continue
                if state.page_done(page_id) and not self.options.force:
                    continue
                try:
                    result = self._export_page(client, page_id, path, parent_id)
                except Exception as exc:  # noqa: BLE001
                    failed += 1
                    payload = {"reason": str(exc), "stage": "export_page"}
                    state.mark_page_failed(page_id, payload)
                    failure_rows.append(["page", page_id, "", "export_page", str(exc)])
                    state.save(self.state_path)
                    continue

                page_rows.append(
                    [
                        result["page_id"],
                        result["title"],
                        result["path"],
                        result["markdown_path"],
                        result["status"],
                    ]
                )
                if result["status"] == "exported":
                    exported += 1
                else:
                    partial += 1
                assets_downloaded += int(result.get("assets_downloaded", 0))
                for asset in result.get("assets", []):
                    asset_rows.append(
                        [
                            asset.get("page_id"),
                            asset.get("block_id"),
                            asset.get("type"),
                            asset.get("local_path"),
                            asset.get("status", ""),
                        ]
                    )
                for child in result.get("child_pages", []):
                    child_id = child.get("page_id")
                    if child_id and child_id not in seen:
                        seen.add(child_id)
                        child_path = f"{result['path']} / {child.get('title', '')}".strip(" /")
                        queue.append((child_id, child_path, page_id, depth + 1))
                state.mark_page_done(page_id, result)
                state.save(self.state_path)

        self._write_reports(page_rows, asset_rows, failure_rows)
        return {
            "exported": exported,
            "partial": partial,
            "failed": failed,
            "assets_downloaded": assets_downloaded,
        }

    def _export_page(
        self, client: WolaiClient, page_id: str, path: str, parent_id: str
    ) -> dict[str, Any]:
        doc_raw = client.get_doc(page_id)
        blocks_raw = client.get_page_blocks(page_id)
        outline_raw = client.get_page_outline(page_id)
        doc = unwrap_mcp_data(doc_raw)
        blocks = unwrap_mcp_data(blocks_raw)
        outline = unwrap_mcp_data(outline_raw)
        if not isinstance(blocks, list):
            blocks = []
        title = self._title_from_doc(doc, page_id)
        wolai_path = path or title
        markdown_path = self.renderer.output_path(self.pages_root, title, wolai_path, page_id)
        media_blocks = collect_media_blocks(blocks, page_id)
        downloaded: list[dict[str, object]] = []
        failures: list[dict[str, object]] = []
        if self.options.download_assets:
            for media in media_blocks:
                try:
                    asset = download_asset(client=client, media=media, assets_root=self.assets_root)
                    asset["status"] = "downloaded"
                    downloaded.append(asset)
                except Exception as exc:  # noqa: BLE001
                    failures.append(
                        {
                            "page_id": media.page_id,
                            "block_id": media.block_id,
                            "type": media.block_type,
                            "status": "failed",
                            "reason": str(exc),
                        }
                    )
        asset_links = build_asset_links(markdown_path, downloaded)
        markdown, child_pages, databases, assets = self.renderer.render_page(
            page_id=page_id,
            title=title,
            wolai_path=wolai_path,
            parent_id=parent_id,
            blocks=blocks,
            asset_links=asset_links,
        )
        markdown_path.parent.mkdir(parents=True, exist_ok=True)
        markdown_path.write_text(markdown, encoding="utf-8")
        raw_path = self.json_pages_root / f"{page_id}.json"
        write_json(
            raw_path, {"doc": doc, "outline": outline, "blocks": blocks, "asset_failures": failures}
        )
        report_assets = [self._asset_for_report(asset) for asset in downloaded]
        report_assets.extend(failures)
        return {
            "page_id": page_id,
            "title": title,
            "path": wolai_path,
            "parent_id": parent_id,
            "status": "exported" if blocks else "partial",
            "markdown_path": self._relative_output(markdown_path),
            "json_path": self._relative_output(raw_path),
            "child_pages": child_pages,
            "databases": databases,
            "assets": report_assets,
            "assets_downloaded": len(downloaded),
        }

    def _relative_output(self, path: Path) -> str:
        return path.relative_to(self.options.output_dir).as_posix()

    def _asset_for_report(self, asset: dict[str, object]) -> dict[str, object]:
        local_path = asset.get("local_path")
        if local_path:
            asset = dict(asset)
            asset["local_path"] = self._relative_output(Path(str(local_path)))
        return asset

    def _title_from_doc(self, doc: Any, page_id: str) -> str:
        if isinstance(doc, dict):
            content = doc.get("content")
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get("title"):
                        return str(item["title"])
            if doc.get("title"):
                return str(doc["title"])
        return page_id

    def _write_reports(
        self,
        page_rows: list[list[object]],
        asset_rows: list[list[object]],
        failure_rows: list[list[object]],
    ) -> None:
        write_markdown_table(
            self.reports_root / "index.md",
            "Wolai Export Index",
            ["page_id", "title", "path", "markdown", "status"],
            page_rows,
        )
        write_markdown_table(
            self.reports_root / "assets.md",
            "Wolai Assets",
            ["page_id", "block_id", "type", "local_path", "status"],
            asset_rows,
        )
        write_markdown_table(
            self.reports_root / "failures.md",
            "Wolai Export Failures",
            ["type", "id", "title", "stage", "reason"],
            failure_rows,
        )
        write_json(self.reports_root / "index.json", page_rows)
        write_json(self.reports_root / "assets.json", asset_rows)
        write_json(self.reports_root / "failures.json", failure_rows)
