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

import pathlib
import json
import typing as tp
import rich_click as click

from genesis_devtools.builder import base as base_builder
from genesis_devtools.common.table import get_table, print_table
from genesis_devtools.repo import base as base_repo
from genesis_devtools.repo import utils as repo_utils
from genesis_devtools import constants as c

if tp.TYPE_CHECKING:
    from genesis_devtools.common.cmd_context import ContextObject


@click.group("repo", help="Manage Genesis repository")
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
@click.pass_obj
def repo_init_cmd(
    obj: "ContextObject",
    genesis_cfg_file: str,
    target: str | None,
    force: bool,
    project_dir: str,
) -> None:

    driver = repo_utils.load_repo_driver(
        genesis_cfg_file, target, project_dir, obj.cfg_path
    )

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
@click.pass_obj
def repo_delete_cmd(
    obj: "ContextObject",
    genesis_cfg_file: str,
    target: str | None,
    project_dir: str,
) -> None:
    driver = repo_utils.load_repo_driver(
        genesis_cfg_file, target, project_dir, obj.cfg_path
    )
    driver.delete_repo()


@repository_group.command("list", help="List elements in the repository")
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
@click.pass_obj
def repo_list_cmd(
    obj: "ContextObject",
    genesis_cfg_file: str,
    target: str | None,
    element: str | None,
    project_dir: str,
) -> None:
    table = get_table()
    driver = repo_utils.load_repo_driver(
        genesis_cfg_file, target, project_dir, obj.cfg_path
    )
    try:
        elements = driver.list()
    except base_repo.RepoNotFoundError:
        click.secho("Repository not found", fg="red")
        return

    click.secho(f"Repository: {driver.name}", fg="green")
    if element is not None:
        if element not in elements:
            raise click.UsageError(f"Element {element} not found")

        table.add_column("version")

        for version in sorted(elements[element]):
            table.add_row(version)

        print_table(table)
        return

    table.add_column("name")
    table.add_column("last version")
    table.add_column("versions")

    for element in elements:
        table.add_row(
            element, sorted(elements[element])[-1], str(len(elements[element]))
        )

    print_table(table)


@repository_group.command("push", help="Push the element to the repository")
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
    "--element-dir",
    default=c.DEF_GEN_OUTPUT_DIR_NAME,
    help="Directory where element artifacts are stored",
    type=click.Path(),
)
@click.option(
    "-f",
    "--force",
    show_default=True,
    is_flag=True,
    help="Force push even if the element already exists",
)
@click.option(
    "-l",
    "--latest",
    show_default=True,
    is_flag=True,
    help="Push the element too as the latest version (if stable version)",
)
@click.argument("project_dir", type=click.Path(), default=".")
@click.pass_obj
def push_cmd(
    obj: "ContextObject",
    genesis_cfg_file: str,
    target: str | None,
    element_dir: str,
    force: bool,
    latest: bool,
    project_dir: str,
) -> None:
    driver = repo_utils.load_repo_driver(
        genesis_cfg_file, target, project_dir, obj.cfg_path
    )

    # Push elements
    path = pathlib.Path(element_dir) / base_builder.ElementInventory.file_name
    with open(path, "r") as f:
        inventories = json.load(f)

    # Backward compatibility: support both single
    # inventory and list of inventories
    if not isinstance(inventories, list):
        inventories = [inventories]

    for inventory in inventories:
        element = base_builder.ElementInventory.from_dict(inventory)
        try:
            driver.push(element, latest=latest)
        except base_repo.ElementAlreadyExistsError:
            if force:
                driver.remove(element)
                driver.push(element, latest=latest)
                continue

            click.secho(
                f"Element {element.name} version {element.version} already exists.",
                fg="red",
            )
