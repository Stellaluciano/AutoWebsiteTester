from __future__ import annotations

from dataclasses import dataclass, field

from playwright.async_api import Page

from autowebsitetester.browser.detectors import (
    detect_blank_page,
    detect_console_errors,
    detect_network_failures,
)
from autowebsitetester.types import Failure


@dataclass(slots=True)
class OracleState:
    console_logs: list[str] = field(default_factory=list)
    network_events: list[dict] = field(default_factory=list)


class OracleAgent:
    def __init__(self) -> None:
        self.state = OracleState()

    def attach(self, page: Page) -> None:
        page.on("console", lambda msg: self.state.console_logs.append(msg.text))
        page.on(
            "response",
            lambda response: self.state.network_events.append(
                {"request_url": response.url, "status": response.status}
            ),
        )

    async def inspect(self, page: Page, url: str) -> list[Failure]:
        body_text = await page.text_content("body")
        failures = [
            *detect_blank_page(url, body_text),
            *detect_console_errors(url, self.state.console_logs),
            *detect_network_failures(url, self.state.network_events),
        ]
        return failures
