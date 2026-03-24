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

import click
import prettytable

from gcl_sdk.clients.http import base as http_client

from genesis_devtools.clients import element as elements_lib
from genesis_devtools.common import utils


@click.group("resources", help="Manage resources in the Genesis installation")
def resources_group():
    pass


@resources_group.command("list", help="List resources")
@click.argument(
    "name_uuid",
    type=str,
    required=True,
)
@click.pass_context
def list_resource_cmd(ctx: click.Context, name_uuid: str) -> None:
    """List resources"""
    client: http_client.CollectionBaseClient = ctx.obj.client
    if not utils.is_valid_uuid(name_uuid):
        elements = elements_lib.list_elements(client, name=name_uuid)
        if elements:
            uuid = elements[0]["uuid"]
            resources = elements_lib.list_resources(client, uuid)
        else:
            raise click.ClickException(f"Element with name {name_uuid} not found")
    else:
        resources = elements_lib.list_resources(client, name_uuid)

    _print_resources(resources)


@resources_group.command("show", help="Show resource")
@click.argument(
    "element_name_uuid",
    type=str,
    required=True,
)
@click.argument(
    "resource_name_uuid",
    type=str,
    required=True,
)
@click.pass_context
def show_resource_cmd(
    ctx: click.Context,
    element_name_uuid: str,
    resource_name_uuid: str,
) -> None:
    client: http_client.CollectionBaseClient = ctx.obj.client

    if not utils.is_valid_uuid(element_name_uuid):
        elements = elements_lib.list_elements(client, name=element_name_uuid)
        if elements:
            element_name_uuid = elements[0]["uuid"]
        else:
            raise click.ClickException(
                f"Element with name {element_name_uuid} not found"
            )

    if not utils.is_valid_uuid(resource_name_uuid):
        resources = elements_lib.list_resources(
            client, element_name_uuid, name=resource_name_uuid
        )
        if resources:
            resource_name_uuid = resources[0]["uuid"]
        else:
            raise click.ClickException(
                f"resource with name {resource_name_uuid} not found"
            )

    resource = elements_lib.get_resource(client, element_name_uuid, resource_name_uuid)
    _print_resources([resource])


def _print_resources(resources: tp.List[dict]) -> None:
    table = prettytable.PrettyTable()
    table.field_names = [
        "UUID",
        "Name",
        "Kind",
        "Full hash",
        "Status",
        "Created at",
        "Updated at",
    ]

    for resource in resources:
        table.add_row(
            [
                resource["uuid"],
                resource["name"],
                resource["kind"],
                resource["full_hash"],
                resource["status"],
                resource["created_at"],
                resource["updated_at"],
            ]
        )

    click.echo(table)
