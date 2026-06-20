from __future__ import annotations

from pathlib import Path

from wolai_obsidian_exporter.markdown.blocks import MediaBlock
from wolai_obsidian_exporter.utils.paths import relative_markdown_path


def build_asset_links(
    markdown_path: Path, downloaded_assets: list[dict[str, object]]
) -> dict[str, str]:
    links: dict[str, str] = {}
    for asset in downloaded_assets:
        block_id = str(asset.get("block_id") or "")
        local_path = asset.get("local_path")
        if not block_id or not local_path:
            continue
        links[block_id] = relative_markdown_path(markdown_path, Path(str(local_path)))
    return links


def media_to_asset_rows(media_blocks: list[MediaBlock]) -> list[dict[str, str]]:
    return [
        {
            "page_id": block.page_id,
            "block_id": block.block_id,
            "type": block.block_type,
            "name": block.filename or block.caption,
        }
        for block in media_blocks
    ]
