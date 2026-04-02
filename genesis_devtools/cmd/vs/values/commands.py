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

from genesis_devtools.clients import value as value_lib
from genesis_devtools.common import utils
from genesis_devtools import constants as c


@click.group("values", help="Manage values in the Genesis installation")
def values_group():
    pass


@values_group.command("list", help="List values")
@click.pass_context
def list_values(ctx: click.Context) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    values = value_lib.list_values(client)
    _print_values(values)


@values_group.command("show", help="Show value")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.pass_context
def show_value_cmd(
    ctx: click.Context,
    uuid: str,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    if not utils.is_valid_uuid(uuid):
        values = value_lib.list_values(client, name=uuid)
        if values:
            uuid = values[0]["uuid"]
        else:
            raise click.ClickException(f"Value with name {uuid} not found")
    value = value_lib.get_value(client, uuid)
    show_data(value)


@values_group.command("delete", help="Delete value")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.pass_context
def delete_value_cmd(
    ctx: click.Context,
    uuid: str,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    if not utils.is_valid_uuid(uuid):
        values = value_lib.list_values(client, name=uuid)
        if values:
            uuid = values[0]["uuid"]
        else:
            raise click.ClickException(f"Value with name {uuid} not found")
    value_lib.delete_value(client, uuid)


@values_group.command("add", help="Add a new value to the Genesis installation")
@click.pass_context
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help="UUID of the value",
)
@click.option(
    "-p",
    "--project-id",
    type=click.UUID,
    required=True,
    help="Name of the project in which to deploy the value",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default="test_value",
    help="Name of the value",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default="",
    help="Description of the value",
)
@click.option(
    "--var",
    type=str,
    default=None,
    help="UUID of a variable the value belongs to",
)
@click.option(
    "-V",
    "--value",
    type=click.STRING,
    default="",
    help="value",
)
def add_value_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    project_id: sys_uuid.UUID,
    name: str,
    description: str,
    var: str | None,
    value: str,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    if uuid is None:
        uuid = sys_uuid.uuid4()

    data = {
        "uuid": str(uuid),
        "project_id": str(project_id),
        "name": name,
        "description": description,
        "value": utils.convert_to_nearest_type(value),
    }

    # Validate variable UUID if provided
    if var:
        try:
            sys_uuid.UUID(var)
        except ValueError:
            raise click.ClickException(f"Variable {var} is not a valid UUID")
        data["variable"] = f"{c.VARIABLE_COLLECTION}{var}"

    value_resp = value_lib.add_value(client, data)
    show_data(value_resp)


@values_group.command("update", help="Update value")
@click.pass_context
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.option(
    "-p",
    "--project-id",
    type=click.UUID,
    default=None,
    help="Name of the project in which to deploy the value",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default=None,
    help="Name of the value",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default=None,
    help="Description of the value",
)
@click.option(
    "-V",
    "--value",
    type=click.STRING,
    default=None,
    help="value",
)
@click.option(
    "-v",
    "--variable",
    type=str,
    default=None,
    help="uuid of the variable",
)
def update_value_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID,
    project_id: sys_uuid.UUID | None,
    name: str | None,
    description: str | None,
    value: str | None,
    variable: str | None,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    data = {}
    if project_id is not None:
        data["project_id"] = str(project_id)
    if name is not None:
        data["name"] = name
    if description is not None:
        data["description"] = description
    if value is not None:
        data["value"] = utils.convert_to_nearest_type(value)
    if variable is not None:
        data["variable"] = variable
    value_resp = value_lib.update_value(client, uuid, data)
    show_data(value_resp)


def _print_values(values: tp.List[dict]) -> None:
    table = get_table()
    table.add_column("UUID")
    table.add_column("Project")
    table.add_column("Name")
    table.add_column("Variable")
    table.add_column("Value")
    table.add_column("ReadOnly")
    table.add_column("Status")

    for value in values:
        table.add_row(
            value["uuid"],
            value["project_id"],
            value["name"],
            value.get("variable", ""),
            str(value["value"]),
            str(value["read_only"]),
            value["status"],
        )

    print_table(table)
