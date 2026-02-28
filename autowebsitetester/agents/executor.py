from __future__ import annotations

from playwright.async_api import Page

from autowebsitetester.browser.actions import perform_basic_actions
from autowebsitetester.types import ActionRecord


class ExecutorAgent:
    async def execute(self, page: Page, page_url: str) -> list[ActionRecord]:
        steps = await perform_basic_actions(page)
        return [
            ActionRecord(page_url=page_url, action_type="interaction", target="page", detail=step)
            for step in steps
        ]
