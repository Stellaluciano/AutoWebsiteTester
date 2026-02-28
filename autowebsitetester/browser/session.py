from __future__ import annotations

from contextlib import asynccontextmanager

from playwright.async_api import async_playwright, Browser, BrowserContext, Page


@asynccontextmanager
async def browser_session(headless: bool = True):
    playwright = await async_playwright().start()
    browser: Browser = await playwright.chromium.launch(headless=headless)
    context: BrowserContext = await browser.new_context(ignore_https_errors=True)
    page: Page = await context.new_page()
    try:
        yield context, page
    finally:
        await context.close()
        await browser.close()
        await playwright.stop()
