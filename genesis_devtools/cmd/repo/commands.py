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

import click
import prettytable
from genesis_devtools.repo import base as base_repo
from genesis_devtools.repo import utils as repo_utils

from genesis_devtools import constants as c


@click.group("repo", help="Manager Genesis repository")
def repository_group():
    pass


@repository_group.command("init", help="Initialize the repository")
@click.option(
    "-c",
    "--genesis-cfg-file",
    default=c.DEF_GEN_CFG_FILE_NAME,
    help="Name of the project configuration file",
)
@click.option(
    "-t",
    "--target",
    default=None,
    help="Target repository to push to",
)
@click.option(
    "-f",
    "--force",
    show_default=True,
    is_flag=True,
    help="Force init even if the repo already exists",
)
@click.argument("project_dir", type=click.Path(), default=".")
def repo_init_cmd(
    genesis_cfg_file: str,
    target: str | None,
    force: bool,
    project_dir: str,
) -> None:
    driver = repo_utils.load_repo_driver(genesis_cfg_file, target, project_dir)

    try:
        driver.init_repo()
    except base_repo.RepoAlreadyExistsError:
        if force:
            driver.delete_repo()
            driver.init_repo()
            return

        click.secho(
            "Repository already exists.",
            fg="red",
        )


@repository_group.command("delete", help="Delete the repository")
@click.option(
    "-c",
    "--genesis-cfg-file",
    default=c.DEF_GEN_CFG_FILE_NAME,
    help="Name of the project configuration file",
)
@click.option(
    "-t",
    "--target",
    default=None,
    help="Target repository to push to",
)
@click.argument("project_dir", type=click.Path(), default=".")
def repo_delete_cmd(
    genesis_cfg_file: str,
    target: str | None,
    project_dir: str,
) -> None:
    driver = repo_utils.load_repo_driver(genesis_cfg_file, target, project_dir)
    driver.delete_repo()


@repository_group.command("list", help="List the repository")
@click.option(
    "-c",
    "--genesis-cfg-file",
    default=c.DEF_GEN_CFG_FILE_NAME,
    help="Name of the project configuration file",
)
@click.option(
    "-t",
    "--target",
    default=None,
    help="Target repository to push to",
)
@click.option(
    "-e",
    "--element",
    default=None,
    help="Element to list",
)
@click.argument("project_dir", type=click.Path(), default=".")
def repo_list_cmd(
    genesis_cfg_file: str,
    target: str | None,
    element: str | None,
    project_dir: str,
) -> None:
    table = prettytable.PrettyTable()

    driver = repo_utils.load_repo_driver(genesis_cfg_file, target, project_dir)
    try:
        elements = driver.list()
    except base_repo.RepoNotFoundError:
        click.secho("Repository not found", fg="red")
        return

    if element is not None:
        if element not in elements:
            raise click.UsageError(f"Element {element} not found")

        table.field_names = [
            "version",
        ]

        for version in sorted(elements[element]):
            table.add_row([version])

        click.echo(table)
        return

    table.field_names = [
        "name",
        "last version",
        "versions",
    ]

    for element in elements:
        table.add_row([element, sorted(elements[element])[-1], len(elements[element])])

    click.echo(table)
