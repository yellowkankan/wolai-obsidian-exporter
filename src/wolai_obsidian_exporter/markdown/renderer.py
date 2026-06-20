from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from wolai_obsidian_exporter.markdown.blocks import (
    collect_media_blocks,
    media_filename,
    render_inline,
)
from wolai_obsidian_exporter.markdown.frontmatter import frontmatter
from wolai_obsidian_exporter.utils.slugify import slugify_filename, split_wolai_path


class MarkdownRenderer:
    def __init__(self, link_style: str = "markdown") -> None:
        self.link_style = link_style

    def render_page(
        self,
        *,
        page_id: str,
        title: str,
        wolai_path: str,
        parent_id: str = "",
        blocks: list[dict[str, Any]],
        asset_links: Optional[dict[str, str]] = None,
    ) -> tuple[str, list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
        asset_links = asset_links or {}
        blocks_by_id = {b["id"]: b for b in blocks if isinstance(b, dict) and b.get("id")}
        root = blocks_by_id.get(page_id) or (blocks[0] if blocks else None)
        child_pages: list[dict[str, str]] = []
        databases: list[dict[str, str]] = []
        assets = [m.__dict__ for m in collect_media_blocks(blocks, page_id)]

        body: list[str] = []
        if root:
            for child_id in (root.get("children") or {}).get("ids") or []:
                child = blocks_by_id.get(child_id)
                if child:
                    body.extend(
                        self._block_to_md(
                            child,
                            blocks_by_id,
                            page_id,
                            child_pages,
                            databases,
                            asset_links,
                        )
                    )

        fields = {
            "笔记类型": "迁移原始页面",
            "source": "wolai",
            "mirror_type": "raw_page",
            "wolai_page_id": page_id,
            "wolai_parent_id": parent_id,
            "wolai_title": title,
            "wolai_path": wolai_path,
            "export_status": "exported" if blocks else "partial",
            "block_count": max(0, len(blocks) - 1),
        }
        markdown = (
            frontmatter(fields)
            + "\n\n"
            + f"# {title or 'Untitled'}\n\n"
            + "\n".join(body).rstrip()
            + "\n"
        )
        return markdown, child_pages, databases, assets

    def output_path(self, pages_root: Path, title: str, wolai_path: str, page_id: str) -> Path:
        parts = split_wolai_path(wolai_path)
        safe_title = slugify_filename(title)
        if parts and parts[-1] == safe_title:
            parts = parts[:-1]
        return pages_root.joinpath(*parts, f"{safe_title}-{page_id}.md")

    def _block_to_md(
        self,
        block: dict[str, Any],
        blocks_by_id: dict[str, dict[str, Any]],
        page_id: str,
        child_pages: list[dict[str, str]],
        databases: list[dict[str, str]],
        asset_links: dict[str, str],
        depth: int = 0,
    ) -> list[str]:
        block_type = block.get("type", "")
        block_id = block.get("id", "")
        text = render_inline(block.get("content", []))
        indent = "  " * depth
        lines: list[str] = []

        if block_type == "page":
            if block_id != page_id:
                title = text or "Untitled"
                child_pages.append({"title": title, "page_id": block_id, "parent_page_id": page_id})
                lines.append(f"{indent}- [[{title}]]")
            return lines
        if block_type == "heading":
            level = min(max(int(block.get("level", 1) or 1), 1), 3)
            lines.append(f"{'#' * level} {text}")
        elif block_type in {"text", "paragraph"}:
            lines.append(text)
        elif block_type == "quote":
            lines.append("> " + text)
        elif block_type == "callout":
            lines.append("> [!note]")
            for line in text.splitlines() or [""]:
                lines.append("> " + line)
        elif block_type == "bull_list":
            lines.append(f"{indent}- {text}")
        elif block_type == "enum_list":
            lines.append(f"{indent}1. {text}")
        elif block_type == "todo_list":
            mark = "x" if block.get("checked") else " "
            lines.append(f"{indent}- [{mark}] {text}")
        elif block_type == "todo_list_pro":
            mark = {"todo": " ", "doing": "/", "done": "x", "cancel": "-"}.get(
                block.get("task_status"), " "
            )
            lines.append(f"{indent}- [{mark}] {text}")
        elif block_type == "toggle_list":
            lines.append(f"{indent}- {text}")
        elif block_type == "divider":
            lines.append("---")
        elif block_type == "code":
            lang = block.get("language", "")
            lines.extend([f"```{lang}", text, "```"])
        elif block_type == "block_equation":
            lines.extend(["$$", text, "$$"])
        elif block_type == "image":
            alt = block.get("caption") or "image"
            link = asset_links.get(block_id, "")
            lines.append(f"![{alt}]({link})" if link else f"![{alt}]()")
        elif block_type in {"video", "audio", "file"}:
            name = media_filename(block)
            link = asset_links.get(block_id, "")
            lines.append(f"[{name}]({link})" if link else f"[{name}]()")
        elif block_type == "embed":
            link = block.get("original_link") or block.get("embed_link") or ""
            lines.append(f"[embed]({link})")
        elif block_type == "bookmark":
            link = block.get("link", "")
            lines.append(f"[bookmark]({link})")
        elif block_type == "table":
            rows = block.get("table_content") or []
            if rows:
                header = [str(cell) for cell in rows[0]]
                lines.append("| " + " | ".join(header) + " |")
                lines.append("| " + " | ".join("---" for _ in header) + " |")
                for row in rows[1:]:
                    lines.append("| " + " | ".join(str(cell) for cell in row) + " |")
        elif block_type == "database":
            databases.append(
                {"title": text or "database", "database_id": block_id, "source_page_id": page_id}
            )
            lines.append(f"[database: {block_id}]")
        elif text:
            lines.append(text)
        else:
            lines.append(f"[{block_type}: {block_id}]")

        child_depth = (
            depth + 1
            if block_type in {"bull_list", "enum_list", "todo_list", "todo_list_pro", "toggle_list"}
            else depth
        )
        for child_id in (block.get("children") or {}).get("ids") or []:
            child = blocks_by_id.get(child_id)
            if child:
                lines.extend(
                    self._block_to_md(
                        child,
                        blocks_by_id,
                        page_id,
                        child_pages,
                        databases,
                        asset_links,
                        child_depth,
                    )
                )
        return lines
