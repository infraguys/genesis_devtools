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

import time
import uuid as sys_uuid

from bazooka import exceptions as bazooka_exc
import rich_click as click
from genesis_devtools.common.table import get_table, print_table, show_data

from genesis_devtools.clients import base_client
from genesis_devtools import logger
from genesis_devtools import utils
from genesis_devtools import constants as c

ENTITY = "node"
ENTITY_COLLECTION = c.NODE_COLLECTION

LIST_FIELDS = ["UUID", "Project", "Name", "Cores", "RAM", "IP", "Status"]


@click.group("nodes", help="Manage nodes in the Genesis installation")
def nodes_group():
    pass


@nodes_group.command("list", help=f"List {ENTITY}s")
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


@nodes_group.command("show", help=f"Show {ENTITY}")
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


@nodes_group.command("delete", help=f"Delete {ENTITY}")
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


@nodes_group.command("add", help="Add a new node to the Genesis installation")
@click.pass_context
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help="UUID of the node",
)
@click.option(
    "-p",
    "--project-id",
    type=click.UUID,
    required=True,
    help="Name of the project in which to deploy the node",
)
@click.option(
    "-c",
    "--cores",
    type=int,
    default=1,
    show_default=True,
    help="Number of cores to allocate for the node",
)
@click.option(
    "-r",
    "--ram",
    type=int,
    default=1024,
    show_default=True,
    help="Amount of RAM in Mb to allocate for the node",
)
@click.option(
    "-d",
    "--root-disk",
    type=int,
    default=10,
    show_default=True,
    help="Number of GiB of root disk to allocate for the node",
)
@click.option(
    "-i",
    "--image",
    type=str,
    required=True,
    help="Name of the image to deploy",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default="node",
    help="Name of the node",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default="",
    help="Description of the node",
)
@click.option(
    "--wait",
    type=bool,
    is_flag=True,
    default=False,
    help="Wait until the node is running",
)
def add_node_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    project_id: sys_uuid.UUID,
    cores: int,
    ram: int,
    root_disk: int,
    image: str,
    name: str,
    description: str,
    wait: bool,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    log = logger.ClickLogger()
    if uuid is None:
        uuid = sys_uuid.uuid4()
    data = {
        "uuid": str(uuid),
        "project_id": str(project_id),
        "cores": cores,
        "ram": ram,
        "name": name,
        "description": description,
        "disk_spec": {
            "kind": "root_disk",
            "size": root_disk,
            "image": image,
        },
    }
    entity = base_client.add_entity(client, ENTITY_COLLECTION, data)
    if not wait:
        show_data(entity)
        return
    while entity["status"] != "ACTIVE":
        log.info(f"Waiting for node to be ready. Status: {entity['status']}")
        time.sleep(2)
        entity = client.get(c.NODE_COLLECTION, uuid=uuid)
    show_data(entity)


@nodes_group.command("add-or-update", help="Add a new node or update an existing one")
@click.pass_context
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help="UUID of the node",
)
@click.option(
    "-p",
    "--project-id",
    type=click.UUID,
    required=True,
    help="Name of the project in which to deploy the node",
)
@click.option(
    "-c",
    "--cores",
    type=int,
    default=1,
    show_default=True,
    help="Number of cores to allocate for the node",
)
@click.option(
    "-r",
    "--ram",
    type=int,
    default=1024,
    show_default=True,
    help="Amount of RAM in Mb to allocate for the node",
)
@click.option(
    "-d",
    "--root-disk",
    type=int,
    default=10,
    show_default=True,
    help="Number of GiB of root disk to allocate for the node",
)
@click.option(
    "-i",
    "--image",
    type=str,
    required=True,
    help="Name of the image to deploy",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default="node",
    help="Name of the node",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default="",
    help="Description of the node",
)
@click.option(
    "--wait",
    type=bool,
    is_flag=True,
    default=False,
    help="Wait until the node is running",
)
def add_or_update_node_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    project_id: sys_uuid.UUID,
    cores: int,
    ram: int,
    root_disk: int,
    image: str,
    name: str,
    description: str,
    wait: bool,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    if uuid is None:
        return ctx.invoke(
            add_node_cmd,
            uuid=uuid,
            project_id=project_id,
            cores=cores,
            ram=ram,
            root_disk=root_disk,
            image=image,
            name=name,
            description=description,
            wait=wait,
        )

    try:
        base_client.get_entity(client, ENTITY_COLLECTION, uuid)
    except bazooka_exc.NotFoundError:
        return ctx.invoke(
            add_node_cmd,
            uuid=uuid,
            project_id=project_id,
            cores=cores,
            ram=ram,
            root_disk=root_disk,
            image=image,
            name=name,
            description=description,
            wait=wait,
        )

    data = {
        "cores": cores,
        "ram": ram,
        "name": name,
        "description": description,
        "disk_spec": {
            "kind": "root_disk",
            "size": root_disk,
            "image": image,
        },
    }
    entity = base_client.update_entity(client, ENTITY_COLLECTION, uuid, data)
    if not wait:
        show_data(entity)
        return None
    log = logger.ClickLogger()
    while entity["status"] != "ACTIVE":
        log.info(f"Waiting for node to be ready. Status: {entity['status']}")
        time.sleep(2)
        entity = client.get(c.NODE_COLLECTION, uuid=uuid)
    show_data(entity)
    return None


def _print_entities(entities) -> None:
    table = get_table(*LIST_FIELDS)

    for node in entities:
        table.add_row(
            node["uuid"],
            node["project_id"],
            node["name"],
            str(node["cores"]),
            str(node["ram"]),
            node["default_network"].get("ipv4", ""),
            node["status"],
        )

    print_table(table)
