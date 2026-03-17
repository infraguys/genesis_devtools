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

import dataclasses

from genesis_devtools.wizards.scenarios import base


@dataclasses.dataclass
class CICDScenario(base.TemplateScenario):
    name: str = "cicd"
    description: str = (
        "CI/CD pipeline configuration scenario for generating "
        "project automation workflows"
    )


@dataclasses.dataclass
class GitHubScenario(CICDScenario):
    name: str = "github"
    description: str = (
        "Generate CI/CD configuration targeting GitHub workflows and conventions"
    )


@dataclasses.dataclass
class GitLabScenario(CICDScenario):
    name: str = "gitlab"
    description: str = (
        "Generate GitLab CI/CD configuration (pipeline, image, and runner tag settings)"
    )
    template: str = "cicd.gitlab"
    actions: dict = dataclasses.field(
        default_factory=lambda: {
            "gitlab_genesis_installations": base.Action(
                "List of installations(comma-separated)",
                description=(
                    "List of Genesis installations (stands) that should be deployed. "
                    "Each installation should be a valid Genesis installation name. "
                    "For example: `stage,preprod,prod`"
                ),
                required=True,
            ),
            "gitlab_runner_tag": base.Action(
                "GitLab runner tag", required=True, default="genesis"
            ),
            "gitlab_deploy_mode": base.Action(
                "GitLab deploy mode",
                choices=[
                    "manual",
                    "on_success",
                ],
            ),
            "gitlab_templates_repo": base.Action(
                "Name of templates repository",
                description=(
                    "Name of the GitLab templates repository. "
                    "For example: `ci-templates`"
                ),
                default="ci-templates",
            ),
        }
    )


@dataclasses.dataclass
class GitHubAndGitLabScenario(CICDScenario):
    name: str = "github+gitlab"
    description: str = (
        "Generate CI/CD configuration for both GitHub and GitLab in a single project"
    )


@dataclasses.dataclass
class NoCICDScenario(CICDScenario):
    name: str = "none"
    description: str = "Do not generate CI/CD configuration files for this project"
