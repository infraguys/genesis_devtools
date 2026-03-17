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

import time
import typing as tp
import uuid as sys_uuid

import click
import os
import prettytable
import yaml

from gcl_sdk.clients.http import base as http_client

from genesis_devtools.clients import elements as elements_lib
from genesis_devtools.clients import repo as repo_lib
from genesis_devtools import logger


@click.group("elements", help="Manage elements in the Genesis installation")
def elements_group():
    pass


def apply_element(
    client: http_client.CollectionBaseClient,
    repository: str,
    path_or_name: str,
    install_only: bool = False,
) -> dict[str, tp.Any]:
    """Install or update element from a YAML file or repository.

    The command will install the element if it's not installed or update it
    if it's installed.
    """
    log = logger.ClickLogger()

    if os.path.exists(path_or_name):
        with open(path_or_name, "r", encoding="utf-8") as f:
            manifest = yaml.safe_load(f)
    else:
        manifest = repo_lib.download_manifest(repository, path_or_name)

    requirements: dict = manifest.get("requirements", {})

    installed = bool(elements_lib.list_elements(client, name=manifest["name"]))

    if installed and install_only:
        raise click.ClickException(f"Element {manifest['name']} is already installed")

    apply_func = (
        elements_lib.install_manifest if install_only else elements_lib.apply_manifest
    )

    # Install element if no requirements
    if not requirements:
        manifest = elements_lib.add_manifest(client, manifest)
        apply_func(client, manifest["uuid"])
        return manifest

    # Resolve dependencies
    installed_elements = {e["name"] for e in elements_lib.list_elements(client)}
    required_elements = set(requirements.keys()) - installed_elements

    log.info(
        "The following elements will be installed: "
        f"{required_elements.union({manifest['name']})}"
    )

    while required_elements:
        # TODO(akremenetsky): Use queue to resolve dependencies
        requirement = required_elements.pop()
        req_manifest = repo_lib.download_manifest(repository, requirement)

        # Determine requirements for the element
        requirements = set(req_manifest.get("requirements", {}).keys())
        requirements = requirements - installed_elements
        required_elements.update(requirements)

        # NOTE(akremenetsky): We should install the element since there are
        # unresolved dependencies but for the simplicity we will install it here
        req_manifest = elements_lib.add_manifest(client, req_manifest)
        elements_lib.install_manifest(client, req_manifest["uuid"])
        log.important(f"Element {req_manifest['name']} installed successfully")

        installed_elements.add(req_manifest["name"])

        # TODO(akremenetsky): The installation is stuck for some reason
        # so we need to wait a bit. Solve the issue in GC and remove this
        # sleep.
        time.sleep(3)

    manifest = elements_lib.add_manifest(client, manifest)
    apply_func(client, manifest["uuid"])
    return manifest


@elements_group.command("install", help="Install element from a manifest (YAML file)")
@click.option(
    "-r",
    "--repository",
    default="http://10.20.0.1:8080/genesis-elements/",
    show_default=True,
    help="Repository endpoint",
)
@click.argument("path_or_name")
@click.pass_context
def install_element_cmd(ctx: click.Context, repository: str, path_or_name: str) -> None:
    """Install element from a YAML file"""
    log = logger.ClickLogger()
    manifest = apply_element(
        ctx.obj.client, repository, path_or_name, install_only=True
    )
    log.important(f"Element {manifest['name']} installed successfully")


@elements_group.command("update", help="Update element from a YAML file")
@click.option(
    "-r",
    "--repository",
    default="http://10.20.0.1:8080/genesis-elements/",
    show_default=True,
    help="Repository endpoint",
)
@click.argument("path_or_name")
@click.pass_context
def update_element_cmd(ctx: click.Context, repository: str, path_or_name: str) -> None:
    """Update element from a YAML file"""
    log = logger.ClickLogger()
    manifest = apply_element(ctx.obj.client, repository, path_or_name)
    log.important(f"Element {manifest['name']} updated successfully")


@elements_group.command("uninstall", help="Uninstall element by UUID, path or name")
@click.argument("path_uuid_name", type=str)
@click.pass_context
def uninstall_element_cmd(ctx: click.Context, path_uuid_name: str) -> None:
    """Uninstall element by UUID, path or name"""
    client: http_client.CollectionBaseClient = ctx.obj.client
    log = logger.ClickLogger()

    def _uninstall(uuid: sys_uuid.UUID) -> None:
        elements_lib.uninstall_manifest(client, uuid)
        elements_lib.delete_manifest(client, uuid)
        log.important(f"Element {uuid} uninstalled successfully")

    # UUID
    try:
        uuid = sys_uuid.UUID(path_uuid_name)
        _uninstall(uuid)
        return
    except ValueError:
        pass

    # Name
    name = path_uuid_name
    manifests = elements_lib.list_manifest(client, name=name)
    if len(manifests) == 1:
        uuid = manifests[0]["uuid"]
        _uninstall(uuid)
        return
    if len(manifests) > 1:
        raise click.ClickException(f"Multiple elements found with name {name}")

    # Path
    if os.path.exists(path_uuid_name):
        with open(path_uuid_name, "r") as f:
            manifest = yaml.safe_load(f)
        if "uuid" in manifest:
            filters = {"uuid": manifest["uuid"]}
        elif "name" in manifest:
            filters = {"name": manifest["name"]}
        else:
            raise click.ClickException("Manifest must have uuid or name")

        manifests = elements_lib.list_manifest(client, **filters)
        if len(manifests) == 1:
            uuid = manifests[0]["uuid"]
            _uninstall(uuid)
            return
        if len(manifests) > 1:
            raise click.ClickException(f"Multiple elements found with name {name}")
        log.warn(f"Element {list(filters.values())[0]} not found")
        return

    log.warn(f"Element {path_uuid_name} not found")


@elements_group.command("list", help="List elements")
@click.pass_context
def list_element_cmd(ctx: click.Context) -> None:
    """List elements"""
    client: http_client.CollectionBaseClient = ctx.obj.client
    table = prettytable.PrettyTable()
    table.field_names = [
        "UUID",
        "Name",
        "Description",
        "Version",
        "Status",
    ]

    elements = elements_lib.list_elements(client)
    for element in elements:
        table.add_row(
            [
                element["uuid"],
                element["name"],
                element["description"],
                element["version"],
                element["status"],
            ]
        )
    click.echo(table)


@elements_group.command("show", help="Show element general information")
@click.argument("name")
@click.pass_context
def show_element_cmd(ctx: click.Context, name: str) -> None:
    """Show element general information"""
    client: http_client.CollectionBaseClient = ctx.obj.client

    element = elements_lib.list_elements(client, name=name)
    if not element:
        raise click.ClickException(f"Element {name} not found")

    if len(element) > 1:
        raise click.ClickException(f"Multiple elements found with name {name}")

    element = element[0]

    table = prettytable.PrettyTable()
    table.field_names = [
        "UUID",
        "Name",
        "Description",
        "Version",
        "Status",
    ]

    table.add_row(
        [
            element["uuid"],
            element["name"],
            element["description"],
            element["version"],
            element["status"],
        ]
    )

    click.echo(f"Element {name}:")
    click.echo(table)

    resources = elements_lib.list_resources(client, sys_uuid.UUID(element["uuid"]))
    table = prettytable.PrettyTable()
    table.field_names = [
        "UUID",
        "Name",
        "Kind",
        "Full hash",
        "Status",
        "Created at",
        "Updated at",
    ]

    for resource in resources:
        table.add_row(
            [
                resource["uuid"],
                resource["name"],
                resource["kind"],
                resource["full_hash"],
                resource["status"],
                resource["created_at"],
                resource["updated_at"],
            ]
        )

    click.echo("Resources:")
    click.echo(table)
