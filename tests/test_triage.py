from autowebsitetester.agents.triage import TriageAgent
from autowebsitetester.types import Failure, Severity


def test_group_failures_merges_duplicates() -> None:
    triage = TriageAgent()
    failures = [
        Failure(
            title="JavaScript console error",
            message="Uncaught TypeError: x is not a function",
            page_url="https://example.com/dashboard",
            category="console",
            stack_trace="stack-a",
        ),
        Failure(
            title="JavaScript console error",
            message="Uncaught TypeError: x is not a function",
            page_url="https://example.com/dashboard",
            category="console",
            stack_trace="stack-a",
        ),
    ]

    grouped = triage.group_failures(failures)

    assert len(grouped) == 1
    assert grouped[0].severity == Severity.P0
    assert "Observed 2 times during crawl" in grouped[0].reproduction_steps


def test_severity_classification_levels() -> None:
    triage = TriageAgent()

    p0 = Failure(
        title="Blank page detected",
        message="Page content appears empty.",
        page_url="https://example.com",
        category="blank_page",
    )
    p1 = Failure(
        title="HTTP request failure",
        message="Request returned HTTP 404",
        page_url="https://example.com",
        category="network",
    )
    p2 = Failure(
        title="UI warning",
        message="Missing submit button",
        page_url="https://example.com",
        category="ui",
    )
    p3 = Failure(
        title="Suggestion",
        message="Consider adding aria labels",
        page_url="https://example.com",
        category="a11y",
    )

    assert triage.classify_severity(p0) == Severity.P0
    assert triage.classify_severity(p1) == Severity.P1
    assert triage.classify_severity(p2) == Severity.P2
    assert triage.classify_severity(p3) == Severity.P3
