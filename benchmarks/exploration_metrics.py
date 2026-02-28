from __future__ import annotations

from autowebsitetester.types import ScanResult


def compute_exploration_metrics(result: ScanResult) -> dict[str, float]:
    pages_discovered = len(result.visited_urls)
    unique_states = len({url.split('#')[0] for url in result.visited_urls})
    bugs_found = len(result.failures)
    actions_per_bug = len(result.actions) / bugs_found if bugs_found else float(len(result.actions))

    return {
        "pages_discovered": float(pages_discovered),
        "unique_states": float(unique_states),
        "bugs_found": float(bugs_found),
        "actions_per_bug": actions_per_bug,
    }
