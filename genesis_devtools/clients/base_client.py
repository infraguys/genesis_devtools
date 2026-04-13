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

import os
import typing as tp
import uuid as sys_uuid

import certifi
import rich_click as click

from bazooka import exceptions as bazooka_exc
from gcl_sdk.clients.http import base as http_client

os.environ["SSL_CERT_FILE"] = certifi.where()


def get_user_api_client(auth_data: dict) -> http_client.CollectionBaseClient:
    auth = http_client.CoreIamAuthenticator(
        base_url=auth_data["endpoint"],
        username=auth_data["username"],
        password=auth_data["password"],
        access_token=auth_data["access_token"],
        refresh_token=auth_data["refresh_token"],
        scope=auth_data["scope"],
    )
    client = http_client.CollectionBaseClient(
        base_url=auth_data["endpoint"],
        auth=auth,
    )
    return client


def list_entities(
    client: http_client.CollectionBaseClient, collection: str, **filters
) -> list[dict[str, tp.Any]]:
    return client.filter(collection, **filters)


def get_entity(
    client: http_client.CollectionBaseClient,
    collection: str,
    entity_uuid: sys_uuid.UUID | str,
):
    entity = client.get(collection, uuid=entity_uuid)
    return entity


def add_entity(
    client: http_client.CollectionBaseClient,
    collection: str,
    data: dict[str, tp.Any],
) -> dict[str, tp.Any]:
    try:
        variable_resp = client.create(collection, data=data)
    except bazooka_exc.ConflictError:
        raise click.ClickException("Already exists")
    return variable_resp


def delete_entity(
    client: http_client.CollectionBaseClient,
    collection: str,
    uuid: sys_uuid.UUID | str,
) -> None:
    try:
        client.delete(collection, uuid=uuid)
    except bazooka_exc.NotFoundError:
        raise click.ClickException(f"UUID {uuid} not found")


def action_entity(
    client: http_client.CollectionBaseClient,
    collection: str,
    action: str,
    uuid: sys_uuid.UUID | str,
) -> None:
    try:
        client.do_action(collection, uuid=uuid, name=action, invoke=True)
    except bazooka_exc.NotFoundError:
        raise click.ClickException(f"UUID {uuid} not found")
