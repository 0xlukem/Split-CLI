from __future__ import annotations

from split_cli.models import ParticipantBalance, Transfer
from split_cli.services.splitter import amount_to_cents, cents_to_amount


def build_settlements(balances: list[ParticipantBalance]) -> list[Transfer]:
    """Generate a deterministic, minimal transfer plan from participant balances."""
    creditors = [
        [balance.name, amount_to_cents(balance.balance)]
        for balance in balances
        if amount_to_cents(balance.balance) > 0
    ]
    debtors = [
        [balance.name, abs(amount_to_cents(balance.balance))]
        for balance in balances
        if amount_to_cents(balance.balance) < 0
    ]

    creditors.sort(key=lambda item: (-item[1], item[0]))
    debtors.sort(key=lambda item: (-item[1], item[0]))

    transfers: list[Transfer] = []
    debtor_index = 0
    creditor_index = 0

    while debtor_index < len(debtors) and creditor_index < len(creditors):
        debtor_name, debt_amount = debtors[debtor_index]
        creditor_name, credit_amount = creditors[creditor_index]
        settled_amount = min(debt_amount, credit_amount)

        transfers.append(
            Transfer(
                from_person=debtor_name,
                to_person=creditor_name,
                amount=cents_to_amount(settled_amount),
            )
        )

        debtors[debtor_index][1] -= settled_amount
        creditors[creditor_index][1] -= settled_amount

        if debtors[debtor_index][1] == 0:
            debtor_index += 1
        if creditors[creditor_index][1] == 0:
            creditor_index += 1

    return transfers
