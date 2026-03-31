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


def list_certificates(
    client: http_client.CollectionBaseClient, **filters
) -> list[dict[str, tp.Any]]:
    return client.filter(c.CERTIFICATE_COLLECTION, **filters)


def get_certificate(
    client: http_client.CollectionBaseClient,
    certificate_uuid: sys_uuid.UUID,
):
    certificate = client.get(c.CERTIFICATE_COLLECTION, uuid=certificate_uuid)
    return certificate


def add_certificate(
    client: http_client.CollectionBaseClient,
    certificate: dict[str, tp.Any],
) -> dict[str, tp.Any]:
    try:
        certificate_resp = client.create(c.CERTIFICATE_COLLECTION, data=certificate)
    except bazooka_exc.ConflictError:
        raise click.ClickException("certificate already exists")
    return certificate_resp


def update_certificate(
    client: http_client.CollectionBaseClient,
    certificate_uuid: sys_uuid.UUID,
    data: dict[str, tp.Any],
) -> dict[str, tp.Any]:
    certificate_resp = client.update(c.CERTIFICATE_COLLECTION, certificate_uuid, **data)
    return certificate_resp


def delete_certificate(
    client: http_client.CollectionBaseClient,
    uuid: sys_uuid.UUID,
) -> None:
    try:
        client.delete(c.CERTIFICATE_COLLECTION, uuid=uuid)
    except bazooka_exc.NotFoundError:
        raise click.ClickException(f"certificate with UUID {uuid} not found")
