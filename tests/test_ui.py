from __future__ import annotations

from decimal import Decimal
from io import StringIO

from rich.console import Console
from rich.text import Text

from split_cli.models import (
    EventInsights,
    ExpenseHighlight,
    ParticipantSpendingStat,
    PayerBreakdownItem,
)
from split_cli import ui


def test_animated_chart_scales_values_before_final_render(monkeypatch) -> None:
    calls: list[list[Decimal]] = []
    x_limits: list[Decimal | None] = []
    test_console = Console(file=StringIO(), force_terminal=True, width=120, height=32)

    monkeypatch.setattr(ui, "console", test_console)
    monkeypatch.setattr(ui.time, "sleep", lambda *_args, **_kwargs: None)
    monkeypatch.setattr(ui, "CHART_ANIMATION_FRAMES", 3)
    monkeypatch.setattr(ui, "CHART_ANIMATION_DELAY_SECONDS", 0)

    def fake_build_chart_text(
        _title: str,
        _labels: list[str],
        values: list[Decimal],
        x_max: Decimal | None = None,
    ) -> Text:
        calls.append(values)
        x_limits.append(x_max)
        return Text("chart")

    monkeypatch.setattr(ui, "build_chart_text", fake_build_chart_text)

    ui.show_chart_panel("Animated", ["A", "B"], [Decimal("10"), Decimal("20")])

    assert calls[0] == [Decimal("0"), Decimal("0")]
    assert Decimal("0") < calls[1][0] < Decimal("10")
    assert calls[-1] == [Decimal("10"), Decimal("20")]
    assert all(limit == Decimal("20") for limit in x_limits)


def test_static_chart_used_when_not_terminal(monkeypatch) -> None:
    calls = 0
    test_console = Console(file=StringIO(), force_terminal=False, width=120, height=32)

    monkeypatch.setattr(ui, "console", test_console)

    def fake_build_chart_text(
        _title: str,
        _labels: list[str],
        _values: list[Decimal],
        x_max: Decimal | None = None,
    ) -> Text:
        nonlocal calls
        calls += 1
        return Text("chart")

    monkeypatch.setattr(ui, "build_chart_text", fake_build_chart_text)

    ui.show_chart_panel("Static", ["A"], [Decimal("10")])

    assert calls == 1


def test_detailed_insights_adds_compact_ascii_badges(monkeypatch) -> None:
    test_console = Console(file=StringIO(), force_terminal=False, width=140)
    monkeypatch.setattr(ui, "console", test_console)
    monkeypatch.setattr(ui, "show_chart_panel", lambda *_args, **_kwargs: None)

    insights = EventInsights(
        top_spender=ParticipantSpendingStat(name="Lucas", amount_paid=Decimal("30.00")),
        lowest_spender=ParticipantSpendingStat(name="Andre", amount_paid=Decimal("10.00")),
        most_expensive_expense=ExpenseHighlight(
            label="Pizza - paid by Lucas",
            payer="Lucas",
            amount=Decimal("30.00"),
            description="Pizza",
        ),
        expense_breakdown=[],
        payer_breakdown=[PayerBreakdownItem(payer="Lucas", amount=Decimal("30.00"))],
    )

    ui.show_detailed_insights(insights)
    output = test_console.file.getvalue()

    assert "[#1]" in output
    assert "[$]" in output
