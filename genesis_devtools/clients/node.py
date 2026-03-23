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
import typing as tp
import uuid as sys_uuid

import click
from bazooka import exceptions as bazooka_exc
from gcl_sdk.clients.http import base as http_client

from genesis_devtools import constants as c
from genesis_devtools import logger


def list_nodes(
    client: http_client.CollectionBaseClient,
    **filters,
) -> list[dict[str, tp.Any]]:
    return client.filter(c.NODE_COLLECTION, **filters)


def get_node(
    client: http_client.CollectionBaseClient,
    node_uuid: sys_uuid.UUID,
):
    node = client.get(c.NODE_COLLECTION, uuid=node_uuid)
    return node


def get_node_ip(node_data: dict[str, tp.Any]) -> str | None:
    return node_data["default_network"].get("ipv4", None)


def add_node(
    client: http_client.CollectionBaseClient,
    uuid: sys_uuid.UUID | None,
    project_id: sys_uuid.UUID,
    cores: int,
    ram: int,
    root_disk: int,
    image: str,
    name: str,
    description: str,
    wait: bool,
) -> dict[str, tp.Any]:
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

    # TODO(akremenetsky): Check the image exists

    try:
        node = client.create(c.NODE_COLLECTION, data=data)
    except bazooka_exc.ConflictError:
        raise click.ClickException(f"Node with UUID {uuid} already exists")

    if not wait:
        log.important(f"Node {uuid} created")
        return node

    while node["status"] != "ACTIVE":
        log.info(f"Waiting for node to be ready. Status: {node['status']}")
        time.sleep(2)
        node = client.get(c.NODE_COLLECTION, uuid=uuid)

    return node


def add_or_update_node(
    client: http_client.CollectionBaseClient,
    uuid: sys_uuid.UUID | None,
    project_id: sys_uuid.UUID,
    cores: int,
    ram: int,
    root_disk: int,
    image: str,
    name: str,
    description: str,
    wait: bool,
) -> dict[str, tp.Any]:
    # If no UUID is provided, create a new node
    if uuid is None:
        return add_node(
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

    # If UUID is provided, check if the node exists
    try:
        client.get(c.NODE_COLLECTION, uuid=uuid)
    except bazooka_exc.NotFoundError:
        return add_node(
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

    # If the node exists, update it
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

    return client.update(c.NODE_COLLECTION, uuid=uuid, **data)


def delete_node(
    client: http_client.CollectionBaseClient,
    uuid: sys_uuid.UUID | None,
) -> None:
    if uuid is None:
        raise click.UsageError("UUID must be provided")

    log = logger.ClickLogger()

    client.delete(c.NODE_COLLECTION, uuid=uuid)
    log.important(f"Deleted node {uuid}")
