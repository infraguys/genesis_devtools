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

import uuid as sys_uuid

import click
import prettytable

from gcl_sdk.clients.http import base as http_client

from genesis_devtools.clients import element as elements_lib


@click.group("elements", help="Manage elements in the Genesis installation")
def elements_group():
    pass


@elements_group.command("list", help="List elements")
@click.pass_context
def list_element_cmd(ctx: click.Context) -> None:
    """List elements"""
    client: http_client.CollectionBaseClient = ctx.obj.client
    table = prettytable.PrettyTable()
    table.field_names = [
        "UUID",
        "Name",
        "Description",
        "Version",
        "Status",
    ]

    elements = elements_lib.list_elements(client)
    for element in elements:
        table.add_row(
            [
                element["uuid"],
                element["name"],
                element["description"],
                element["version"],
                element["status"],
            ]
        )
    click.echo(table)


@elements_group.command("show", help="Show element general information")
@click.argument("name")
@click.pass_context
def show_element_cmd(ctx: click.Context, name: str) -> None:
    """Show element general information"""
    client: http_client.CollectionBaseClient = ctx.obj.client

    element = elements_lib.list_elements(client, name=name)
    if not element:
        raise click.ClickException(f"Element {name} not found")

    if len(element) > 1:
        raise click.ClickException(f"Multiple elements found with name {name}")

    element = element[0]

    table = prettytable.PrettyTable()
    table.field_names = [
        "UUID",
        "Name",
        "Description",
        "Version",
        "Status",
    ]

    table.add_row(
        [
            element["uuid"],
            element["name"],
            element["description"],
            element["version"],
            element["status"],
        ]
    )

    click.echo(f"Element {name}:")
    click.echo(table)

    resources = elements_lib.list_resources(client, sys_uuid.UUID(element["uuid"]))
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

    click.echo("Resources:")
    click.echo(table)
