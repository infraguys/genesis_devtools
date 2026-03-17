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

from genesis_devtools.clients import node as node_lib


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
    client: http_client.CollectionBaseClient = ctx.obj.client
    table = prettytable.PrettyTable()
    nodes = node_lib.list_nodes(client, project_id)

    table.field_names = [
        "UUID",
        "Project",
        "Name",
        "Cores",
        "RAM",
        "Root Disk",
        "Image",
        "IP",
        "Status",
    ]

    for node in nodes:
        table.add_row(
            [
                node["uuid"],
                node["project_id"],
                node["name"],
                node["cores"],
                node["ram"],
                node["disk_spec"].get("size", "unknown"),
                node["disk_spec"].get("image", "unknown"),
                node["default_network"].get("ipv4", ""),
                node["status"],
            ]
        )

    print(table)


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
    client: http_client.CollectionBaseClient = ctx.obj.client
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
    _print_node(node)


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
    client: http_client.CollectionBaseClient = ctx.obj.client
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
    _print_node(node)


@nodes_group.command("delete", help="Delete node")
@click.argument(
    "uuid",
    type=click.UUID,
)
@click.pass_context
def delete_node_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
) -> None:
    client: http_client.CollectionBaseClient = ctx.obj.client
    node_lib.delete_node(client, uuid)


def _print_node(node: dict) -> None:
    table = prettytable.PrettyTable()
    table.field_names = [
        "UUID",
        "Project",
        "Name",
        "Cores",
        "RAM",
        "Root Disk",
        "Image",
        "IP",
        "Status",
    ]
    table.add_row(
        [
            node["uuid"],
            node["project_id"],
            node["name"],
            node["cores"],
            node["ram"],
            node["disk_spec"]["size"],
            node["disk_spec"]["image"],
            node["default_network"].get("ipv4", ""),
            node["status"],
        ]
    )
    click.echo(table)
