from __future__ import annotations

import os
import time
from decimal import Decimal
from typing import Sequence

import plotext as plt
from rich.columns import Columns
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.prompt import IntPrompt, Prompt
from rich.table import Table
from rich.text import Text

from split_cli.intro import show_intro
from split_cli.models import EventInsights, EventReport, Expense, Person, Transfer

console = Console()

CHART_ANIMATION_FRAMES = 14
CHART_ANIMATION_DELAY_SECONDS = 0.045

TROPHY_ASCII = "[#1]"
DOLLAR_ASCII = "[$]"


def format_money(value: Decimal) -> str:
    return f"${value:,.2f}"


def show_welcome(animations: bool = True) -> None:
    show_intro(console, animations=animations)


def show_section(title: str) -> None:
    console.rule(f"[bold bright_magenta]{title}")


def show_info(message: str) -> None:
    console.print(f"[bright_cyan]• {message}[/bright_cyan]")


def show_success(message: str) -> None:
    console.print(f"[bold green]OK  {message}[/bold green]")


def show_error(message: str) -> None:
    console.print(Panel(message, title="[bold red]Error[/bold red]", border_style="bright_red"))


def prompt_text(message: str, default: str | None = None, allow_blank: bool = False) -> str:
    while True:
        value = Prompt.ask(f"[bold bright_cyan]{message}[/bold bright_cyan]", default=default or "")
        if allow_blank:
            return value.strip()
        if value.strip():
            return value.strip()
        show_error("This field cannot be empty.")


def prompt_optional_text(message: str) -> str | None:
    value = Prompt.ask(f"[bold bright_cyan]{message}[/bold bright_cyan]", default="")
    cleaned = value.strip()
    return cleaned or None


def prompt_participant_count() -> int:
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
    if not people:
        return

    table = Table(title="Participants added", header_style="bold bright_cyan")
    table.add_column("#", justify="right", style="bright_black")
    table.add_column("Name", style="bold white")

    for index, person in enumerate(people, start=1):
        table.add_row(str(index), person.name)

    console.print(table)


def show_expenses_table(expenses: Sequence[Expense]) -> None:
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


def build_chart_text(
    title: str,
    labels: Sequence[str],
    values: Sequence[Decimal],
    x_max: Decimal | None = None,
) -> Text:
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
    if x_max is not None and x_max > 0:
        plt.xlim(0, float(x_max))
    plt.build()
    chart = plt.build()
    plt.clear_figure()
    return Text.from_ansi(chart)


def build_chart_panel(
    title: str,
    labels: Sequence[str],
    values: Sequence[Decimal],
    x_max: Decimal | None = None,
) -> Panel:
    return Panel(
        build_chart_text(title, labels, values, x_max=x_max),
        title=title,
        border_style="bright_magenta",
        padding=(1, 2),
    )


def show_chart_panel(title: str, labels: Sequence[str], values: Sequence[Decimal]) -> None:
    if should_animate_charts(labels, values):
        animate_chart_panel(title, labels, values)
        return

    console.print(build_chart_panel(title, labels, values))


def should_animate_charts(labels: Sequence[str], values: Sequence[Decimal]) -> bool:
    if not labels or not values:
        return False
    if os.getenv("CI") or os.getenv("SPLITTY_NO_ANIMATIONS"):
        return False
    return console.is_terminal


def animate_chart_panel(title: str, labels: Sequence[str], values: Sequence[Decimal]) -> None:
    empty_values = [Decimal("0") for _ in values]
    final_x_max = max(values, default=Decimal("0"))
    with Live(
        build_chart_panel(title, labels, empty_values, x_max=final_x_max),
        console=console,
        refresh_per_second=18,
        transient=False,
    ) as live:
        for frame in range(1, CHART_ANIMATION_FRAMES + 1):
            progress = Decimal(frame) / Decimal(CHART_ANIMATION_FRAMES)
            eased_progress = Decimal(str(_ease_out_cubic(float(progress))))
            animated_values = [value * eased_progress for value in values]
            live.update(
                build_chart_panel(title, labels, animated_values, x_max=final_x_max),
                refresh=True,
            )
            time.sleep(CHART_ANIMATION_DELAY_SECONDS)

        final_panel = build_chart_panel(title, labels, values, x_max=final_x_max)
        live.update(final_panel, refresh=True)


def _ease_out_cubic(progress: float) -> float:
    return 1 - (1 - progress) ** 3


def show_final_report(report: EventReport) -> None:
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
    show_section("Deep dive insights")

    stat_panels = [
        Panel(
            build_highlight_content(
                f"[bold white]{insights.top_spender.name}[/bold white]\n[green]{format_money(insights.top_spender.amount_paid)}[/green]",
                TROPHY_ASCII,
                "bright_green",
            ),
            title="Top spender",
            border_style="green",
        ),
        Panel(
            f"[bold white]{insights.lowest_spender.name}[/bold white]\n[yellow]{format_money(insights.lowest_spender.amount_paid)}[/yellow]",
            title="Lowest spender",
            border_style="yellow",
        ),
        Panel(
            build_highlight_content(
                (
                    f"[bold white]{insights.most_expensive_expense.label}[/bold white]\n"
                    f"[magenta]{format_money(insights.most_expensive_expense.amount)}[/magenta]"
                ),
                DOLLAR_ASCII,
                "bright_magenta",
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


def build_highlight_content(summary: str, ascii_art: str, art_style: str) -> Table:
    content = Table.grid(expand=True)
    art_width = max(len(line) for line in ascii_art.splitlines())
    content.add_column(ratio=1)
    content.add_column(width=art_width, justify="center", no_wrap=True)
    content.add_row(summary, Text(ascii_art, style=art_style, no_wrap=True))
    return content
