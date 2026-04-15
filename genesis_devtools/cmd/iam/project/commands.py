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
import uuid as sys_uuid

import rich_click as click
from genesis_devtools.common.table import get_table, print_table, show_data

from genesis_devtools.clients.base_client import get_user_api_client

from genesis_devtools.clients import project as project_lib
from genesis_devtools.common import utils


@click.group("projects", help="Manage projects in the Genesis installation")
def projects_group():
    pass


@projects_group.command("list", help="List projects")
@click.pass_context
def list_projects(
    ctx: click.Context,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    projects = project_lib.list_projects(client)
    _print_values(projects)


@projects_group.command("show", help="Show project")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.pass_context
def show_project(
    ctx: click.Context,
    uuid: str,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    if not utils.is_valid_uuid(uuid):
        projects = project_lib.list_projects(client, projectname=uuid)
        if projects:
            uuid = projects[0]["uuid"]
        else:
            raise click.ClickException(f"project with name {uuid} not found")
    data = project_lib.get_project(client, uuid)
    show_data(data)


@projects_group.command("delete", help="Delete project")
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help="project UUID",
)
@click.pass_context
def delete_project(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    project_lib.delete_project(client, uuid)


def _print_values(projects: tp.List[dict]) -> None:
    table = get_table()
    table.add_column("UUID")
    table.add_column("Name")
    table.add_column("Organization")
    table.add_column("Status")

    for project in projects:
        table.add_row(
            project["uuid"],
            project["name"],
            project["organization"],
            project["status"],
        )

    print_table(table)
