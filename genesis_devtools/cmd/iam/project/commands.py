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

from genesis_devtools.clients import base_client

from genesis_devtools import utils
from genesis_devtools import constants as c

ENTITY = "project"


@click.group("projects", help=f"Manage {ENTITY}s in the Genesis installation")
def projects_group():
    pass


@projects_group.command("list", help=f"List {ENTITY}s")
@click.option(
    "-f",
    "--filters",
    multiple=True,
    help=(
        "Additional filters to pass to the api. "
        "The format is 'key=value'. For example: --f "
        "parent=11111111-1111-1111-1111-11111111111 --filters status=NEW"
    ),
)
@click.pass_context
def list_projects(
    ctx: click.Context,
    filters: tuple[str, ...],
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    filters = utils.convert_input_multiply(filters)
    entities = base_client.list_entities(client, c.PROJECT_COLLECTION, **filters)
    _print_entities(entities)


@projects_group.command("show", help=f"Show {ENTITY}")
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
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    data = base_client.get_entity(client, c.PROJECT_COLLECTION, uuid)
    show_data(data)


@projects_group.command("delete", help=f"Delete {ENTITY}")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.pass_context
def delete_project(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    base_client.delete_entity(client, c.PROJECT_COLLECTION, uuid)


@projects_group.command("add", help=f"Add a new {ENTITY} to the Genesis installation")
@click.pass_context
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help=f"UUID of the {ENTITY}",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default=f"test-{ENTITY}",
    help=f"Name of the {ENTITY}",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default="",
    help=f"Description of the {ENTITY}",
)
@click.option(
    "-o",
    "--organization",
    type=click.UUID,
    required=True,
    help="uuid of parent organization",
)
def add_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    name: str,
    description: str,
    organization: sys_uuid.UUID,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    if uuid is None:
        uuid = sys_uuid.uuid4()

    data = {
        "uuid": str(uuid),
        "name": name,
        "description": description,
        "organization": f"{c.ORGANIZATION_COLLECTION}{organization}",
    }

    entity = base_client.add_entity(client, c.PROJECT_COLLECTION, data)
    show_data(entity)


def _print_entities(projects: tp.List[dict]) -> None:
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
