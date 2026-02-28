from __future__ import annotations

import asyncio

import typer

from autowebsitetester.config import ScanConfig
from autowebsitetester.runner import ScanRunner

app = typer.Typer(help="AI-powered website QA crawler")


@app.command()
def scan(
    url: str,
    depth: int = typer.Option(3, help="BFS depth to crawl"),
    max_pages: int = typer.Option(50, help="Maximum number of pages to visit"),
    headless: bool = typer.Option(True, help="Run browser in headless mode"),
    ai_analysis: bool = typer.Option(False, help="Enable optional OpenAI analysis"),
    out: str = typer.Option("./report", help="Output directory"),
) -> None:
    """Scan a website and generate bug reports."""
    config = ScanConfig.from_cli(
        root_url=url,
        depth=depth,
        max_pages=max_pages,
        headless=headless,
        ai_analysis=ai_analysis,
        out=out,
    )
    result = asyncio.run(ScanRunner(config).run())
    typer.echo(f"Scan completed. Found {len(result.failures)} potential issues.")


if __name__ == "__main__":
    app()
