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

import os
import textwrap
import typing as tp

import rich_click as click

from genesis_devtools.wizards.scenarios import platformizers
from genesis_devtools.wizards.engines.templaters import templaters
from genesis_devtools.wizards.wizards import console


def _iter_all_actions(
    scenario: platformizers.PlatformizerScenario,
) -> tp.Iterator[tuple[str, platformizers.base.Action]]:
    visited_scenarios: set[int] = set()
    visited_action_keys: set[str] = set()

    def walk(
        scn: platformizers.base.Scenario,
    ) -> tp.Iterator[tuple[str, platformizers.base.Action]]:
        scn_id = id(scn)
        if scn_id in visited_scenarios:
            return
        visited_scenarios.add(scn_id)

        for action_key, action in scn.actions.items():
            if action_key not in visited_action_keys:
                visited_action_keys.add(action_key)
                yield action_key, action

            if isinstance(action.result, platformizers.base.Scenario):
                yield from walk(action.result)

            if action.choices:
                for choice in action.choices:
                    if isinstance(choice, platformizers.base.Scenario):
                        yield from walk(choice)

    yield from walk(scenario)


def _dynamic_help() -> str:
    """Generate dynamic help text for all scenario actions."""

    scenario = platformizers.PlatformizerScenario()

    lines: list[str] = []
    lines.append("Dynamic options (derived from scenario actions):")
    lines.append("")

    for action_key, action in sorted(_iter_all_actions(scenario), key=lambda x: x[0]):
        option_name = f"--{action_key.replace('_', '-')}"
        prompt = action.prompt

        if action.description:
            desc = " ".join(str(action.description).split())
            msg = f"{option_name}: {prompt}. {desc}"
        else:
            msg = f"{option_name}: {prompt}"

        wrapped = textwrap.fill(
            msg,
            width=88,
            initial_indent="  ",
            subsequent_indent="    ",
            break_long_words=False,
            break_on_hyphens=False,
        )
        lines.append(wrapped)

    return "\n".join(lines)


def _parse_extra_args(
    extra_args: list[str],
    ignored_keys: set[str] | None = None,
) -> dict[str, tp.Any]:
    result: dict[str, tp.Any] = {}
    ignored_keys = ignored_keys or set()
    i = 0

    while i < len(extra_args):
        token = extra_args[i]

        if not token.startswith("--") or len(token) <= 2:
            i += 1
            continue

        key, sep, value = token[2:].partition("=")
        key = key.replace("-", "_")

        if key in ignored_keys:
            i += 1
            continue

        if sep:
            result[key] = value
            i += 1
        elif i + 1 < len(extra_args) and not extra_args[i + 1].startswith("--"):
            result[key] = extra_args[i + 1]
            i += 2
        else:
            result[key] = True
            i += 1

    return result


class _InitDynamicHelpCommand(click.Command):
    def parse_args(self, ctx: click.Context, args: list[str]) -> list[str]:
        ctx.meta["raw_init_args"] = list(args)
        return super().parse_args(ctx, args)

    def get_help(self, ctx: click.Context) -> str:
        base_help = super().get_help(ctx)
        return f"{base_help}\n\n{_dynamic_help()}\n"


@click.command(
    cls=_InitDynamicHelpCommand,
    context_settings={
        "ignore_unknown_options": True,
        "allow_extra_args": True,
    },
    help="Platformize the project",
)
@click.option(
    "--force",
    show_default=True,
    is_flag=True,
    help="Overwrite existing generated files",
)
@click.option(
    "--project-dir",
    show_default=True,
    type=click.Path(),
    default=".",
    help="Project directory",
)
# TODO(akremenetsky): Add build-dependencies
@click.pass_context
def init_cmd(
    ctx: click.Context,
    force: bool,
    project_dir: str,
) -> None:
    defaults: dict[str, tp.Any] = {}
    raw_args = list(ctx.meta.get("raw_init_args", []))
    defaults.update(_parse_extra_args(raw_args, ignored_keys={"force"}))

    platformizer = platformizers.PlatformizerScenario()
    wizard = console.ConsoleWizard()
    scenario = wizard.run(platformizer, defaults=defaults)
    template_engine = templaters.JinjaTemplateEngine(
        template_scenario=scenario,
        target_path=os.path.abspath(project_dir),
        force=force,
    )

    # Run the template engine to render templates and initialize the project
    try:
        template_engine.run()
    except FileExistsError:
        click.secho(
            "Error: Some files already exist. Use --force to overwrite.",
            fg="red",
            err=True,
        )
        raise click.Abort()
