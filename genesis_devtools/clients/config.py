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
import json
import base64 as base64_lib
import typing as tp
import uuid as sys_uuid

import rich_click as click

if tp.TYPE_CHECKING:
    from gcl_sdk.clients.http import base as http_client

from genesis_devtools import logger
from genesis_devtools import constants as c


def list_config(
    client: http_client.CollectionBaseClient,
    node: sys_uuid.UUID | None,
) -> list[dict[str, tp.Any]]:

    configs = client.filter("/v1/config/configs/")

    # TODO(akremenetsky): Add set support
    if node is not None:
        configs = [c for c in configs if c["target"]["node"] == str(node)]

    return configs


def add_config_from_env(
    client: http_client.CollectionBaseClient,
    project_id: sys_uuid.UUID,
    env_prefix: str,
    env_path: str,
    env_format: c.ENV_FILE_FORMAT,
    cfg_prefix: str,
    base64: bool,
    node: sys_uuid.UUID,
    uuid: sys_uuid.UUID | None = None,
) -> dict[str, tp.Any]:
    envs = {}
    cfgs = {}
    log = logger.ClickLogger()

    # Handle envs
    for e in os.environ:
        if e.startswith(env_prefix):
            key = e[len(env_prefix) :]

            log.info(f"Found env {key}")
            value = os.environ[e]
            envs[key] = value

    if envs:
        if env_format == "env":
            content = "\n".join([f"{k}={v}" for k, v in envs.items()])
        elif env_format == "json":
            content = json.dumps(envs, indent=2)
        else:
            raise ValueError(f"Unknown env format {env_format}")

        client.create(
            "/v1/config/configs/",
            data={
                "uuid": str(uuid) if uuid is not None else str(sys_uuid.uuid4()),
                "name": "envs",
                "target": {"kind": "node", "node": str(node)},
                "path": env_path,
                "body": {"content": content, "kind": "text"},
                "project_id": str(project_id),
            },
        )
        log.important(f"Saved envs to {env_path}")

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
            raise ValueError(f"Config {key} dons't have text or path")

        log.info(f"Found config {key}")

        if base64:
            cfg["text"] = base64_lib.b64decode(cfg["text"]).decode("utf-8")

        client.create(
            "/v1/config/configs/",
            data={
                "name": name,
                "target": {"kind": "node", "node": str(node)},
                "path": cfg["path"],
                "body": {"content": cfg["text"], "kind": "text"},
                "project_id": str(project_id),
            },
        )
        log.important(f"Saved config to {cfg['path']}")


def delete_config(
    client: http_client.CollectionBaseClient,
    uuid: sys_uuid.UUID | None,
    node: sys_uuid.UUID | None,
) -> None:
    if uuid is None and node is None:
        raise click.UsageError("Either uuid or node must be provided")

    log = logger.ClickLogger()

    if uuid is not None:
        client.delete("/v1/config/configs/", uuid=uuid)
        log.important(f"Deleted config {uuid}")
    else:
        configs = client.filter("/v1/config/configs/")
        for config in configs:
            if config["target"]["node"] == str(node):
                client.delete("/v1/config/configs/", uuid=config["uuid"])
                log.important(f"Deleted config {config['uuid']}")
