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

import click
import prettytable

from gcl_sdk.clients.http import base as http_client

from genesis_devtools.clients import rsa_key as rsa_key_lib
from genesis_devtools.common import utils


@click.group("rsa_keys", help="Manage rsa_keys in the Genesis installation")
def rsa_keys_group():
    pass


@rsa_keys_group.command("list", help="List rsa_keys")
@click.pass_context
def list_rsa_keys(ctx: click.Context) -> None:
    client = ctx.obj.client
    rsa_keys = rsa_key_lib.list_rsa_keys(client)
    _print_rsa_keys(rsa_keys)


@rsa_keys_group.command("show", help="Show rsa_key")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.pass_context
def show_rsa_key_cmd(
    ctx: click.Context,
    uuid: str,
) -> None:
    client: http_client.CollectionBaseClient = ctx.obj.client
    if not utils.is_valid_uuid(uuid):
        rsa_keys = rsa_key_lib.list_rsa_keys(client, name=uuid)
        if rsa_keys:
            uuid = rsa_keys[0]["uuid"]
        else:
            raise click.ClickException(f"rsa_key with name {uuid} not found")
    rsa_key = rsa_key_lib.get_rsa_key(client, uuid)
    _print_rsa_keys([rsa_key])


@rsa_keys_group.command("delete", help="Delete rsa_key")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.pass_context
def delete_rsa_key_cmd(
    ctx: click.Context,
    uuid: str,
) -> None:
    client: http_client.CollectionBaseClient = ctx.obj.client
    if not utils.is_valid_uuid(uuid):
        rsa_keys = rsa_key_lib.list_rsa_keys(client, name=uuid)
        if rsa_keys:
            uuid = rsa_keys[0]["uuid"]
        else:
            raise click.ClickException(f"rsa_key with name {uuid} not found")
    rsa_key_lib.delete_rsa_key(client, uuid)


@rsa_keys_group.command("add", help="Add a new rsa_key to the Genesis installation")
@click.pass_context
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help="UUID of the rsa_key",
)
@click.option(
    "-p",
    "--project-id",
    type=click.UUID,
    required=True,
    help="Name of the project in which to deploy the rsa_key",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default="test_rsa_key",
    help="Name of the rsa_key",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default="",
    help="Description of the rsa_key",
)
def add_rsa_key_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    project_id: sys_uuid.UUID,
    name: str,
    description: str,
) -> None:
    client: http_client.CollectionBaseClient = ctx.obj.client
    if uuid is None:
        uuid = sys_uuid.uuid4()

    data = {
        "uuid": str(uuid),
        "project_id": str(project_id),
        "name": name,
        "description": description,
    }

    rsa_key_resp = rsa_key_lib.add_rsa_key(client, data)
    _print_rsa_keys([rsa_key_resp])


@rsa_keys_group.command("update", help="Update rsa_key")
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
    help="Name of the project in which to deploy the rsa_key",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default=None,
    help="Name of the rsa_key",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default=None,
    help="Description of the rsa_key",
)
def update_rsa_key_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID,
    project_id: sys_uuid.UUID | None,
    name: str | None,
    description: str | None,
) -> None:
    client: http_client.CollectionBaseClient = ctx.obj.client
    data = {}
    if project_id is not None:
        data["project_id"] = str(project_id)
    if name is not None:
        data["name"] = name
    if description is not None:
        data["description"] = description
    rsa_key_resp = rsa_key_lib.update_rsa_key(client, uuid, data)
    _print_rsa_keys([rsa_key_resp])


def _print_rsa_keys(rsa_keys: tp.List[dict]) -> None:
    table = prettytable.PrettyTable()
    table.field_names = [
        "UUID",
        "Project",
        "Name",
        "Status",
    ]

    for rsa_key in rsa_keys:
        table.add_row(
            [
                rsa_key["uuid"],
                rsa_key["project_id"],
                rsa_key["name"],
                rsa_key["status"],
            ]
        )

    click.echo(table)
