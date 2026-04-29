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

from genesis_devtools import constants as c
from genesis_devtools import utils

ENTITY = "resource"
ENTITY_COLLECTION = c.RESOURCE_COLLECTION


@click.group(f"{ENTITY}s", help=f"Manage {ENTITY}s in the Genesis installation")
def resources_group():
    pass


@resources_group.command("list", help=f"List {ENTITY}s")
@click.option(
    "-e",
    "--element",
    default=None,
    help="Name or uuid of the element",
)
@click.pass_context
def list_resource_cmd(ctx: click.Context, element: str) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    if element is None:
        resources = base_client.list_entities(client, c.RESOURCE_COLLECTION)
    else:
        if not utils.is_valid_uuid(element):
            elements = base_client.list_entities(
                client, c.ELEMENT_COLLECTION, name=element
            )
            if elements:
                uuid = elements[0]["uuid"]
                resources = base_client.list_entities(
                    client, f"{c.ELEMENT_COLLECTION}{uuid}/resources/"
                )
            else:
                raise click.ClickException(f"Element with name {element} not found")
        else:
            resources = base_client.list_entities(
                client, f"{c.ELEMENT_COLLECTION}{element}/resources/"
            )

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
    client = base_client.get_user_api_client(ctx.obj.auth_data)

    if element is None:
        if not utils.is_valid_uuid(resource_name_uuid):
            resources = base_client.list_entities(
                client, c.RESOURCE_COLLECTION, name=resource_name_uuid
            )
            if resources:
                resource_name_uuid = resources[0]["uuid"]
            else:
                raise click.ClickException(
                    f"resource with name {resource_name_uuid} not found"
                )
        resource = base_client.get_entity(
            client, c.RESOURCE_COLLECTION, resource_name_uuid
        )

    else:
        if not utils.is_valid_uuid(element):
            elements = base_client.list_entities(
                client, ENTITY_COLLECTION, name=element
            )
            if elements:
                element = elements[0]["uuid"]
            else:
                raise click.ClickException(f"Element with name {element} not found")

        if not utils.is_valid_uuid(resource_name_uuid):
            resources = base_client.list_entities(
                client,
                f"{c.ELEMENT_COLLECTION}{element}/resources/",
                name=resource_name_uuid,
            )
            if resources:
                resource_name_uuid = resources[0]["uuid"]
            else:
                raise click.ClickException(
                    f"resource with name {resource_name_uuid} not found"
                )

        resource = base_client.get_entity(
            client, f"{c.ELEMENT_COLLECTION}{element}/resources/", resource_name_uuid
        )

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
