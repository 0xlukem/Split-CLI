"""Typer entrypoint for the split CLI."""

from __future__ import annotations

from pathlib import Path

import typer
from pydantic import ValidationError
from rich.prompt import Confirm

from split_cli.models import Event, EventReport, Expense, Person
from split_cli.services.analytics import build_insights
from split_cli.services.exporter import build_default_export_path, export_report_to_json
from split_cli.services.settlements import build_settlements
from split_cli.services.splitter import build_report
from split_cli.ui import (
    console,
    prompt_amount,
    prompt_optional_text,
    prompt_participant_count,
    prompt_person_choice,
    prompt_text,
    show_error,
    show_detailed_insights,
    show_expenses_table,
    show_final_report,
    show_info,
    show_people_table,
    show_section,
    show_success,
    show_welcome,
)

app = typer.Typer(
    add_completion=False,
    help="Interactive terminal app for splitting group expenses.",
    no_args_is_help=False,
)


def collect_people(participant_count: int) -> list[Person]:
    """Collect participants interactively."""
    participants: list[Person] = []
    seen_names: set[str] = set()

    show_section("Participants")
    for index in range(1, participant_count + 1):
        while True:
            name = prompt_text(f"Participant name #{index}")

            try:
                participant = Person(name=name)
            except ValidationError as error:
                show_error(error.errors()[0]["msg"])
                continue

            normalized_name = participant.name.casefold()
            if normalized_name in seen_names:
                show_error("Each participant must have a unique name.")
                continue

            participants.append(participant)
            seen_names.add(normalized_name)
            show_people_table(participants)
            break

    return participants


def collect_expenses(participants: list[Person]) -> list[Expense]:
    """Collect expenses interactively."""
    expenses: list[Expense] = []
    expense_number = 1

    show_section("Expenses")
    show_info("Add at least one expense. You can keep adding more one by one.")

    while True:
        show_info(f"Expense #{expense_number}")
        payer = prompt_person_choice("Who paid for this expense? Pick a number", participants)
        amount = prompt_amount("Amount")
        description = prompt_optional_text("Description (optional)")

        try:
            expense = Expense(payer=payer.name, amount=amount, description=description)
        except ValidationError as error:
            show_error(error.errors()[0]["msg"])
            continue

        expenses.append(expense)
        show_expenses_table(expenses)
        expense_number += 1

        if not Confirm.ask("[bold bright_cyan]Do you want to add another expense?[/bold bright_cyan]", default=True):
            return expenses


def maybe_export_report(report: EventReport, export_json: Path | None) -> None:
    """Prompt the user to export the final report when needed."""
    destination = export_json
    if destination is None:
        if not Confirm.ask("[bold bright_cyan]Do you want to export this session to JSON?[/bold bright_cyan]"):
            return

        suggested_path = build_default_export_path(report.event_name)
        raw_path = prompt_text("JSON output path", default=str(suggested_path))
        destination = Path(raw_path).expanduser()

    exported_file = export_report_to_json(report, destination)
    show_success(f"Session exported to {exported_file}")


def run_interactive(export_json: Path | None = None) -> None:
    """Execute the full interactive flow."""
    show_welcome()
    show_section("Session setup")

    event_name = prompt_text("Event name")
    participant_count = prompt_participant_count()
    participants = collect_people(participant_count)
    expenses = collect_expenses(participants)

    try:
        event = Event(name=event_name, participants=participants, expenses=expenses)
    except ValidationError as error:
        show_error(error.errors()[0]["msg"])
        raise typer.Exit(code=1) from error

    report = build_report(event)
    full_report = report.model_copy(
        update={
            "transfers": build_settlements(report.balances),
            "insights": build_insights(event, report),
        }
    )

    show_final_report(full_report)
    if full_report.insights is not None and Confirm.ask(
        "[bold bright_cyan]Do you want more info about this split?[/bold bright_cyan]",
        default=False,
    ):
        show_detailed_insights(full_report.insights)
    maybe_export_report(full_report, export_json)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    export_json: Path | None = typer.Option(
        None,
        "--export-json",
        "-o",
        help="Write the final session report to a JSON file.",
    ),
) -> None:
    """Run the interactive expense splitter."""
    if ctx.invoked_subcommand is not None:
        return

    try:
        run_interactive(export_json=export_json)
    except (KeyboardInterrupt, EOFError):
        console.print()
        show_error("Session cancelled by user.")
        raise typer.Exit(code=130) from None


if __name__ == "__main__":
    app()
