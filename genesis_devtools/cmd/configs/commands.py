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
from genesis_devtools.clients import config as config_lib
from genesis_devtools import constants as c


@click.group("configs", help="Manager configs in the Genesis installation")
def configs_group():
    pass


@configs_group.command("list", help="List configs")
@click.option(
    "-n",
    "--node",
    type=click.UUID,
    default=None,
    help="Filter configs by node",
)
@click.pass_context
def list_config_cmd(
    ctx: click.Context,
    node: sys_uuid.UUID | None,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    table = get_table()

    configs = config_lib.list_config(client, node)

    table.add_column("UUID")
    table.add_column("Name")
    table.add_column("Path")
    table.add_column("Mode")
    table.add_column("Owner")
    table.add_column("Group")
    table.add_column("Status")

    for config in configs:
        table.add_row(
            config["uuid"],
            config["name"],
            config["path"],
            config["mode"],
            config["owner"],
            config["group"],
            config["status"],
        )

    print_table(table)


@configs_group.command(
    "add-from-env", help="Add configuration from environment variables"
)
@click.option(
    "-p",
    "--project-id",
    type=click.UUID,
    required=True,
    help="Project ID ofthe config",
)
@click.option(
    "--env-prefix",
    default="GCT_ENV_",
    help="Prefix used to filter environment variables for envs",
)
@click.option(
    "--env-path",
    default="/var/lib/genesis/app.env",
    help="Path to the env file will be saved on the node",
)
@click.option(
    "--env-format",
    default="env",
    type=click.Choice([s for s in tp.get_args(c.ENV_FILE_FORMAT)]),
    show_default=True,
    help="Format of the env file",
)
@click.option(
    "--cfg-prefix",
    default="GCT_CFG_",
    help="Prefix used to filter environment variables for configs",
)
@click.option(
    "--base64",
    is_flag=True,
    default=False,
    help="Base64 encode is enabled for configs",
)
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help="Config UUID",
)
@click.argument("node", type=click.UUID)
@click.pass_context
def add_config_from_env_cmd(
    ctx: click.Context,
    project_id: sys_uuid.UUID,
    env_prefix: str,
    env_path: str,
    env_format: c.ENV_FILE_FORMAT,
    cfg_prefix: str,
    base64: bool,
    uuid: sys_uuid.UUID | None,
    node: sys_uuid.UUID,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    config_lib.add_config_from_env(
        client,
        project_id,
        env_prefix,
        env_path,
        env_format,
        cfg_prefix,
        base64,
        node,
        uuid,
    )


@configs_group.command("delete", help="Delete configuration from environment variables")
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help="Config UUID",
)
@click.option(
    "-n",
    "--node",
    type=click.UUID,
    default=None,
    help="Delete all configs for the node",
)
@click.pass_context
def delete_config_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    node: sys_uuid.UUID | None,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    config_lib.delete_config(client, uuid, node)
