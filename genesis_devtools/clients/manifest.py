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


def list_manifests(
    client: http_client.CollectionBaseClient, **filters
) -> list[dict[str, tp.Any]]:
    return client.filter(c.MANIFEST_COLLECTION, **filters)


def get_manifest_uuid(
    client: http_client.CollectionBaseClient,
    manifest: dict[str, tp.Any],
) -> sys_uuid.UUID:
    # Try to get manifest by name
    if "uuid" not in manifest:
        if "name" not in manifest:
            raise click.ClickException("Manifest must have a name")
        manifests = list_manifests(client, name=manifest["name"])

        if not manifests:
            raise click.ClickException(f"Manifest '{manifest['name']}' not found")

        if len(manifests) > 1:
            raise click.ClickException(
                f"Multiple manifests found for '{manifest['name']}'"
            )

        return sys_uuid.UUID(manifests[0]["uuid"])

    return sys_uuid.UUID(manifest["uuid"])


def add_manifest(
    client: http_client.CollectionBaseClient,
    manifest: dict[str, tp.Any],
) -> dict[str, tp.Any]:
    uuid = sys_uuid.uuid4()
    if "uuid" in manifest:
        uuid = sys_uuid.UUID(manifest["uuid"])
    else:
        manifest["uuid"] = str(uuid)

    try:
        manifest_resp = client.create(c.MANIFEST_COLLECTION, data=manifest)
    except bazooka_exc.ConflictError:
        raise click.ClickException(f"Manifest with UUID {uuid} already exists")

    return manifest_resp


def update_manifest(
    client: http_client.CollectionBaseClient,
    manifest: dict[str, tp.Any],
) -> dict[str, tp.Any]:
    uuid = get_manifest_uuid(client, manifest)

    # Remove fields that are not allowed to be updated
    data = manifest.copy()
    data.pop("uuid", None)
    data.pop("version", None)
    data.pop("name", None)
    data.pop("schema_version", None)

    try:
        manifest_resp = client.update(c.MANIFEST_COLLECTION, uuid=uuid, **data)
    except bazooka_exc.NotFoundError:
        raise click.ClickException(f"Manifest with UUID {uuid} not found")

    return manifest_resp


def delete_manifest(
    client: http_client.CollectionBaseClient,
    uuid: sys_uuid.UUID,
) -> None:
    try:
        client.delete(c.MANIFEST_COLLECTION, uuid=uuid)
    except bazooka_exc.NotFoundError:
        raise click.ClickException(f"Manifest with UUID {uuid} not found")


def install_manifest(
    client: http_client.CollectionBaseClient,
    uuid: sys_uuid.UUID,
) -> None:
    try:
        client.do_action(c.MANIFEST_COLLECTION, uuid=uuid, name="install", invoke=True)
    except bazooka_exc.ConflictError:
        raise click.ClickException(f"Manifest with UUID {uuid} already installed")


def upgrade_manifest(
    client: http_client.CollectionBaseClient,
    uuid: sys_uuid.UUID,
) -> None:
    try:
        client.do_action(c.MANIFEST_COLLECTION, uuid=uuid, name="upgrade", invoke=True)
    except bazooka_exc.NotFoundError:
        raise click.ClickException(f"Manifest with UUID {uuid} not found")


def uninstall_manifest(
    client: http_client.CollectionBaseClient,
    uuid: sys_uuid.UUID,
) -> None:
    try:
        client.do_action(
            c.MANIFEST_COLLECTION, uuid=uuid, name="uninstall", invoke=True
        )
    except bazooka_exc.NotFoundError:
        raise click.ClickException(f"Manifest with UUID {uuid} not found")


def list_elements(
    client: http_client.CollectionBaseClient, **filters
) -> list[dict[str, tp.Any]]:
    return client.filter(c.ELEMENT_COLLECTION, **filters)


def list_resources(
    client: http_client.CollectionBaseClient,
    element_uuid: sys_uuid.UUID,
    **filters,
) -> list[dict[str, tp.Any]]:
    collection = f"{c.ELEMENT_COLLECTION}{element_uuid}/resources/"
    return client.filter(collection, **filters)
