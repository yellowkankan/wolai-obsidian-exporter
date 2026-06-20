from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console

from wolai_obsidian_exporter import __version__
from wolai_obsidian_exporter.config import ConfigError, load_settings
from wolai_obsidian_exporter.exporter import ExportOptions, WolaiExporter
from wolai_obsidian_exporter.reports.sensitive_scan import scan_path
from wolai_obsidian_exporter.utils.logging import configure_logging

app = typer.Typer(help="Export Wolai pages and assets into an Obsidian-friendly folder.")
console = Console()


@app.command()
def version() -> None:
    console.print(__version__)


@app.command("check-config")
def check_config(out: Path = typer.Option(Path("./WolaiMirror"), "--out")) -> None:
    try:
        settings = load_settings(out)
    except ConfigError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc
    console.print("[green]Config OK[/green]")
    console.print(f"Output: {settings.output_dir}")
    console.print(f"API: {settings.api_base_url}")


@app.command("export")
def export_command(
    root_page: list[str] = typer.Option(
        ..., "--root-page", help="Root Wolai page ID. Can be passed multiple times."
    ),
    out: Path = typer.Option(Path("./WolaiMirror"), "--out", help="Output directory."),
    resume: bool = typer.Option(True, "--resume/--no-resume"),
    force: bool = typer.Option(False, "--force"),
    max_depth: int = typer.Option(10, "--max-depth"),
    link_style: str = typer.Option("markdown", "--link-style"),
    download_assets: bool = typer.Option(True, "--assets/--no-assets"),
    verbose: bool = typer.Option(False, "--verbose"),
) -> None:
    configure_logging(verbose)
    try:
        settings = load_settings(out)
    except ConfigError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(1) from exc
    options = ExportOptions(
        root_pages=root_page,
        output_dir=settings.output_dir,
        resume=resume,
        force=force,
        max_depth=max_depth,
        link_style=link_style,
        download_assets=download_assets,
    )
    summary = WolaiExporter(settings, options).export()
    console.print(summary)


@app.command("scan-secrets")
def scan_secrets(path: Path = typer.Option(..., "--path")) -> None:
    hits = scan_path(path)
    for hit in hits:
        console.print(f"{hit.file}:{hit.line} {hit.kind}")
    if hits:
        raise typer.Exit(1)
    console.print("No sensitive patterns found.")


@app.command("clean-state")
def clean_state(out: Path = typer.Option(Path("./WolaiMirror"), "--out")) -> None:
    state_dir = out / ".wolai-export-state"
    if not state_dir.exists():
        console.print("No state directory found.")
        return
    console.print(f"State directory: {state_dir}")
    console.print("Remove it manually after reviewing. This command is non-destructive by design.")


if __name__ == "__main__":
    app()
