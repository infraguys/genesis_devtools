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

import rich_click as click
from genesis_devtools.common.table import get_table, print_table

from genesis_devtools.clients.base_client import get_user_api_client
from genesis_devtools.clients import set as set_lib
from genesis_devtools.common import utils


@click.group("sets", help="Manage sets in the Genesis installation")
def sets_group():
    pass


@sets_group.command("list", help="List sets")
@click.pass_context
def list_sets(ctx: click.Context) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    sets = set_lib.list_sets(client)
    _print_sets(sets)


@sets_group.command("show", help="Show set")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.pass_context
def show_set_cmd(
    ctx: click.Context,
    uuid: str,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    if not utils.is_valid_uuid(uuid):
        sets = set_lib.list_sets(client, name=uuid)
        if sets:
            uuid = sets[0]["uuid"]
        else:
            raise click.ClickException(f"set with name {uuid} not found")
    set_obj = set_lib.get_set(client, uuid)
    _print_sets([set_obj])


@sets_group.command("delete", help="Delete set")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.pass_context
def delete_set_cmd(
    ctx: click.Context,
    uuid: str,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    if not utils.is_valid_uuid(uuid):
        sets = set_lib.list_sets(client, name=uuid)
        if sets:
            uuid = sets[0]["uuid"]
        else:
            raise click.ClickException(f"set with name {uuid} not found")
    set_lib.delete_set(client, uuid)


def _print_sets(sets: tp.List[dict]) -> None:
    table = get_table()
    table.add_column("UUID")
    table.add_column("Project")
    table.add_column("Name")
    table.add_column("Node Type")
    table.add_column("Cores")
    table.add_column("RAM")
    table.add_column("Status")

    for set_obj in sets:
        table.add_row(
            set_obj["uuid"],
            set_obj["project_id"],
            set_obj["name"],
            set_obj["node_type"],
            str(set_obj["cores"]),
            str(set_obj["ram"]),
            set_obj["status"],
        )

    print_table(table)
