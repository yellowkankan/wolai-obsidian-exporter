# v0.1.0 Draft

## Highlights

This first version focuses on a practical migration problem: preserving Wolai pages together with their local assets for Obsidian.

- Export Wolai pages into Obsidian-friendly Markdown.
- Save raw JSON snapshots for archival and debugging.
- Download images, files, videos, and audio locally.
- Refresh expiring media URLs right before download.
- Resume interrupted exports.
- Generate index, asset, failure, and sensitive-info reports.

## Install

```bash
git clone https://github.com/yellowkankan/wolai-obsidian-exporter.git
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
