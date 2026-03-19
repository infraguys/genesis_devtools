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


def list_idps(
    client: http_client.CollectionBaseClient, **filters
) -> list[dict[str, tp.Any]]:
    return client.filter(c.IDP_COLLECTION, **filters)


def get_idp(
    client: http_client.CollectionBaseClient,
    idp_uuid: sys_uuid.UUID,
):
    idp = client.get(c.IDP_COLLECTION, uuid=idp_uuid)
    return idp


def add_idp(
    client: http_client.CollectionBaseClient,
    idp: dict[str, tp.Any],
) -> dict[str, tp.Any]:
    try:
        idp_resp = client.create(c.IDP_COLLECTION, data=idp)
    except bazooka_exc.ConflictError:
        raise click.ClickException("idp already exists")
    return idp_resp


def delete_idp(
    client: http_client.CollectionBaseClient,
    uuid: sys_uuid.UUID,
) -> None:
    try:
        client.delete(c.IDP_COLLECTION, uuid=uuid)
    except bazooka_exc.NotFoundError:
        raise click.ClickException(f"idp with UUID {uuid} not found")
