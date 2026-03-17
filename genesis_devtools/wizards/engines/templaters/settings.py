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

import importlib.resources
import json
import os
import pathlib
import shutil
import tempfile

from genesis_devtools.wizards.engines.templaters import functions
from genesis_devtools.wizards.scenarios import base as scenario_base


class TemplateSetting:
    TEMPLATE_INFO_SECTION = "template_info"
    FUNCTIONS_SECTION = "functions"

    def __init__(self, template_scenario: scenario_base.TemplateScenario):
        self._template_scenario = template_scenario
        self._settings_vars = self._load_template_settings(template_scenario)
        self._fill_template_parameters(template_scenario)

    def _load_template_settings(
        self,
        template_scenario: scenario_base.TemplateScenario,
    ) -> dict:
        """
        Build template settings from scenario actions.

        This method extracts the final values from scenario actions using each
        action ``result`` field.

        :param template_scenario: A template scenario with prepared actions.
        :type template_scenario: TemplateScenario
        :return: The resulting template settings.
        :rtype: dict
        """
        return {
            action_key: self._extract_result(action.result)
            for action_key, action in template_scenario
            if not isinstance(action.result, scenario_base.Scenario)
        }

    def _extract_result(
        self,
        action_result: scenario_base.ActionValueType | None,
    ) -> scenario_base.ActionValueType | dict | None:
        return action_result

    def _fill_template_parameters(
        self,
        template_scenario: scenario_base.TemplateScenario,
    ) -> None:
        """
        Fill template metadata based on the template scenario.

        :param template_scenario: The template scenario.
        :type template_scenario: TemplateScenario
        """
        self._name = template_scenario.name
        self._version = ""
        self._path = self._get_template_path(template_scenario.template)
        self._template_setting_path = self._path

    def save(self, new_project_settings_path: str) -> None:
        """
        Save the project settings to the specified path.

        This method takes the path to the new project settings file and saves
        the current project settings to the file.

        :param new_project_settings_path: The path to the new project settings
            file.
        :type new_project_settings_path: str
        """
        settings_vars = self.settings_vars
        settings_vars.pop(self.FUNCTIONS_SECTION)
        settings_vars.update(
            {
                self.TEMPLATE_INFO_SECTION: {
                    "name": self.name,
                    "version": self.version,
                    "template_file_name": self.file_name,
                }
            }
        )
        with open(new_project_settings_path, "w", encoding="utf-8") as fp:
            json.dump(settings_vars, fp, indent=4)

    def _get_template_path(self, path_from_settings: str) -> str:
        """
        Resolve the absolute path of the template by scenario template name.

        Scenario template value should be in ``dir0.dir1.target_template_dir``
        format and is resolved under the project ``templates`` directory.

        :param path_from_settings: Dot-based template path from scenario.
        :type path_from_settings: str
        :return: The absolute path of the template.
        :rtype: str
        """
        template_rel_path = pathlib.Path(*path_from_settings.split("."))
        templates_root = (
            importlib.resources.files("genesis_devtools")
            .joinpath("templates")
            .joinpath(template_rel_path)
        )

        tmp_dir = tempfile.TemporaryDirectory(prefix="genesis_devtools_templates_")
        self._tmp_dir = tmp_dir
        dst_root = pathlib.Path(tmp_dir.name)

        with importlib.resources.as_file(templates_root) as src_root:
            shutil.copytree(src_root, dst_root, dirs_exist_ok=True)

        return dst_root.as_posix()

    @property
    def settings_vars(self) -> dict:
        """
        The original template settings.

        :return: The original template settings.
        :rtype: dict
        """
        copy_settings = self._settings_vars.copy()
        copy_settings[self.FUNCTIONS_SECTION] = functions.get_jinja_functions()
        return copy_settings

    @property
    def name(self) -> str:
        """
        The name of the template setting.

        :return: The name of the template setting.
        :rtype: str
        """
        return self._name

    @property
    def version(self) -> str:
        """
        The version of the template setting.

        :return: The version of the template setting.
        :rtype: str
        """
        return self._version

    @property
    def path(self) -> str:
        """
        The path of the template setting.

        :return: The path of the template setting.
        :rtype: str
        """
        return self._path

    @property
    def template_files(self) -> list[str]:
        """
        Retrieve all file paths within the template directory.

        This property method traverses the template directory specified by the
        `path` attribute, collecting all directory and file paths.

        :return: A list of directory and file paths within the template
                 directory.
        :rtype: list
        """

        all_paths = []
        for dirpath, _, filenames in os.walk(self.path):
            all_paths.append(dirpath)
            for filename in filenames:
                full_file_path = os.path.join(dirpath, filename)
                all_paths.append(full_file_path)

        return all_paths

    @property
    def file_name(self) -> str:
        """
        The file name of the template setting.

        :return: The file name of the template setting.
        :rtype: str
        """
        return os.path.basename(self._template_setting_path)
