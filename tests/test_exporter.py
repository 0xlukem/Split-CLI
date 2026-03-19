import json
from datetime import date
from decimal import Decimal

from split_cli.models import Event, Expense, Person
from split_cli.services.analytics import build_insights
from split_cli.services.exporter import (
    build_default_export_path,
    build_export_path_from_name,
    export_report_to_json,
)
from split_cli.services.settlements import build_settlements
from split_cli.services.splitter import build_report


def test_export_report_to_json_includes_insights(tmp_path) -> None:
    event = Event(
        name="Weekend trip",
        participants=[Person(name="Alice"), Person(name="Ben")],
        expenses=[Expense(payer="Alice", amount="42", description="Museum tickets")],
    )
    report = build_report(event).model_copy(
        update={
            "transfers": build_settlements(build_report(event).balances),
            "insights": build_insights(event, build_report(event)),
        }
    )

    destination = export_report_to_json(report, tmp_path / "report.json")
    payload = json.loads(destination.read_text(encoding="utf-8"))

    assert payload["event_name"] == "Weekend trip"
    assert payload["insights"]["top_spender"]["name"] == "Alice"
    assert payload["insights"]["most_expensive_expense"]["amount"] == "42.00"
    assert payload["balances"][0]["share"] == "21.00"


def test_build_default_export_path_uses_backup_folder_and_session_date(tmp_path) -> None:
    destination = build_default_export_path(
        "Asado",
        session_started_at=date(2026, 3, 19),
        home_dir=tmp_path,
    )

    assert destination == tmp_path / ".splitty-cli" / "backups" / "asado-2026-03-19.json"


def test_build_export_path_from_name_keeps_backup_folder(tmp_path) -> None:
    backup_dir = tmp_path / ".splitty-cli" / "backups"

    destination = build_export_path_from_name("reports/hola", backup_dir, "asado-2026-03-19")

    assert destination == backup_dir / "hola.json"
