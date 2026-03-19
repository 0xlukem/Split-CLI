from __future__ import annotations

import json
import re
from datetime import date, datetime
from pathlib import Path

from split_cli.models import EventReport

BACKUP_DIRECTORY = Path(".split-cli") / "backups"


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "split-report"


def build_backup_directory(home_dir: Path | None = None) -> Path:
    root_dir = home_dir or Path.home()
    return root_dir / BACKUP_DIRECTORY


def build_default_export_name(
    event_name: str,
    session_started_at: datetime | date | None = None,
) -> str:
    if session_started_at is None:
        session_date = datetime.now().astimezone().date()
    elif isinstance(session_started_at, datetime):
        session_date = session_started_at.date()
    else:
        session_date = session_started_at

    return f"{slugify(event_name)}-{session_date.isoformat()}"


def build_default_export_path(
    event_name: str,
    session_started_at: datetime | date | None = None,
    home_dir: Path | None = None,
) -> Path:
    backup_dir = build_backup_directory(home_dir)
    file_name = build_default_export_name(event_name, session_started_at)
    return backup_dir / f"{file_name}.json"


def build_export_path_from_name(file_name: str, backup_dir: Path, fallback_name: str) -> Path:
    cleaned_name = Path(file_name.strip()).name or fallback_name
    stem = cleaned_name[:-5] if cleaned_name.lower().endswith(".json") else cleaned_name
    stem = stem.strip() or fallback_name
    return backup_dir / f"{stem}.json"


def export_report_to_json(report: EventReport, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    payload = report.model_dump()
    destination.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, default=str),
        encoding="utf-8",
    )
    return destination
