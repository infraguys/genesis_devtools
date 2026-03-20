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

import click
import prettytable

from gcl_sdk.clients.http import base as http_client

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
    table = prettytable.PrettyTable()
    table.field_names = [
        "UUID",
        "Project",
        "Name",
        "Value",
        "Status",
    ]

    for variable in variables:
        table.add_row(
            [
                variable["uuid"],
                variable["project_id"],
                variable["name"],
                variable.get("value", ""),
                variable["status"],
            ]
        )

    click.echo(table)
