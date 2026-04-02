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
from genesis_devtools.clients import hypervisor as hypervisor_lib
from genesis_devtools.common import utils


@click.group("hypervisors", help="Manage hypervisors in the Genesis installation")
def hypervisors_group():
    pass


@hypervisors_group.command("list", help="List hypervisors")
@click.pass_context
def list_hypervisors(
    ctx: click.Context,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    hypervisors = hypervisor_lib.list_hypervisors(client)
    _print_values(hypervisors)


@hypervisors_group.command("show", help="Show hypervisor")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.pass_context
def show_hypervisor(
    ctx: click.Context,
    uuid: str,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    if not utils.is_valid_uuid(uuid):
        hypervisors = hypervisor_lib.list_hypervisors(client, name=uuid)
        if hypervisors:
            uuid = hypervisors[0]["uuid"]
        else:
            raise click.ClickException(f"hypervisor with name {uuid} not found")
    hypervisor = hypervisor_lib.get_hypervisor(client, uuid)
    show_data(hypervisor)


@hypervisors_group.command("delete", help="Delete hypervisor")
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help="hypervisor UUID",
)
@click.pass_context
def delete_hypervisor(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    hypervisor_lib.delete_hypervisor(client, uuid)


def _print_values(hypervisors: tp.List[dict]) -> None:
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
