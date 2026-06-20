from pathlib import Path

from wolai_obsidian_exporter.state import ExportState


def test_state_resume_round_trip(tmp_path: Path):
    state_path = tmp_path / "state.json"
    state = ExportState()
    state.mark_page_done("page_1", {"title": "Demo"})
    state.mark_asset_failed("asset_1", {"reason": "network"})
    state.save(state_path)

    loaded = ExportState.load(state_path)
    assert loaded.page_done("page_1")
    assert loaded.failed_assets["asset_1"]["reason"] == "network"
