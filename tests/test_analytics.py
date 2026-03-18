from decimal import Decimal

from split_cli.models import Event, Expense, Person
from split_cli.services.analytics import build_insights
from split_cli.services.splitter import build_report


def test_build_insights_returns_expected_highlights() -> None:
    event = Event(
        name="Weekend trip",
        participants=[
            Person(name="Alice"),
            Person(name="Ben"),
            Person(name="Cara"),
        ],
        expenses=[
            Expense(payer="Ben", amount="30", description="Snacks"),
            Expense(payer="Alice", amount="90", description="Cabin"),
            Expense(payer="Alice", amount="20"),
        ],
    )

    report = build_report(event)
    insights = build_insights(event, report)

    assert insights.top_spender.name == "Alice"
    assert insights.top_spender.amount_paid == Decimal("110.00")
    assert insights.lowest_spender.name == "Cara"
    assert insights.lowest_spender.amount_paid == Decimal("0.00")
    assert insights.most_expensive_expense.label == "Cabin - paid by Alice"
    assert insights.most_expensive_expense.amount == Decimal("90.00")
    assert insights.expense_breakdown[2].label == "Untitled expense - paid by Alice"
    assert [(item.payer, item.amount) for item in insights.payer_breakdown] == [
        ("Alice", Decimal("110.00")),
        ("Ben", Decimal("30.00")),
        ("Cara", Decimal("0.00")),
    ]


def test_build_insights_uses_deterministic_tie_breakers() -> None:
    event = Event(
        name="Lunch",
        participants=[
            Person(name="Alice"),
            Person(name="Ben"),
            Person(name="Cara"),
            Person(name="Drew"),
        ],
        expenses=[
            Expense(payer="Ben", amount="20", description="Pasta"),
            Expense(payer="Alice", amount="20", description="Pizza"),
        ],
    )

    report = build_report(event)
    insights = build_insights(event, report)

    assert insights.top_spender.name == "Alice"
    assert insights.lowest_spender.name == "Cara"
    assert insights.most_expensive_expense.label == "Pasta - paid by Ben"


def test_build_expense_breakdown_aggregates_remainder_after_top_twelve() -> None:
    event = Event(
        name="Long weekend",
        participants=[
            Person(name="Alice"),
            Person(name="Ben"),
        ],
        expenses=[
            Expense(
                payer="Alice" if index % 2 == 0 else "Ben",
                amount=str(100 - index),
                description=f"Expense {index}",
            )
            for index in range(14)
        ],
    )

    report = build_report(event)
    insights = build_insights(event, report)

    assert len(insights.expense_breakdown) == 13
    assert insights.expense_breakdown[-1].label == "Other expenses"
    assert insights.expense_breakdown[-1].amount == Decimal("175.00")
