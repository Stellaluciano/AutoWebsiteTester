from __future__ import annotations

from collections.abc import Iterable

from autowebsitetester.types import Failure


def detect_blank_page(url: str, text_content: str | None) -> list[Failure]:
    if text_content and text_content.strip():
        return []
    return [
        Failure(
            title="Blank page detected",
            message="Page content appears empty.",
            page_url=url,
            category="blank_page",
            debugging_hints=["Validate server-side rendering output", "Check client bootstrap scripts"],
        )
    ]


def detect_network_failures(url: str, failures: Iterable[dict]) -> list[Failure]:
    bugs: list[Failure] = []
    for failure in failures:
        status = failure.get("status", 0)
        if status >= 400:
            bugs.append(
                Failure(
                    title="HTTP request failure",
                    message=f"Request to {failure.get('request_url')} returned HTTP {status}",
                    page_url=url,
                    category="network",
                    debugging_hints=["Review backend logs", "Validate endpoint availability"],
                )
            )
    return bugs


def detect_console_errors(url: str, logs: Iterable[str]) -> list[Failure]:
    bugs: list[Failure] = []
    for line in logs:
        if "error" in line.lower() or "uncaught" in line.lower():
            bugs.append(
                Failure(
                    title="JavaScript console error",
                    message=line,
                    page_url=url,
                    category="console",
                    debugging_hints=["Inspect browser devtools stack trace", "Check recent frontend deploy"],
                )
            )
    return bugs
