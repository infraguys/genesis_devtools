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

import os

import click
import prettytable

from genesis_devtools.clients import iam as iam_client


@click.group("auth", help="Authenticate and manage IAM token")
def auth_group() -> None:
    pass


@auth_group.command("login", help="Authenticate in IAM and store tokens locally")
@click.option(
    "--iam-client-endpoint",
    required=True,
    type=str,
    help="Full URL of the IAM client",
)
@click.option(
    "--project-id",
    required=True,
    type=str,
    help="Project ID for IAM authentication",
)
@click.option(
    "--client-id",
    default=None,
    type=str,
    help="OAuth client id (optional)",
)
@click.option(
    "--client-secret",
    default=None,
    type=str,
    help="OAuth client secret (optional)",
)
@click.option(
    "--scope",
    default="profile",
    type=str,
    show_default=True,
    help="OAuth scope",
)
@click.option(
    "--ttl",
    default=15 * 60,
    type=int,
    show_default=True,
    help="Access token lifetime in seconds",
)
@click.option(
    "--refresh-ttl",
    default=60 * 60,
    type=int,
    show_default=True,
    help="Refresh token lifetime in seconds",
)
@click.option(
    "-f",
    "--force",
    show_default=True,
    is_flag=True,
    help="Overwrite existing auth file",
)
@click.argument("project_dir", type=click.Path())
def auth_login_cmd(
    iam_client_endpoint: str,
    project_id: str,
    client_id: str | None,
    client_secret: str | None,
    scope: str,
    ttl: int,
    refresh_ttl: int,
    force: bool,
    project_dir: str,
) -> None:
    project_dir = os.path.abspath(project_dir)

    auth_dir = os.path.join(project_dir, ".genesis")
    auth_file = os.path.join(auth_dir, "auth.json")

    login = click.prompt("Login", type=str)
    password = click.prompt("Password", type=str, hide_input=True)

    client = iam_client.IAMClient(
        iam_client_endpoint=iam_client_endpoint,
        project_id=project_id,
        client_id=client_id,
        client_secret=client_secret,
        scope=scope,
        ttl=ttl,
        refresh_ttl=refresh_ttl,
    )

    try:
        token = client.get_token_by_password(login, password)
        token.save(project_dir, force=force)
    except iam_client.TokenFileAlreadyExistsError:
        click.secho(
            f"Auth file '{auth_file}' already exists. Use '--force' to overwrite.",
            fg="yellow",
        )
        return
    except iam_client.IAMClientError as exc:
        raise click.ClickException(str(exc))

    click.secho(f"Auth data saved to '{auth_file}'", fg="green")


@auth_group.command("me", help="Validate stored token and show user info")
@click.argument("project_dir", type=click.Path())
def auth_me_cmd(project_dir: str) -> None:
    project_dir = os.path.abspath(project_dir)

    try:
        token = iam_client.Token.load(project_dir)
    except iam_client.TokenFileNotFoundError as exc:
        raise click.ClickException(str(exc))

    client = iam_client.IAMClient(
        iam_client_endpoint=token.url,
        project_id=token.project_id,
    )

    try:
        me_data = client.me(token)
    except iam_client.IAMClientError as exc:
        raise click.ClickException(str(exc))

    user = me_data.get("user") or {}
    orgs = me_data.get("organization") or []
    org = orgs[0] if orgs else {}

    table = prettytable.PrettyTable()
    table.field_names = ["field", "value"]
    table.add_row(["uuid", user.get("uuid")])
    table.add_row(["username", user.get("username")])
    table.add_row(["name", user.get("name")])
    table.add_row(["email", user.get("email")])
    table.add_row(["status", user.get("status")])
    table.add_row(["organization", org.get("name")])

    click.echo(table)


@auth_group.command("refresh", help="Refresh stored token using refresh token")
@click.option(
    "--ttl",
    default=None,
    type=int,
    help="Access token lifetime in seconds (optional)",
)
@click.option(
    "--scope",
    default=None,
    type=str,
    help="OAuth scope (optional)",
)
@click.argument("project_dir", type=click.Path())
def auth_refresh_cmd(ttl: int | None, scope: str | None, project_dir: str) -> None:
    project_dir = os.path.abspath(project_dir)

    try:
        token = iam_client.Token.load(project_dir)
    except iam_client.TokenFileNotFoundError as exc:
        raise click.ClickException(str(exc))

    client = iam_client.IAMClient(
        iam_client_endpoint=token.url,
        project_id=token.project_id,
    )

    try:
        new_token = client.refresh(token, ttl=ttl, scope=scope)
        new_token.save(project_dir, force=True)
    except iam_client.IAMClientError as exc:
        raise click.ClickException(str(exc))

    auth_file = iam_client.Token.file_path(project_dir)
    click.secho(f"Auth data saved to '{auth_file}'", fg="green")
