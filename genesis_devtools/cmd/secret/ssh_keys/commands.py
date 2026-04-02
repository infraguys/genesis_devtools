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
from genesis_devtools.common.table import get_table, print_table

from genesis_devtools.clients.base_client import get_user_api_client

from genesis_devtools.clients import ssh_key as ssh_key_lib
from genesis_devtools.common import utils


@click.group("ssh_keys", help="Manage ssh_keys in the Genesis installation")
def ssh_keys_group():
    pass


@ssh_keys_group.command("list", help="List ssh_keys")
@click.pass_context
def list_ssh_keys(ctx: click.Context) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    ssh_keys = ssh_key_lib.list_ssh_keys(client)
    _print_ssh_keys(ssh_keys)


@ssh_keys_group.command("show", help="Show ssh_key")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.pass_context
def show_ssh_key_cmd(
    ctx: click.Context,
    uuid: str,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    if not utils.is_valid_uuid(uuid):
        ssh_keys = ssh_key_lib.list_ssh_keys(client, name=uuid)
        if ssh_keys:
            uuid = ssh_keys[0]["uuid"]
        else:
            raise click.ClickException(f"ssh_key with name {uuid} not found")
    ssh_key = ssh_key_lib.get_ssh_key(client, uuid)
    _print_ssh_keys([ssh_key])


@ssh_keys_group.command("delete", help="Delete ssh_key")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.pass_context
def delete_ssh_key_cmd(
    ctx: click.Context,
    uuid: str,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    if not utils.is_valid_uuid(uuid):
        ssh_keys = ssh_key_lib.list_ssh_keys(client, name=uuid)
        if ssh_keys:
            uuid = ssh_keys[0]["uuid"]
        else:
            raise click.ClickException(f"ssh_key with name {uuid} not found")
    ssh_key_lib.delete_ssh_key(client, uuid)


@ssh_keys_group.command("add", help="Add a new ssh_key to the Genesis installation")
@click.pass_context
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help="UUID of the ssh_key",
)
@click.option(
    "-p",
    "--project-id",
    type=click.UUID,
    required=True,
    help="Name of the project in which to deploy the ssh_key",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default="test_ssh_key",
    help="Name of the ssh_key",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default="",
    help="Description of the ssh_key",
)
@click.option(
    "--node",
    type=click.UUID,
    required=True,
    help="node uuid of the ssh_key",
)
@click.option(
    "--user",
    type=str,
    required=True,
    help="user uuid of the ssh_key",
)
@click.option(
    "--target_public_key",
    type=str,
    default=None,
)
def add_ssh_key_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    project_id: sys_uuid.UUID,
    name: str,
    description: str,
    node: sys_uuid.UUID,
    user: str,
    target_public_key: str | None,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    if uuid is None:
        uuid = sys_uuid.uuid4()

    data = {
        "uuid": str(uuid),
        "project_id": str(project_id),
        "name": name,
        "description": description,
        "target": {
            "kind": "node",
            "node": str(node),
        },
        "user": str(user),
    }

    if target_public_key is not None:
        data["target_public_key"] = target_public_key

    ssh_key_resp = ssh_key_lib.add_ssh_key(client, data)
    _print_ssh_keys([ssh_key_resp])


@ssh_keys_group.command("update", help="Update ssh_key")
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
    help="Name of the project in which to deploy the ssh_key",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default=None,
    help="Name of the ssh_key",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default=None,
    help="Description of the ssh_key",
)
def update_ssh_key_cmd(
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
    ssh_key_resp = ssh_key_lib.update_ssh_key(client, uuid, data)
    _print_ssh_keys([ssh_key_resp])


def _print_ssh_keys(ssh_keys: tp.List[dict]) -> None:
    table = get_table()
    table.add_column("UUID")
    table.add_column("Project")
    table.add_column("Name")
    table.add_column("Target")
    table.add_column("User")
    table.add_column("Status")

    for ssh_key in ssh_keys:
        table.add_row(
            ssh_key["uuid"],
            ssh_key["project_id"],
            ssh_key["name"],
            ssh_key["target"],
            ssh_key["user"],
            ssh_key["status"],
        )

    print_table(table)
