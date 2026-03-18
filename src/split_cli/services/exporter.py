"""Export helpers for split-cli reports."""

from __future__ import annotations

import json
import re
from pathlib import Path

from split_cli.models import EventReport


def slugify(value: str) -> str:
    """Convert an event name to a file-safe slug."""
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "split-report"


def build_default_export_path(event_name: str, base_dir: Path | None = None) -> Path:
    """Build a sensible default path for JSON export."""
    target_dir = base_dir or Path.cwd()
    return target_dir / f"{slugify(event_name)}.json"


def export_report_to_json(report: EventReport, destination: Path) -> Path:
    """Write the final report to a JSON file."""
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = report.model_dump()
    destination.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    return destination
