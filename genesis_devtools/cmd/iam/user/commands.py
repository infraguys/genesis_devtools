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

import questionary
import rich_click as click
from genesis_devtools.common.table import get_table, print_table, show_data

from genesis_devtools.clients import base_client
from genesis_devtools import utils
from genesis_devtools import constants as c


ENTITY = "user"
ENTITY_COLLECTION = c.USER_COLLECTION


@click.group(f"{ENTITY}s", help=f"Manage {ENTITY}s in the Genesis installation")
def users_group():
    pass


@users_group.command("list", help=f"List {ENTITY}s")
@click.option(
    "-f",
    "--filters",
    multiple=True,
    help=(
        "Additional filters to pass to the api. "
        "The format is 'key=value'. For example: --f "
        "parent=11111111-1111-1111-1111-11111111111 --filters status=NEW"
    ),
)
@click.pass_context
def list_cmd(ctx: click.Context, filters: tuple[str, ...]) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    filters = utils.convert_input_multiply(filters)
    entities = base_client.list_entities(client, ENTITY_COLLECTION, **filters)
    _print_entities(entities)


@users_group.command("show", help=f"Show {ENTITY}")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.pass_context
def show_cmd(
    ctx: click.Context,
    uuid: str,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    if not utils.is_valid_uuid(uuid):
        entities = base_client.list_entities(client, ENTITY_COLLECTION, name=uuid)
        if entities:
            uuid = entities[0]["uuid"]
        else:
            raise click.ClickException(f"{ENTITY} with name {uuid} not found")
    data = base_client.get_entity(client, ENTITY_COLLECTION, uuid)
    show_data(data)


@users_group.command("delete", help=f"Delete {ENTITY}")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.pass_context
def delete_cmd(
    ctx: click.Context,
    uuid: str,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    if not utils.is_valid_uuid(uuid):
        entities = base_client.list_entities(client, ENTITY_COLLECTION, name=uuid)
        if entities:
            uuid = entities[0]["uuid"]
        else:
            raise click.ClickException(f"{ENTITY} with name {uuid} not found")
    base_client.delete_entity(client, ENTITY_COLLECTION, uuid)


@users_group.command("add", help=f"Add a new {ENTITY} to the Genesis installation")
@click.pass_context
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help=f"UUID of the {ENTITY}",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default=f"test_{ENTITY}",
    help=f"Name of the {ENTITY}",
)
@click.option(
    "-p",
    "--password",
    type=str,
    required=False,
    help=f"Password of the {ENTITY}. If not provided, will be asked interactively",
    hide_input=True,
)
@click.option(
    "-D",
    "--description",
    type=str,
    default="",
    help=f"Description of the {ENTITY}",
)
@click.option(
    "--first_name",
    type=str,
    required=False,
)
@click.option(
    "--last_name",
    type=str,
    required=False,
)
@click.option(
    "--surname",
    type=str,
    required=False,
)
@click.option(
    "--phone",
    type=str,
    required=False,
)
@click.option(
    "--email",
    type=str,
    required=True,
)
@click.option(
    "--email_verified",
    type=bool,
    is_flag=True,
    default=False,
)
@click.option(
    "--confirmation_code",
    type=str,
    required=False,
)
@click.option(
    "--confirmation_code_made_at",
    type=str,
    required=False,
)
@click.option(
    "--otp_secret",
    type=str,
    required=False,
)
@click.option(
    "--otp_enabled",
    type=bool,
    is_flag=True,
    default=False,
)
def add_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    name: str,
    password: str | None,
    description: str,
    first_name: str | None,
    last_name: str | None,
    surname: str | None,
    phone: str | None,
    email: str | None,
    email_verified: bool,
    confirmation_code: str | None,
    confirmation_code_made_at: str | None,
    otp_secret: str | None,
    otp_enabled: bool,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    if uuid is None:
        uuid = sys_uuid.uuid4()

    data = {
        "uuid": str(uuid),
        "username": name,
        "password": password
        or questionary.password(f"Enter password for {ENTITY} {name}:").ask(),
        "description": description,
        "email": email,
        "email_verified": email_verified,
        "otp_enabled": otp_enabled,
    }

    if first_name is not None:
        data["first_name"] = first_name
    if last_name is not None:
        data["last_name"] = last_name
    if surname is not None:
        data["surrname"] = surname
    if phone is not None:
        data["phone"] = phone
    if confirmation_code is not None:
        data["confirmation_code"] = confirmation_code
    if confirmation_code_made_at is not None:
        data["confirmation_code_made_at"] = confirmation_code_made_at
    if otp_secret is not None:
        data["otp_secret"] = otp_secret

    entity = base_client.add_entity(client, ENTITY_COLLECTION, data)
    show_data(entity)


def _print_entities(users: tp.List[dict]) -> None:
    table = get_table()
    table.add_column("UUID")
    table.add_column("Username")
    table.add_column("First Name")
    table.add_column("Last Name")
    table.add_column("Email")
    table.add_column("Status")

    for user in users:
        table.add_row(
            user["uuid"],
            user["username"],
            user.get("first_name", ""),
            user.get("last_name", ""),
            user["email"],
            user["status"],
        )

    print_table(table)
