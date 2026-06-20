from __future__ import annotations

import mimetypes
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

import httpx

from wolai_obsidian_exporter.assets.sanitizer import sanitize_url_for_reports
from wolai_obsidian_exporter.markdown.blocks import MediaBlock
from wolai_obsidian_exporter.utils.slugify import slugify_filename
from wolai_obsidian_exporter.wolai_client import WolaiClient, unwrap_mcp_data

TYPE_DIRS = {
    "image": "images",
    "file": "files",
    "video": "videos",
    "audio": "audios",
}


class AssetDownloadError(RuntimeError):
    pass


def resolve_download_url(client: WolaiClient, block_id: str) -> str:
    payload = client.get_block(block_id)
    block = unwrap_mcp_data(payload)
    if isinstance(block, dict) and "data" in block and isinstance(block["data"], dict):
        block = block["data"]
    media = block.get("media") if isinstance(block, dict) else None
    if not isinstance(media, dict):
        raise AssetDownloadError("block has no media payload")
    url = media.get("download_url")
    if not isinstance(url, str) or not url.startswith("http"):
        raise AssetDownloadError("block has no downloadable media url")
    return url


def extension_from_url_or_name(url: str, name: str, fallback: str = ".bin") -> str:
    candidates = [name]
    split = urlsplit(url)
    query_name = (parse_qs(split.query).get("download") or [""])[0]
    candidates.append(unquote(query_name))
    candidates.append(Path(split.path).name)
    for candidate in candidates:
        suffix = Path(candidate).suffix
        if suffix and len(suffix) <= 10:
            return suffix.lower()
    guessed = mimetypes.guess_extension(mimetypes.guess_type(name)[0] or "")
    return guessed or fallback


def local_asset_path(assets_root: Path, media: MediaBlock, download_url: str) -> Path:
    subdir = TYPE_DIRS.get(media.block_type, "files")
    ext = media.ext_hint or extension_from_url_or_name(download_url, media.filename)
    filename = slugify_filename(media.block_id, fallback="asset") + ext
    return assets_root / subdir / slugify_filename(media.page_id) / filename


def download_asset(
    *,
    client: WolaiClient,
    media: MediaBlock,
    assets_root: Path,
    timeout_seconds: float = 120.0,
) -> dict[str, object]:
    url = resolve_download_url(client, media.block_id)
    target = local_asset_path(assets_root, media, url)
    target.parent.mkdir(parents=True, exist_ok=True)
    with httpx.stream("GET", url, timeout=timeout_seconds, follow_redirects=True) as response:
        response.raise_for_status()
        with target.open("wb") as fh:
            for chunk in response.iter_bytes():
                fh.write(chunk)
    sanitized = sanitize_url_for_reports(url)
    return {
        "page_id": media.page_id,
        "block_id": media.block_id,
        "type": media.block_type,
        "local_path": str(target),
        "file_bytes": target.stat().st_size,
        "url_redacted": sanitized.redacted,
    }
