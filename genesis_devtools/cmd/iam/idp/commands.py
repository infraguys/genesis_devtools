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

import json
import typing as tp
import uuid as sys_uuid

import rich_click as click
from genesis_devtools.common.table import get_table, print_table, show_data

from genesis_devtools.clients import base_client

from genesis_devtools import utils
from genesis_devtools import constants as c

ENTITY = "idp"
ENTITY_COLLECTION = c.IDP_COLLECTION


@click.group(f"{ENTITY}s", help=f"Manage {ENTITY}s in the Genesis installation")
def idps_group():
    pass


@idps_group.command("list", help=f"List {ENTITY}s")
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
def list_cmd(ctx: click.Context, filters: tuple[str, ...]) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    filters = utils.convert_input_multiply(filters)
    entities = base_client.list_entities(client, ENTITY_COLLECTION, **filters)
    _print_entities(entities)


@idps_group.command("show", help=f"Show {ENTITY}")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.pass_context
def show_cmd(
    ctx: click.Context,
    uuid: str,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    data = base_client.get_entity(client, ENTITY_COLLECTION, uuid)
    show_data(data)


@idps_group.command("delete", help=f"Delete {ENTITY}")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.pass_context
def delete_cmd(
    ctx: click.Context,
    uuid: str,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    base_client.delete_entity(client, ENTITY_COLLECTION, uuid)


@idps_group.command("add", help=f"Add a new {ENTITY} to the Genesis installation")
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
    default=f"test_{ENTITY}",
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
    "-p",
    "--project-id",
    type=click.UUID,
    required=True,
    help="Uuid of the project",
)
@click.option(
    "-i",
    "--iam-client",
    type=click.UUID,
    required=True,
    help="Uuid of iam_client",
)
@click.option(
    "--scope",
    type=str,
    required=False,
    help="scope",
)
@click.option(
    "--nonce_required",
    type=bool,
    is_flag=True,
    default=True,
)
@click.option(
    "--callback",
    type=str,
    required=True,
    help="JSON string for callbacks",
)
def add_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    name: str,
    description: str,
    project_id: sys_uuid.UUID,
    iam_client: sys_uuid.UUID,
    scope: str | None,
    nonce_required: bool,
    callback: str,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    if uuid is None:
        uuid = sys_uuid.uuid4()
    try:
        # Convert string to dictionary
        callback_data = json.loads(callback)
    except json.JSONDecodeError:
        click.echo(f"Error: Invalid JSON string: '{callback}'", err=True)
        return

    data = {
        "uuid": str(uuid),
        "name": name,
        "description": description,
        "project_id": str(project_id),
        "iam_client": f"{c.CLIENT_COLLECTION}{iam_client}",
        "nonce_required": nonce_required,
        "callback": callback_data,
    }
    if scope is not None:
        data["scope"] = scope

    entity = base_client.add_entity(client, ENTITY_COLLECTION, data)
    show_data(entity)


def _print_entities(idps: tp.List[dict]) -> None:
    table = get_table()
    table.add_column("UUID")
    table.add_column("Name")
    table.add_column("Scope")
    table.add_column("Iam_client")
    table.add_column("Status")

    for idp in idps:
        table.add_row(
            idp["uuid"],
            idp["name"],
            idp["scope"],
            idp["iam_client"],
            idp["status"],
        )

    print_table(table)
