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
#    License for the specific language governing role_bindings and limitations
#    under the License.
from __future__ import annotations

import typing as tp
import uuid as sys_uuid

import rich_click as click
from genesis_devtools.common.table import get_table, print_table

from genesis_devtools.clients.base_client import get_user_api_client

from genesis_devtools.clients import role_binding as role_binding_lib
from genesis_devtools.common import utils


@click.group("role_bindings", help="Manage role_bindings in the Genesis installation")
def role_bindings_group():
    pass


@role_bindings_group.command("list", help="List role_bindings")
@click.pass_context
def list_role_bindings(
    ctx: click.Context,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    role_bindings = role_binding_lib.list_role_bindings(client)
    _print_values(role_bindings)


@role_bindings_group.command("show", help="Show role_binding")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.pass_context
def show_role_binding(
    ctx: click.Context,
    uuid: str,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    if not utils.is_valid_uuid(uuid):
        role_bindings = role_binding_lib.list_role_bindings(
            client, role_bindingname=uuid
        )
        if role_bindings:
            uuid = role_bindings[0]["uuid"]
        else:
            raise click.ClickException(f"role_binding with name {uuid} not found")
    value = role_binding_lib.get_role_binding(client, uuid)
    _print_values([value])


@role_bindings_group.command("delete", help="Delete role_binding")
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help="role_binding UUID",
)
@click.pass_context
def delete_role_binding(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    role_binding_lib.delete_role_binding(client, uuid)


def _print_values(role_bindings: tp.List[dict]) -> None:
    table = get_table()
    table.add_column("UUID")
    table.add_column("Role")
    table.add_column("User")
    table.add_column("Status")

    for role_binding in role_bindings:
        table.add_row(
            role_binding["uuid"],
            role_binding["role"],
            role_binding["user"],
            role_binding["status"],
        )

    print_table(table)
