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

    def build_bug_predicate(self, bug_url: str, bug_message: str):
        bug_tokens = {token for token in bug_message.lower().split() if len(token) > 3}

        def predicate(actions: list[ActionRecord]) -> bool:
            has_url = any(action.page_url == bug_url for action in actions)
            has_interaction = any(action.action_type == "interaction" for action in actions)
            has_relevant_context = any(
                action.detail and any(token in action.detail.lower() for token in bug_tokens)
                for action in actions
            )
            return has_url and has_interaction and (has_relevant_context or len(actions) <= 2)

        return predicate
