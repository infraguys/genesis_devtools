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

import rich_click as click
from genesis_devtools.common.table import get_table, print_table

from genesis_devtools.clients.base_client import get_user_api_client
from genesis_devtools.clients import node as node_lib
from genesis_devtools.common import utils


@click.group("nodes", help="Manager nodes in the Genesis installation")
def nodes_group():
    pass


@nodes_group.command("list", help="List nodes")
@click.option(
    "-P",
    "--project-id",
    type=str,
    default=None,
    help="Filter nodes by project",
)
@click.pass_context
def list_node_cmd(
    ctx: click.Context,
    project_id: str | None,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    nodes = node_lib.list_nodes(client, project_id=project_id)
    _print_nodes(nodes)


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
    client = get_user_api_client(ctx.obj.auth_data)
    node = node_lib.add_node(
        client,
        uuid,
        project_id,
        cores,
        ram,
        root_disk,
        image,
        name,
        description,
        wait,
    )
    _print_nodes([node])


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
    client = get_user_api_client(ctx.obj.auth_data)
    node = node_lib.add_or_update_node(
        client,
        uuid,
        project_id,
        cores,
        ram,
        root_disk,
        image,
        name,
        description,
        wait,
    )
    _print_nodes([node])


@nodes_group.command("delete", help="Delete node")
@click.argument(
    "uuid_name",
    type=str,
)
@click.pass_context
def delete_node_cmd(
    ctx: click.Context,
    uuid_name: str,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    if not utils.is_valid_uuid(uuid_name):
        nodes = node_lib.list_nodes(client, name=uuid_name)
        if nodes:
            uuid_name = nodes[0]["uuid"]
        else:
            raise click.ClickException(f"Node with name {uuid_name} not found")
    node_lib.delete_node(client, uuid_name)


@nodes_group.command("show", help="Show node")
@click.argument(
    "uuid_name",
    type=str,
)
@click.pass_context
def show_node_cmd(
    ctx: click.Context,
    uuid_name: str,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    if not utils.is_valid_uuid(uuid_name):
        nodes = node_lib.list_nodes(client, name=uuid_name)
        if nodes:
            uuid_name = nodes[0]["uuid"]
        else:
            raise click.ClickException(f"node with name {uuid_name} not found")
    node = node_lib.get_node(client, uuid_name)
    _print_nodes([node])


def _print_nodes(nodes: list) -> None:
    table = get_table()
    table.add_column("UUID")
    table.add_column("Project")
    table.add_column("Name")
    table.add_column("Cores")
    table.add_column("RAM")
    table.add_column("Root Disk")
    table.add_column("Image")
    table.add_column("IP")
    table.add_column("Status")

    for node in nodes:
        table.add_row(
            node["uuid"],
            node["project_id"],
            node["name"],
            str(node["cores"]),
            str(node["ram"]),
            str(node["disk_spec"].get("size", "Unknown")),
            node["disk_spec"].get("image", "Unknown"),
            node["default_network"].get("ipv4", ""),
            node["status"],
        )
    print_table(table)
