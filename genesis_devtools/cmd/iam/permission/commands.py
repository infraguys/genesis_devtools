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

from gcl_sdk.clients.http import base as http_client

from genesis_devtools.clients import permission as permission_lib
from genesis_devtools.common import utils


@click.group("permissions", help="Manager permissions in the Genesis installation")
def permissions_group():
    pass


@permissions_group.command("list", help="List permissions")
@click.pass_context
def list_permissions(
    ctx: click.Context,
) -> None:
    client: http_client.CollectionBaseClient = ctx.obj.client
    permissions = permission_lib.list_permissions(client)
    _print_values(permissions)


@permissions_group.command("show", help="Show permission")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.pass_context
def show_permission(
    ctx: click.Context,
    uuid: str,
) -> None:
    client: http_client.CollectionBaseClient = ctx.obj.client
    if not utils.is_valid_uuid(uuid):
        permissions = permission_lib.list_permissions(client, permissionname=uuid)
        if permissions:
            uuid = permissions[0]["uuid"]
        else:
            raise click.ClickException(f"permission with name {uuid} not found")
    value = permission_lib.get_permission(client, uuid)
    _print_values([value])


@permissions_group.command("delete", help="Delete permission")
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help="permission UUID",
)
@click.pass_context
def delete_permission(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
) -> None:
    client: http_client.CollectionBaseClient = ctx.obj.client
    permission_lib.delete_permission(client, uuid)


def _print_values(permissions: tp.List[dict]) -> None:
    table = get_table()
    table.add_column("UUID")
    table.add_column("Name")
    table.add_column("Status")

    for permission in permissions:
        table.add_row(
            permission["uuid"],
            permission["name"],
            permission["status"],
        )

    print_table(table)
