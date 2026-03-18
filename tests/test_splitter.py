from decimal import Decimal

import pytest

from split_cli.models import Event, Expense, Person
from split_cli.services.splitter import build_report


def test_build_report_for_equal_split_event() -> None:
    event = Event(
        name="Dinner",
        participants=[
            Person(name="Alice"),
            Person(name="Ben"),
            Person(name="Cara"),
        ],
        expenses=[
            Expense(payer="Alice", amount="90"),
            Expense(payer="Ben", amount="30"),
        ],
    )

    report = build_report(event)

    assert report.total_spent == Decimal("120.00")
    assert report.average_share == Decimal("40.00")
    assert [(item.name, item.paid, item.share, item.balance) for item in report.balances] == [
        ("Alice", Decimal("90.00"), Decimal("40.00"), Decimal("50.00")),
        ("Ben", Decimal("30.00"), Decimal("40.00"), Decimal("-10.00")),
        ("Cara", Decimal("0.00"), Decimal("40.00"), Decimal("-40.00")),
    ]


def test_build_report_distributes_remainder_cents() -> None:
    event = Event(
        name="Cab",
        participants=[
            Person(name="Alice"),
            Person(name="Ben"),
            Person(name="Cara"),
        ],
        expenses=[
            Expense(payer="Alice", amount="10"),
        ],
    )

    report = build_report(event)

    assert [item.share for item in report.balances] == [
        Decimal("3.34"),
        Decimal("3.33"),
        Decimal("3.33"),
    ]
    assert sum((item.balance for item in report.balances), Decimal("0.00")) == Decimal("0.00")


def test_event_rejects_duplicate_participants() -> None:
    with pytest.raises(ValueError, match="Duplicate participant name"):
        Event(
            name="Night out",
            participants=[Person(name="Alice"), Person(name="alice")],
            expenses=[Expense(payer="Alice", amount="10")],
        )
