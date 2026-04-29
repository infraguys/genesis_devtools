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

from genesis_devtools import utils

os.environ["SSL_CERT_FILE"] = certifi.where()


def get_user_api_client(auth_data: dict) -> http_client.CollectionBaseClient:
    auth = http_client.CoreIamAuthenticator(
        base_url=auth_data["endpoint"],
        username=auth_data.get("username"),
        password=auth_data.get("password"),
        access_token=auth_data.get("access_token"),
        refresh_token=auth_data.get("refresh_token"),
        scope=auth_data.get("scope"),
    )
    client = http_client.CollectionBaseClient(
        base_url=auth_data["endpoint"],
        auth=auth,
    )
    return client


def _get_entity_uuid(
    client: http_client.CollectionBaseClient,
    collection: str,
    entity_uuid_or_name: sys_uuid.UUID | str,
) -> sys_uuid.UUID | str:
    if not utils.is_valid_uuid(entity_uuid_or_name):
        entities = list_entities(client, collection, name=entity_uuid_or_name)
        if entities:
            if len(entities) > 1:
                raise click.ClickException(
                    f"Multiple entities ({collection}) with name {entity_uuid_or_name} found"
                )
            return entities[0]["uuid"]
        else:
            raise click.ClickException(
                f"entity ({collection}) with name {entity_uuid_or_name} not found"
            )
    return entity_uuid_or_name


def list_entities(
    client: http_client.CollectionBaseClient, collection: str, **filters
) -> list[dict[str, tp.Any]]:
    return client.filter(collection, **filters)


def get_entity(
    client: http_client.CollectionBaseClient,
    collection: str,
    entity_uuid_or_name: sys_uuid.UUID | str,
):
    if not utils.is_valid_uuid(entity_uuid_or_name):
        entities = list_entities(client, collection, name=entity_uuid_or_name)
        if entities:
            if len(entities) > 1:
                raise click.ClickException(
                    f"Multiple entities ({collection}) with name {entity_uuid_or_name} found"
                )
            return entities[0]
        else:
            raise click.ClickException(
                f"entity ({collection}) with name {entity_uuid_or_name} not found"
            )
    return client.get(collection, uuid=entity_uuid_or_name)


def add_entity(
    client: http_client.CollectionBaseClient,
    collection: str,
    data: dict[str, tp.Any],
    handle_conflict_error: bool = True,
) -> dict[str, tp.Any]:
    try:
        entity = client.create(collection, data=data)
    except bazooka_exc.ConflictError:
        if handle_conflict_error:
            raise click.ClickException(f"Already exists: {data}")
        raise
    return entity


def update_entity(
    client: http_client.CollectionBaseClient,
    collection: str,
    entity_uuid_or_name: sys_uuid.UUID | str,
    data: dict[str, tp.Any],
) -> dict[str, tp.Any]:
    return client.update(
        collection, _get_entity_uuid(client, collection, entity_uuid_or_name), **data
    )


def delete_entity(
    client: http_client.CollectionBaseClient,
    collection: str,
    entity_uuid_or_name: sys_uuid.UUID | str,
) -> None:
    client.delete(
        collection, uuid=_get_entity_uuid(client, collection, entity_uuid_or_name)
    )


def action_entity(
    client: http_client.CollectionBaseClient,
    collection: str,
    action: str,
    uuid: sys_uuid.UUID | str,
    invoke: bool = True,
    **kwargs,
) -> None:
    try:
        client.do_action(collection, uuid=uuid, name=action, invoke=invoke, **kwargs)
    except bazooka_exc.NotFoundError:
        raise click.ClickException(f"UUID {uuid} not found")
