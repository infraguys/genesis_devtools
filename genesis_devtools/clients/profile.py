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


def list_profiles(
    client: http_client.CollectionBaseClient, **filters
) -> list[dict[str, tp.Any]]:
    return client.filter(c.PROFILE_COLLECTION, **filters)


def get_profile(
    client: http_client.CollectionBaseClient,
    profile_uuid: sys_uuid.UUID,
):
    profile = client.get(c.PROFILE_COLLECTION, uuid=profile_uuid)
    return profile


def add_profile(
    client: http_client.CollectionBaseClient,
    profile: dict[str, tp.Any],
) -> dict[str, tp.Any]:
    try:
        profile_resp = client.create(c.PROFILE_COLLECTION, data=profile)
    except bazooka_exc.ConflictError:
        raise click.ClickException("Profile already exists")
    return profile_resp


def delete_profile(
    client: http_client.CollectionBaseClient,
    uuid: sys_uuid.UUID,
) -> None:
    try:
        client.delete(c.PROFILE_COLLECTION, uuid=uuid)
    except bazooka_exc.NotFoundError:
        raise click.ClickException(f"Profile with UUID {uuid} not found")


def activate_profile(
    client: http_client.CollectionBaseClient,
    uuid: sys_uuid.UUID,
) -> None:
    try:
        client.do_action(c.PROFILE_COLLECTION, uuid=uuid, name="activate", invoke=True)
    except bazooka_exc.NotFoundError:
        raise click.ClickException(f"Profile with UUID {uuid} not found")
