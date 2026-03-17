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

from genesis_devtools.clients import certificate as certificate_lib
from genesis_devtools.common import utils


@click.group("certificates", help="Manage certificates in the Genesis installation")
def certificates_group():
    pass


@certificates_group.command("list", help="List certificates")
@click.pass_context
def list_certificates(ctx: click.Context) -> None:
    client = ctx.obj.client
    certificates = certificate_lib.list_certificates(client)
    _print_certificates(certificates)


@certificates_group.command("show", help="Show certificate")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.pass_context
def show_certificate_cmd(
    ctx: click.Context,
    uuid: str,
) -> None:
    client: http_client.CollectionBaseClient = ctx.obj.client
    if not utils.is_valid_uuid(uuid):
        certificates = certificate_lib.list_certificates(client, name=uuid)
        if certificates:
            uuid = certificates[0]["uuid"]
        else:
            raise click.ClickException(f"certificate with name {uuid} not found")
    certificate = certificate_lib.get_certificate(client, uuid)
    _print_certificates([certificate])


@certificates_group.command("delete", help="Delete certificate")
@click.argument(
    "uuid",
    type=str,
    required=True,
)
@click.pass_context
def delete_certificate_cmd(
    ctx: click.Context,
    uuid: str,
) -> None:
    client: http_client.CollectionBaseClient = ctx.obj.client
    if not utils.is_valid_uuid(uuid):
        certificates = certificate_lib.list_certificates(client, name=uuid)
        if certificates:
            uuid = certificates[0]["uuid"]
        else:
            raise click.ClickException(f"certificate with name {uuid} not found")
    certificate_lib.delete_certificate(client, uuid)


@certificates_group.command("add", help="Add a new certificate to the Genesis installation")
@click.pass_context
@click.option(
    "-u",
    "--uuid",
    type=click.UUID,
    default=None,
    help="UUID of the certificate",
)
@click.option(
    "-p",
    "--project-id",
    type=click.UUID,
    required=True,
    help="Name of the project in which to deploy the certificate",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default="test_certificate",
    help="Name of the certificate",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default="",
    help="Description of the certificate",
)
def add_certificate_cmd(
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

    certificate_resp = certificate_lib.add_certificate(client, data)
    _print_certificates([certificate_resp])


@certificates_group.command("update", help="Update certificate")
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
    help="Name of the project in which to deploy the certificate",
)
@click.option(
    "-n",
    "--name",
    type=str,
    default=None,
    help="Name of the certificate",
)
@click.option(
    "-D",
    "--description",
    type=str,
    default=None,
    help="Description of the certificate",
)
def update_certificate_cmd(
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
    certificate_resp = certificate_lib.update_certificate(client, uuid, data)
    _print_certificates([certificate_resp])


def _print_certificates(certificates: tp.List[dict]) -> None:
    table = prettytable.PrettyTable()
    table.field_names = [
        "UUID",
        "Project",
        "Name",
        "Email",
        "Expiration_at",
        "Status",
    ]

    for certificate in certificates:
        table.add_row(
            [
                certificate["uuid"],
                certificate["project_id"],
                certificate["name"],
                certificate.get("email", ""),
                certificate["certificate"],
                certificate["status"],
            ]
        )

    click.echo(table)
