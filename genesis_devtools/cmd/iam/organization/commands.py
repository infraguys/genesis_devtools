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
from genesis_devtools.common.table import get_table, print_table

from genesis_devtools.clients.base_client import get_user_api_client

from genesis_devtools.clients import organization as organization_lib
from genesis_devtools.common import utils


@click.group("organizations", help="Manager organizations in the Genesis installation")
def organizations_group():
    pass


@organizations_group.command("list", help="List organizations")
@click.pass_context
def list_organizations(
    ctx: click.Context,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    organizations = organization_lib.list_organizations(client)
    _print_values(organizations)


@organizations_group.command("show", help="Show organization")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.pass_context
def show_organization(
    ctx: click.Context,
    uuid: str,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    if not utils.is_valid_uuid(uuid):
        organizations = organization_lib.list_organizations(
            client, organizationname=uuid
        )
        if organizations:
            uuid = organizations[0]["uuid"]
        else:
            raise click.ClickException(f"organization with name {uuid} not found")
    value = organization_lib.get_organization(client, uuid)
    _print_values([value])


@organizations_group.command("delete", help="Delete organization")
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help="organization UUID",
)
@click.pass_context
def delete_organization(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
) -> None:
    client = get_user_api_client(ctx.obj.auth_data)
    organization_lib.delete_organization(client, uuid)


def _print_values(organizations: tp.List[dict]) -> None:
    table = get_table()
    table.add_column("UUID")
    table.add_column("Name")
    table.add_column("Status")

    for organization in organizations:
        table.add_row(
            organization["uuid"],
            organization["name"],
            organization["status"],
        )

    print_table(table)
