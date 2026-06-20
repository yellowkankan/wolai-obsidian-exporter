from pathlib import Path

from wolai_obsidian_exporter.reports.sensitive_scan import scan_path


def test_sensitive_scan_reports_kind_without_secret_value(tmp_path: Path):
    file = tmp_path / "note.md"
    file.write_text("token=abc123456789SECRET\n", encoding="utf-8")

    hits = scan_path(tmp_path)

    assert len(hits) == 1
    assert hits[0].kind == "auth_query"
    assert "SECRET" not in repr(hits[0])
