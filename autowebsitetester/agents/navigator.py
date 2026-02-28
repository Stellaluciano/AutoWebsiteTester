from __future__ import annotations

from collections import deque
from urllib.parse import urljoin, urlparse

from playwright.async_api import Page


class NavigatorAgent:
    def __init__(self, root_url: str, max_depth: int, max_pages: int) -> None:
        self.root_url = root_url
        self.max_depth = max_depth
        self.max_pages = max_pages
        self._root_domain = urlparse(root_url).netloc

    async def bfs_discover(self, page: Page) -> list[str]:
        visited: set[str] = set()
        queue: deque[tuple[str, int]] = deque([(self.root_url, 0)])
        ordered: list[str] = []

        while queue and len(visited) < self.max_pages:
            url, depth = queue.popleft()
            if url in visited or depth > self.max_depth:
                continue

            visited.add(url)
            ordered.append(url)
            await page.goto(url, wait_until="domcontentloaded")

            links = await page.eval_on_selector_all(
                "a[href]",
                "nodes => nodes.map(n => n.getAttribute('href')).filter(Boolean)",
            )
            for href in links:
                full = urljoin(url, href)
                parsed = urlparse(full)
                if parsed.netloc != self._root_domain:
                    continue
                normalized = parsed._replace(fragment="").geturl()
                if normalized not in visited:
                    queue.append((normalized, depth + 1))

        return ordered
