from __future__ import annotations

from autowebsitetester.types import ScanResult


def render_markdown(result: ScanResult) -> str:
    lines = [
        "# AutoWebsiteTester Scan Report",
        f"- Root URL: {result.root_url}",
        f"- Visited pages: {len(result.visited_urls)}",
        f"- Actions executed: {len(result.actions)}",
        f"- Bugs found: {len(result.failures)}",
        "",
        "## Bugs",
    ]

    if not result.failures:
        lines.append("No bugs detected.")
        return "\n".join(lines)

    for idx, bug in enumerate(result.failures, start=1):
        lines.extend(
            [
                f"### {idx}. {bug.title}",
                f"- Severity: **{bug.severity.value}**",
                f"- Page: {bug.page_url}",
                f"- Message: {bug.message}",
                f"- Reproduction steps: {'; '.join(bug.reproduction_steps) if bug.reproduction_steps else 'N/A'}",
                f"- Screenshot: {bug.evidence.screenshot or 'N/A'}",
                f"- Logs: {' | '.join(bug.evidence.console_logs) if bug.evidence.console_logs else 'N/A'}",
                f"- Debug hints: {'; '.join(bug.debugging_hints) if bug.debugging_hints else 'N/A'}",
                "",
            ]
        )

    return "\n".join(lines)
