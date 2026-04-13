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

from genesis_devtools.clients.base_client import get_user_api_client

from genesis_devtools.clients import element as elements_lib
from genesis_devtools.common import utils


@click.group("resources", help="Manage resources in the Genesis installation")
def resources_group():
    pass


@resources_group.command("list", help="List resources")
@click.option(
    "-e",
    "--element",
    default=None,
    help="Name or uuid of the element",
)
@click.pass_context
def list_resource_cmd(ctx: click.Context, element: str) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    if element is None:
        resources = elements_lib.list_all_resources(client)
    else:
        if not utils.is_valid_uuid(element):
            elements = elements_lib.list_elements(client, name=element)
            if elements:
                uuid = elements[0]["uuid"]
                resources = elements_lib.list_resources(client, uuid)
            else:
                raise click.ClickException(f"Element with name {element} not found")
        else:
            resources = elements_lib.list_resources(client, element)

    _print_resources(resources)


@resources_group.command("show", help="Show resource")
@click.option(
    "-e",
    "--element",
    default=None,
    help="Name or uuid of the element",
)
@click.argument(
    "resource_name_uuid",
    type=str,
    required=True,
)
@click.pass_context
def show_resource_cmd(
    ctx: click.Context,
    element: str | None,
    resource_name_uuid: str | None,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)

    if element is None:
        if not utils.is_valid_uuid(resource_name_uuid):
            resources = elements_lib.list_all_resources(client, name=resource_name_uuid)
            if resources:
                resource_name_uuid = resources[0]["uuid"]
            else:
                raise click.ClickException(
                    f"resource with name {resource_name_uuid} not found"
                )
        resource = elements_lib.get_all_resource(client, resource_name_uuid)

    else:
        if not utils.is_valid_uuid(element):
            elements = elements_lib.list_elements(client, name=element)
            if elements:
                element = elements[0]["uuid"]
            else:
                raise click.ClickException(f"Element with name {element} not found")

        if not utils.is_valid_uuid(resource_name_uuid):
            resources = elements_lib.list_resources(
                client, element, name=resource_name_uuid
            )
            if resources:
                resource_name_uuid = resources[0]["uuid"]
            else:
                raise click.ClickException(
                    f"resource with name {resource_name_uuid} not found"
                )

        resource = elements_lib.get_resource(client, element, resource_name_uuid)

    show_data(resource)


def _print_resources(resources: tp.List[dict]) -> None:
    if resources:
        table = get_table(
            "UUID", "Name", "Kind", "Full hash", "Status", "Created at", "Updated at"
        )
        for resource in resources:
            table.add_row(
                resource["uuid"],
                resource["name"],
                resource["kind"],
                resource["full_hash"],
                resource["status"],
                resource["created_at"],
                resource["updated_at"],
            )

        print_table(table)
