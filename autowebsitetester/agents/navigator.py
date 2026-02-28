from __future__ import annotations

from collections import deque
from urllib.parse import urljoin, urlparse

from playwright.async_api import Page

from autowebsitetester.algorithms.coverage_guided_exploration import (
    CandidateAction,
    CoverageGuidedNavigator,
    PageState,
)


class NavigatorAgent:
    def __init__(self, root_url: str, max_depth: int, max_pages: int) -> None:
        self.root_url = root_url
        self.max_depth = max_depth
        self.max_pages = max_pages
        self._root_domain = urlparse(root_url).netloc
        self.coverage = CoverageGuidedNavigator()

    async def bfs_discover(self, page: Page) -> list[str]:
        visited: set[str] = set()
        queued: set[str] = {self.root_url}
        queue: deque[tuple[str, int]] = deque([(self.root_url, 0)])
        ordered: list[str] = []

        while queue and len(visited) < self.max_pages:
            url, depth = queue.popleft()
            if url in visited or depth > self.max_depth:
                continue

            visited.add(url)
            ordered.append(url)
            await page.goto(url, wait_until="domcontentloaded")

            state = await self._capture_state(page, url)
            links = await page.eval_on_selector_all(
                "a[href]",
                "nodes => nodes.map(n => n.getAttribute('href')).filter(Boolean)",
            )
            candidates = self._build_candidates(url, links, state)

            while candidates:
                selected = self.coverage.select_next_action(state, candidates)
                if selected is None:
                    break
                parsed = urlparse(selected.target_url)
                if parsed.netloc == self._root_domain and selected.target_url not in visited:
                    if selected.target_url not in queued:
                        queue.append((selected.target_url, depth + 1))
                        queued.add(selected.target_url)
                candidates = [c for c in candidates if c.action_id != selected.action_id]

        return ordered

    async def _capture_state(self, page: Page, url: str) -> PageState:
        body_html = await page.inner_html("body")
        visible_text = (await page.inner_text("body"))[:2_000]
        endpoint_urls = await page.evaluate(
            """
            () => {
              const entries = performance.getEntriesByType('resource') || [];
              return entries.map(e => e.name);
            }
            """
        )
        return PageState(
            url=url,
            dom_structure=body_html,
            visible_text=visible_text,
            network_endpoints=set(endpoint_urls),
        )

    def _build_candidates(
        self,
        base_url: str,
        hrefs: list[str],
        state: PageState,
    ) -> list[CandidateAction]:
        candidates: list[CandidateAction] = []
        for href in hrefs:
            full = urljoin(base_url, href)
            parsed = urlparse(full)
            normalized = parsed._replace(fragment="").geturl()
            if parsed.netloc != self._root_domain:
                continue

            features = {
                f"path:{parsed.path}",
                f"query:{parsed.query}",
                f"state:{self.coverage.state_fingerprint(state)[:12]}",
            }
            candidates.append(
                CandidateAction(
                    action_id=f"navigate:{normalized}",
                    target_url=normalized,
                    features=features,
                )
            )
        return candidates
