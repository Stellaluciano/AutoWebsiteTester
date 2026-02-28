from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class ScanConfig:
    root_url: str
    depth: int = 3
    max_pages: int = 50
    headless: bool = True
    ai_analysis: bool = False
    output_dir: Path = Path("report")
    timeout_ms: int = 10_000

    @classmethod
    def from_cli(
        cls,
        root_url: str,
        depth: int,
        max_pages: int,
        headless: bool,
        ai_analysis: bool,
        out: str,
    ) -> "ScanConfig":
        return cls(
            root_url=root_url,
            depth=depth,
            max_pages=max_pages,
            headless=headless,
            ai_analysis=ai_analysis,
            output_dir=Path(out),
        )
