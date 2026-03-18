"""Analytics helpers for end-of-session reporting."""

from __future__ import annotations

from decimal import Decimal

from split_cli.models import (
    Event,
    EventInsights,
    EventReport,
    Expense,
    ExpenseBreakdownItem,
    ExpenseHighlight,
    ParticipantSpendingStat,
    PayerBreakdownItem,
    quantize_money,
)

MAX_EXPENSE_BREAKDOWN_ITEMS = 12


def expense_title(expense: Expense) -> str:
    """Return a user-facing expense title."""
    return expense.description or "Untitled expense"


def expense_label(expense: Expense) -> str:
    """Return the chart label used for a single expense."""
    return f"{expense_title(expense)} - paid by {expense.payer}"


def build_expense_breakdown(expenses: list[Expense]) -> list[ExpenseBreakdownItem]:
    """Return chart-ready expense rows sorted by descending amount."""
    indexed_expenses = sorted(
        enumerate(expenses),
        key=lambda item: (-item[1].amount, item[0]),
    )
    breakdown = [
        ExpenseBreakdownItem(
            label=expense_label(expense),
            payer=expense.payer,
            amount=expense.amount,
            description=expense.description,
        )
        for _, expense in indexed_expenses
    ]

    if len(breakdown) <= MAX_EXPENSE_BREAKDOWN_ITEMS:
        return breakdown

    remainder_total = quantize_money(
        sum((item.amount for item in breakdown[MAX_EXPENSE_BREAKDOWN_ITEMS:]), Decimal("0.00"))
    )
    return breakdown[:MAX_EXPENSE_BREAKDOWN_ITEMS] + [
        ExpenseBreakdownItem(
            label="Other expenses",
            payer="Multiple",
            amount=remainder_total,
            description=None,
        )
    ]


def build_payer_breakdown(report: EventReport) -> list[PayerBreakdownItem]:
    """Return total paid by participant, sorted by amount and name."""
    sorted_balances = sorted(report.balances, key=lambda item: (-item.paid, item.name))
    return [
        PayerBreakdownItem(payer=balance.name, amount=balance.paid)
        for balance in sorted_balances
    ]


def build_insights(event: Event, report: EventReport) -> EventInsights:
    """Compute the analytics shown after the main split summary."""
    top_spender = sorted(report.balances, key=lambda item: (-item.paid, item.name))[0]
    lowest_spender = sorted(report.balances, key=lambda item: (item.paid, item.name))[0]
    largest_expense = max(event.expenses, key=lambda expense: expense.amount)

    return EventInsights(
        top_spender=ParticipantSpendingStat(
            name=top_spender.name,
            amount_paid=top_spender.paid,
        ),
        lowest_spender=ParticipantSpendingStat(
            name=lowest_spender.name,
            amount_paid=lowest_spender.paid,
        ),
        most_expensive_expense=ExpenseHighlight(
            label=expense_label(largest_expense),
            payer=largest_expense.payer,
            amount=largest_expense.amount,
            description=largest_expense.description,
        ),
        expense_breakdown=build_expense_breakdown(event.expenses),
        payer_breakdown=build_payer_breakdown(report),
    )
