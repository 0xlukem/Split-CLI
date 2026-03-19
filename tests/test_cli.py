from datetime import datetime, timezone
from pathlib import Path

from rich.text import Text
from typer.testing import CliRunner

from split_cli.cli import app


runner = CliRunner()


def test_cli_happy_path_keeps_output_in_english(monkeypatch) -> None:
    monkeypatch.setattr("split_cli.ui.build_chart_text", lambda *args, **kwargs: Text("chart"))

    result = runner.invoke(
        app,
        input="\n".join(
            [
                "Road trip",
                "3",
                "Alice",
                "Ben",
                "Cara",
                "1",
                "90",
                "Fuel",
                "n",
                "n",
                "n",
            ]
        )
        + "\n",
        color=False,
    )

    assert result.exit_code == 0
    assert "Session setup" in result.stdout
    assert "Participant name #1" in result.stdout
    assert "Expense breakdown" in result.stdout
    assert "Do you want more info about this split?" in result.stdout
    assert "Do you want to save a JSON backup of this session?" in result.stdout


def test_cli_shows_optional_insights_when_confirmed(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("split_cli.ui.build_chart_text", lambda *args, **kwargs: Text("chart"))

    result = runner.invoke(
        app,
        ["--export-json", str(tmp_path / "trip.json")],
        input="\n".join(
            [
                "Trip",
                "3",
                "Alice",
                "Ben",
                "Cara",
                "1",
                "90",
                "Hotel",
                "n",
                "y",
            ]
        )
        + "\n",
        color=False,
    )

    assert result.exit_code == 0
    assert "Deep dive insights" in result.stdout
    assert "Top spender" in result.stdout
    assert "Most expensive expense" in result.stdout
    assert "Paid by participant" in result.stdout


def test_cli_skips_optional_insights_when_declined(monkeypatch) -> None:
    monkeypatch.setattr("split_cli.ui.build_chart_text", lambda *args, **kwargs: Text("chart"))

    result = runner.invoke(
        app,
        input="\n".join(
            [
                "Trip",
                "2",
                "Alice",
                "Ben",
                "1",
                "50",
                "Lunch",
                "n",
                "n",
                "n",
            ]
        )
        + "\n",
        color=False,
    )

    assert result.exit_code == 0
    assert "Do you want more info about this split?" in result.stdout
    assert "Deep dive insights" not in result.stdout


def test_cli_saves_custom_backup_name_in_fixed_directory(monkeypatch, tmp_path: Path) -> None:
    monkeypatch.setattr("split_cli.ui.build_chart_text", lambda *args, **kwargs: Text("chart"))
    monkeypatch.setattr("split_cli.services.exporter.Path.home", lambda: tmp_path)

    result = runner.invoke(
        app,
        input="\n".join(
            [
                "Trip",
                "2",
                "Alice",
                "Ben",
                "1",
                "50",
                "Lunch",
                "n",
                "n",
                "y",
                "y",
            ]
        )
        + "\n",
        color=False,
    )

    assert result.exit_code == 0
    assert "Backup file name" in result.stdout
    assert "JSON file path" not in result.stdout
    assert (tmp_path / ".split-cli" / "backups" / "y.json").exists()


def test_cli_uses_event_name_and_session_date_for_default_backup_name(
    monkeypatch,
    tmp_path: Path,
) -> None:
    class FrozenDateTime(datetime):
        @classmethod
        def now(cls, tz=None):
            frozen = cls(2026, 3, 19, 15, 0, tzinfo=timezone.utc)
            if tz is not None:
                return frozen.astimezone(tz)
            return frozen

    monkeypatch.setattr("split_cli.ui.build_chart_text", lambda *args, **kwargs: Text("chart"))
    monkeypatch.setattr("split_cli.services.exporter.Path.home", lambda: tmp_path)
    monkeypatch.setattr("split_cli.cli.datetime", FrozenDateTime)

    result = runner.invoke(
        app,
        input="\n".join(
            [
                "Asado",
                "2",
                "Alice",
                "Ben",
                "1",
                "50",
                "Lunch",
                "n",
                "n",
                "y",
                "",
            ]
        )
        + "\n",
        color=False,
    )

    assert result.exit_code == 0
    assert (tmp_path / ".split-cli" / "backups" / "asado-2026-03-19.json").exists()
