from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable

from autowebsitetester.algorithms.ddmin_min_repro import minimize_actions
from autowebsitetester.types import ActionRecord, Failure, Severity


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

    def minimize_reproduction_path(
        self,
        actions: list[ActionRecord],
        bug_predicate: Callable[[list[ActionRecord]], bool],
    ) -> list[ActionRecord]:
        return minimize_actions(actions, bug_predicate)

    def group_failures(
        self,
        failures: list[Failure],
        actions: list[ActionRecord] | None = None,
        predicate_builder: Callable[[Failure], Callable[[list[ActionRecord]], bool]] | None = None,
    ) -> list[Failure]:
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

            if actions and predicate_builder is not None:
                scoped_actions = [action for action in actions if action.page_url == representative.page_url]
                if scoped_actions:
                    minimized = self.minimize_reproduction_path(
                        scoped_actions,
                        predicate_builder(representative),
                    )
                    representative.reproduction_steps = [
                        action.detail or f"{action.action_type} {action.target}" for action in minimized
                    ]

            grouped_failures.append(representative)

        return grouped_failures
