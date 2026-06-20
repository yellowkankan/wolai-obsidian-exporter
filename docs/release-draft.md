# v0.1.0 Draft

## Highlights

- Export Wolai pages into Obsidian-friendly Markdown.
- Save raw JSON snapshots for archival and debugging.
- Download images, files, videos, and audio locally.
- Refresh expiring media URLs right before download.
- Resume interrupted exports.
- Generate index, asset, failure, and sensitive-info reports.

## Install

```bash
git clone <repo-url>
cd wolai-obsidian-exporter
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Quick start

```bash
export WOLAI_TOKEN="..."
wolai-obsidian-export export --root-page "<page_id>" --out "./WolaiMirror" --resume
```

## Notes

This is an unofficial local-first exporter. It is not affiliated with Wolai.
