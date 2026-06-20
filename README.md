# Wolai Obsidian Exporter

Local-first CLI for exporting Wolai pages into an Obsidian-friendly folder.

It exports:

- Markdown pages
- Raw JSON snapshots
- Images, files, videos, and audio as local assets
- Index, asset, failure, and sensitive-info reports
- Resume state for interrupted exports

This project is unofficial and is not affiliated with Wolai.

## What it does

Wolai media URLs can expire quickly, so this exporter refreshes each media block right before downloading the asset.

```text
get page blocks
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
- It does not clean or rewrite your notes into knowledge cards.

## Install for local development

```bash
git clone <repo-url>
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

## Asset handling

Media blocks are downloaded into local folders and referenced from Markdown by relative paths. Signed URLs are not written into Markdown or reports.

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

This is an early local-first exporter. The API adapter may need adjustment depending on whether your Wolai account uses the public OpenAPI token or the MCP token endpoint.
