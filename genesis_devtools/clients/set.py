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

from genesis_devtools import constants as c

if tp.TYPE_CHECKING:
    from gcl_sdk.clients.http import base as http_client


def list_sets(
    client: http_client.CollectionBaseClient, **filters
) -> list[dict[str, tp.Any]]:
    return client.filter(c.SET_COLLECTION, **filters)


def get_set(
    client: http_client.CollectionBaseClient,
    set_uuid: str | sys_uuid.UUID,
):
    return client.get(c.SET_COLLECTION, uuid=set_uuid)


def add_set(
    client: http_client.CollectionBaseClient,
    data: dict[str, tp.Any],
) -> dict[str, tp.Any]:
    try:
        return client.create(c.SET_COLLECTION, data=data)
    except bazooka_exc.ConflictError:
        raise click.ClickException("set already exists")


def update_set(
    client: http_client.CollectionBaseClient,
    set_uuid: str | sys_uuid.UUID,
    data: dict[str, tp.Any],
) -> dict[str, tp.Any]:
    return client.update(c.SET_COLLECTION, set_uuid, **data)


def delete_set(
    client: http_client.CollectionBaseClient,
    uuid: str | sys_uuid.UUID,
) -> None:
    try:
        client.delete(c.SET_COLLECTION, uuid=uuid)
    except bazooka_exc.NotFoundError:
        raise click.ClickException(f"set with UUID {uuid} not found")
