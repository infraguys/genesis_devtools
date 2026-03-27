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
import time
import typing as tp
import uuid as sys_uuid
import yaml

import rich_click as click
from genesis_devtools.common.table import get_table, print_table

from gcl_sdk.clients.http import base as http_client

from genesis_devtools.clients import element as elements_lib
from genesis_devtools.clients import manifest as manifests_lib
from genesis_devtools.clients import node as node_lib
from genesis_devtools.clients import repo as repo_lib
import genesis_devtools.constants as c
from genesis_devtools import logger


@click.group("elements", help="Manage elements in the Genesis installation")
def elements_group():
    pass


@elements_group.command("list", help="List elements")
@click.pass_context
def list_element_cmd(ctx: click.Context) -> None:
    """List elements"""
    client: http_client.CollectionBaseClient = ctx.obj.client
    table = get_table()
    table.add_column("UUID")
    table.add_column("Name")
    table.add_column("Description")
    table.add_column("Version")
    table.add_column("Status")

    elements = elements_lib.list_elements(client)
    for element in elements:
        table.add_row(
            element["uuid"],
            element["name"],
            element["description"],
            element["version"],
            element["status"],
        )
    print_table(table)


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

    table = get_table()
    table.add_column("UUID")
    table.add_column("Name")
    table.add_column("Description")
    table.add_column("Version")
    table.add_column("Status")

    table.add_row(
        element["uuid"],
        element["name"],
        element["description"],
        element["version"],
        element["status"],
    )

    click.echo(f"Element {name}:")
    print_table(table)

    resources = elements_lib.list_resources(client, sys_uuid.UUID(element["uuid"]))
    table = get_table()
    table.add_column("UUID")
    table.add_column("Name")
    table.add_column("Kind")
    table.add_column("Full hash")
    table.add_column("Status")
    table.add_column("Created at")
    table.add_column("Updated at")

    for resource in resources:
        table.add_row(
            resource["uuid"],
            resource["name"],
            resource["kind"],
            resource["full_hash"],
            resource["status"],
            resource["created_at"],
            resource["updated_at"],
        )

    click.echo("Resources:")
    print_table(table)


@elements_group.command("ips", help="Show element ips")
@click.argument("name")
@click.pass_context
def show_element_ips(ctx: click.Context, name: str) -> None:
    client: http_client.CollectionBaseClient = ctx.obj.client

    element = elements_lib.list_elements(client, name=name)
    if not element:
        raise click.ClickException(f"Element {name} not found")

    if len(element) > 1:
        raise click.ClickException(f"Multiple elements found with name {name}")

    resources = elements_lib.list_resources(
        client, sys_uuid.UUID(element[0]["uuid"]), kind="em_core_compute_nodes"
    )
    if len(resources) == 0:
        raise click.ClickException(f"No nodes found for element {name}")
    elif len(resources) > 1:
        for resource in resources:
            node = node_lib.get_node(client, resource["uuid"])
            click.echo(f"Name: {node['name']}, IP: {node_lib.get_node_ip(node)}")
    else:
        node = node_lib.get_node(client, resources[0]["uuid"])
        click.echo(node_lib.get_node_ip(node))


def _apply_with_cleanup(
    client: http_client.CollectionBaseClient,
    manifest_data: dict[str, tp.Any],
    apply_func: tp.Callable[[http_client.CollectionBaseClient, str], None],
) -> dict[str, tp.Any]:
    """Apply a manifest and clean up old versions on success."""

    found_manifest_uuids = [
        sys_uuid.UUID(item["uuid"])
        for item in manifests_lib.list_manifests(client, name=manifest_data["name"])
    ]
    manifest_data = manifests_lib.add_manifest(client, manifest_data)
    manifest_uuid = sys_uuid.UUID(manifest_data["uuid"])

    try:
        apply_func(client, manifest_data["uuid"])
    except Exception:
        manifests_lib.delete_manifest(client, manifest_uuid)
        raise

    for manifest_uuid in found_manifest_uuids:
        manifests_lib.delete_manifest(client, manifest_uuid)

    return manifest_data


def upgrade_manifest(
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
        manifests_lib.install_manifest
        if install_only
        else manifests_lib.upgrade_manifest
    )

    # Install element if no requirements
    if not requirements:
        manifest = _apply_with_cleanup(client, manifest, apply_func)
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
        req_manifest = manifests_lib.add_manifest(client, req_manifest)
        manifests_lib.install_manifest(client, req_manifest["uuid"])
        log.important(f"Element {req_manifest['name']} installed successfully")

        installed_elements.add(req_manifest["name"])

        # TODO(akremenetsky): The installation is stuck for some reason
        # so we need to wait a bit. Solve the issue in GC and remove this
        # sleep.
        time.sleep(3)

    manifest = _apply_with_cleanup(client, manifest, apply_func)
    return manifest


@elements_group.command("install", help="Install element from a manifest (YAML file)")
@click.option(
    "-r",
    "--repository",
    default=f"{c.ELEMENT_REPO_URL}/",
    show_default=True,
    help="Repository endpoint",
)
@click.argument("path_or_name")
@click.pass_context
def install_manifest_cmd(
    ctx: click.Context, repository: str, path_or_name: str
) -> None:
    """Install manifest from a YAML file"""
    log = logger.ClickLogger()
    manifest = upgrade_manifest(
        ctx.obj.client, repository, path_or_name, install_only=True
    )
    log.important(f"Element {manifest['name']} installed successfully")


@elements_group.command("update", help="Update element from a YAML file")
@click.option(
    "-r",
    "--repository",
    default=f"{c.ELEMENT_REPO_URL}/",
    show_default=True,
    help="Repository endpoint",
)
@click.argument("path_or_name")
@click.pass_context
def update_manifest_cmd(ctx: click.Context, repository: str, path_or_name: str) -> None:
    """Update manifest from a YAML file"""
    log = logger.ClickLogger()
    manifest = upgrade_manifest(ctx.obj.client, repository, path_or_name)
    log.important(f"Element {manifest['name']} updated successfully")


@elements_group.command("uninstall", help="Uninstall manifest by UUID, path or name")
@click.argument("path_uuid_name", type=str)
@click.pass_context
def uninstall_manifest_cmd(ctx: click.Context, path_uuid_name: str) -> None:
    """Uninstall manifest by UUID, path or name"""
    client: http_client.CollectionBaseClient = ctx.obj.client
    log = logger.ClickLogger()

    def _uninstall(uuid: sys_uuid.UUID) -> None:
        manifests_lib.uninstall_manifest(client, uuid)
        manifests_lib.delete_manifest(client, uuid)
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
    manifests = manifests_lib.list_manifests(client, name=name)
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

        manifests = manifests_lib.list_manifests(client, **filters)
        if len(manifests) == 1:
            uuid = manifests[0]["uuid"]
            _uninstall(uuid)
            return
        if len(manifests) > 1:
            raise click.ClickException(f"Multiple elements found with name {name}")
        log.warn(f"manifest {list(filters.values())[0]} not found")
        return

    log.warn(f"Element {path_uuid_name} not found")
