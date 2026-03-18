import json
from decimal import Decimal

from split_cli.models import Event, Expense, Person
from split_cli.services.analytics import build_insights
from split_cli.services.exporter import export_report_to_json
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
