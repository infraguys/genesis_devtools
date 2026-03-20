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

import json
import uuid as sys_uuid

import click
import prettytable

from gcl_sdk.clients.http import base as http_client

from genesis_devtools.clients import manifest as manifests_lib


@click.group("manifests", help="Manage manifests in the Genesis installation")
def manifests_group():
    pass


@manifests_group.command("list", help="List manifests")
@click.pass_context
def list_manifest_cmd(ctx: click.Context) -> None:
    """List manifests"""
    client: http_client.CollectionBaseClient = ctx.obj.client
    table = prettytable.PrettyTable()
    table.field_names = [
        "UUID",
        "Name",
        "Description",
        "Version",
        "Status",
    ]

    manifests = manifests_lib.list_manifests(client)
    for manifest in manifests:
        table.add_row(
            [
                manifest["uuid"],
                manifest["name"],
                manifest["description"],
                manifest["version"],
                manifest["status"],
            ]
        )
    click.echo(table)


@manifests_group.command("show", help="Show manifest general information")
@click.argument("name")
@click.pass_context
def show_manifest_cmd(ctx: click.Context, name: str) -> None:
    """Show manifest general information"""
    client: http_client.CollectionBaseClient = ctx.obj.client

    manifest = manifests_lib.list_manifests(client, name=name)
    if not manifest:
        raise click.ClickException(f"manifest {name} not found")

    if len(manifest) > 1:
        raise click.ClickException(f"Multiple manifests found with name {name}")

    manifest = manifest[0]

    table = prettytable.PrettyTable()
    table.field_names = [
        "UUID",
        "Name",
        "Version",
        "Status",
    ]

    table.add_row(
        [
            manifest["uuid"],
            manifest["name"],
            manifest["version"],
            manifest["status"],
        ]
    )

    click.echo(f"manifest {name}:")
    click.echo(table)

    if manifest["resources"]:
        click.echo("Resources json:")
        click.echo(json.dumps(manifest["resources"], indent=4))
    if manifest["requirements"]:
        click.echo("Requirements json:")
        click.echo(json.dumps(manifest["requirements"], indent=4))
    if manifest["imports"]:
        click.echo("Imports json:")
        click.echo(json.dumps(manifest["imports"], indent=4))
    if manifest["exports"]:
        click.echo("Exports json:")
        click.echo(json.dumps(manifest["exports"], indent=4))

    resources = manifests_lib.list_resources(client, sys_uuid.UUID(manifest["uuid"]))
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
