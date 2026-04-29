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

import base64 as base64_lib
import json
import os
import typing as tp
import uuid as sys_uuid

import rich_click as click
from genesis_devtools.common.table import get_table, print_table, show_data

from genesis_devtools.clients import base_client
from genesis_devtools import constants as c

ENTITY = "config"
ENTITY_COLLECTION = c.CONFIG_COLLECTION


@click.group(f"{ENTITY}s", help=f"Manage {ENTITY}s in the Genesis installation")
def configs_group():
    pass


@configs_group.command("list", help=f"List {ENTITY}s")
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
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    entities = base_client.list_entities(client, ENTITY_COLLECTION)
    if node is not None:
        entities = [
            config for config in entities if config["target"]["node"] == str(node)
        ]

    _print_entities(entities)


@configs_group.command("show", help=f"Show {ENTITY}")
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
    client = base_client.get_user_api_client(ctx.obj.auth_data)

    envs = {}
    cfgs = {}
    # Handle envs
    for e in os.environ:
        if e.startswith(env_prefix):
            key = e[len(env_prefix) :]
            click.echo(f"Found env {key}")
            value = os.environ[e]
            envs[key] = value

    if envs:
        if env_format == "env":
            content = "\n".join([f"{k}={v}" for k, v in envs.items()])
        elif env_format == "json":
            content = json.dumps(envs, indent=2)
        else:
            raise ValueError(f"Unknown env format {env_format}")

        data = {
            "uuid": str(uuid) if uuid is not None else str(sys_uuid.uuid4()),
            "name": "envs",
            "target": {"kind": "node", "node": str(node)},
            "path": env_path,
            "body": {"content": content, "kind": "text"},
            "project_id": str(project_id),
        }
        base_client.add_entity(client, ENTITY_COLLECTION, data)
        click.echo(f"Saved envs to {env_path}")

    # Handle configs
    for e in os.environ:
        if not e.startswith(cfg_prefix):
            continue

        key = e[len(cfg_prefix) :]

        # Detect key kind, There are following mandatory envs to detect key kind:
        # GCT_CFG_TEXT_<key>
        # GCT_CFG_PATH_<key>
        if key.startswith("TEXT_"):
            name = key[len("TEXT_") :]
            value = os.environ[e]
            cfgs.setdefault(name, {})["text"] = value
        elif key.startswith("PATH_"):
            name = key[len("PATH_") :]
            value = os.environ[e]
            cfgs.setdefault(name, {})["path"] = value
        else:
            raise ValueError(f"Unknown kind {key}")

    # Validate configurations
    # Foramt:
    # {
    #     "name": {"path": "/path/to/config", "text": "content is here ..."},
    # }
    for name, cfg in cfgs.items():
        if "text" not in cfg or "path" not in cfg:
            raise ValueError(f"Config {name} doesn't have text or path")

        click.echo(f"Found config {name}")

        if base64:
            cfg["text"] = base64_lib.b64decode(cfg["text"]).decode("utf-8")

        data = {
            "name": name,
            "target": {"kind": "node", "node": str(node)},
            "path": cfg["path"],
            "body": {"content": cfg["text"], "kind": "text"},
            "project_id": str(project_id),
        }
        base_client.add_entity(client, ENTITY_COLLECTION, data)
        click.echo(f"Saved config to {cfg['path']}")


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
    if uuid is None and node is None:
        raise click.UsageError("Either uuid or node must be provided")

    client = base_client.get_user_api_client(ctx.obj.auth_data)

    if uuid is not None:
        base_client.delete_entity(client, ENTITY_COLLECTION, uuid)
    else:
        configs = base_client.list_entities(client, ENTITY_COLLECTION)
        for config in configs:
            if config["target"]["node"] == str(node):
                base_client.delete_entity(client, ENTITY_COLLECTION, config["uuid"])


def _print_entities(entities: tp.List[dict]) -> None:
    table = get_table()
    table.add_column("UUID")
    table.add_column("Name")
    table.add_column("Path")
    table.add_column("Mode")
    table.add_column("Owner")
    table.add_column("Group")
    table.add_column("Status")

    for entity in entities:
        table.add_row(
            entity["uuid"],
            entity["name"],
            entity["path"],
            entity["mode"],
            entity["owner"],
            entity["group"],
            entity["status"],
        )

    print_table(table)
