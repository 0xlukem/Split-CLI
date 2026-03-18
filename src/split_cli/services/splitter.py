"""Core split calculations for the current equal-share release."""

from __future__ import annotations

from decimal import Decimal
from typing import Sequence

from split_cli.models import Event, EventReport, ParticipantBalance, Person, quantize_money


def amount_to_cents(value: Decimal) -> int:
    """Convert a Decimal amount to integer cents."""
    return int((quantize_money(value) * 100).to_integral_value())


def cents_to_amount(value: int) -> Decimal:
    """Convert integer cents back to a Decimal amount."""
    return quantize_money(Decimal(value) / Decimal("100"))


def compute_equal_shares(total: Decimal, participants: Sequence[Person]) -> dict[str, Decimal]:
    """Split the total equally, distributing remainder cents deterministically."""
    total_cents = amount_to_cents(total)
    base_share, remainder = divmod(total_cents, len(participants))

    shares: dict[str, Decimal] = {}
    for index, participant in enumerate(participants):
        participant_share = base_share + (1 if index < remainder else 0)
        shares[participant.name] = cents_to_amount(participant_share)
    return shares


def build_report(event: Event) -> EventReport:
    """Build the final report used by the CLI and JSON export."""
    paid_by_person = {participant.name: Decimal("0.00") for participant in event.participants}
    for expense in event.expenses:
        paid_by_person[expense.payer] += expense.amount

    total = quantize_money(sum((expense.amount for expense in event.expenses), Decimal("0.00")))
    shares = compute_equal_shares(total, event.participants)

    balances: list[ParticipantBalance] = []
    for participant in event.participants:
        paid = quantize_money(paid_by_person[participant.name])
        share = shares[participant.name]
        balance = quantize_money(paid - share)
        balances.append(
            ParticipantBalance(
                name=participant.name,
                paid=paid,
                share=share,
                balance=balance,
            )
        )

    average_share = quantize_money(total / Decimal(len(event.participants)))

    return EventReport(
        event_name=event.name,
        participant_count=len(event.participants),
        total_spent=total,
        average_share=average_share,
        balances=balances,
    )
