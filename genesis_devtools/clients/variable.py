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


def list_variables(
    client: http_client.CollectionBaseClient, **filters
) -> list[dict[str, tp.Any]]:
    return client.filter(c.VARIABLE_COLLECTION, **filters)


def get_variable(
    client: http_client.CollectionBaseClient,
    variable_uuid: sys_uuid.UUID,
):
    variable = client.get(c.VARIABLE_COLLECTION, uuid=variable_uuid)
    return variable


def add_variable(
    client: http_client.CollectionBaseClient,
    variable: dict[str, tp.Any],
) -> dict[str, tp.Any]:
    try:
        variable_resp = client.create(c.VARIABLE_COLLECTION, data=variable)
    except bazooka_exc.ConflictError:
        raise click.ClickException("variable already exists")
    return variable_resp


def delete_variable(
    client: http_client.CollectionBaseClient,
    uuid: sys_uuid.UUID,
) -> None:
    try:
        client.delete(c.VARIABLE_COLLECTION, uuid=uuid)
    except bazooka_exc.NotFoundError:
        raise click.ClickException(f"variable with UUID {uuid} not found")


def select_value(
    client: http_client.CollectionBaseClient,
    uuid: sys_uuid.UUID | str,
    value: sys_uuid.UUID | str,
) -> None:
    try:
        client.do_action(
            c.VARIABLE_COLLECTION,
            uuid=uuid,
            name="select_value",
            invoke=True,
            value=value,
        )
    except bazooka_exc.NotFoundError:
        raise click.ClickException(f"variable with UUID {uuid} not found")
