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
from rich.prompt import Prompt
import subprocess
import tempfile
import time
import typing as tp
import yaml

import rich_click as click

from bazooka import exceptions as bazooka_exc
from gcl_sdk.clients.http import base as http_client

from genesis_devtools.common.table import get_table, print_table, show_data
from genesis_devtools import utils
from genesis_devtools.clients import base_client
from genesis_devtools.clients import repo as repo_lib
import genesis_devtools.constants as c
from genesis_devtools.logger import ClickLogger


ENTITY = "element"
ENTITY_COLLECTION = c.ELEMENT_COLLECTION


@click.group(f"{ENTITY}s", help=f"Manage {ENTITY}s in the Genesis installation")
def elements_group():
    pass


@elements_group.command("list", help=f"List {ENTITY}s")
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


@elements_group.command("show", help="Show element general information")
@click.argument("name")
@click.pass_context
def show_element_cmd(ctx: click.Context, name: str) -> None:
    """Show element general information"""
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    data = base_client.get_entity(client, ENTITY_COLLECTION, name)
    show_data(data)

    resources = base_client.list_entities(
        client, f"{c.ELEMENT_COLLECTION}{data['uuid']}/resources/"
    )
    table = get_table(
        "UUID", "Name", "Kind", "Full hash", "Status", "Created at", "Updated at"
    )
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

    imports = base_client.list_entities(
        client, f"{c.ELEMENT_COLLECTION}{data['uuid']}/imports/"
    )
    table = get_table("UUID", "Name", "Kind", "Link", "Created at", "Updated at")
    for resource in imports:
        table.add_row(
            resource["uuid"],
            resource["name"],
            resource["kind"],
            resource["link"],
            resource["created_at"],
            resource["updated_at"],
        )
    click.echo("Imports:")
    print_table(table)

    exports = base_client.list_entities(
        client, f"{c.ELEMENT_COLLECTION}{data['uuid']}/exports/"
    )
    table = get_table("UUID", "Name", "Kind", "Link", "Created at", "Updated at")
    for resource in exports:
        table.add_row(
            resource["uuid"],
            resource["name"],
            resource["kind"],
            resource["link"],
            resource["created_at"],
            resource["updated_at"],
        )
    click.echo("Exports:")
    print_table(table)


@elements_group.command("ips", help="Show element ips")
@click.argument("name")
@click.pass_context
def show_element_ips(ctx: click.Context, name: str) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)

    data = base_client.get_entity(client, ENTITY_COLLECTION, name)

    resources = base_client.list_entities(
        client,
        f"{c.ELEMENT_COLLECTION}{data['uuid']}/resources/",
        kind="em_core_compute_nodes",
    )
    if len(resources) == 0:
        raise click.ClickException(f"No nodes found for element {name}")
    elif len(resources) > 1:
        for resource in resources:
            node = client.get(c.NODE_COLLECTION, uuid=resource["uuid"])
            click.echo(
                f"Name: {node['name']}, IP: {node['default_network'].get('ipv4', None)}"
            )
    else:
        node = client.get(c.NODE_COLLECTION, uuid=resources[0]["uuid"])
        click.echo(node["default_network"].get("ipv4", None))


def _apply_with_cleanup(
    client: http_client.CollectionBaseClient,
    manifest_data: dict[str, tp.Any],
    install_only: bool = False,
    update_manifest: bool = False,
    **kwargs: tp.Any,
) -> dict[str, tp.Any]:
    """Apply a manifest and clean up old versions on success."""

    found_manifest_uuids = [
        item["uuid"]
        for item in base_client.list_entities(
            client, c.MANIFEST_COLLECTION, name=manifest_data["name"]
        )
    ]
    if update_manifest:
        manifest_uuid = kwargs["manifest_uuid"]
        manifest_data.pop("created_at", None)
        manifest_data.pop("updated_at", None)
        manifest_data.pop("status", None)
        try:
            manifest_data = base_client.update_entity(
                client, c.MANIFEST_COLLECTION, manifest_uuid, manifest_data
            )
        except bazooka_exc.NotFoundError:
            manifest_data = base_client.add_entity(
                client, c.MANIFEST_COLLECTION, manifest_data
            )
        manifest_data["uuid"] = manifest_uuid
    else:
        manifest_data = base_client.add_entity(
            client, c.MANIFEST_COLLECTION, manifest_data
        )
    manifest_uuid = manifest_data["uuid"]

    try:
        if install_only:
            base_client.action_entity(
                client, c.MANIFEST_COLLECTION, "install", manifest_uuid
            )
        else:
            base_client.action_entity(
                client, c.MANIFEST_COLLECTION, "upgrade", manifest_uuid
            )
    except Exception:
        base_client.delete_entity(client, c.MANIFEST_COLLECTION, manifest_uuid)
        raise

    for found_manifest_uuid in found_manifest_uuids:
        if found_manifest_uuid != manifest_uuid:
            base_client.delete_entity(
                client, c.MANIFEST_COLLECTION, found_manifest_uuid
            )

    return manifest_data


def upgrade_manifest(
    client: http_client.CollectionBaseClient,
    repository: str,
    path_or_name: str,
    install_only: bool = False,
    version: str | None = None,
    update_manifest: bool = False,
    **kwargs: tp.Any,
) -> dict[str, tp.Any]:
    """Install or update element from a YAML file or repository.

    The command will install the element if it's not installed or update it
    if it's installed.
    """

    if os.path.exists(path_or_name):
        if not os.path.isfile(path_or_name):
            raise click.ClickException(f"{path_or_name} is not a file")
        with open(path_or_name, "r", encoding="utf-8") as f:
            manifest = yaml.safe_load(f)
    else:
        manifest = repo_lib.download_manifest(repository, path_or_name, version)

    requirements: dict = manifest.get("requirements", {})

    installed = bool(
        base_client.list_entities(client, ENTITY_COLLECTION, name=manifest["name"])
    )

    if installed and install_only:
        raise click.ClickException(f"Element {manifest['name']} is already installed")

    # Install element if no requirements
    if not requirements:
        new_manifest = _apply_with_cleanup(
            client, manifest, install_only, update_manifest, **kwargs
        )
        return new_manifest

    # Resolve dependencies
    installed_elements = {
        e["name"] for e in base_client.list_entities(client, ENTITY_COLLECTION)
    }
    required_elements = set(requirements.keys()) - installed_elements

    all_installed_elements = required_elements.union({manifest["name"]})
    click.echo(
        f"The following elements will be {'installed' if install_only else 'upgraded'}: "
        f"{click.style(', '.join(all_installed_elements), fg='green')}"
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
        req_manifest = base_client.add_entity(
            client, c.MANIFEST_COLLECTION, req_manifest
        )
        base_client.action_entity(
            client, c.MANIFEST_COLLECTION, "install", req_manifest["uuid"]
        )
        installed_name = f"{req_manifest['name']} ({req_manifest['version']})"
        click.echo(
            f"Element {click.style(installed_name, fg='green')} was installed successfully"
        )

        installed_elements.add(req_manifest["name"])

        # TODO(akremenetsky): The installation is stuck for some reason
        # so we need to wait a bit. Solve the issue in GC and remove this
        # sleep.
        time.sleep(3)

    new_manifest = _apply_with_cleanup(client, manifest, install_only, update_manifest)
    return new_manifest


@elements_group.command("install", help="Install element from a manifest (YAML file)")
@click.option(
    "-r",
    "--repository",
    default=f"{c.ELEMENT_REPO_URL}/",
    show_default=True,
    help="Repository endpoint",
)
@click.option(
    "-v",
    "--version",
    type=str,
    required=False,
    help="version of the element",
)
@click.argument("path_or_name", required=False)
@click.pass_context
def install_manifest_cmd(
    ctx: click.Context, repository: str, version: str | None, path_or_name: str | None
) -> None:
    """Install manifest from a YAML file"""
    log = ClickLogger()

    if not path_or_name:
        all_elements = repo_lib.get_all_elements(repository)
        path_or_name = Prompt.ask(
            "Select manifest to install",
            choices=all_elements,
        )
    manifest = upgrade_manifest(
        base_client.get_user_api_client(ctx.obj.auth_data),
        repository,
        path_or_name,
        install_only=True,
        version=version,
    )
    log.important(
        f"Element {manifest['name']} ({manifest['version']}) was installed successfully"
    )


@elements_group.command("i", help="Install element from a manifest (YAML file)")
@click.option(
    "-r",
    "--repository",
    default=f"{c.ELEMENT_REPO_URL}/",
    show_default=True,
    help="Repository endpoint",
)
@click.option(
    "-v",
    "--version",
    type=str,
    required=False,
    help="version of the element",
)
@click.argument("path_or_name", required=False)
@click.pass_context
def i(
    ctx: click.Context, repository: str, version: str | None, path_or_name: str | None
) -> None:  # pragma: no cover
    ctx.invoke(
        install_manifest_cmd,
        repository=repository,
        path_or_name=path_or_name,
        version=version,
    )
    return None


@elements_group.command("update", help="Update element from a YAML file")
@click.option(
    "-r",
    "--repository",
    default=f"{c.ELEMENT_REPO_URL}/",
    show_default=True,
    help="Repository endpoint",
)
@click.option(
    "-v",
    "--version",
    type=str,
    required=False,
    help="version of the element",
)
@click.argument("path_or_name")
@click.pass_context
def update_manifest_cmd(
    ctx: click.Context, repository: str, version: str | None, path_or_name: str
) -> None:
    """Update manifest from a YAML file"""
    manifest = upgrade_manifest(
        base_client.get_user_api_client(ctx.obj.auth_data),
        repository,
        path_or_name,
        version=version,
    )
    click.echo(
        f"Element {click.style(manifest['name'], fg='green')} was successfully updated to version {click.style(manifest['version'], fg='green')}"
    )


@elements_group.command(help="Update element from a YAML file")
@click.option(
    "-r",
    "--repository",
    default=f"{c.ELEMENT_REPO_URL}/",
    show_default=True,
    help="Repository endpoint",
)
@click.option(
    "-v",
    "--version",
    type=str,
    required=False,
    help="version of the element",
)
@click.argument("path_or_name")
@click.pass_context
def u(
    ctx: click.Context, repository: str, version: str | None, path_or_name: str | None
) -> None:  # pragma: no cover
    ctx.invoke(
        update_manifest_cmd,
        repository=repository,
        version=version,
        path_or_name=path_or_name,
    )
    return None


@elements_group.command("uninstall", help="Uninstall manifest by UUID, path or name")
@click.argument("path_uuid_name", type=str)
@click.pass_context
def uninstall_manifest_cmd(ctx: click.Context, path_uuid_name: str) -> None:
    """Uninstall manifest by UUID, path or name"""
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    log = ClickLogger()

    def _uninstall(element_uuid: str, element_name: str = None) -> None:
        base_client.action_entity(
            client, c.MANIFEST_COLLECTION, "uninstall", element_uuid
        )
        base_client.delete_entity(client, c.MANIFEST_COLLECTION, element_uuid)
        log.important(
            f"Element {element_name or element_uuid} uninstalled successfully"
        )

    # UUID
    if utils.is_valid_uuid(path_uuid_name):
        _uninstall(path_uuid_name)
        return

    # Name
    name = path_uuid_name

    manifests = base_client.list_entities(client, c.MANIFEST_COLLECTION, name=name)
    if len(manifests) == 1:
        uuid = manifests[0]["uuid"]
        _uninstall(uuid, name)
        return
    elif len(manifests) > 1:

        manifest_choice = Prompt.ask(
            "Select manifest to uninstall",
            choices=[f"{manifest['name']} {manifest['version']}" for manifest in manifests],
        )
        m_name, m_version = manifest_choice.split(" ")
        for manifest in manifests:
            if manifest["name"] == m_name and manifest["version"] == m_version:
                uuid = manifest["uuid"]
                _uninstall(uuid, name)
                break
        return

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

        manifests = base_client.list_entities(client, c.MANIFEST_COLLECTION, **filters)
        if len(manifests) == 1:
            uuid = manifests[0]["uuid"]
            _uninstall(uuid, manifests[0]["name"])
            return
        if len(manifests) > 1:
            raise click.ClickException(f"Multiple elements found with name {name}")
        log.warn(f"manifest {list(filters.values())[0]} not found")
        return

    log.warn(f"Element {path_uuid_name} not found")


@elements_group.command("available", help="Print available elements in repository")
def available_elements() -> None:
    """Update manifest from a YAML file"""
    elements = repo_lib.get_all_elements(c.ELEMENT_REPO_URL)
    for e in elements:
        click.echo(e)


@elements_group.command("versions", help="Print available elements in repository")
@click.argument("name")
def versions(name) -> None:
    """Update manifest from a YAML file"""
    element_versions = repo_lib.get_element_versions_by_inventory(
        c.ELEMENT_REPO_URL, name
    )
    for version in element_versions:
        click.echo(version)


def edit_data(data: str, editor: str = "nano") -> tp.Tuple[str, dict]:
    tf_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".yaml", mode="a+", delete=False) as tf:
            tf.write(data)
            tf.flush()
            tf_path = tf.name
            subprocess.call([editor, tf_path])
            tf.seek(0)
            new_data = tf.read()
    finally:
        if tf_path and os.path.exists(tf_path):
            os.remove(tf_path)
    json_data = yaml.load(new_data, Loader=yaml.FullLoader)
    return new_data, json_data


@elements_group.command(help="Edit manifest", context_settings={"show_default": True})
@click.argument("uuid_name")
@click.option(
    "-e",
    "--editor",
    default="nano",
    type=click.Choice(["nano", "vim"], case_sensitive=False),
    help="Editor (nano or vim)",
)
@click.option(
    "-r",
    "--repository",
    default=f"{c.ELEMENT_REPO_URL}/",
    show_default=True,
    help="Repository endpoint",
)
@click.pass_context
def edit(ctx: click.Context, uuid_name: str, editor: str, repository: str) -> None:
    client = base_client.get_user_api_client(ctx.obj.auth_data)
    data = base_client.get_entity(client, c.MANIFEST_COLLECTION, uuid_name)
    tf_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".yaml", mode="a+", delete=False) as tf:
            yaml.dump(data, tf)
            tf.flush()
            tf_path = tf.name
            subprocess.call([editor, tf_path])
            tf.seek(0)
            manifest = upgrade_manifest(
                client,
                repository,
                tf_path,
                update_manifest=True,
                manifest_uuid=data["uuid"],
            )
    finally:
        if tf_path and os.path.exists(tf_path):
            os.remove(tf_path)
    click.echo(
        f"Element {click.style(manifest['name'], fg='green')} was successfully edited"
    )


def _print_entities(entities: tp.List[dict]) -> None:
    table = get_table("UUID", "Name", "Description", "Version", "Status")

    for entity in entities:
        table.add_row(
            entity["uuid"],
            entity["name"],
            entity["description"],
            entity["version"],
            entity["status"],
        )

    print_table(table)
