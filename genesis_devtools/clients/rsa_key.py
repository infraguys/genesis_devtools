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


def list_rsa_keys(
    client: http_client.CollectionBaseClient, **filters
) -> list[dict[str, tp.Any]]:
    return client.filter(c.RSA_KEY_COLLECTION, **filters)


def get_rsa_key(
    client: http_client.CollectionBaseClient,
    rsa_key_uuid: sys_uuid.UUID,
):
    rsa_key = client.get(c.RSA_KEY_COLLECTION, uuid=rsa_key_uuid)
    return rsa_key


def add_rsa_key(
    client: http_client.CollectionBaseClient,
    rsa_key: dict[str, tp.Any],
) -> dict[str, tp.Any]:
    try:
        rsa_key_resp = client.create(c.RSA_KEY_COLLECTION, data=rsa_key)
    except bazooka_exc.ConflictError:
        raise click.ClickException("rsa_key already exists")
    return rsa_key_resp


def update_rsa_key(
    client: http_client.CollectionBaseClient,
    rsa_key_uuid: sys_uuid.UUID,
    data: dict[str, tp.Any],
) -> dict[str, tp.Any]:
    rsa_key_resp = client.update(c.RSA_KEY_COLLECTION, rsa_key_uuid, **data)
    return rsa_key_resp


def delete_rsa_key(
    client: http_client.CollectionBaseClient,
    uuid: sys_uuid.UUID,
) -> None:
    try:
        client.delete(c.RSA_KEY_COLLECTION, uuid=uuid)
    except bazooka_exc.NotFoundError:
        raise click.ClickException(f"rsa_key with UUID {uuid} not found")
