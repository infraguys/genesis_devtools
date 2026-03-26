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


def list_element(
    client: http_client.CollectionBaseClient, **filters
) -> list[dict[str, tp.Any]]:
    return client.filter(c.ELEMENT_COLLECTION, **filters)


def get_element_uuid(
    client: http_client.CollectionBaseClient,
    element: dict[str, tp.Any],
) -> sys_uuid.UUID:
    # Try to get element by name
    if "uuid" not in element:
        if "name" not in element:
            raise click.ClickException("element must have a name")
        elements = list_element(client, name=element["name"])

        if not elements:
            raise click.ClickException(f"element '{element['name']}' not found")

        if len(elements) > 1:
            raise click.ClickException(
                f"Multiple elements found for '{element['name']}'"
            )

        return sys_uuid.UUID(elements[0]["uuid"])

    return sys_uuid.UUID(element["uuid"])


def add_element(
    client: http_client.CollectionBaseClient,
    element: dict[str, tp.Any],
) -> dict[str, tp.Any]:
    uuid = sys_uuid.uuid4()
    if "uuid" in element:
        uuid = sys_uuid.UUID(element["uuid"])
    else:
        element["uuid"] = str(uuid)

    try:
        element_resp = client.create(c.ELEMENT_COLLECTION, data=element)
    except bazooka_exc.ConflictError:
        raise click.ClickException(f"element with UUID {uuid} already exists")

    return element_resp


def update_element(
    client: http_client.CollectionBaseClient,
    element: dict[str, tp.Any],
) -> dict[str, tp.Any]:
    uuid = get_element_uuid(client, element)

    # Remove fields that are not allowed to be updated
    data = element.copy()
    data.pop("uuid", None)
    data.pop("version", None)
    data.pop("name", None)
    data.pop("schema_version", None)

    try:
        element_resp = client.update(c.ELEMENT_COLLECTION, uuid=uuid, **data)
    except bazooka_exc.NotFoundError:
        raise click.ClickException(f"element with UUID {uuid} not found")

    return element_resp


def delete_element(
    client: http_client.CollectionBaseClient,
    uuid: sys_uuid.UUID,
) -> None:
    try:
        client.delete(c.ELEMENT_COLLECTION, uuid=uuid)
    except bazooka_exc.NotFoundError:
        raise click.ClickException(f"element with UUID {uuid} not found")


def list_elements(
    client: http_client.CollectionBaseClient, **filters
) -> list[dict[str, tp.Any]]:
    return client.filter(c.ELEMENT_COLLECTION, **filters)


def list_resources(
    client: http_client.CollectionBaseClient,
    element_uuid: sys_uuid.UUID | str,
    **filters,
) -> list[dict[str, tp.Any]]:
    collection = f"{c.ELEMENT_COLLECTION}{element_uuid}/resources/"
    return client.filter(collection, **filters)


def get_resource(
    client: http_client.CollectionBaseClient,
    element_uuid: sys_uuid.UUID | str,
    resource_uuid: sys_uuid.UUID | str,
) -> dict[str, tp.Any]:
    return client.get(f"{c.ELEMENT_COLLECTION}{element_uuid}/resources/", resource_uuid)
