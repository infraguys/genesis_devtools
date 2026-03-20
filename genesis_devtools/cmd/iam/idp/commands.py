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
import prettytable

from gcl_sdk.clients.http import base as http_client

from genesis_devtools.clients import idp as idp_lib
from genesis_devtools.common import utils


@click.group("idps", help="Manager idps in the Genesis installation")
def idps_group():
    pass


@idps_group.command("list", help="List idps")
@click.pass_context
def list_idps(
    ctx: click.Context,
) -> None:
    client: http_client.CollectionBaseClient = ctx.obj.client
    idps = idp_lib.list_idps(client)
    _print_values(idps)


@idps_group.command("show", help="Show idp")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.pass_context
def show_idp(
    ctx: click.Context,
    uuid: str,
) -> None:
    client: http_client.CollectionBaseClient = ctx.obj.client
    if not utils.is_valid_uuid(uuid):
        idps = idp_lib.list_idps(client, idpname=uuid)
        if idps:
            uuid = idps[0]["uuid"]
        else:
            raise click.ClickException(f"idp with name {uuid} not found")
    value = idp_lib.get_idp(client, uuid)
    _print_values([value])


@idps_group.command("delete", help="Delete idp")
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help="idp UUID",
)
@click.pass_context
def delete_idp(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
) -> None:
    client: http_client.CollectionBaseClient = ctx.obj.client
    idp_lib.delete_idp(client, uuid)


def _print_values(idps: tp.List[dict]) -> None:
    table = prettytable.PrettyTable()
    table.field_names = [
        "UUID",
        "Name",
        "Scope",
        "Iam_client",
        "Status",
    ]

    for idp in idps:
        table.add_row(
            [
                idp["uuid"],
                idp["name"],
                idp["scope"],
                idp["iam_client"],
                idp["status"],
            ]
        )

    click.echo(table)
