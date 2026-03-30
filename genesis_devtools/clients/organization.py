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
from gcl_sdk.clients.http import base as http_client

from genesis_devtools import constants as c


def list_organizations(
    client: http_client.CollectionBaseClient, **filters
) -> list[dict[str, tp.Any]]:
    return client.filter(c.ORGANIZATION_COLLECTION, **filters)


def get_organization(
    client: http_client.CollectionBaseClient,
    organization_uuid: sys_uuid.UUID,
):
    organization = client.get(c.ORGANIZATION_COLLECTION, uuid=organization_uuid)
    return organization


def add_organization(
    client: http_client.CollectionBaseClient,
    organization: dict[str, tp.Any],
) -> dict[str, tp.Any]:
    try:
        organization_resp = client.create(c.ORGANIZATION_COLLECTION, data=organization)
    except bazooka_exc.ConflictError:
        raise click.ClickException("organization already exists")
    return organization_resp


def delete_organization(
    client: http_client.CollectionBaseClient,
    uuid: sys_uuid.UUID,
) -> None:
    try:
        client.delete(c.ORGANIZATION_COLLECTION, uuid=uuid)
    except bazooka_exc.NotFoundError:
        raise click.ClickException(f"organization with UUID {uuid} not found")
