from decimal import Decimal

from split_cli.models import ParticipantBalance
from split_cli.services.settlements import build_settlements


def test_build_settlements_for_single_creditor() -> None:
    balances = [
        ParticipantBalance(
            name="Alice",
            paid=Decimal("90.00"),
            share=Decimal("40.00"),
            balance=Decimal("50.00"),
        ),
        ParticipantBalance(
            name="Ben",
            paid=Decimal("30.00"),
            share=Decimal("40.00"),
            balance=Decimal("-10.00"),
        ),
        ParticipantBalance(
            name="Cara",
            paid=Decimal("0.00"),
            share=Decimal("40.00"),
            balance=Decimal("-40.00"),
        ),
    ]

    transfers = build_settlements(balances)

    assert [(item.from_person, item.to_person, item.amount) for item in transfers] == [
        ("Cara", "Alice", Decimal("40.00")),
        ("Ben", "Alice", Decimal("10.00")),
    ]


def test_build_settlements_for_multiple_creditors() -> None:
    balances = [
        ParticipantBalance(
            name="Alice",
            paid=Decimal("80.00"),
            share=Decimal("40.00"),
            balance=Decimal("40.00"),
        ),
        ParticipantBalance(
            name="Ben",
            paid=Decimal("50.00"),
            share=Decimal("40.00"),
            balance=Decimal("10.00"),
        ),
        ParticipantBalance(
            name="Cara",
            paid=Decimal("20.00"),
            share=Decimal("40.00"),
            balance=Decimal("-20.00"),
        ),
        ParticipantBalance(
            name="Dana",
            paid=Decimal("10.00"),
            share=Decimal("40.00"),
            balance=Decimal("-30.00"),
        ),
    ]

    transfers = build_settlements(balances)

    assert [(item.from_person, item.to_person, item.amount) for item in transfers] == [
        ("Dana", "Alice", Decimal("30.00")),
        ("Cara", "Alice", Decimal("10.00")),
        ("Cara", "Ben", Decimal("10.00")),
    ]
