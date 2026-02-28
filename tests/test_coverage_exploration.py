from autowebsitetester.algorithms.coverage_guided_exploration import (
    CandidateAction,
    CoverageGuidedNavigator,
    PageState,
)


def test_select_next_action_prefers_novelty() -> None:
    nav = CoverageGuidedNavigator(epsilon=0.0)
    state = PageState(
        url="https://example.com",
        dom_structure="<main><a href='/a'>A</a></main>",
        visible_text="hello world",
        network_endpoints={"https://example.com/api/home"},
    )

    low_novelty = CandidateAction(
        action_id="a",
        target_url="https://example.com/a",
        features={"path:/a", "query:"},
    )
    high_novelty = CandidateAction(
        action_id="b",
        target_url="https://example.com/b",
        features={"path:/b", "query:q=1", "new:state"},
    )

    nav.seen_features.update({"path:/a", "query:"})
    selected = nav.select_next_action(state, [low_novelty, high_novelty])

    assert selected is not None
    assert selected.action_id == "b"


def test_state_fingerprint_normalizes_url_query_order() -> None:
    nav = CoverageGuidedNavigator()
    s1 = PageState(
        url="https://example.com/path?b=2&a=1#frag",
        dom_structure="<div>dom</div>",
        visible_text="txt",
        network_endpoints={"/api/a"},
    )
    s2 = PageState(
        url="https://example.com/path?a=1&b=2",
        dom_structure="<div>dom</div>",
        visible_text="txt",
        network_endpoints={"/api/a"},
    )

    assert nav.state_fingerprint(s1) == nav.state_fingerprint(s2)
