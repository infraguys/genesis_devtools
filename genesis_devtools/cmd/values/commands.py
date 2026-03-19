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

import click
import prettytable

from gcl_sdk.clients.http import base as http_client

from genesis_devtools.clients import value as value_lib
from genesis_devtools.common import utils


@click.group("values", help="Manage values in the Genesis installation")
def values_group():
    pass


@values_group.command("list", help="List values")
@click.pass_context
def list_values(ctx: click.Context) -> None:
    client = ctx.obj.client
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
    client: http_client.CollectionBaseClient = ctx.obj.client
    if not utils.is_valid_uuid(uuid):
        values = value_lib.list_values(client, name=uuid)
        if values:
            uuid = values[0]["uuid"]
        else:
            raise click.ClickException(f"Value with name {uuid} not found")
    value = value_lib.get_value(client, uuid)
    _print_values([value])


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
    client: http_client.CollectionBaseClient = ctx.obj.client
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
    value: str,
) -> None:
    client: http_client.CollectionBaseClient = ctx.obj.client
    if uuid is None:
        uuid = sys_uuid.uuid4()
    value_resp = value_lib.add_value(
        client,
        {
            "uuid": str(uuid),
            "project_id": str(project_id),
            "name": name,
            "description": description,
            "value": _convert_to_nearest_type(value),
        },
    )
    _print_values([value_resp])


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
    client: http_client.CollectionBaseClient = ctx.obj.client
    data = {}
    if project_id is not None:
        data["project_id"] = str(project_id)
    if name is not None:
        data["name"] = name
    if description is not None:
        data["description"] = description
    if value is not None:
        data["value"] = _convert_to_nearest_type(value)
    if variable is not None:
        data["variable"] = variable
    value_resp = value_lib.update_value(client, uuid, data)
    _print_values([value_resp])


def _print_values(values: tp.List[dict]) -> None:
    table = prettytable.PrettyTable()
    table.field_names = [
        "UUID",
        "Project",
        "Name",
        "Variable",
        "Value",
        "ReadOnly",
        "Status",
    ]

    for value in values:
        table.add_row(
            [
                value["uuid"],
                value["project_id"],
                value["name"],
                value.get("variable", ""),
                value["value"],
                value["read_only"],
                value["status"],
            ]
        )

    click.echo(table)


def _convert_to_nearest_type(value: str) -> bool | int | float | list | dict | str:
    """
    Convert input string to the nearest appropriate type.

    Args:
        value: String value to convert

    Returns:
        Converted value in appropriate type (bool, int, float, list, dict, or str)
    """
    # Try boolean
    if value.lower() in ("true", "false"):
        return value.lower() == "true"

    # Try integer
    try:
        return int(value)
    except ValueError:
        pass

    # Try float
    try:
        return float(value)
    except ValueError:
        pass

    # Try list (JSON array or object)
    if (value.startswith("[") and value.endswith("]")) or (
        value.startswith("[") and value.endswith("]")
    ):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, (list, dict)):
                return parsed
        except (ValueError, TypeError):
            pass

    # Return as string if no other type matches
    return value
