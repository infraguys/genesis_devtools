#    Copyright 2026 Genesis Corporation.
#
#    All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
from __future__ import annotations

import readline
import sys

import rich.align
import simple_term_menu
from rich import console as rich_console
from rich import markdown as rich_markdown
from rich import panel as rich_panel
from rich import text as rich_text

DEFAULT_PROMPT_COLOR = "grey50"
DEFAULT_TEXT_COLOR = "grey80"
_CONSOLE = rich_console.Console()


def get_console(use_global: bool = True) -> rich_console.Console:
    """Get console instance.

    Args:
        use_global: If True, return the global console instance.
    """
    if use_global:
        return _CONSOLE
    return rich_console.Console()


def markdown_message(
    text: str,
    title: str | None = None,
    with_border: bool = True,
    text_color: str = DEFAULT_TEXT_COLOR,
    title_color: str = "cyan",
    border_color: str = "sky_blue1",
    length_ratio: float = 0.5,
) -> None:
    """Render Markdown text for wizard intro/outro style messages."""
    markdown = rich_markdown.Markdown(text, style=text_color)
    console = get_console()
    content_width = max(20, int(console.size.width * length_ratio))

    if with_border:
        panel_title = None
        if title:
            panel_title = f"[{title_color}]{title}[/{title_color}]"

        console.print(
            rich.align.Align.center(
                rich_panel.Panel(
                    markdown,
                    border_style=border_color,
                    expand=False,
                    padding=(0, 1),
                    title=panel_title,
                    title_align="center",
                    width=content_width,
                )
            )
        )
        return

    if title:
        console.print(
            rich.align.Align.center(
                rich_text.Text(title, style=title_color),
                width=content_width,
            )
        )
    console.print(
        rich.align.Align.center(
            markdown,
            width=content_width,
        )
    )


def framed_prompt(
    prompt: str,
    description: str | None = None,
    default: str | None = None,
    border_color: str = DEFAULT_PROMPT_COLOR,
    accent_color: str = "cyan",
    initial_text: str | None = None,
    user_input: bool = True,
) -> str:
    console = get_console()

    # Compute frame width based on terminal size.
    # We deliberately avoid printing in the last terminal column to prevent
    # terminal-specific wrapping issues that can make the right border vanish.
    width = console.size.width - 1
    if width < 10:
        width = 10

    # Build the top border with an embedded title (prompt + optional default).
    title_offset = 3
    left_prefix = "╭" + ("─" * (title_offset - 1))
    available = max(0, (width - 2) - (title_offset - 1))

    title_parts: list[tuple[str, str]] = [(f"  {prompt} ", border_color)]
    if default is not None:
        title_parts.append((f"({default})", accent_color))
        title_parts.append(("  ", border_color))
    else:
        title_parts.append((" ", border_color))

    clipped_parts: list[tuple[str, str]] = []
    remaining = available
    for part_text, part_style in title_parts:
        if remaining <= 0:
            break
        clipped = part_text[:remaining]
        clipped_parts.append((clipped, part_style))
        remaining -= len(clipped)

    top_line = rich_text.Text()
    top_line.append(left_prefix, style=border_color)
    for part_text, part_style in clipped_parts:
        top_line.append(part_text, style=part_style)

    dashes_remaining = max(0, (width - 1) - len(top_line.plain))
    top_line.append("─" * dashes_remaining, style=border_color)
    top_line.append("╮", style=border_color)
    console.print(top_line)

    # Render the input line inside the frame. The actual input cursor will be
    # moved into this line later via ANSI cursor movement.
    middle_line = rich_text.Text("│" + (" " * (width - 2)) + "│", style=border_color)
    console.print(middle_line)

    # Column where the user starts typing (after the left border and padding).
    input_column = 4

    description_lines: list[rich_text.Text] = []
    if description:
        # Render an optional description block inside the same frame.
        # The separator visually splits the input from the markdown content.
        separator_line = rich_text.Text(
            "├" + ("─" * (width - 2)) + "┤", style=border_color
        )
        console.print(separator_line)

        # Render Markdown with a constrained width so that the right border is
        # always preserved. Then wrap each rendered line with frame borders.
        content_width = max(0, width - 6)
        md = rich_markdown.Markdown(description)
        options = console.options.update(width=content_width)
        rendered = console.render_lines(md, options)
        for segments in rendered:
            line_text = rich_text.Text.assemble(
                *[(s.text.replace("\n", ""), s.style) for s in segments]
            )
            line_text.truncate(content_width, overflow="crop")
            if len(line_text.plain) < content_width:
                line_text.append(" " * (content_width - len(line_text.plain)))

            wrapped = rich_text.Text()
            wrapped.append("│  ", style=border_color)
            wrapped.append_text(line_text)
            wrapped.append("  │", style=border_color)
            description_lines.append(wrapped)
            console.print(wrapped)

    bottom_line = rich_text.Text("╰" + ("─" * (width - 2)) + "╯", style=border_color)
    console.print(bottom_line)

    # Move the cursor back to the input line (we render the whole frame first
    # so it doesn't get "blocked" by the input read).
    moves_up_to_input = 2
    moves_down_after_enter = 1
    if description:
        moves_up_to_input = 3 + len(description_lines)
        moves_down_after_enter = 2 + len(description_lines)

    sys.stdout.write(f"\x1b[{moves_up_to_input}A\x1b[{input_column}G")
    sys.stdout.flush()

    if not user_input:
        value_str = ""
        if initial_text is not None:
            value_str = str(initial_text)
        elif default is not None:
            value_str = str(default)

        if value_str != "":
            max_value_len = max(0, width - input_column - 1)
            clipped_value = value_str[:max_value_len]
            sys.stdout.write(f"\x1b[{input_column}G{clipped_value}")
            sys.stdout.flush()

        moves_down = moves_down_after_enter + 1
        sys.stdout.write(f"\x1b[{moves_down}B\r")
        sys.stdout.flush()
        return value_str

    # Read user input from stdin. If initial_text is provided, prefill it as an
    # editable value. If the user submits an empty value and a default is
    # available, we apply the default and also render it into the input field
    # for visual consistency.
    if initial_text is not None:
        readline.set_startup_hook(lambda: readline.insert_text(str(initial_text)))

    try:
        value_str = input()
    finally:
        readline.set_startup_hook()

    used_default = False
    if value_str == "" and default is not None:
        value_str = str(default)
        used_default = True

    if used_default:
        max_value_len = max(0, width - input_column - 1)
        clipped_value = value_str[:max_value_len]
        sys.stdout.write(f"\x1b[1A\x1b[{input_column}G{clipped_value}\x1b[1B")
        sys.stdout.flush()

    if moves_down_after_enter:
        sys.stdout.write(f"\x1b[{moves_down_after_enter}B\r")
    else:
        sys.stdout.write("\r")
    sys.stdout.flush()
    return value_str


def selector(options: list[str], title: str) -> int:
    """Select an option from a list of options."""
    # rich_menu
    # text = rich_menu.Menu(*options, title=action.prompt).ask()
    # index = options.index(text)

    # # Show the selector choice
    # if show_result:
    #     tui.markdown_message(text=text, title=action.prompt)

    # return action.choices[index]

    menu = simple_term_menu.TerminalMenu(
        options,
        title=title,
    )
    index = menu.show()
    return index
