from __future__ import annotations

from io import StringIO

import pytest
from rich.console import Console

from split_cli.intro import (
    COMPACT_TITLE,
    INTRO_STEPS,
    START_PROMPT,
    SUBTITLE,
    WORDMARK,
    render_compact_intro,
    render_intro_frame,
    show_intro,
)


@pytest.mark.parametrize("width", [60, 100, 140])
def test_render_intro_frame_adapts_to_terminal_width(width: int) -> None:
    output = _render_to_text(render_intro_frame(width, 32, show_prompt=True))

    assert "Splitty" in output
    assert SUBTITLE in output
    assert "Use your terminal" in output
    assert "npm" in output
    assert "run dev" in output
    assert START_PROMPT in output
    assert "++++++" in output
    assert "########" in output
    assert "arcade" not in output.lower()
    assert "$" not in output


def test_render_intro_frame_can_use_partial_wordmark() -> None:
    output = _render_to_text(
        render_intro_frame(
            120,
            32,
            wordmark=WORDMARK.splitlines()[0],
            show_prompt=False,
        )
    )

    assert "Splitty" in output
    assert "_____" in output


def test_render_intro_frame_uses_multicolor_arcade_background() -> None:
    frame = render_intro_frame(140, 34, frame_index=5, show_prompt=True)
    styles = {str(span.style) for span in frame.spans}

    assert "Use your terminal for more than call folders or do npm run dev." in frame.plain
    assert any("bright_magenta" in style for style in styles)
    assert any("bright_cyan" in style for style in styles)
    assert any("bright_yellow" in style for style in styles)


@pytest.mark.parametrize("width", [60, 120])
def test_render_compact_intro_shows_brand_scale_copy_and_steps(width: int) -> None:
    output = _render_to_text(render_compact_intro(width))

    assert COMPACT_TITLE in output
    assert SUBTITLE in output
    assert "Use your terminal" in output
    assert "npm" in output
    assert "dev" in output
    assert "Turn shared expenses" in output
    assert "focused prompts" in output
    assert INTRO_STEPS[0] in output
    assert "Guided flow" not in output
    assert "++++++++" in output
    assert "$" not in output


def test_show_intro_no_animations_does_not_wait_for_enter(monkeypatch) -> None:
    monkeypatch.setattr("builtins.input", lambda: pytest.fail("input should not be called"))
    console = Console(file=StringIO(), force_terminal=True, width=120, height=32)

    show_intro(console, animations=False)

    output = console.file.getvalue()
    assert COMPACT_TITLE in output
    assert "Turn shared expenses" in output
    assert "focused prompts" in output
    assert INTRO_STEPS[0] in output


def test_show_intro_non_terminal_does_not_wait_for_enter(monkeypatch) -> None:
    monkeypatch.setattr("builtins.input", lambda: pytest.fail("input should not be called"))
    console = Console(file=StringIO(), force_terminal=False, width=120, height=32)

    show_intro(console, animations=True)

    output = console.file.getvalue()
    assert COMPACT_TITLE in output
    assert "Turn shared expenses" in output
    assert "focused prompts" in output
    assert INTRO_STEPS[0] in output


def _render_to_text(renderable: object) -> str:
    stream = StringIO()
    console = Console(file=stream, force_terminal=False, width=160, color_system=None)
    console.print(renderable)
    return stream.getvalue()
