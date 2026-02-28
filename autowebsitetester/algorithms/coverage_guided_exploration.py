from __future__ import annotations

import hashlib
import math
import random
from dataclasses import dataclass
from urllib.parse import urlparse, urlunparse


@dataclass(slots=True)
class PageState:
    url: str
    dom_structure: str
    visible_text: str
    network_endpoints: set[str]


@dataclass(slots=True)
class CandidateAction:
    action_id: str
    target_url: str
    features: set[str]


class CoverageGuidedNavigator:
    """Coverage-guided action chooser using novelty + UCB exploration bonus."""

    def __init__(self, epsilon: float = 0.1, ucb_c: float = 1.2) -> None:
        self.epsilon = epsilon
        self.ucb_c = ucb_c
        self.seen_features: set[str] = set()
        self.action_stats: dict[str, dict[str, float]] = {}
        self.total_steps: int = 0

    def state_fingerprint(self, state: PageState) -> str:
        normalized_url = self._normalize_url(state.url)
        dom_hash = hashlib.sha1(state.dom_structure.encode("utf-8")).hexdigest()
        text_hash = hashlib.sha1(state.visible_text.encode("utf-8")).hexdigest()
        endpoint_hash = hashlib.sha1(
            "|".join(sorted(state.network_endpoints)).encode("utf-8")
        ).hexdigest()
        raw = f"{normalized_url}:{dom_hash}:{text_hash}:{endpoint_hash}"
        return hashlib.sha1(raw.encode("utf-8")).hexdigest()

    def select_next_action(
        self,
        state: PageState,
        actions: list[CandidateAction],
    ) -> CandidateAction | None:
        """Select next action maximizing novelty and exploration."""
        if not actions:
            return None

        _ = self.state_fingerprint(state)

        if random.random() < self.epsilon:
            chosen = random.choice(actions)
            self._register(chosen, self._novelty(chosen.features))
            return chosen

        best = max(actions, key=self._score)
        self._register(best, self._novelty(best.features))
        return best

    def _score(self, action: CandidateAction) -> float:
        novelty = self._novelty(action.features)
        stats = self.action_stats.get(action.action_id, {"count": 0.0, "reward": 0.0})
        count = stats["count"]
        if count == 0:
            exploration_bonus = float("inf")
        else:
            exploration_bonus = self.ucb_c * math.sqrt(
                math.log(max(self.total_steps, 1) + 1) / count
            )
        if math.isinf(exploration_bonus):
            return 1_000_000 + novelty
        return novelty + exploration_bonus

    def _register(self, action: CandidateAction, reward: float) -> None:
        stats = self.action_stats.setdefault(action.action_id, {"count": 0.0, "reward": 0.0})
        stats["count"] += 1
        stats["reward"] += reward
        self.total_steps += 1
        self.seen_features.update(action.features)

    def _novelty(self, features: set[str]) -> float:
        if not features:
            return 0.0
        new_features = len(features - self.seen_features)
        return new_features / len(features)

    @staticmethod
    def _normalize_url(url: str) -> str:
        parsed = urlparse(url)
        query = "&".join(sorted(filter(None, parsed.query.split("&"))))
        normalized = parsed._replace(fragment="", query=query)
        return urlunparse(normalized)
