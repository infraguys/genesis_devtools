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

from gcl_sdk.clients.http import base as http_client

from genesis_devtools.clients import password as password_lib
from genesis_devtools.common import utils


@click.group("passwords", help="Manage passwords in the Genesis installation")
def passwords_group():
    pass


@passwords_group.command("list", help="List passwords")
@click.pass_context
def list_passwords(ctx: click.Context) -> None:
    client = ctx.obj.client
    passwords = password_lib.list_passwords(client)
    _print_passwords(passwords)


@passwords_group.command("show", help="Show password")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.pass_context
def show_password_cmd(
    ctx: click.Context,
    uuid: str,
) -> None:
    client: http_client.CollectionBaseClient = ctx.obj.client
    if not utils.is_valid_uuid(uuid):
        passwords = password_lib.list_passwords(client, name=uuid)
        if passwords:
            uuid = passwords[0]["uuid"]
        else:
            raise click.ClickException(f"password with name {uuid} not found")
    password = password_lib.get_password(client, uuid)
    _print_passwords([password])


@passwords_group.command("delete", help="Delete password")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.pass_context
def delete_password_cmd(
    ctx: click.Context,
    uuid: str,
) -> None:
    client: http_client.CollectionBaseClient = ctx.obj.client
    if not utils.is_valid_uuid(uuid):
        passwords = password_lib.list_passwords(client, name=uuid)
        if passwords:
            uuid = passwords[0]["uuid"]
        else:
            raise click.ClickException(f"password with name {uuid} not found")
    password_lib.delete_password(client, uuid)


@passwords_group.command("add", help="Add a new password to the Genesis installation")
@click.pass_context
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help="UUID of the password",
)
@click.option(
    "-p",
    "--project-id",
    type=click.UUID,
    required=True,
    help="Name of the project in which to deploy the password",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default="test_password",
    help="Name of the password",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default="",
    help="Description of the password",
)
def add_password_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    project_id: sys_uuid.UUID,
    name: str,
    description: str,
) -> None:
    client: http_client.CollectionBaseClient = ctx.obj.client
    if uuid is None:
        uuid = sys_uuid.uuid4()

    data = {
        "uuid": str(uuid),
        "project_id": str(project_id),
        "name": name,
        "description": description,
    }

    password_resp = password_lib.add_password(client, data)
    _print_passwords([password_resp])


@passwords_group.command("update", help="Update password")
@click.pass_context
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.option(
    "-p",
    "--project-id",
    type=click.UUID,
    default=None,
    help="Name of the project in which to deploy the password",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default=None,
    help="Name of the password",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default=None,
    help="Description of the password",
)
def update_password_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID,
    project_id: sys_uuid.UUID | None,
    name: str | None,
    description: str | None,
) -> None:
    client: http_client.CollectionBaseClient = ctx.obj.client
    data = {}
    if project_id is not None:
        data["project_id"] = str(project_id)
    if name is not None:
        data["name"] = name
    if description is not None:
        data["description"] = description
    password_resp = password_lib.update_password(client, uuid, data)
    _print_passwords([password_resp])


def _print_passwords(passwords: tp.List[dict]) -> None:
    table = get_table()
    table.add_column("UUID")
    table.add_column("Project")
    table.add_column("Name")
    table.add_column("Method")
    table.add_column("Status")

    for password in passwords:
        table.add_row(
            password["uuid"],
            password["project_id"],
            password["name"],
            password["method"],
            password["status"],
        )

    print_table(table)
