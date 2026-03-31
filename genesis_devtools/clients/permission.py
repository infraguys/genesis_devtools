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


def list_permissions(
    client: http_client.CollectionBaseClient, **filters
) -> list[dict[str, tp.Any]]:
    return client.filter(c.PERMISSION_COLLECTION, **filters)


def get_permission(
    client: http_client.CollectionBaseClient,
    permission_uuid: sys_uuid.UUID,
):
    permission = client.get(c.PERMISSION_COLLECTION, uuid=permission_uuid)
    return permission


def add_permission(
    client: http_client.CollectionBaseClient,
    permission: dict[str, tp.Any],
) -> dict[str, tp.Any]:
    try:
        permission_resp = client.create(c.PERMISSION_COLLECTION, data=permission)
    except bazooka_exc.ConflictError:
        raise click.ClickException("permission already exists")
    return permission_resp


def delete_permission(
    client: http_client.CollectionBaseClient,
    uuid: sys_uuid.UUID,
) -> None:
    try:
        client.delete(c.PERMISSION_COLLECTION, uuid=uuid)
    except bazooka_exc.NotFoundError:
        raise click.ClickException(f"permission with UUID {uuid} not found")
