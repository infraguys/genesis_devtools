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
import pathlib

import jinja2

from genesis_devtools.wizards.engines import base
from genesis_devtools.wizards.engines.templaters import settings
from genesis_devtools.wizards.scenarios import base as scenarios


class JinjaTemplateEngine(base.AbstractEngine):
    """Jinja template engine class."""

    def __init__(
        self,
        template_scenario: scenarios.TemplateScenario,
        target_path: str | pathlib.Path,
        force: bool = False,
    ):
        super().__init__()
        self._settings = []
        for scenario in template_scenario.flatten():
            scenario_actions = list(scenario)
            if scenario_actions and all(
                isinstance(action.result, scenarios.Scenario)
                for _, action in scenario_actions
            ):
                continue

            self._settings.append(settings.TemplateSetting(scenario))
        self._target_path = pathlib.Path(str(target_path))
        self._force = force

        if not self._target_path.is_dir():
            raise ValueError(
                f"Target path must be a directory, not a file `{self._target_path}`"
            )

    def _render_template_files(
        self,
        template_path: str,
        template_files: list[str],
        all_settings: dict,
    ) -> list[str]:
        target_files = [
            jinja2.Template(template_file).render(**all_settings)
            for template_file in template_files
        ]

        # Replace template path prefix to repository path prefix
        target_files = [
            (self._target_path / target_file[len(template_path) + 1 :]).as_posix()
            for target_file in target_files
        ]

        # Save rendered files to have an ability to rollback
        saved_files = []

        for source_path, target_path in zip(template_files, target_files):
            if (
                not self._force
                and os.path.exists(target_path)
                and not os.path.isdir(target_path)
            ):
                raise FileExistsError(f"File {target_path} already exists")

            # create directory if it does not exist
            if os.path.isdir(source_path):
                os.makedirs(target_path, exist_ok=True)
                continue

            # Render and copy files
            with open(source_path, "r", encoding="utf-8") as fp1:
                with open(target_path, "w", encoding="utf-8") as fp2:
                    fp2.write(jinja2.Template(fp1.read()).render(**all_settings))
                    saved_files.append(target_path)

        return saved_files

    def run(self) -> None:
        """Run the engine."""
        self.render_template()

    def render_template(self):
        # Collect all settings
        all_settings = {}
        for template_settings in self._settings:
            all_settings.update(template_settings.settings_vars)

        # Save rendered files to have an ability to rollback
        saved_files = []

        for template_settings in self._settings:
            try:
                saved_files += self._render_template_files(
                    template_settings.path,
                    template_settings.template_files,
                    all_settings,
                )
            except FileExistsError:
                # Revert all already saved files
                for saved_file in saved_files:
                    os.remove(saved_file)
                raise
