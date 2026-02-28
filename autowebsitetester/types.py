from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any


class Severity(str, Enum):
    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


@dataclass(slots=True)
class ActionRecord:
    page_url: str
    action_type: str
    target: str
    detail: str | None = None


@dataclass(slots=True)
class FailureEvidence:
    screenshot: str | None = None
    html_snapshot: str | None = None
    console_logs: list[str] = field(default_factory=list)
    network_summary: list[dict[str, Any]] = field(default_factory=list)


@dataclass(slots=True)
class Failure:
    title: str
    message: str
    page_url: str
    category: str
    stack_trace: str | None = None
    reproduction_steps: list[str] = field(default_factory=list)
    evidence: FailureEvidence = field(default_factory=FailureEvidence)
    severity: Severity = Severity.P2
    debugging_hints: list[str] = field(default_factory=list)


@dataclass(slots=True)
class ScanResult:
    root_url: str
    visited_urls: list[str]
    actions: list[ActionRecord]
    failures: list[Failure]
    started_at: datetime
    finished_at: datetime
    output_dir: Path
