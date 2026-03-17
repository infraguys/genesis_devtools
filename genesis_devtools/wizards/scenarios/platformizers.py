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
import dataclasses

from genesis_devtools import utils
from genesis_devtools.wizards.scenarios import base
from genesis_devtools.wizards.scenarios import cicd

# Type aliases for better readability
A: type[base.Action] = base.Action


_PROJECT_WELCOME_FOOTER = """
\n\n
After generation, you can use the `genesis` command to 
[build](https://infraguys.github.io/genesis_devtools/cli/genesis_build/) 
and [deploy](https://infraguys.github.io/genesis_devtools/cli/genesis_deploy/) 
the element.\n\n
For more information about Genesis Core, please visit 
[https://infraguys.github.io/genesis_core](https://infraguys.github.io/genesis_core)
"""


@dataclasses.dataclass
class GenericProject(base.TemplateScenario):
    name: str = "generic_project"
    description: str = (
        "Generic language-agnostic project without a specific runtime or framework"
    )
    welcome: str = (
        "## Generic project\n\n"
        "This scenario generates Genesis and CI/CD configurations for "
        "a generic project. After generation, you will get "
        "three groups of files:\n"
        "- Manifest\n"
        "- Common Genesis configuration files like `genesis.yaml` and manifests\n"
        "- CI/CD configuration\n"
        "\n"
        "All files related to the Genesis configuration will be placed "
        "in the `genesis` directory. CI/CD configuration will be placed "
        "in the root of the project. " + _PROJECT_WELCOME_FOOTER
    )

    template: str = "platformizers.languages.common"
    actions: dict = dataclasses.field(
        default_factory=lambda: {
            "project_name": A(
                "Project name", required=True, default=utils.current_dir_name
            ),
            "author_name": A("Author name", default="Genesis developer"),
            "author_email": A("Author email", default="developer@genesis-core.tech"),
            "project_url": A("Project URL"),
        }
    )


@dataclasses.dataclass
class PythonProject(GenericProject):
    name: str = "python"
    template: str = "platformizers.languages.python"
    description: str = "Python backend project template with Genesis configuration and CI/CD scaffolding"
    welcome: str = (
        "## Python project\n\n"
        "This scenario generates Genesis and CI/CD configurations for "
        "a Python backend project. After generation, you will get "
        "three groups of files:\n"
        "- Manifest\n"
        "- Common Genesis configuration files like `genesis.yaml` and manifests\n"
        "- CI/CD configuration\n"
        "\n"
        "All files related to the Genesis configuration will be placed "
        "in the `genesis` directory. CI/CD configuration will be placed "
        "in the root of the project. " + _PROJECT_WELCOME_FOOTER
    )

    def __post_init__(self):
        project_node_paramters = {
            "project_systemd_services": A(
                "Project systemd services (comma-separated)",
                description=(
                    "List of systemd services that should be managed by the project. "
                    "Each service should be a valid systemd service name. "
                    "For example: `service1,service2,service3`"
                ),
            ),
            "project_python_package_manager": A(
                "Python package manager",
                choices=[
                    "uv",
                    "pip",
                ],
            ),
        }

        self.actions.update(project_node_paramters)


@dataclasses.dataclass
class NodeProjectBase(GenericProject):
    node_version: str = ""

    def _welcome(self) -> str:
        return (
            f"## Node.js {self.node_version} project\n\n"
            "This scenario generates Genesis and CI/CD configurations for "
            f"a Node.js {self.node_version} project. After generation, you will get "
            "three groups of files:\n"
            "- Manifest\n"
            "- Common Genesis configuration files like `genesis.yaml` and manifests\n"
            "- CI/CD configuration\n"
            "\n"
            "All files related to the Genesis configuration will be placed "
            "in the `genesis` directory. CI/CD configuration will be placed "
            "in the root of the project. " + _PROJECT_WELCOME_FOOTER
        )

    def __post_init__(self):
        super().__post_init__()
        self.welcome = self._welcome

        project_node_paramters = {
            "project_node_install_redis": A(
                "Install Redis",
                default=False,
                choices=[
                    False,
                    True,
                ],
                description=(
                    "Install Redis as a dependency for the project. "
                    "This will install Redis and configure it to be managed by the project. "
                ),
            ),
            "project_node_install_nginx": A(
                "Install Nginx",
                default=False,
                choices=[
                    False,
                    True,
                ],
                description=(
                    "Install Nginx as a dependency for the project. "
                    "This will install Nginx and configure it to be managed by the project. "
                ),
            ),
            "project_node_install_pm2": A(
                "Install PM2",
                default=False,
                choices=[
                    False,
                    True,
                ],
                description=(
                    "Install PM2 as a dependency for the project. "
                    "This will install PM2 and configure it to be managed by the project. "
                ),
            ),
            "project_node_packages": A(
                "Project packages (comma-separated)",
                description=(
                    "List of packages that should be managed by the project. "
                    "Each package should be a valid package name. "
                    "For example: `package1,package2,package3`"
                ),
            ),
            "project_node_user": A(
                "Project user",
                default="ubuntu",
                description="User that will be used to run the project services.",
            ),
        }

        self.actions.update(project_node_paramters)


@dataclasses.dataclass
class Node20Project(NodeProjectBase):
    name: str = "node20"
    template: str = "platformizers.languages.node20"
    description: str = "Node.js 20 backend project template with Genesis configuration and CI/CD scaffolding"
    node_version: str = "20"


@dataclasses.dataclass
class Node22Project(NodeProjectBase):
    name: str = "node22"
    template: str = "platformizers.languages.node22"
    description: str = "Node.js 22 backend project template with Genesis configuration and CI/CD scaffolding"
    node_version: str = "22"


@dataclasses.dataclass
class Node24Project(NodeProjectBase):
    name: str = "node24"
    template: str = "platformizers.languages.node24"
    description: str = "Node.js 24 backend project template with Genesis configuration and CI/CD scaffolding"
    node_version: str = "24"


@dataclasses.dataclass
class ProjectTypeSelector(base.TemplateScenario):
    name: str = "project_type_selector"
    description: str = "Project type selector to chose a project type"

    welcome: str = (
        "## Choose a platformizer for your project!\n\n"
        "To proceed, please select a project type you are working on.\n\n"
        "For more information about Genesis Core, please visit "
        "[https://infraguys.github.io/genesis_core]"
        "(https://infraguys.github.io/genesis_core)"
    )

    actions: dict = dataclasses.field(
        default_factory=lambda: {
            "project_type": A(
                "Choose project type",
                default=GenericProject(),
                choices=[
                    GenericProject(),
                    PythonProject(),
                ],
            ),
        }
    )


@dataclasses.dataclass
class ManifestPGConstructorScenario(base.TemplateScenario):
    name: str = "manifest_constructor"
    description: str = "Manifest constructor to prepare a manifest for the project"

    actions: dict = dataclasses.field(
        default_factory=lambda: {
            "enable_pgsql": base.ConfirmationAction(
                "The project uses PostgreSQL",
                default=False,
                choices=[
                    False,
                    True,
                ],
            ),
            "pgsql_usage_mode": A(
                "Use the communal PG cluster or create your own",
                default="communal",
                choices=[
                    "communal - The communal PG cluster, other projects can use it",
                    "own_cluster - Create your own PG cluster",
                ],
            ),
            "pgsql_database_name": A(
                "PostgreSQL database name",
                required=True,
                default=utils.current_dir_name,
            ),
            "pgsql_username": A(
                "PostgreSQL username",
                required=True,
                default=utils.current_dir_name,
            ),
        }
    )


@dataclasses.dataclass
class ManifestConstructorScenario(base.TemplateScenario):
    name: str = "manifest_constructor"
    description: str = "Manifest constructor to prepare a manifest for the project"

    # NOTE(akremenetsky): The template will be determined after
    # finishing the scenario
    template: str = ""

    welcome: str = (
        "## Choose infrastructure requirements\n\n"
        "This group of questions will help you to choose the right infrastructure "
        "requirements for your project and prepare a manifest based on them.\n\n"
        "For more information about Genesis Core, please visit "
        "[https://infraguys.github.io/genesis_core]"
        "(https://infraguys.github.io/genesis_core)"
    )

    actions: dict = dataclasses.field(
        default_factory=lambda: {
            "manifest_description": A(
                "Manifest description",
                default="",
                description=(
                    "**Manifest** is a YAML file that specifies the project's "
                    "dependencies, infrastructure configuration, and other "
                    "settings. "
                    "Follow the [developer guide]"
                    "(https://infraguys.github.io/genesis_core/guides/developer/elements/) "
                    "for more details."
                ),
            ),
            "repository": A(
                "Repository",
                default="https://repository.genesis-core.tech/genesis-elements",
                description=(
                    "Choose the repository where the elements will be stored. "
                    "It can be a local or remote repository. "
                    "The public repository is used by default."
                ),
            ),
            "manifest_constructor_pg": A(
                "Manifest PostgreSQL constructor",
                result=ManifestPGConstructorScenario(),
            ),
        }
    )

    def _finalize_template(self) -> str:
        base_prefix = "platformizers.manifests"

        # FIXME(akremenetsky): The current logic is pretty simple.
        # We can use `stateless` or a manifest with PG cluster.
        pg_scenario = self.actions["manifest_constructor_pg"].result
        enable_pgsql = pg_scenario.actions["enable_pgsql"].result

        if enable_pgsql:
            pgsql_usage_mode = pg_scenario.actions["pgsql_usage_mode"].result

            if pgsql_usage_mode.startswith("communal"):
                main_template = "pgsql_communal"
            else:
                main_template = "pgsql"
        else:
            main_template = "stateless"

        self.template = f"{base_prefix}.{main_template}"

        # Keep summary is empty
        return None

    def __post_init__(self):
        # We don't need summary for this scenario but some finilization
        # logic is needed
        # FIXME(akremenetsky): Dedicated logic for finalization
        self.summary = self._finalize_template


@dataclasses.dataclass
class PlatformizerScenario(base.TemplateScenario):
    name: str = "platformizer_scenario"
    description: str = "Platformizer scenario"

    template: str = "platformizers.empty"
    welcome: str = (
        "## Choose a platformizer for your project!\n\n"
        "To proceed, please select a project type you are working on.\n\n"
        "For more information about Genesis Core, please visit "
        "[https://infraguys.github.io/genesis_core]"
        "(https://infraguys.github.io/genesis_core)"
    )

    actions: dict = dataclasses.field(
        default_factory=lambda: {
            "project_type": A(
                "Choose project type",
                default=GenericProject(),
                choices=[
                    GenericProject(),
                    PythonProject(),
                    Node20Project(),
                    Node22Project(),
                    Node24Project(),
                ],
            ),
            "manifest_constructor": A(
                "Manifest constructor",
                result=ManifestConstructorScenario(),
            ),
            "ci_cd": A(
                "CI/CD configuration",
                default=cicd.GitLabScenario(),
                choices=[
                    cicd.GitLabScenario(),
                    cicd.GitHubScenario(),
                    cicd.GitHubAndGitLabScenario(),
                    cicd.NoCICDScenario(),
                ],
            ),
        }
    )

    def _summary(self) -> str:
        summary_template = (
            "## Summary\n\n"
            "- Genesis configuration -> `{genesis_path}`\n"
            "- Manifest for {project_name} -> `{manifest_path}`\n"
            "- Image provisioning script -> `{install_sh_path}`\n"
            "- Node bootstrap script -> `{bootstrap_sh_path}`\n\n"
            "Please check files and adjust them to your needs.\n\n"
            "#### Next steps\n\n"
            "To [build]"
            "(https://infraguys.github.io/genesis_devtools/cli/genesis_build/) "
            "the element use command\n\n```bash\n genesis build .\n```\n\n"
            "#### Docs\n\n"
            "For more information about Genesis Core, please visit "
            "[https://infraguys.github.io/genesis_core]"
            "(https://infraguys.github.io/genesis_core)"
        )

        genesis_path = os.path.join("genesis", "genesis.yaml")

        project_name = (
            self.actions["project_type"].result.actions["project_name"].result
        )

        manifest_path = os.path.join("genesis", "manifests", f"{project_name}.yaml.j2")

        install_sh_path = os.path.join("genesis", "images", "install.sh")

        bootstrap_sh_path = os.path.join("genesis", "images", "bootstrap.sh")

        return summary_template.format(
            genesis_path=genesis_path,
            manifest_path=manifest_path,
            project_name=project_name,
            install_sh_path=install_sh_path,
            bootstrap_sh_path=bootstrap_sh_path,
        )

    def __post_init__(self):
        # Set the summary after initialization to have
        # references to instance attributes
        self.summary = self._summary
