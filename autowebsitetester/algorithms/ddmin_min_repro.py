from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import TypeVar

T = TypeVar("T")


def minimize_actions(actions: Sequence[T], bug_predicate: Callable[[list[T]], bool]) -> list[T]:
    """Return the smallest action sequence that still reproduces the bug."""
    current = list(actions)
    if not current or not bug_predicate(current):
        return current

    n = 2
    while len(current) >= 2:
        subset_len = max(1, len(current) // n)
        reduced = False

        for start in range(0, len(current), subset_len):
            candidate = current[start : start + subset_len]
            if candidate and bug_predicate(candidate):
                current = candidate
                n = max(2, n - 1)
                reduced = True
                break

        if reduced:
            continue

        for start in range(0, len(current), subset_len):
            candidate = current[:start] + current[start + subset_len :]
            if candidate and bug_predicate(candidate):
                current = candidate
                n = max(2, n - 1)
                reduced = True
                break

        if not reduced:
            if n >= len(current):
                break
            n = min(len(current), n * 2)

    return current
