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

import os
import typing as tp
import uuid as sys_uuid

import rich_click as click
from genesis_devtools.common.table import get_table, print_table, show_data

from genesis_devtools.clients import base_client

from genesis_devtools import constants as c
from genesis_devtools import utils

ENTITY = "ssh_key"
ENTITY_COLLECTION = c.SSH_KEY_COLLECTION


@click.group(f"{ENTITY}s", help=f"Manage {ENTITY}s in the Genesis installation")
def ssh_keys_group():
    pass


@ssh_keys_group.command("list", help=f"List {ENTITY}s")
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


@ssh_keys_group.command("show", help=f"Show {ENTITY}")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.pass_context
def show_cmd(
    ctx: click.Context,
    uuid: str,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    data = base_client.get_entity(client, ENTITY_COLLECTION, uuid)
    show_data(data)


@ssh_keys_group.command("delete", help=f"Delete {ENTITY}")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.pass_context
def delete_cmd(
    ctx: click.Context,
    uuid: str,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    base_client.delete_entity(client, ENTITY_COLLECTION, uuid)


@ssh_keys_group.command(
    "add",
    help=f"Add a new {ENTITY} to the Genesis installation, example: `secret ssh_keys add "
    f"--node 2cc70850-3df7-4234-b9c1-0e20ed3672c7 --user ubuntu --target_public_key ~/.ssh/id_rsa.pub`",
)
@click.pass_context
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help=f"UUID of the {ENTITY}",
)
@click.option(
    "-p",
    "--project-id",
    type=click.UUID,
    required=False,
    help=f"Name of the project in which to deploy the {ENTITY}",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default=f"test_{ENTITY}",
    help=f"Name of the {ENTITY}",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default="",
    help=f"Description of the {ENTITY}",
)
@click.option(
    "--node",
    type=click.UUID,
    required=False,
    help="node uuid",
)
@click.option(
    "--node_set",
    type=click.UUID,
    required=False,
    help="node_set uuid",
)
@click.option(
    "--user",
    type=str,
    required=True,
    help=f"user name of the {ENTITY}",
)
@click.option(
    "--target_public_key",
    type=str,
    required=False,
    help="key or path to it, for example: /home/user/.ssh/id_rsa.pub",
)
def add_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    project_id: sys_uuid.UUID | None,
    name: str,
    description: str,
    node: sys_uuid.UUID | None,
    node_set: sys_uuid.UUID | None,
    user: str,
    target_public_key: str | None,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    if uuid is None:
        uuid = sys_uuid.uuid4()

    data: dict[str, tp.Any] = {
        "uuid": str(uuid),
        "name": name,
        "description": description,
        "user": str(user),
    }

    if node is None and node_set is None:
        raise click.ClickException("Either node or node_set must be specified")
    if node is not None:
        target_entity = base_client.get_entity(client, c.NODE_COLLECTION, node)
        data["target"] = {
            "kind": "node",
            "node": str(node),
        }
    else:
        target_entity = base_client.get_entity(client, c.SET_COLLECTION, node_set)
        data["target"] = {
            "kind": "node_set",
            "node_set": str(node_set),
        }

    if target_public_key is not None:
        path = os.path.expanduser(target_public_key)
        if os.path.exists(path):
            with open(path, "r") as f:
                target_public_key = f.read()
        data["target_public_key"] = target_public_key.strip()

    if project_id is None:
        project_id = target_entity["project_id"]
    data["project_id"] = str(project_id)

    entity = base_client.add_entity(client, ENTITY_COLLECTION, data)
    show_data(entity)


@ssh_keys_group.command("update", help=f"Update {ENTITY}")
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
    help=f"Name of the project in which to deploy the {ENTITY}",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default=None,
    help=f"Name of the {ENTITY}",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default=None,
    help=f"Description of the {ENTITY}",
)
def update_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID,
    project_id: sys_uuid.UUID | None,
    name: str | None,
    description: str | None,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    data = {}
    if project_id is not None:
        data["project_id"] = str(project_id)
    if name is not None:
        data["name"] = name
    if description is not None:
        data["description"] = description

    entity = base_client.update_entity(client, ENTITY_COLLECTION, uuid, data)
    show_data(entity)


def _print_entities(ssh_keys: tp.List[dict]) -> None:
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
            str(ssh_key["target"]),
            ssh_key["user"],
            ssh_key["status"],
        )

    print_table(table)
