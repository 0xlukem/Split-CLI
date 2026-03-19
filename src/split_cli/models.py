from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP

from pydantic import BaseModel, Field, field_validator, model_validator

CENTS = Decimal("0.01")


def quantize_money(value: Decimal | str | int | float) -> Decimal:
    """Normalize a numeric value into currency precision."""
    return Decimal(str(value)).quantize(CENTS, rounding=ROUND_HALF_UP)


class Person(BaseModel):
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Name cannot be empty.")
        return cleaned


class Expense(BaseModel):
    payer: str
    amount: Decimal
    description: str | None = None

    @field_validator("payer")
    @classmethod
    def validate_payer(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Payer cannot be empty.")
        return cleaned

    @field_validator("amount", mode="before")
    @classmethod
    def validate_amount(cls, value: Decimal | str | int | float) -> Decimal:
        amount = quantize_money(value)
        if amount <= Decimal("0"):
            raise ValueError("Amount must be greater than zero.")
        return amount

    @field_validator("description")
    @classmethod
    def validate_description(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = value.strip()
        return cleaned or None


class Event(BaseModel):
    name: str
    participants: list[Person]
    expenses: list[Expense] = Field(default_factory=list)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Event name cannot be empty.")
        return cleaned

    @field_validator("participants")
    @classmethod
    def validate_participants(cls, participants: list[Person]) -> list[Person]:
        if len(participants) < 2:
            raise ValueError("At least two participants are required.")

        seen: set[str] = set()
        for participant in participants:
            normalized = participant.name.casefold()
            if normalized in seen:
                raise ValueError(f"Duplicate participant name: {participant.name}")
            seen.add(normalized)
        return participants

    @model_validator(mode="after")
    def validate_expenses(self) -> "Event":
        if not self.expenses:
            raise ValueError("At least one expense is required.")

        valid_names = {participant.name for participant in self.participants}
        invalid_payers = sorted(
            {expense.payer for expense in self.expenses if expense.payer not in valid_names}
        )
        if invalid_payers:
            raise ValueError(
                "Every expense payer must be one of the participants: "
                + ", ".join(invalid_payers)
            )
        return self


class ParticipantBalance(BaseModel):
    name: str
    paid: Decimal
    share: Decimal
    balance: Decimal


class Transfer(BaseModel):
    from_person: str
    to_person: str
    amount: Decimal


class ParticipantSpendingStat(BaseModel):
    name: str
    amount_paid: Decimal


class ExpenseBreakdownItem(BaseModel):
    label: str
    payer: str
    amount: Decimal
    description: str | None = None


class PayerBreakdownItem(BaseModel):
    payer: str
    amount: Decimal


class ExpenseHighlight(BaseModel):
    label: str
    payer: str
    amount: Decimal
    description: str | None = None


class EventInsights(BaseModel):
    top_spender: ParticipantSpendingStat
    lowest_spender: ParticipantSpendingStat
    most_expensive_expense: ExpenseHighlight
    expense_breakdown: list[ExpenseBreakdownItem]
    payer_breakdown: list[PayerBreakdownItem]


class EventReport(BaseModel):
    event_name: str
    participant_count: int
    total_spent: Decimal
    average_share: Decimal
    balances: list[ParticipantBalance]
    transfers: list[Transfer] = Field(default_factory=list)
    insights: EventInsights | None = None
