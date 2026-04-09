#    Copyright 2025 Genesis Corporation.
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


class ClickAliasedGroup(click.Group):
    def __init__(self, *args: tp.Any, **kwargs: tp.Any) -> None:
        super().__init__(*args, **kwargs)
        self._commands: tp.Dict[str, list[str]] = {}
        self._aliases: tp.Dict[str, str] = {}

    def add_command(self, *args: tp.Any, **kwargs: tp.Any) -> None:
        aliases = kwargs.pop("aliases", [])
        super().add_command(*args, **kwargs)
        if aliases:
            cmd = args[0]
            name = args[1] if len(args) > 1 else None
            name = name or cmd.name
            if name is None:
                raise TypeError("Command has no name.")

            self._commands[name] = aliases
            for alias in aliases:
                self._aliases[alias] = name

    def command(  # type: ignore[override]
        self, *args: tp.Any, **kwargs: tp.Any
    ) -> tp.Union[
        tp.Callable[[tp.Callable[..., tp.Any]], click.Command], click.Command
    ]:
        aliases = kwargs.pop("aliases", [])
        decorator = super().command(*args, **kwargs)
        if not aliases:
            return decorator

        def _decorator(f):
            cmd = decorator(f)
            if aliases:
                self._commands[cmd.name] = aliases
                for alias in aliases:
                    self._aliases[alias] = cmd.name
            return cmd

        return _decorator

    def group(  # type: ignore[override]
        self, *args: tp.Any, **kwargs: tp.Any
    ) -> tp.Union[tp.Callable[[tp.Callable[..., tp.Any]], click.Group], click.Group]:
        aliases = kwargs.pop("aliases", [])
        decorator = super().group(*args, **kwargs)
        if not aliases:
            return decorator

        def _decorator(f):
            cmd = decorator(f)
            if aliases:
                self._commands[cmd.name] = aliases
                for alias in aliases:
                    self._aliases[alias] = cmd.name
            return cmd

        return _decorator

    def resolve_alias(self, cmd_name: str) -> str:
        if cmd_name in self._aliases:
            return self._aliases[cmd_name]
        return cmd_name

    def get_command(
        self, ctx: click.Context, cmd_name: str
    ) -> tp.Optional[click.Command]:
        cmd_name = self.resolve_alias(cmd_name)
        command = super().get_command(ctx, cmd_name)
        if command:
            return command
        return None

    def format_commands(
        self, ctx: click.Context, formatter: click.HelpFormatter
    ) -> None:
        rows = []

        sub_commands = self.list_commands(ctx)

        max_len = 0
        if len(sub_commands) > 0:
            max_len = max(len(cmd) for cmd in sub_commands)

        limit = formatter.width - 6 - max_len

        for sub_command in sub_commands:
            cmd = self.get_command(ctx, sub_command)
            if cmd is None:
                continue
            if hasattr(cmd, "hidden") and cmd.hidden:
                continue
            if sub_command in self._commands:
                aliases = ",".join(sorted(self._commands[sub_command]))
                sub_command = f"{sub_command} ({aliases})"
            cmd_help = cmd.get_short_help_str(limit) or ""
            rows.append((sub_command, cmd_help))

        if rows:
            with formatter.section("Commands"):
                formatter.write_dl(rows)
