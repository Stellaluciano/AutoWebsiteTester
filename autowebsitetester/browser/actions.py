from __future__ import annotations

from dataclasses import dataclass

from playwright.async_api import Page


@dataclass(slots=True)
class InteractiveElement:
    selector: str
    kind: str


async def discover_interactive_elements(page: Page) -> list[InteractiveElement]:
    selectors = {
        "a[href]": "link",
        "button": "button",
        "input": "input",
        "textarea": "input",
        "select": "input",
        "form": "form",
    }
    found: list[InteractiveElement] = []
    for selector, kind in selectors.items():
        count = await page.locator(selector).count()
        if count:
            found.append(InteractiveElement(selector=selector, kind=kind))
    return found


async def perform_basic_actions(page: Page) -> list[str]:
    steps: list[str] = []

    link = page.locator("a[href]").first
    if await link.count():
        href = await link.get_attribute("href")
        steps.append(f"Click first link ({href})")
        await link.click(timeout=3000)

    button = page.locator("button").first
    if await button.count():
        button_text = (await button.text_content()) or "<button>"
        steps.append(f"Click first button ({button_text.strip()})")
        await button.click(timeout=3000)

    input_box = page.locator("input[type='text'], input:not([type])").first
    if await input_box.count():
        steps.append("Fill first text input")
        await input_box.fill("autowebsitetester")

    form = page.locator("form").first
    if await form.count():
        steps.append("Submit first form")
        await form.evaluate("form => form.requestSubmit()")

    return steps
