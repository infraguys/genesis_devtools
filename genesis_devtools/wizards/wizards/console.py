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

import typing as tp

import rich_click as click

from genesis_devtools.wizards.wizards import base
from genesis_devtools.wizards.scenarios import base as scenarios
from genesis_devtools.wizards.wizards import terminal as tui


class SimpleConsoleWizard(base.AbstractWizard):
    """Simple console wizard class."""

    def _interactive_selector(
        self,
        title: str,
        options: tp.Collection[tuple[str, str | None]],
    ) -> str:
        click.echo(f"\n{title}")
        click.echo(
            "Use Arrow Up / Arrow Down to switch options. Press Enter to confirm."
        )

        index = 0

        while True:
            value, description = options[index]
            if description:
                click.echo(f"\r> {value} - {description}", nl=False)
            else:
                click.echo(f"\r> {value}", nl=False)

            key = click.getchar()
            if key in ("\r", "\n"):
                click.echo("")
                return value

            if key in ("\x1b[A", "\x1bOA"):
                index = (index - 1) % len(options)
                continue
            if key in ("\x1b[B", "\x1bOB"):
                index = (index + 1) % len(options)
                continue

            if key != "\x1b":
                continue

            sequence_head = click.getchar()
            sequence_tail = click.getchar()
            if sequence_head not in ("[", "O"):
                continue

            if sequence_tail == "A":
                index = (index - 1) % len(options)
            elif sequence_tail == "B":
                index = (index + 1) % len(options)

    def play_action(
        self, action: scenarios.Action, initial_value: str | None = None
    ) -> tp.Any:
        """Play a single action."""
        # Ask a user to provide a value
        if action.choices:
            if not isinstance(action.choices[0], scenarios.Scenario):
                options = [(str(c), None) for c in action.choices]
                return self._interactive_selector(action.prompt, options)

            options = [(c.name, c.description) for c in action.choices]
            name = self._interactive_selector(action.prompt, options)
            return next(c for c in action.choices if c.name == name)

        if action.default:
            return click.prompt(
                action.prompt, default=action.default, show_default=True
            )
        else:
            return click.prompt(action.prompt)

    def welcome(self, scenario: scenarios.Scenario) -> None:
        """Display a welcome message."""
        if scenario.welcome:
            content = scenario.welcome
            if callable(content):
                content = content()
            click.secho(content)

    def summary(self, scenario: scenarios.Scenario) -> None:
        """Display a summary message."""
        if scenario.summary:
            content = scenario.summary
            if callable(content):
                content = content()
            click.secho(content)


class ConsoleWizard(SimpleConsoleWizard):
    """Console wizard class."""

    def play_action(
        self, action: scenarios.Action, initial_value: str | None = None
    ) -> tp.Any:
        """Play a single action."""
        # Just display the prompt with initial value if provided
        # and return it
        if initial_value is not None:
            tui.framed_prompt(
                action.prompt,
                action.description,
                initial_text=initial_value,
                user_input=False,
            )
            return initial_value

        # Ask a user to provide a value
        if action.choices:
            if not isinstance(action.choices[0], scenarios.Scenario):
                options = [str(c) for c in action.choices]
            else:
                options = [f"{c.name} - {c.description}" for c in action.choices]

            index = tui.selector(options, action.prompt)
            return action.choices[index]

        if action.default:
            return tui.framed_prompt(action.prompt, action.description, action.default)

        return tui.framed_prompt(action.prompt, action.description)

    def welcome(self, scenario: scenarios.Scenario) -> None:
        """Display a welcome message."""
        if scenario.welcome:
            content = scenario.welcome
            if callable(content):
                content = content()

            if content:
                tui.markdown_message(
                    text=content,
                    with_border=True,
                )

    def summary(self, scenario: scenarios.Scenario) -> None:
        """Display a summary message."""
        if scenario.summary:
            content = scenario.summary
            if callable(content):
                content = content()

            if content:
                tui.markdown_message(
                    text=content,
                    with_border=True,
                )
