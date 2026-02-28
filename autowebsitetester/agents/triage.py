from __future__ import annotations

from collections import defaultdict

from autowebsitetester.types import Failure, Severity


class TriageAgent:
    def classify_severity(self, failure: Failure) -> Severity:
        message = f"{failure.title} {failure.message}".lower()
        if any(token in message for token in ["500", "timeout", "uncaught", "blank page"]):
            return Severity.P0
        if any(token in message for token in ["404", "failed", "not responding"]):
            return Severity.P1
        if any(token in message for token in ["missing", "ui", "warning"]):
            return Severity.P2
        return Severity.P3

    def group_failures(self, failures: list[Failure]) -> list[Failure]:
        grouped: dict[tuple[str, str, str], list[Failure]] = defaultdict(list)
        for failure in failures:
            key = (
                failure.message.split("\n")[0],
                failure.page_url,
                failure.stack_trace or "",
            )
            grouped[key].append(failure)

        grouped_failures: list[Failure] = []
        for _, bucket in grouped.items():
            representative = bucket[0]
            representative.severity = self.classify_severity(representative)
            if len(bucket) > 1:
                representative.reproduction_steps.append(
                    f"Observed {len(bucket)} times during crawl"
                )
            grouped_failures.append(representative)

        return grouped_failures
