from __future__ import annotations

import math
import os
import re
import textwrap
import time
from collections.abc import Iterable

from rich.console import Console
from rich.live import Live
from rich.text import Text

BRAND_LABEL = "Splitty"
SUBTITLE = "Split your expenses, fun edition."
TERMINAL_TAGLINE = "Use your terminal for more than call folders or do npm run dev."
START_PROMPT = "Press Enter to begin"
COMPACT_TITLE = "Splitty"
INTRO_COPY = "Turn shared expenses into a clear settlement plan in a few focused prompts."
INTRO_STEPS = (
    "1. Name the event.",
    "2. Add participants.",
    "3. Record who paid, the amount, and an optional note.",
    "4. Review balances, transfers, and charts.",
    "5. Save a JSON backup if you want to keep it.",
)

MIN_ANIMATED_WIDTH = 70
MIN_ANIMATED_HEIGHT = 22
SIDE_BY_SIDE_WIDTH = 100
INTRO_ART_TOP_GAP = 3
WORDMARK_TOP_OFFSET = 24
WORDMARK_LEFT_OFFSET = -100
ANIMATION_FPS = 12
ANIMATION_SECONDS = 2.4

ANSI_PATTERN = re.compile(r"\x1b\[[0-?]*[ -/]*[@-~]")
ARCADE_PALETTE = (
    "bright_cyan",
    "bright_magenta",
    "bright_green",
    "bright_yellow",
    "bright_blue",
)

WORDMARK = r"""
  _____  _____  _      ___  _____  _____ __   __
 / ____||  __ \| |    |_ _||_   _||_   _|\ \ / /
| (___  | |__) | |     | |   | |    | |   \ V /
 \___ \ |  ___/| |     | |   | |    | |    | |
 ____) || |    | |___ _| |_  | |    | |    | |
|_____/ |_|    |_____||___|  |_|    |_|    |_|
""".strip("\n")

SCALE_FRAMES = (
    r"""
                       ++++++
                      ++====++
                     +++====+++
                     ++++++++++
                       ++++++
                      ++====++
              *++++++  +====+  ++++++*
            ++======+++======+++======++
          ++++++++++++++====+++++++++++++
          ++++++++      ++++++      +++++
          +++++          ++++          +++
         ++++ +++        ++++        +++ +++
        +++  +++         ++++         +++  +++
       +++   +++         ++++         +++   +++
      +++    +++         ++++         +++    +++
   ---++=====+++---    ++++++++    ---+++=====++---
  ===+#########+===   ++======++   ===+#########+===
    ====+++++====     ++++++++++     ====+++++====
                     ++++++++++++
                  ++++++++++++++++++
               ++++==============++++
              ++++++++++++++++++++++++
    """,
    r"""
                       ++++++
                      ++====++
                     +++====+++
                     ++++++++++
                       ++++++
                      ++====++
              *++++++  +====+  ++++++*
            ++======+++======+++======++
          ++++++++++++++====+++++++++++++
          +++++++       ++++++       ++++
          ++++           ++++           ++
         +++  +++        ++++        +++  ++
        +++   +++        ++++        +++   +++
       +++    +++        ++++        +++    +++
      +++     +++        ++++        +++     +++
    --++======+++--    ++++++++    --+++======++--
  ===+#########+===   ++======++   ===+#########+===
    ====+++++====     ++++++++++     ====+++++====
                     ++++++++++++
                  ++++++++++++++++++
               ++++==============++++
              ++++++++++++++++++++++++
    """,
    r"""
                       ++++++
                      ++====++
                     +++====+++
                     ++++++++++
                       ++++++
                      ++====++
              *++++++  +====+  ++++++*
            ++======+++======+++======++
          ++++++++++++++====+++++++++++++
          ++++       ++++++       +++++++
          ++           ++++           ++++
         ++  +++       ++++        +++  +++
        +++   +++      ++++       +++   +++
       +++    +++      ++++      +++    +++
      +++     +++      ++++      +++     +++
    --++======+++--  ++++++++  --+++======++--
  ===+#########+=== ++======++ ===+#########+===
    ====+++++====   ++++++++++   ====+++++====
                    ++++++++++++
                 ++++++++++++++++++
              ++++==============++++
             ++++++++++++++++++++++++
    """,
    r"""
                       ++++++
                      ++====++
                     +++====+++
                     ++++++++++
                       ++++++
                      ++====++
              *++++++  +====+  ++++++*
            ++======+++======+++======++
          ++++++++++++++====+++++++++++++
          ++++++++      ++++++      +++++
          +++++          ++++          +++
         ++++ +++        ++++        +++ +++
        +++  +++         ++++         +++  +++
       +++   +++         ++++         +++   +++
      +++    +++         ++++         +++    +++
   ---++=====+++---    ++++++++    ---+++=====++---
  ===+#########+===   ++======++   ===+#########+===
    ====+++++====     ++++++++++     ====+++++====
                     ++++++++++++
                  ++++++++++++++++++
               ++++==============++++
              ++++++++++++++++++++++++
    """,
)

COMPACT_SCALE = r"""
                                        
                  +=++                  
                  ++++                  
      +=+         +=++         +=+*     
     +++++   +++++==+++++++   +++++     
      ++++++++++++++++++++++++++++      
     +++++        +**+        +++++     
     +++++         +++        +++ +     
    ++ + ++        +++       ++ + ++    
    ++ + ++        +++       ++ + ++    
   *+  +  ++       +++       +  +  ++   
   ++  +  ++       +++      ++  +  ++   
  ++   +   ++      +++     ++   +   ++  
  +*   +   ++      +++     ++   +    +  
 ++    +    ++     +++     +    +    ++ 
 +=++++++++==+    ++++    +=++++++++==+ 
 =--===+======   +==+++   ==-===+====== 
   =--=====      ++++++      --======   
               ++++++++++               
            ++====++++++++++            
            ++++++++++++++++            
                                        
""".strip("\n")


def intro_is_enabled(console: Console, animations: bool = True) -> bool:
    if not animations:
        return False
    if os.getenv("CI") or os.getenv("SPLITTY_NO_ANIMATIONS"):
        return False
    if not console.is_terminal:
        return False
    return console.width >= MIN_ANIMATED_WIDTH and console.height >= MIN_ANIMATED_HEIGHT


def render_intro_frame(
    width: int,
    height: int,
    *,
    scale_frame_index: int = 0,
    frame_index: int = 0,
    wordmark: str = WORDMARK,
    show_prompt: bool = False,
    highlight: bool = False,
) -> Text:
    width = max(width, 40)
    height = max(height, 12)
    scale_lines = _normalize_lines(SCALE_FRAMES[scale_frame_index % len(SCALE_FRAMES)])
    wordmark_lines = _normalize_lines(wordmark or WORDMARK)
    body = Text(no_wrap=True)

    content_height = _content_height(width, scale_lines, wordmark_lines, show_prompt)
    top_padding = max((height - content_height) // 2, 0)
    row = 0
    for _ in range(top_padding):
        _append_ambient_line(body, width, row, frame_index)
        row += 1

    for index, line in enumerate(_intro_header_lines(width)):
        style = "bold bright_cyan" if index == 0 else "bright_magenta" if index == 1 else "bright_cyan"
        row = _append_centered(body, line, width, style, row, frame_index)
    for _ in range(INTRO_ART_TOP_GAP):
        _append_ambient_line(body, width, row, frame_index)
        row += 1

    if width >= SIDE_BY_SIDE_WIDTH:
        row = _append_side_by_side(body, scale_lines, wordmark_lines, width, highlight, row, frame_index)
    else:
        row = _append_stacked(body, scale_lines, wordmark_lines, width, highlight, row, frame_index)

    _append_ambient_line(body, width, row, frame_index)
    row += 1
    if show_prompt:
        _append_ambient_line(body, width, row, frame_index)
        row += 1
        row = _append_centered(body, START_PROMPT, width, "bold bright_green", row, frame_index)

    while row < height:
        _append_ambient_line(body, width, row, frame_index)
        row += 1

    return body


def show_intro(console: Console, *, animations: bool = True, wait_for_enter: bool = True) -> None:
    if not intro_is_enabled(console, animations=animations):
        show_compact_intro(console)
        return

    wordmark_frames = _build_wordmark_frames()
    frame_count = max(1, int(ANIMATION_SECONDS * ANIMATION_FPS))

    try:
        with Live(
            render_intro_frame(console.width, console.height),
            console=console,
            refresh_per_second=ANIMATION_FPS,
            screen=True,
            transient=True,
        ) as live:
            for index in range(frame_count):
                wordmark = _select_wordmark_frame(wordmark_frames, index, frame_count)
                live.update(
                    render_intro_frame(
                        console.width,
                        console.height,
                        scale_frame_index=index,
                        frame_index=index,
                        wordmark=wordmark,
                        highlight=index >= frame_count - 4,
                    ),
                    refresh=True,
                )
                time.sleep(1 / ANIMATION_FPS)

            live.update(
                render_intro_frame(
                    console.width,
                    console.height,
                    scale_frame_index=frame_count,
                    frame_index=frame_count,
                    wordmark=WORDMARK,
                    show_prompt=wait_for_enter,
                    highlight=True,
                ),
                refresh=True,
            )
            if wait_for_enter:
                input()
    except (KeyboardInterrupt, EOFError):
        raise
    except Exception:
        show_compact_intro(console)


def show_static_intro(console: Console) -> None:
    show_compact_intro(console)


def show_compact_intro(console: Console) -> None:
    console.print()
    console.print(render_compact_intro(console.width))


def render_compact_intro(width: int) -> Text:
    width = max(width, 40)
    body = Text(no_wrap=True)
    scale_lines = _normalize_lines(COMPACT_SCALE)

    if width >= 88:
        _append_compact_side_by_side(body, scale_lines, width)
    else:
        _append_compact_stacked(body, scale_lines, width)

    return body


def _content_height(
    width: int,
    scale_lines: list[str],
    wordmark_lines: list[str],
    show_prompt: bool,
) -> int:
    if width >= SIDE_BY_SIDE_WIDTH:
        layout_height = max(len(scale_lines), len(wordmark_lines) + WORDMARK_TOP_OFFSET)
    else:
        layout_height = len(scale_lines) + len(wordmark_lines) + 1
    return len(_intro_header_lines(width)) + INTRO_ART_TOP_GAP + 1 + layout_height + (3 if show_prompt else 0)


def _append_side_by_side(
    body: Text,
    scale_lines: list[str],
    wordmark_lines: list[str],
    width: int,
    highlight: bool,
    row: int,
    frame_index: int,
) -> int:
    scale_width = max(len(line) for line in scale_lines)
    gap = 4
    word_style = "bold bright_white" if highlight else "bold bright_magenta"

    layout_height = max(len(scale_lines), len(wordmark_lines) + WORDMARK_TOP_OFFSET)
    for item_index in range(layout_height):
        wordmark_index = item_index - WORDMARK_TOP_OFFSET
        scale_part = scale_lines[item_index] if item_index < len(scale_lines) else ""
        word_part = wordmark_lines[wordmark_index] if 0 <= wordmark_index < len(wordmark_lines) else ""
        reserved_scale_width = scale_width if scale_part else max(scale_width + WORDMARK_LEFT_OFFSET, 0)
        active_gap = gap if scale_part else 0
        _append_composed_line(
            body,
            [
                (scale_part.ljust(reserved_scale_width), _scale_style(item_index, frame_index)),
                (" " * active_gap, ""),
                (word_part, word_style),
            ],
            width,
            row,
            frame_index,
        )
        row += 1
    return row


def _append_stacked(
    body: Text,
    scale_lines: list[str],
    wordmark_lines: list[str],
    width: int,
    highlight: bool,
    row: int = 0,
    frame_index: int = 0,
) -> int:
    for line_index, line in enumerate(scale_lines):
        row = _append_centered(body, line, width, _scale_style(line_index, frame_index), row, frame_index)
    _append_ambient_line(body, width, row, frame_index)
    row += 1
    word_style = "bold bright_white" if highlight else "bold bright_magenta"
    for line in wordmark_lines:
        row = _append_centered(body, line, width, word_style, row, frame_index)
    return row


def _append_compact_side_by_side(body: Text, scale_lines: list[str], width: int) -> None:
    scale_width = max(len(line) for line in scale_lines)
    gap = 5
    text_width = min(58, max(28, width - scale_width - gap - 4))
    text_lines = _compact_text_lines(text_width)
    total_width = scale_width + gap + max(len(line) for line in text_lines)
    left_padding = max((width - total_width) // 2, 0)

    for row in range(max(len(scale_lines), len(text_lines))):
        scale_part = scale_lines[row] if row < len(scale_lines) else ""
        text_part = text_lines[row] if row < len(text_lines) else ""
        body.append(" " * left_padding)
        body.append(scale_part.ljust(scale_width), style="bold bright_green")
        body.append(" " * gap)
        _append_compact_text_part(body, text_part, row)
        body.append("\n")


def _append_compact_stacked(body: Text, scale_lines: list[str], width: int) -> None:
    for line in scale_lines:
        _append_plain_centered(body, line, width, "bold bright_green")
    body.append("\n")
    _append_plain_centered(body, COMPACT_TITLE, width, "bold bright_cyan")
    for line in _compact_text_lines(min(width - 4, 64)):
        if line == COMPACT_TITLE:
            continue
        style = "bright_magenta" if line == SUBTITLE else "bright_cyan"
        _append_plain_centered(body, line, width, style)


def _append_compact_text_part(body: Text, text_part: str, row: int) -> None:
    if row == 0:
        body.append(text_part, style="bold bright_cyan")
    elif row == 1:
        body.append(text_part, style="bright_magenta")
    else:
        body.append(text_part, style="bright_cyan")


def _append_plain_centered(body: Text, line: str, width: int, style: str) -> None:
    cleaned = _fit_line(line, width)
    left_padding = max((width - len(cleaned)) // 2, 0)
    body.append(" " * left_padding)
    body.append(cleaned, style=style)
    body.append("\n")


def _append_centered(
    body: Text,
    line: str,
    width: int,
    style: str,
    row: int = 0,
    frame_index: int = 0,
) -> int:
    cleaned = _fit_line(line, width)
    _append_composed_line(body, [(cleaned, style)], width, row, frame_index)
    return row + 1


def _append_composed_line(
    body: Text,
    segments: list[tuple[str, str]],
    width: int,
    row: int,
    frame_index: int,
) -> None:
    content_width = sum(len(segment) for segment, _ in segments)
    left_padding = max((width - content_width) // 2, 0)
    right_padding = max(width - content_width - left_padding, 0)

    if left_padding > 0:
        _append_ambient_span(body, left_padding - 1, row, 0, frame_index)
        body.append(" ", style="dim bright_black")
    cursor = left_padding
    for segment, style in segments:
        body.append(segment, style=style or "bright_black")
        cursor += len(segment)
    if right_padding > 0:
        body.append(" ", style="dim bright_black")
        _append_ambient_span(body, right_padding - 1, row, cursor + 1, frame_index)
    body.append("\n")


def _append_ambient_line(body: Text, width: int, row: int, frame_index: int) -> None:
    _append_ambient_span(body, width, row, 0, frame_index)
    body.append("\n")


def _append_ambient_span(
    body: Text,
    length: int,
    row: int,
    start_column: int,
    frame_index: int,
) -> None:
    if length <= 0:
        return

    for offset in range(length):
        column = start_column + offset
        char = _ambient_char(column, row, frame_index)
        style = _ambient_style(column, row, frame_index, char)
        body.append(char, style=style)


def _ambient_char(column: int, row: int, frame_index: int) -> str:
    if row == (frame_index // 2) % 10 or (row + frame_index) % 17 == 0:
        return "." if (column + frame_index) % 8 == 0 else " "
    sparkle = (column * 17 + row * 31 + frame_index * 7) % 97
    if sparkle == 0:
        return "."
    if sparkle == 1:
        return "'"
    if sparkle == 2:
        return "`"
    return " "


def _ambient_style(column: int, row: int, frame_index: int, char: str) -> str:
    if char == " ":
        return "dim bright_black"
    palette_index = (column + row * 2 + frame_index) % len(ARCADE_PALETTE)
    return f"dim {ARCADE_PALETTE[palette_index]}"


def _scale_style(row: int, frame_index: int) -> str:
    palette_index = (row + frame_index) % len(ARCADE_PALETTE)
    return f"bold {ARCADE_PALETTE[palette_index]}"


def _normalize_lines(value: str) -> list[str]:
    return [line.rstrip() for line in value.strip("\n").splitlines()]


def _fit_line(line: str, width: int) -> str:
    if len(line) <= width:
        return line
    return line[: max(width - 1, 1)]


def _wrap_copy(value: str, width: int) -> list[str]:
    return textwrap.wrap(value, width=max(width, 20))


def _compact_text_lines(width: int) -> list[str]:
    lines = [
        COMPACT_TITLE,
        SUBTITLE,
        *_wrap_copy(TERMINAL_TAGLINE, width),
        "",
        *_wrap_copy(INTRO_COPY, width),
        "",
    ]
    lines.extend(INTRO_STEPS)
    return lines


def _intro_header_lines(width: int) -> list[str]:
    return [
        BRAND_LABEL,
        SUBTITLE,
        *_wrap_copy(TERMINAL_TAGLINE, min(width - 4, len(TERMINAL_TAGLINE))),
    ]


def _build_wordmark_frames() -> list[str]:
    tte_frames = _build_tte_wordmark_frames(limit=28)
    if tte_frames:
        return tte_frames
    return list(_build_reveal_wordmark_frames(total_frames=28))


def _build_tte_wordmark_frames(limit: int) -> list[str]:
    try:
        from terminaltexteffects.effects.effect_sweep import Sweep
    except Exception:
        return []

    try:
        effect = Sweep(WORDMARK)
        effect.terminal_config.frame_rate = 0
        effect.terminal_config.canvas_width = max(len(line) for line in WORDMARK.splitlines())
        effect.terminal_config.canvas_height = len(WORDMARK.splitlines())
        effect.terminal_config.ignore_terminal_dimensions = True
        frames: list[str] = []
        for frame in effect:
            cleaned = ANSI_PATTERN.sub("", frame).strip("\n")
            if cleaned.strip():
                frames.append(cleaned)
            if len(frames) >= limit:
                break
        if frames and frames[-1].strip() != WORDMARK.strip():
            frames.append(WORDMARK)
        return frames
    except Exception:
        return []


def _build_reveal_wordmark_frames(total_frames: int) -> Iterable[str]:
    lines = WORDMARK.splitlines()
    max_width = max(len(line) for line in lines)
    for frame in range(total_frames):
        visible_width = math.ceil(max_width * ((frame + 1) / total_frames))
        yield "\n".join(line[:visible_width].ljust(len(line)) for line in lines)
    yield WORDMARK


def _select_wordmark_frame(frames: list[str], index: int, frame_count: int) -> str:
    if not frames:
        return WORDMARK
    frame_index = min(len(frames) - 1, int(index / max(frame_count - 1, 1) * (len(frames) - 1)))
    return frames[frame_index]
