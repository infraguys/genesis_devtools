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

from genesis_devtools.clients import base_client

from genesis_devtools.common import utils
from genesis_devtools import constants as c


@click.group("profiles", help="Manage profiles in the Genesis installation")
def profiles_group():
    pass


@profiles_group.command("list", help="List profiles")
@click.pass_context
def list_profiles(ctx: click.Context) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    profiles = base_client.list_entities(client, c.PROFILE_COLLECTION)
    _print_profiles(profiles)


@profiles_group.command("show", help="Show profile")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.pass_context
def show_profile_cmd(
    ctx: click.Context,
    uuid: str,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    if not utils.is_valid_uuid(uuid):
        profiles = base_client.list_entities(client, c.PROFILE_COLLECTION, name=uuid)
        if profiles:
            uuid = profiles[0]["uuid"]
        else:
            raise click.ClickException(f"Profile with name {uuid} not found")
    profile = base_client.get_entity(client, c.PROFILE_COLLECTION, uuid)
    _print_profiles([profile])


@profiles_group.command("delete", help="Delete profile")
@click.argument(
    "uuid",
    type=str,
)
@click.pass_context
def delete_profile_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    if not utils.is_valid_uuid(uuid):
        profiles = base_client.list_entities(client, c.PROFILE_COLLECTION, name=uuid)
        if profiles:
            uuid = profiles[0]["uuid"]
        else:
            raise click.ClickException(f"Profile with name {uuid} not found")
    base_client.delete_entity(client, c.PROFILE_COLLECTION, uuid)


@profiles_group.command("activate", help="Activate profile")
@click.argument(
    "uuid",
    type=str,
)
@click.pass_context
def activate_profile_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    if not utils.is_valid_uuid(uuid):
        profiles = base_client.list_entities(client, c.PROFILE_COLLECTION, name=uuid)
        if profiles:
            uuid = profiles[0]["uuid"]
        else:
            raise click.ClickException(f"Profile with name {uuid} not found")
    base_client.action_entity(client, c.PROFILE_COLLECTION, "activate", uuid)


@profiles_group.command("add", help="Add a new profile to the Genesis installation")
@click.pass_context
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help="UUID of the profile",
)
@click.option(
    "-p",
    "--project-id",
    type=click.UUID,
    required=True,
    help="Name of the project in which to deploy the profile",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default="profile",
    help="Name of the profile",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default="",
    help="Description of the profile",
)
@click.option(
    "-t",
    "--profile_type",
    type=str,
    default="GLOBAL",
    help="Profile_type (ELEMENT, GLOBAL)",
)
def add_profile_cmd(
    ctx: click.Context,
    uuid: sys_uuid.UUID | None,
    project_id: sys_uuid.UUID,
    name: str,
    description: str,
    profile_type: str,
) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    if uuid is None:
        uuid = sys_uuid.uuid4()
    data = {
        "uuid": str(uuid),
        "project_id": str(project_id),
        "name": name,
        "description": description,
        "profile_type": profile_type,
    }
    profile = base_client.add_entity(client, c.PROFILE_COLLECTION, data)
    _print_profiles([profile])


def _print_profiles(profiles: tp.List[dict]) -> None:
    table = get_table()
    table.add_column("UUID")
    table.add_column("Project")
    table.add_column("Name")
    table.add_column("ProfileType")
    table.add_column("Active")
    table.add_column("Status")

    for profile in profiles:
        table.add_row(
            profile["uuid"],
            profile["project_id"],
            profile["name"],
            profile["profile_type"],
            str(profile["active"]),
            profile["status"],
        )

    print_table(table)
