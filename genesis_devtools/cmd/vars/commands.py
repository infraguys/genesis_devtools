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
from genesis_devtools.common.table import get_table, print_table
from bazooka import exceptions as bazooka_exc

from gcl_sdk.clients.http import base as http_client

from genesis_devtools import constants as c
from genesis_devtools.clients import value as value_lib
from genesis_devtools.clients import variable as variable_lib
from genesis_devtools.common import utils


@click.group("vars", help="Manage variables in the Genesis installation")
def variables_group():
    pass


@variables_group.command("list", help="List variables")
@click.pass_context
def list_variables(ctx: click.Context) -> None:
    client = ctx.obj.client
    variables = variable_lib.list_variables(client)
    _print_variables(variables)


@variables_group.command("show", help="Show variable")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.pass_context
def show_variable_cmd(
    ctx: click.Context,
    uuid: str,
) -> None:
    client: http_client.CollectionBaseClient = ctx.obj.client
    if not utils.is_valid_uuid(uuid):
        variables = variable_lib.list_variables(client, name=uuid)
        if variables:
            uuid = variables[0]["uuid"]
        else:
            raise click.ClickException(f"Variable with name {uuid} not found")
    variable = variable_lib.get_variable(client, uuid)
    _print_variables([variable])


@variables_group.command(
    "set",
    help="Create variable if missing and set its value by creating a new value record",
)
@click.argument(
    "var_uuid_or_name",
    type=str,
    required=True,
)
@click.argument(
    "value",
    type=click.STRING,
    required=True,
)
@click.option(
    "-p",
    "--project-id",
    type=click.UUID,
    default=None,
    help="UUID of the project in which to deploy the variable",
)
@click.option(
    "--name",
    type=str,
    default=None,
    help="Name of the variable to create if it does not exist",
)
@click.option(
    "--description",
    type=str,
    default=None,
    help="Description of the variable to create if it does not exist",
)
@click.option(
    "--rotate",
    is_flag=True,
    default=False,
    help="Delete all existing values for the variable before creating the new one",
)
@click.pass_context
def set_variable_cmd(
    ctx: click.Context,
    var_uuid_or_name: str,
    value: str,
    project_id: sys_uuid.UUID | None,
    name: str | None,
    description: str | None,
    rotate: bool,
) -> None:
    client: http_client.CollectionBaseClient = ctx.obj.client

    var_uuid: str | None = None
    variable: dict[str, tp.Any] | None = None

    if utils.is_valid_uuid(var_uuid_or_name):
        var_uuid = str(var_uuid_or_name)
        # Try to find variable by UUID
        try:
            variable = variable_lib.get_variable(client, sys_uuid.UUID(var_uuid))
        except bazooka_exc.NotFoundError:
            # No message found, just to create a variable with specified UUID
            pass
    else:
        variables = variable_lib.list_variables(client, name=var_uuid_or_name)
        if len(variables) > 1:
            raise click.ClickException(
                f"Multiple variables with name {var_uuid_or_name} found; use UUID"
            )
        if len(variables) == 1:
            variable = variables[0]
            var_uuid = variable["uuid"]

    # No variable found, create new one
    if variable is None:
        root_ctx = ctx.find_root()
        project_id = project_id or root_ctx.params.get("project_id")
        if project_id is None:
            raise click.ClickException(
                "Unable to create variable: project id is not set. "
                "Provide it via '--project-id' (or set 'project_id' in config)."
            )

        variable_name = name if name else var_uuid_or_name
        variable_description = description if description else ""

        created = variable_lib.add_variable(
            client,
            {
                "uuid": var_uuid if var_uuid else str(sys_uuid.uuid4()),
                "project_id": str(project_id),
                "name": variable_name,
                "description": variable_description,
                "setter": {"kind": "selector", "selector_strategy": "latest"},
            },
        )
        variable = created
        var_uuid = created["uuid"]

    if rotate:
        variable_ref = f"{c.VARIABLE_COLLECTION}{var_uuid}"
        existing_values = value_lib.list_values(client, variable=variable_ref)
        for existing in existing_values:
            value_lib.delete_value(client, sys_uuid.UUID(existing["uuid"]))

    data = {
        "uuid": str(sys_uuid.uuid4()),
        "project_id": variable["project_id"],
        "name": f"{variable['name']}_value",
        "description": "",
        "value": utils.convert_to_nearest_type(value),
        "variable": f"{c.VARIABLE_COLLECTION}{var_uuid}",
    }
    value_lib.add_value(client, data)

    variable = variable_lib.get_variable(client, sys_uuid.UUID(var_uuid))
    _print_variables([variable])


@variables_group.command("delete", help="Delete variable")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.pass_context
def delete_variable_cmd(
    ctx: click.Context,
    uuid: str,
) -> None:
    client: http_client.CollectionBaseClient = ctx.obj.client
    if not utils.is_valid_uuid(uuid):
        variables = variable_lib.list_variables(client, name=uuid)
        if variables:
            uuid = variables[0]["uuid"]
        else:
            raise click.ClickException(f"Variable with name {uuid} not found")
    variable_lib.delete_variable(client, uuid)


@variables_group.command("select", help="Select variable")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.option(
    "-v",
    "--value",
    type=click.UUID,
    required=True,
    help="Uuid of the value to select as the value of the variable",
)
@click.pass_context
def select_variable_cmd(
    ctx: click.Context,
    uuid: str,
    value: sys_uuid.UUID,
) -> None:
    client: http_client.CollectionBaseClient = ctx.obj.client
    if not utils.is_valid_uuid(uuid):
        variables = variable_lib.list_variables(client, name=uuid)
        if variables:
            uuid = variables[0]["uuid"]
        else:
            raise click.ClickException(f"Variable with name {uuid} not found")
    variable_lib.select_value(client, uuid, str(value))


@variables_group.command("add", help="Add a new variable to the Genesis installation")
@click.pass_context
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help="UUID of the variable",
)
@click.option(
    "-p",
    "--project-id",
    type=click.UUID,
    required=True,
    help="Name of the project in which to deploy the variable",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default="example_variable",
    help="Name of the variable",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default="",
    help="Description of the variable",
)
def add_variable_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    project_id: sys_uuid.UUID,
    name: str,
    description: str,
) -> None:
    client: http_client.CollectionBaseClient = ctx.obj.client
    if uuid is None:
        uuid = sys_uuid.uuid4()
    variable = variable_lib.add_variable(
        client,
        {
            "uuid": str(uuid),
            "project_id": str(project_id),
            "name": name,
            "description": description,
            "setter": {
                "kind": "profile",
                "fallback_strategy": "ignore",
                "profiles": [],
                "element": None,
            },
        },
    )
    _print_variables([variable])


def _print_variables(variables: tp.List[dict]) -> None:
    table = get_table()
    table.add_column("UUID")
    table.add_column("Project")
    table.add_column("Name")
    table.add_column("Value")
    table.add_column("Status")

    for variable in variables:
        table.add_row(
            variable["uuid"],
            variable["project_id"],
            variable["name"],
            str(variable.get("value", "")),
            variable["status"],
        )

    print_table(table)
