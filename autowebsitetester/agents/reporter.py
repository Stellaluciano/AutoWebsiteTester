from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from autowebsitetester.report.render_html import render_html
from autowebsitetester.report.render_md import render_markdown
from autowebsitetester.types import ScanResult


class ReporterAgent:
    def write_reports(self, result: ScanResult) -> None:
        out_dir = result.output_dir
        out_dir.mkdir(parents=True, exist_ok=True)

        md_report = render_markdown(result)
        html_report = render_html(result)

        (out_dir / "report.md").write_text(md_report, encoding="utf-8")
        (out_dir / "report.html").write_text(html_report, encoding="utf-8")

        payload = asdict(result)
        payload["output_dir"] = str(result.output_dir)
        payload["started_at"] = result.started_at.isoformat()
        payload["finished_at"] = result.finished_at.isoformat()
        (out_dir / "results.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
