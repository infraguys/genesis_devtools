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

from genesis_devtools.clients import user as user_lib
from genesis_devtools.common import utils


@click.group("users", help="Manager users in the Genesis installation")
def users_group():
    pass


@users_group.command("list", help="List users")
@click.pass_context
def list_users(
    ctx: click.Context,
) -> None:
    client: http_client.CollectionBaseClient = ctx.obj.client
    users = user_lib.list_users(client)
    _print_values(users)


@users_group.command("show", help="Show user")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.pass_context
def show_user(
    ctx: click.Context,
    uuid: str,
) -> None:
    client: http_client.CollectionBaseClient = ctx.obj.client
    if not utils.is_valid_uuid(uuid):
        users = user_lib.list_users(client, username=uuid)
        if users:
            uuid = users[0]["uuid"]
        else:
            raise click.ClickException(f"User with name {uuid} not found")
    value = user_lib.get_user(client, uuid)
    _print_values([value])


@users_group.command("delete", help="Delete user")
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help="user UUID",
)
@click.pass_context
def delete_user(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
) -> None:
    client: http_client.CollectionBaseClient = ctx.obj.client
    user_lib.delete_user(client, uuid)


def _print_values(users: tp.List[dict]) -> None:
    table = get_table()
    table.add_column("UUID")
    table.add_column("Username")
    table.add_column("First Name")
    table.add_column("Last Name")
    table.add_column("Email")
    table.add_column("Status")

    for user in users:
        table.add_row(
            user["uuid"],
            user["username"],
            user["first_name"],
            user["last_name"],
            user["email"],
            user["status"],
        )

    print_table(table)
