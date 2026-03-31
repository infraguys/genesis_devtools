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
from bazooka import exceptions as bazooka_exc

if tp.TYPE_CHECKING:
    from gcl_sdk.clients.http import base as http_client

from genesis_devtools import constants as c


def list_ssh_keys(
    client: http_client.CollectionBaseClient, **filters
) -> list[dict[str, tp.Any]]:
    return client.filter(c.SSH_KEY_COLLECTION, **filters)


def get_ssh_key(
    client: http_client.CollectionBaseClient,
    ssh_key_uuid: sys_uuid.UUID,
):
    ssh_key = client.get(c.SSH_KEY_COLLECTION, uuid=ssh_key_uuid)
    return ssh_key


def add_ssh_key(
    client: http_client.CollectionBaseClient,
    ssh_key: dict[str, tp.Any],
) -> dict[str, tp.Any]:
    try:
        ssh_key_resp = client.create(c.SSH_KEY_COLLECTION, data=ssh_key)
    except bazooka_exc.ConflictError:
        raise click.ClickException("ssh_key already exists")
    return ssh_key_resp


def update_ssh_key(
    client: http_client.CollectionBaseClient,
    ssh_key_uuid: sys_uuid.UUID,
    data: dict[str, tp.Any],
) -> dict[str, tp.Any]:
    ssh_key_resp = client.update(c.SSH_KEY_COLLECTION, ssh_key_uuid, **data)
    return ssh_key_resp


def delete_ssh_key(
    client: http_client.CollectionBaseClient,
    uuid: sys_uuid.UUID,
) -> None:
    try:
        client.delete(c.SSH_KEY_COLLECTION, uuid=uuid)
    except bazooka_exc.NotFoundError:
        raise click.ClickException(f"ssh_key with UUID {uuid} not found")
