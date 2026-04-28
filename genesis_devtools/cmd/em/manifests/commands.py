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
import os
import typing as tp
import yaml

import rich_click as click
from genesis_devtools.common.table import get_table, print_table, show_data

from genesis_devtools.clients import base_client

from genesis_devtools.clients import repo as repo_lib
import genesis_devtools.constants as c
from genesis_devtools import utils

ENTITY = "manifest"
ENTITY_COLLECTION = c.MANIFEST_COLLECTION


@click.group(f"{ENTITY}s", help=f"Manage {ENTITY}s in the Genesis installation")
def manifests_group():
    pass


@manifests_group.command("list", help=f"List {ENTITY}s")
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


@manifests_group.command("show", help=f"Show {ENTITY}")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.pass_context
def show_manifest_cmd(ctx: click.Context, uuid: str) -> None:
    """Show manifest general information"""
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    data = base_client.get_entity(client, ENTITY_COLLECTION, uuid)
    show_data(data)

    if data["resources"]:
        click.echo("Resources json:")
        click.echo(json.dumps(data["resources"], indent=4))
    if data["requirements"]:
        click.echo("Requirements json:")
        click.echo(json.dumps(data["requirements"], indent=4))
    if data["imports"]:
        click.echo("Imports json:")
        click.echo(json.dumps(data["imports"], indent=4))
    if data["exports"]:
        click.echo("Exports json:")
        click.echo(json.dumps(data["exports"], indent=4))

    resources = base_client.list_entities(
        client, f"{c.ELEMENT_COLLECTION}{data['uuid']}/resources/"
    )
    table = get_table(
        "UUID", "Name", "Kind", "Full hash", "Status", "Created at", "Updated at"
    )

    for resource in resources:
        table.add_row(
            resource["uuid"],
            resource["name"],
            resource["kind"],
            str(resource["full_hash"]),
            resource["status"],
            resource["created_at"],
            resource["updated_at"],
        )

    click.echo("Resources:")
    print_table(table)


@manifests_group.command("validate", help=f"Validate {ENTITY}")
@click.option(
    "-r",
    "--repository",
    default=f"{c.ELEMENT_REPO_URL}/",
    show_default=True,
    help="Repository endpoint",
)
@click.argument("path_or_name")
@click.pass_context
def validate_manifest_cmd(
    ctx: click.Context, repository: str, path_or_name: str
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)

    if os.path.isfile(path_or_name):
        with open(path_or_name, "r", encoding="utf-8") as f:
            manifest_data = yaml.safe_load(f)
    else:
        manifest_data = repo_lib.download_manifest(repository, path_or_name)
    manifest = base_client.add_entity(client, ENTITY_COLLECTION, manifest_data)
    base_client.action_entity(
        client, ENTITY_COLLECTION, "validate", manifest["uuid"], invoke=False
    )
    click.echo(
        f"Manifest {manifest['name']} {manifest['version']} validated successfully"
    )


def _print_entities(entities: tp.List[dict]) -> None:
    table = get_table()
    table.add_column("UUID")
    table.add_column("Name")
    table.add_column("Description")
    table.add_column("Version")
    table.add_column("Status")

    for entity in entities:
        table.add_row(
            entity["uuid"],
            entity["name"],
            entity["description"],
            entity["version"],
            entity["status"],
        )

    print_table(table)
