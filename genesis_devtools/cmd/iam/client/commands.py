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

from genesis_devtools.clients.base_client import get_user_api_client

from genesis_devtools.clients import client as client_lib
from genesis_devtools.common import utils


@click.group("clients", help="Manager clients in the Genesis installation")
def clients_group():
    pass


@clients_group.command("list", help="List clients")
@click.pass_context
def list_clients(
    ctx: click.Context,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    clients = client_lib.list_clients(client)
    _print_values(clients)


@clients_group.command("show", help="Show client")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.pass_context
def show_client(
    ctx: click.Context,
    uuid: str,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    if not utils.is_valid_uuid(uuid):
        clients = client_lib.list_clients(client, clientname=uuid)
        if clients:
            uuid = clients[0]["uuid"]
        else:
            raise click.ClickException(f"client with name {uuid} not found")
    value = client_lib.get_client(client, uuid)
    _print_values([value])


@clients_group.command("delete", help="Delete client")
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help="client UUID",
)
@click.pass_context
def delete_client(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    client_lib.delete_client(client, uuid)


def _print_values(clients: tp.List[dict]) -> None:
    table = get_table()
    table.add_column("UUID")
    table.add_column("Name")
    table.add_column("ClientId")
    table.add_column("Status")

    for client in clients:
        table.add_row(
            client["uuid"],
            client["name"],
            client["client_id"],
            client["status"],
        )

    print_table(table)
