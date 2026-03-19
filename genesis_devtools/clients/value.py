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

import click
from bazooka import exceptions as bazooka_exc
from gcl_sdk.clients.http import base as http_client

from genesis_devtools import constants as c


def list_values(
    client: http_client.CollectionBaseClient, **filters
) -> list[dict[str, tp.Any]]:
    return client.filter(c.VALUE_COLLECTION, **filters)


def get_value(
    client: http_client.CollectionBaseClient,
    value_uuid: sys_uuid.UUID,
):
    value = client.get(c.VALUE_COLLECTION, uuid=value_uuid)
    return value


def add_value(
    client: http_client.CollectionBaseClient,
    value: dict[str, tp.Any],
) -> dict[str, tp.Any]:
    try:
        value_resp = client.create(c.VALUE_COLLECTION, data=value)
    except bazooka_exc.ConflictError:
        raise click.ClickException("value already exists")
    return value_resp


def update_value(
    client: http_client.CollectionBaseClient,
    value_uuid: sys_uuid.UUID,
    data: dict[str, tp.Any],
) -> dict[str, tp.Any]:
    value_resp = client.update(c.VALUE_COLLECTION, value_uuid, **data)
    return value_resp


def delete_value(
    client: http_client.CollectionBaseClient,
    uuid: sys_uuid.UUID,
) -> None:
    try:
        client.delete(c.VALUE_COLLECTION, uuid=uuid)
    except bazooka_exc.NotFoundError:
        raise click.ClickException(f"value with UUID {uuid} not found")
