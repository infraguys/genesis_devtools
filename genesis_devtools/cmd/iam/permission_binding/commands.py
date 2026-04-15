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

from genesis_devtools.clients import permission_binding as permission_binding_lib
from genesis_devtools.common import utils


@click.group(
    "permission_bindings",
    help="Manage permission_bindings in the Genesis installation",
)
def permission_bindings_group():
    pass


@permission_bindings_group.command("list", help="List permission_bindings")
@click.pass_context
def list_permission_bindings(
    ctx: click.Context,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    permission_bindings = permission_binding_lib.list_permission_bindings(client)
    _print_values(permission_bindings)


@permission_bindings_group.command("show", help="Show permission_binding")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.pass_context
def show_permission_binding(
    ctx: click.Context,
    uuid: str,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    if not utils.is_valid_uuid(uuid):
        permission_bindings = permission_binding_lib.list_permission_bindings(
            client, permission_bindingname=uuid
        )
        if permission_bindings:
            uuid = permission_bindings[0]["uuid"]
        else:
            raise click.ClickException(f"permission_binding with name {uuid} not found")
    data = permission_binding_lib.get_permission_binding(client, uuid)
    show_data(data)


@permission_bindings_group.command("delete", help="Delete permission_binding")
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help="permission_binding UUID",
)
@click.pass_context
def delete_permission_binding(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    permission_binding_lib.delete_permission_binding(client, uuid)


def _print_values(permission_bindings: tp.List[dict]) -> None:
    table = get_table()
    table.add_column("UUID")
    table.add_column("Role")
    table.add_column("Permission")

    for permission_binding in permission_bindings:
        table.add_row(
            permission_binding["uuid"],
            permission_binding["role"],
            permission_binding["permission"],
        )

    print_table(table)
