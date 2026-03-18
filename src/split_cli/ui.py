"""Rich-based UI helpers for the interactive CLI."""

from __future__ import annotations

from decimal import Decimal
from typing import Sequence

import plotext as plt
from rich.align import Align
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.table import Table
from rich.text import Text

from split_cli.models import EventInsights, EventReport, Expense, Person, Transfer

console = Console()

BANNER = r"""
   _____       ___ __     _ __          ____
  / ___/____  / (_) /_   (_) /___  ____/ / /
  \__ \/ __ \/ / / __/  / / / __ \/ __  / /
 ___/ / /_/ / / / /_   / / / /_/ / /_/ /_/
/____/ .___/_/_/\__/  /_/_/\____/\__,_(_)
    /_/
"""


def format_money(value: Decimal) -> str:
    """Render a Decimal amount as currency."""
    return f"${value:,.2f}"


def show_welcome() -> None:
    """Render the ASCII intro panel."""
    console.print()
    banner_text = Text(BANNER.rstrip("\n"), style="bold bright_magenta")
    panel = Panel.fit(
        Align.center(banner_text),
        title="[bold bright_cyan]split-cli[/bold bright_cyan]",
        subtitle="alpha release",
        border_style="magenta",
        padding=(1, 3),
    )
    console.print(panel)
    console.print(
        Align.center(
            "[bright_cyan]Split shared expenses, review clean transfers, and explore the session dashboard.[/bright_cyan]"
        )
    )


def show_section(title: str) -> None:
    """Print a visual section divider."""
    console.rule(f"[bold bright_magenta]{title}")


def show_info(message: str) -> None:
    """Print an informational message."""
    console.print(f"[bright_cyan]• {message}[/bright_cyan]")


def show_success(message: str) -> None:
    """Print a success message."""
    console.print(f"[bold green]OK  {message}[/bold green]")


def show_error(message: str) -> None:
    """Print an error panel."""
    console.print(Panel(message, title="[bold red]Error[/bold red]", border_style="bright_red"))


def prompt_text(message: str, default: str | None = None, allow_blank: bool = False) -> str:
    """Ask for a text input and ensure it is valid."""
    while True:
        value = Prompt.ask(f"[bold bright_cyan]{message}[/bold bright_cyan]", default=default or "")
        if allow_blank:
            return value.strip()
        if value.strip():
            return value.strip()
        show_error("This field cannot be empty.")


def prompt_optional_text(message: str) -> str | None:
    """Ask for an optional text input."""
    value = Prompt.ask(f"[bold bright_cyan]{message}[/bold bright_cyan]", default="")
    cleaned = value.strip()
    return cleaned or None


def prompt_participant_count() -> int:
    """Ask for the participant count."""
    while True:
        count = IntPrompt.ask("[bold bright_cyan]How many people are joining?[/bold bright_cyan]")
        if count >= 2:
            return count
        show_error("You need at least 2 participants to split expenses.")


def prompt_amount(message: str) -> str:
    """Ask for a raw amount string to be validated by Pydantic."""
    while True:
        value = Prompt.ask(f"[bold bright_cyan]{message}[/bold bright_cyan]")
        cleaned = value.strip().replace(",", ".")
        if cleaned:
            return cleaned
        show_error("Enter a valid amount.")


def prompt_person_choice(message: str, people: Sequence[Person]) -> Person:
    """Select a participant by index."""
    table = Table(title="Participants", header_style="bold bright_cyan")
    table.add_column("#", justify="right", style="bright_black")
    table.add_column("Name", style="bold white")
    for index, person in enumerate(people, start=1):
        table.add_row(str(index), person.name)
    console.print(table)

    while True:
        choice = IntPrompt.ask(f"[bold bright_cyan]{message}[/bold bright_cyan]")
        if 1 <= choice <= len(people):
            return people[choice - 1]
        show_error("Choose a number from the list.")


def show_people_table(people: Sequence[Person]) -> None:
    """Render the participants table."""
    if not people:
        return

    table = Table(title="Participants added", header_style="bold bright_cyan")
    table.add_column("#", justify="right", style="bright_black")
    table.add_column("Name", style="bold white")

    for index, person in enumerate(people, start=1):
        table.add_row(str(index), person.name)

    console.print(table)


def show_expenses_table(expenses: Sequence[Expense]) -> None:
    """Render the expenses table."""
    if not expenses:
        return

    table = Table(title="Expenses added", header_style="bold bright_cyan")
    table.add_column("#", justify="right", style="bright_black")
    table.add_column("Paid by", style="bold white")
    table.add_column("Amount", justify="right", style="green")
    table.add_column("Description", style="white")

    for index, expense in enumerate(expenses, start=1):
        table.add_row(
            str(index),
            expense.payer,
            format_money(expense.amount),
            expense.description or "Untitled expense",
        )

    console.print(table)


def build_chart_text(title: str, labels: Sequence[str], values: Sequence[Decimal]) -> Text:
    """Build a chart as ANSI text using plotext."""
    if not labels:
        return Text("No chart data available.", style="dim")

    width = max(70, min(console.width - 10, 120))
    height = max(14, min(len(labels) + 8, 28))
    numeric_values = [float(value) for value in values]

    plt.clear_figure()
    plt.theme("pro")
    plt.plotsize(width, height)
    plt.title(title)
    plt.bar(labels, numeric_values, orientation="horizontal")
    plt.build()
    chart = plt.build()
    plt.clear_figure()
    return Text.from_ansi(chart)


def show_chart_panel(title: str, labels: Sequence[str], values: Sequence[Decimal]) -> None:
    """Render a chart inside a Rich panel."""
    console.print(
        Panel(
            build_chart_text(title, labels, values),
            title=title,
            border_style="bright_magenta",
            padding=(1, 2),
        )
    )


def show_final_report(report: EventReport) -> None:
    """Render the final summary, balances, settlements, and expense chart."""
    show_section(f"Session summary: {report.event_name}")

    summary = Table(show_header=False, box=None, pad_edge=False)
    summary.add_column(style="bold bright_cyan")
    summary.add_column(style="white")
    summary.add_row("Participants", str(report.participant_count))
    summary.add_row("Total spent", format_money(report.total_spent))
    summary.add_row("Fair share", format_money(report.average_share))
    console.print(Panel(summary, title="Snapshot", border_style="bright_cyan"))

    balances_table = Table(title="Balances", header_style="bold bright_cyan")
    balances_table.add_column("Person", style="bold white")
    balances_table.add_column("Paid", justify="right", style="green")
    balances_table.add_column("Share", justify="right", style="yellow")
    balances_table.add_column("Balance", justify="right")
    balances_table.add_column("Status", style="white")

    for balance in report.balances:
        status = "Gets back" if balance.balance > 0 else "Pays" if balance.balance < 0 else "Settled"
        balance_style = (
            "green" if balance.balance > 0 else "red" if balance.balance < 0 else "bright_black"
        )
        balances_table.add_row(
            balance.name,
            format_money(balance.paid),
            format_money(balance.share),
            f"[{balance_style}]{format_money(balance.balance)}[/{balance_style}]",
            status,
        )

    console.print(balances_table)
    show_transfers(report.transfers)
    if report.insights is not None:
        show_chart_panel(
            "Expense breakdown",
            [item.label for item in report.insights.expense_breakdown],
            [item.amount for item in report.insights.expense_breakdown],
        )


def show_transfers(transfers: Sequence[Transfer]) -> None:
    """Render the simplified transfers."""
    if not transfers:
        show_success("No transfers are needed. Everyone is already settled.")
        return

    transfers_table = Table(title="Suggested transfers", header_style="bold bright_cyan")
    transfers_table.add_column("#", justify="right", style="bright_black")
    transfers_table.add_column("From", style="bold white")
    transfers_table.add_column("To", style="bold white")
    transfers_table.add_column("Amount", justify="right", style="green")

    for index, transfer in enumerate(transfers, start=1):
        transfers_table.add_row(
            str(index),
            transfer.from_person,
            transfer.to_person,
            format_money(transfer.amount),
        )

    console.print(transfers_table)


def show_detailed_insights(insights: EventInsights) -> None:
    """Render the optional deep-dive analytics view."""
    show_section("Deep dive insights")

    stat_panels = [
        Panel(
            f"[bold white]{insights.top_spender.name}[/bold white]\n[green]{format_money(insights.top_spender.amount_paid)}[/green]",
            title="Top spender",
            border_style="green",
        ),
        Panel(
            f"[bold white]{insights.lowest_spender.name}[/bold white]\n[yellow]{format_money(insights.lowest_spender.amount_paid)}[/yellow]",
            title="Lowest spender",
            border_style="yellow",
        ),
        Panel(
            (
                f"[bold white]{insights.most_expensive_expense.label}[/bold white]\n"
                f"[magenta]{format_money(insights.most_expensive_expense.amount)}[/magenta]"
            ),
            title="Most expensive expense",
            border_style="magenta",
        ),
    ]
    console.print(Columns(stat_panels, equal=True, expand=True))
    show_chart_panel(
        "Paid by participant",
        [item.payer for item in insights.payer_breakdown],
        [item.amount for item in insights.payer_breakdown],
    )
