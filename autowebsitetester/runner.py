from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from autowebsitetester.agents.executor import ExecutorAgent
from autowebsitetester.agents.navigator import NavigatorAgent
from autowebsitetester.agents.oracle import OracleAgent
from autowebsitetester.agents.reporter import ReporterAgent
from autowebsitetester.agents.triage import TriageAgent
from autowebsitetester.browser.session import browser_session
from autowebsitetester.browser.snapshot import save_snapshot
from autowebsitetester.config import ScanConfig
from autowebsitetester.types import FailureEvidence, ScanResult


class ScanRunner:
    def __init__(self, config: ScanConfig) -> None:
        self.config = config
        self.navigator = NavigatorAgent(config.root_url, config.depth, config.max_pages)
        self.executor = ExecutorAgent()
        self.oracle = OracleAgent()
        self.triage = TriageAgent()
        self.reporter = ReporterAgent()

    async def run(self) -> ScanResult:
        started_at = datetime.now(tz=timezone.utc)

        actions = []
        failures = []
        artifacts_dir = self.config.output_dir / "artifacts"

        async with browser_session(headless=self.config.headless) as (_, page):
            self.oracle.attach(page)
            visited_urls = await self.navigator.bfs_discover(page)

            for idx, url in enumerate(visited_urls):
                await page.goto(url, wait_until="domcontentloaded")
                actions.extend(await self.executor.execute(page, page_url=url))
                local_failures = await self.oracle.inspect(page, url)

                if local_failures:
                    slug = f"page_{idx}"
                    screenshot, html = await save_snapshot(page, artifacts_dir, slug)
                    for bug in local_failures:
                        bug.evidence = FailureEvidence(
                            screenshot=str(Path(screenshot).relative_to(self.config.output_dir)),
                            html_snapshot=str(Path(html).relative_to(self.config.output_dir)),
                            console_logs=self.oracle.state.console_logs[-20:],
                            network_summary=self.oracle.state.network_events[-30:],
                        )
                        if not bug.reproduction_steps:
                            bug.reproduction_steps = [
                                f"Run autowebsitetester scan {self.config.root_url}",
                                f"Navigate to {url}",
                            ]
                    failures.extend(local_failures)

        triaged = self.triage.group_failures(
            failures,
            actions=actions,
            predicate_builder=lambda bug: self.executor.build_bug_predicate(bug.page_url, bug.message),
        )
        finished_at = datetime.now(tz=timezone.utc)
        result = ScanResult(
            root_url=self.config.root_url,
            visited_urls=visited_urls,
            actions=actions,
            failures=triaged,
            started_at=started_at,
            finished_at=finished_at,
            output_dir=self.config.output_dir,
        )
        self.reporter.write_reports(result)
        return result
