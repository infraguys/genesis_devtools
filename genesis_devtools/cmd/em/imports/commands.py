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

ENTITY = "import"
ENTITY_COLLECTION = c.IMPORTS_COLLECTION


@click.group(f"{ENTITY}s", help=f"Manage {ENTITY}s in the Genesis installation")
def imports_group():
    pass


@imports_group.command("list", help=f"List {ENTITY}s")
@click.option(
    "-e",
    "--element",
    default=None,
    help="Name or uuid of the element",
)
@click.pass_context
def list_cmd(ctx: click.Context, element: str) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    if element is None:
        resources = base_client.list_entities(client, ENTITY_COLLECTION)
    else:
        if not utils.is_valid_uuid(element):
            elements = base_client.list_entities(
                client, c.ELEMENT_COLLECTION, name=element
            )
            if elements:
                uuid = elements[0]["uuid"]
                resources = base_client.list_entities(
                    client, f"{c.ELEMENT_COLLECTION}{uuid}/imports/"
                )
            else:
                raise click.ClickException(f"Element with name {element} not found")
        else:
            resources = base_client.list_entities(
                client, f"{c.ELEMENT_COLLECTION}{element}/imports/"
            )

    _print_entities(resources)


@imports_group.command("show", help=f"Show {ENTITY}")
@click.option(
    "-e",
    "--element",
    default=None,
    help="Name or uuid of the element",
)
@click.argument(
    "name_uuid",
    type=str,
    required=True,
)
@click.pass_context
def show_cmd(
    ctx: click.Context,
    element: str | None,
    name_uuid: str | None,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)

    if element is None:
        if not utils.is_valid_uuid(name_uuid):
            entities = base_client.list_entities(
                client, ENTITY_COLLECTION, name=name_uuid
            )
            if entities:
                name_uuid = entities[0]["uuid"]
            else:
                raise click.ClickException(f"{ENTITY} with name {name_uuid} not found")
        entity = base_client.get_entity(client, ENTITY_COLLECTION, name_uuid)

    else:
        if not utils.is_valid_uuid(element):
            elements = base_client.list_entities(
                client, c.ELEMENT_COLLECTION, name=element
            )
            if elements:
                element = elements[0]["uuid"]
            else:
                raise click.ClickException(f"Element with name {element} not found")

        if not utils.is_valid_uuid(name_uuid):
            entities = base_client.list_entities(
                client,
                f"{c.ELEMENT_COLLECTION}{element}/imports/",
                name=name_uuid,
            )
            if entities:
                name_uuid = entities[0]["uuid"]
            else:
                raise click.ClickException(f"resource with name {name_uuid} not found")

        entity = base_client.get_entity(
            client, f"{c.ELEMENT_COLLECTION}{element}/imports/", name_uuid
        )

    show_data(entity)


def _print_entities(entities: tp.List[dict]) -> None:
    if entities:
        table = get_table("UUID", "Name", "Kind", "Link", "Element")
        for entity in entities:
            table.add_row(
                entity["uuid"],
                entity["name"],
                entity["kind"],
                entity["link"],
                entity["element"],
            )

        print_table(table)
