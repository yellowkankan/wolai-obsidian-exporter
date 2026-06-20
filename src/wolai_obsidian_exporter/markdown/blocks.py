from __future__ import annotations

from dataclasses import dataclass
from typing import Any

MEDIA_TYPES = {"image", "file", "video", "audio"}


@dataclass(frozen=True)
class MediaBlock:
    page_id: str
    block_id: str
    block_type: str
    caption: str = ""
    filename: str = ""
    ext_hint: str = ""


def render_inline(content: Any) -> str:
    if not content:
        return ""
    if isinstance(content, str):
        return content
    if not isinstance(content, list):
        return str(content)
    parts: list[str] = []
    for item in content:
        if not isinstance(item, dict):
            continue
        item_type = item.get("type", "text")
        title = item.get("title", "")
        if item_type == "equation":
            parts.append(f"${title}$")
            continue
        if item_type == "bi_link":
            block_id = item.get("block_id", "")
            parts.append(f"[{title}]({block_id})")
            continue
        text = title or ""
        if item.get("inline_code"):
            text = f"`{text}`"
        if item.get("bold"):
            text = f"**{text}**"
        if item.get("italic"):
            text = f"*{text}*"
        if item.get("strikethrough"):
            text = f"~~{text}~~"
        if item.get("underline"):
            text = f"<u>{text}</u>"
        if item.get("link"):
            text = f"[{text}]({item['link']})"
        parts.append(text)
    return "".join(parts)


def media_filename(block: dict[str, Any]) -> str:
    for key in ("file_name", "filename", "name", "caption"):
        value = block.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    media = block.get("media") or {}
    download_url = media.get("download_url") or ""
    if "download=" in download_url:
        return download_url.rsplit("download=", 1)[-1].split("&", 1)[0]
    return block.get("type", "asset")


def collect_media_blocks(blocks: list[dict[str, Any]], page_id: str) -> list[MediaBlock]:
    media: list[MediaBlock] = []
    for block in blocks:
        if block.get("type") not in MEDIA_TYPES:
            continue
        block_id = block.get("id")
        if not block_id:
            continue
        media.append(
            MediaBlock(
                page_id=page_id,
                block_id=block_id,
                block_type=block.get("type", "file"),
                caption=block.get("caption") or "",
                filename=media_filename(block),
            )
        )
    return media
