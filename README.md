# Wolai Obsidian Exporter

I built this while moving an old Wolai knowledge base into Obsidian.

The annoying part was not exporting text. The hard part was preserving the images, files, and videos: Wolai media links are signed URLs and can expire quickly. This tool mirrors Wolai pages into a local folder, refreshes media URLs right before download, and rewrites the Markdown to point at local assets.

It is meant for people who want a local archive they can search, back up, and open in Obsidian without depending on Wolai's temporary media links.

This project is unofficial and is not affiliated with Wolai.

## Features

- Export Wolai pages as Markdown.
- Save raw JSON snapshots for later debugging or re-rendering.
- Download images, files, videos, and audio as local assets.
- Refresh media blocks before downloading expired signed URLs.
- Resume interrupted exports.
- Generate index, asset, failure, and sensitive-info reports.
- Keep tokens and signed URLs out of Markdown and reports.

## Why this exists

A direct copy from Wolai to Markdown is not enough. If the original page has screenshots, design references, videos, spreadsheets, or training files, a text-only export loses most of the value.

This exporter treats attachments as first-class data:

```text
read page blocks
→ render Markdown
→ find media blocks
→ refresh each media block
→ download local assets
→ write relative links
→ save state and reports
```

## What it does not do

- It does not modify Wolai content.
- It does not bypass access controls.
- It does not read browser cookies.
- It does not upload your data anywhere.
- It does not turn your notes into cleaned knowledge cards.

## Install for local development

```bash
git clone https://github.com/yellowkankan/wolai-obsidian-exporter.git
cd wolai-obsidian-exporter
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
```

## Authentication

Set your token in the shell:

```bash
export WOLAI_TOKEN="replace_with_your_token"
```

Do not commit real tokens. `.env` is ignored by default.

## Quick start

```bash
wolai-obsidian-export check-config

wolai-obsidian-export export \
  --root-page "your_root_page_id" \
  --out ./exports/WolaiMirror \
  --resume
```

## Output structure

```text
WolaiMirror/
  pages/
  json/
    pages/
    blocks/
  assets/
    images/
    files/
    videos/
    audios/
  reports/
    index.md
    assets.md
    failures.md
  .wolai-export-state/
    state.json
```

Markdown uses relative asset links by default, so the folder can be moved or backed up as one archive.

## Asset handling

Media blocks are downloaded into local folders and referenced from Markdown by relative paths. Signed URLs are refreshed before download and are not written into Markdown or reports.

## Resume

Use `--resume` to continue an interrupted export. Completed pages and assets are skipped unless `--force` is passed.

## Privacy and security

Before publishing or sharing an export, run:

```bash
wolai-obsidian-export scan-secrets --path ./exports/WolaiMirror
python scripts/check_no_secrets.py
```

The scanner reports file path, line number, and match type only. It does not print full secret values.

## Development

```bash
ruff check .
ruff format --check .
pytest
python scripts/check_no_secrets.py
```

## Status

This is an early exporter. The current implementation targets Wolai's MCP endpoint and has been tested on a small sample page. More block types and database export improvements will be added as real migration cases come up.
