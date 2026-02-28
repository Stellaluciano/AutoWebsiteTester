from autowebsitetester.algorithms.ddmin_min_repro import minimize_actions


def test_minimize_actions_reduces_sequence() -> None:
    actions = ["open", "pricing", "signup", "faq", "back", "trial"]

    def bug_predicate(seq: list[str]) -> bool:
        return "open" in seq and "trial" in seq

    minimized = minimize_actions(actions, bug_predicate)

    assert minimized == ["open", "trial"]


def test_minimize_actions_returns_original_when_not_reproducible() -> None:
    actions = ["a1", "a2", "a3"]

    minimized = minimize_actions(actions, lambda _: False)

    assert minimized == actions
