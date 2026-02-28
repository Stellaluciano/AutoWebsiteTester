from __future__ import annotations

from pathlib import Path

from playwright.async_api import Page


async def save_snapshot(page: Page, out_dir: Path, slug: str) -> tuple[str, str]:
    out_dir.mkdir(parents=True, exist_ok=True)
    screenshot_path = out_dir / f"{slug}.png"
    html_path = out_dir / f"{slug}.html"

    await page.screenshot(path=str(screenshot_path), full_page=True)
    html_path.write_text(await page.content(), encoding="utf-8")
    return str(screenshot_path), str(html_path)
