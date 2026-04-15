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

from genesis_devtools.clients import service as service_lib
from genesis_devtools import utils


@click.group("services", help="Manage services in the Genesis installation")
def services_group():
    pass


@services_group.command("list", help="List services")
@click.pass_context
def list_services(ctx: click.Context) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    services = service_lib.list_services(client)
    _print_services(services)


@services_group.command("show", help="Show service")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.pass_context
def show_service_cmd(
    ctx: click.Context,
    uuid: str,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    if not utils.is_valid_uuid(uuid):
        services = service_lib.list_services(client, name=uuid)
        if services:
            uuid = services[0]["uuid"]
        else:
            raise click.ClickException(f"service with name {uuid} not found")
    service = service_lib.get_service(client, uuid)
    show_data(service)


@services_group.command("delete", help="Delete service")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.pass_context
def delete_service_cmd(
    ctx: click.Context,
    uuid: str,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    if not utils.is_valid_uuid(uuid):
        services = service_lib.list_services(client, name=uuid)
        if services:
            uuid = services[0]["uuid"]
        else:
            raise click.ClickException(f"service with name {uuid} not found")
    service_lib.delete_service(client, uuid)


@services_group.command("add", help="Add a new service to the Genesis installation")
@click.pass_context
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help="UUID of the service",
)
@click.option(
    "-p",
    "--project-id",
    type=click.UUID,
    required=True,
    help="Name of the project in which to deploy the service",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default="test_service",
    help="Name of the service",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default="",
    help="Description of the service",
)
def add_service_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    project_id: sys_uuid.UUID,
    name: str,
    description: str,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    if uuid is None:
        uuid = sys_uuid.uuid4()
    service_resp = service_lib.add_service(
        client,
        {
            "uuid": str(uuid),
            "project_id": str(project_id),
            "name": name,
            "description": description,
        },
    )
    show_data(service_resp)


@services_group.command("update", help="Update service")
@click.pass_context
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.option(
    "-p",
    "--project-id",
    type=click.UUID,
    default=None,
    help="Name of the project in which to deploy the service",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default=None,
    help="Name of the service",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default=None,
    help="Description of the service",
)
def update_service_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID,
    project_id: sys_uuid.UUID | None,
    name: str | None,
    description: str | None,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    data = {}
    if project_id is not None:
        data["project_id"] = str(project_id)
    if name is not None:
        data["name"] = name
    if description is not None:
        data["description"] = description
    service_resp = service_lib.update_service(client, uuid, data)
    show_data(service_resp)


def _print_services(services: tp.List[dict]) -> None:
    table = get_table()
    table.add_column("UUID")
    table.add_column("Project")
    table.add_column("Name")
    table.add_column("Status")

    for service in services:
        table.add_row(
            service["uuid"],
            service["project_id"],
            service["name"],
            service["status"],
        )

    print_table(table)
