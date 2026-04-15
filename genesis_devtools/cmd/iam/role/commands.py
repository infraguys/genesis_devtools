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

from genesis_devtools.clients import role as role_lib
from genesis_devtools.common import utils


@click.group("roles", help="Manage roles in the Genesis installation")
def roles_group():
    pass


@roles_group.command("list", help="List roles")
@click.pass_context
def list_roles(
    ctx: click.Context,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    roles = role_lib.list_roles(client)
    _print_values(roles)


@roles_group.command("show", help="Show role")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.pass_context
def show_role(
    ctx: click.Context,
    uuid: str,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    if not utils.is_valid_uuid(uuid):
        roles = role_lib.list_roles(client, rolename=uuid)
        if roles:
            uuid = roles[0]["uuid"]
        else:
            raise click.ClickException(f"role with name {uuid} not found")
    data = role_lib.get_role(client, uuid)
    show_data(data)


@roles_group.command("delete", help="Delete role")
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help="role UUID",
)
@click.pass_context
def delete_role(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    role_lib.delete_role(client, uuid)


def _print_values(roles: tp.List[dict]) -> None:
    table = get_table()
    table.add_column("UUID")
    table.add_column("Name")
    table.add_column("Status")

    for role in roles:
        table.add_row(
            role["uuid"],
            role["name"],
            role["status"],
        )

    print_table(table)
