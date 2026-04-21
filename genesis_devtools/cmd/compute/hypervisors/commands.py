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
from genesis_devtools.common.table import get_table, print_table, show_data

from genesis_devtools.clients import base_client
from genesis_devtools import utils
from genesis_devtools import constants as c

ENTITY = "hypervisor"
ENTITY_COLLECTION = c.HYPERVISOR_COLLECTION


@click.group(f"{ENTITY}s", help=f"Manage {ENTITY}s in the Genesis installation")
def hypervisors_group():
    pass


@hypervisors_group.command("list", help=f"List {ENTITY}s")
@click.option(
    "-f",
    "--filters",
    multiple=True,
    help=(
        "Additional filters to pass to the api. "
        "The format is 'key=value'. For example: --f "
        "parent=11111111-1111-1111-1111-11111111111 --filters status=NEW"
    ),
)
@click.pass_context
def list_cmd(ctx: click.Context, filters: tuple[str, ...]) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    filters = utils.convert_input_multiply(filters)
    entities = base_client.list_entities(client, ENTITY_COLLECTION, **filters)
    _print_entities(entities)


@hypervisors_group.command("show", help=f"Show {ENTITY}")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.pass_context
def show_cmd(
    ctx: click.Context,
    uuid: str,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    data = base_client.get_entity(client, ENTITY_COLLECTION, uuid)
    show_data(data)


@hypervisors_group.command("delete", help=f"Delete {ENTITY}")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.pass_context
def delete_cmd(
    ctx: click.Context,
    uuid: str,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    base_client.delete_entity(client, ENTITY_COLLECTION, uuid)


def _print_entities(hypervisors: tp.List[dict]) -> None:
    table = get_table()
    table.add_column("UUID")
    table.add_column("Name")
    table.add_column("MachineType")
    table.add_column("All Cores")
    table.add_column("Avail Cores")
    table.add_column("All Ram")
    table.add_column("Avail Ram")
    table.add_column("Status")

    for hypervisor in hypervisors:
        table.add_row(
            hypervisor["uuid"],
            hypervisor["name"],
            hypervisor["machine_type"],
            str(hypervisor["all_cores"]),
            str(hypervisor["avail_cores"]),
            str(hypervisor["all_ram"]),
            str(hypervisor["avail_ram"]),
            hypervisor["status"],
        )

    print_table(table)
