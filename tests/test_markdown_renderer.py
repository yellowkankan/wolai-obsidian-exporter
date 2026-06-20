import json
from pathlib import Path

from wolai_obsidian_exporter.markdown.renderer import MarkdownRenderer

FIXTURES = Path(__file__).parent / "fixtures"


def test_markdown_renderer_outputs_basic_blocks():
    blocks = json.loads((FIXTURES / "sample_blocks.json").read_text())
    markdown, child_pages, databases, assets = MarkdownRenderer().render_page(
        page_id="page_demo",
        title="Demo Page",
        wolai_path="Demo Page",
        blocks=blocks,
        asset_links={"image_1": "../assets/images/page_demo/image_1.png"},
    )

    assert "# Demo Page" in markdown
    assert "## Section" in markdown
    assert "Hello Wolai" in markdown
    assert "![Sample image](../assets/images/page_demo/image_1.png)" in markdown
    assert "- [x] Done task" in markdown
    assert "```python" in markdown
    assert child_pages == []
    assert databases == []
    assert assets[0]["block_id"] == "image_1"


def test_output_path_uses_safe_title(tmp_path):
    path = MarkdownRenderer().output_path(tmp_path, "A/B:C", "Root / A/B:C", "page_1")
    assert path.name == "A_B_C-page_1.md"
