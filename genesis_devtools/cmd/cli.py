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

import logging
import os
import requests
from requests.exceptions import RequestException
import time
import shutil
import typing as tp
import tempfile
import ipaddress
import fnmatch
import pathlib
import uuid as sys_uuid
import json

import yaml
import rich_click as click

from bazooka import exceptions as bazooka_exc
from gcl_sdk.clients.http import base as http_client

import genesis_devtools.constants as c
from genesis_devtools import utils
from genesis_devtools.common.cmd_context import ContextObject
from genesis_devtools.backup import base as backup_base
from genesis_devtools.backup import local as backup_local
from genesis_devtools.logger import ClickLogger
from genesis_devtools.repo import base as base_repo
from genesis_devtools.repo import utils as repo_utils
from genesis_devtools.builder import base as base_builder
from genesis_devtools.builder import builder as simple_builder
from genesis_devtools.builder.packer import PackerBuilder
from genesis_devtools.infra.libvirt import libvirt
from genesis_devtools.stand import models as stand_models
from genesis_devtools.infra.driver import libvirt as libvirt_infra

from genesis_devtools.cmd.iam.auth import commands as auth_commands

from genesis_devtools.cmd.iam import iam_group
from genesis_devtools.cmd.secret import secret_group
from genesis_devtools.cmd.vs import vs_group
from genesis_devtools.cmd.compute import compute_group
from genesis_devtools.cmd.realms.commands import realms_group

from genesis_devtools.cmd.em.manifests import commands as manifests_commands
from genesis_devtools.cmd.em.elements import commands as elements_commands
from genesis_devtools.cmd.em.services import commands as services_commands

from genesis_devtools.cmd.initialization import commands as initialization_commands
from genesis_devtools.cmd.configs import commands as configs_commands
from genesis_devtools.cmd.repo import commands as repo_commands
from genesis_devtools.cmd.em.resources import commands as resources_commands
from genesis_devtools.cmd.settings import commands as settings_commands

from genesis_devtools.cmd.aliases import ClickAliasedGroup

BOOTSTRAP_TAG = "bootstrap"
LaunchModeType = tp.Literal["core", "element", "custom"]
GC_CIDR = ipaddress.IPv4Network("10.20.0.0/22")
GC_BOOT_CIDR = ipaddress.IPv4Network("10.30.0.0/24")


@click.group(
    cls=ClickAliasedGroup,
    invoke_without_command=True,
    help="Provides all the necessary tools for work with Genesis Platform",
)
@click.option(
    "--config",
    default=c.CONFIG_FILE,
    show_default=True,
    type=click.Path(exists=False, dir_okay=False),
    help="Path to YAML config file",
)
@click.option(
    "-e",
    "--endpoint",
    default="http://localhost:11010",
    show_default=True,
    help="Genesis API endpoint",
)
@click.option(
    "-u",
    "--user",
    default=None,
    help="Client user name",
)
@click.option(
    "-p",
    "--password",
    default=None,
    help="Password for the client user",
)
@click.option(
    "-a",
    "--access_token",
    default=None,
    help="access token for the client user",
)
@click.option(
    "--refresh_token",
    default=None,
    help="refresh token for the client user",
)
@click.option(
    "-r",
    "--realm",
    type=str,
    help="Name of the realm",
)
@click.option(
    "-c",
    "--context",
    type=str,
    help="Name of the context",
)
@click.option(
    "-P",
    "--project-id",
    default=None,
    type=click.UUID,
    help="Project ID for the client user",
)
@click.option(
    "-vvv",
    "--verbose",
    show_default=True,
    is_flag=True,
    help="Verbose logs",
)
@click.option(
    "-i",
    "--developer-key-path",
    default=None,
    help="Path to developer public key",
)
@click.option(
    "-s",
    "--silent",
    show_default=True,
    is_flag=True,
    help="Do not print messages, warnings or errors",
)
@click.pass_context
def genesis(
    ctx: click.Context,
    config: str,
    endpoint: str,
    user: str | None,
    password: str | None,
    access_token: str | None,
    refresh_token: str | None,
    realm: str | None,
    context: str | None,
    project_id: sys_uuid.UUID | None,
    verbose: bool | None,
    developer_key_path: str | None,
    silent: bool | None,
) -> None:
    if not ctx.invoked_subcommand:
        click.echo(ctx.get_help())
        return
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    # Load configuration from file (if exists)
    cfg_path = config if config else None
    cfg = settings_commands.load_config(cfg_path, silent)

    realm_conf = settings_commands.get_realm(cfg, realm)
    context_conf = settings_commands.get_context(realm_conf, context)

    def _get_final_value(
        param_name: str, cli_value: tp.Any, base_conf: dict, direct_conf: dict
    ) -> tp.Any:
        if (
            ctx.get_parameter_source(param_name)
            == click.core.ParameterSource.COMMANDLINE
        ):
            return cli_value
        return direct_conf.get(param_name, base_conf.get(param_name, cli_value))

    final_endpoint = _get_final_value("endpoint", endpoint, cfg, realm_conf)
    final_check_updates = _get_final_value("check_updates", False, cfg, realm_conf)
    final_user = _get_final_value("user", user, cfg, context_conf)
    final_password = _get_final_value("password", password, cfg, context_conf)
    final_access_token = _get_final_value(
        "access_token", access_token, cfg, context_conf
    )
    final_refresh_token = _get_final_value(
        "refresh_token", refresh_token, cfg, context_conf
    )
    final_developer_key_path = _get_final_value(
        "developer_key_path", developer_key_path, cfg, {}
    )
    if final_check_updates and should_check_version():
        check_latest_version()
        save_last_check_time()

    final_project_id = _get_final_value("project_id", project_id, cfg, context_conf)

    if final_project_id is not None:
        scope = http_client.CoreIamAuthenticator.project_scope(final_project_id)
    else:
        scope = None

    auth_data = dict(
        endpoint=final_endpoint,
        username=final_user,
        password=final_password,
        access_token=final_access_token,
        refresh_token=final_refresh_token,
        scope=scope,
    )
    ctx.obj = ContextObject(auth_data, config, final_developer_key_path)


@genesis.command(
    "build",
    help=(
        "Build a Genesis element. The command build all images, manifests "
        "and other artifacts required for the element. The manifest in the "
        "project may be a raw YAML file or a template using Jinja2 "
        "templates. For Jinja2 templates, the following variables are "
        "available by default: \n\n"
        "- {{ version }}: version of the element \n\n"
        "- {{ name }}: name of the element \n\n"
        "- {{ images }}: list of images \n\n"
        "- {{ manifests }}: list of manifests \n\n"
        "\n\n"
        "Additional variables can be passed using the --manifest-var "
        "options."
    ),
)
@click.option(
    "-c",
    "--genesis-cfg-file",
    default=c.DEF_GEN_CFG_FILE_NAME,
    help="Name of the project configuration file",
)
@click.option(
    "--deps-dir",
    default=None,
    help="Directory where dependencies will be fetched",
)
@click.option(
    "--build-dir",
    default=None,
    help="Directory where temporary build artifacts will be stored",
)
@click.option(
    "-o",
    "--output-dir",
    default=c.DEF_GEN_OUTPUT_DIR_NAME,
    help="Directory where output artifacts will be stored",
)
@click.option(
    "-i",
    "--developer-key-path",
    default=None,
    help="Path to developer public key",
)
@click.option(
    "-s",
    "--version-suffix",
    default="none",
    type=click.Choice([s for s in tp.get_args(c.VersionSuffixType)]),
    show_default=True,
    help="Version suffix will be used for the build",
)
@click.option(
    "-f",
    "--force",
    show_default=True,
    is_flag=True,
    help="Rebuild if the output already exists",
)
@click.option(
    "--inventory",
    show_default=True,
    is_flag=True,
    help="Build using the inventory format",
)
@click.option(
    "--manifest-var",
    multiple=True,
    help=(
        "Additional variables to pass to the manifest template. "
        "The format is 'key=value'. For example: --manifest-var "
        "key1=value1 --manifest-var key2=value2"
    ),
)
@click.argument("project_dir", type=click.Path())
@click.pass_context
def build_cmd(
    ctx: click.Context,
    genesis_cfg_file: str,
    deps_dir: str | None,
    build_dir: str | None,
    output_dir: str | None,
    developer_key_path: str | None,
    version_suffix: c.VersionSuffixType,
    force: bool,
    project_dir: str,
    inventory: bool,
    manifest_var: tuple[str, ...],
) -> None:
    if not project_dir:
        raise click.UsageError("No project directories specified")

    manifest_vars = utils.convert_input_multiply(manifest_var)

    # Leave 'none' for backward compatibility
    if version_suffix == "none" and inventory:
        version_suffix = "element"
        click.secho(
            "Inventory mode is not supported for 'none' version suffix, "
            "using 'element' instead",
            fg="yellow",
        )

    if os.path.exists(output_dir) and not force:
        click.secho(
            f"The '{output_dir}' directory already exists. Use '--force' "
            "flag to remove current artifacts and new build.",
            fg="yellow",
        )
        return
    elif os.path.exists(output_dir) and force:
        shutil.rmtree(output_dir)

    # Developer keys
    developer_keys = utils.get_keys_by_path_or_env(
        developer_key_path, ctx.obj.developer_key_path
    )

    # Find path to genesis configuration
    try:
        gen_config = utils.get_genesis_config(project_dir, genesis_cfg_file)
    except FileNotFoundError:
        raise click.ClickException(
            f"Genesis configuration file not found in {project_dir}"
        )

    spec = utils.load_spec()
    utils.validate_config(gen_config, spec)
    # Take all build sections from the configuration
    builds = {k: v for k, v in gen_config.items() if k.startswith("build")}
    if not builds:
        click.secho("No builds found in the configuration", fg="yellow")
        return

    logger = ClickLogger()
    packer_image_builder = PackerBuilder(logger)

    # Path where genesis.yaml configuration file is located
    work_dir = os.path.abspath(os.path.join(project_dir, c.DEF_GEN_WORK_DIR_NAME))

    # Prepare a build suffix
    build_suffix = utils.get_version_suffix(version_suffix, project_dir=project_dir)

    for _, build in builds.items():
        builder = simple_builder.SimpleBuilder.from_config(
            work_dir, build, packer_image_builder, logger, output_dir
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            builder.fetch_dependency(deps_dir or temp_dir)
            builder.build(
                build_dir,
                developer_keys,
                build_suffix,
                inventory,
                manifest_vars,
            )


@genesis.command("push", help="Push the element to the repository")
@click.option(
    "-c",
    "--genesis-cfg-file",
    default=c.DEF_GEN_CFG_FILE_NAME,
    help="Name of the project configuration file",
)
@click.option(
    "-t",
    "--target",
    default=None,
    help="Target repository to push to",
)
@click.option(
    "-e",
    "--element-dir",
    default=c.DEF_GEN_OUTPUT_DIR_NAME,
    help="Directory where element artifacts are stored",
    type=click.Path(),
)
@click.option(
    "-f",
    "--force",
    show_default=True,
    is_flag=True,
    help="Force push even if the element already exists",
)
@click.option(
    "-l",
    "--latest",
    show_default=True,
    is_flag=True,
    help="Push the element too as the latest version (if stable version)",
)
@click.argument("project_dir", type=click.Path(), default=".")
def push_cmd(
    genesis_cfg_file: str,
    target: str | None,
    element_dir: str,
    force: bool,
    latest: bool,
    project_dir: str,
) -> None:
    driver = repo_utils.load_repo_driver(genesis_cfg_file, target, project_dir)

    # Push elements
    path = pathlib.Path(element_dir) / base_builder.ElementInventory.file_name
    with open(path, "r") as f:
        inventories = json.load(f)

    # Backward compatibility: support both single
    # inventory and list of inventories
    if not isinstance(inventories, list):
        inventories = [inventories]

    for inventory in inventories:
        element = base_builder.ElementInventory.from_dict(inventory)
        try:
            driver.push(element, latest=latest)
        except base_repo.ElementAlreadyExistsError:
            if force:
                driver.remove(element)
                driver.push(element, latest=latest)
                continue

            click.secho(
                f"Element {element.name} version {element.version} already exists.",
                fg="red",
            )


def _get_core_image_uri_from_manifest(manifest_path: str) -> str:
    """Get image URI from manifest file."""
    if not os.path.exists(manifest_path):
        raise click.UsageError(f"Manifest file {manifest_path} does not exist")

    with open(manifest_path, "r") as f:
        manifest = yaml.safe_load(f)

    # Determine image URI from manifest
    try:
        return manifest["resources"]["$core.compute.sets"]["core_set"]["disk_spec"][
            "disks"
        ][0]["image"]
    except (KeyError, IndexError):
        click.secho("Failed to get image URI from manifest", fg="red")
        raise


@genesis.command("bootstrap", help="Bootstrap genesis locally")
@click.option(
    "-i",
    "--inventory",
    help="Path to the genesis inventory file or directory with inventory.json",
)
@click.option(
    "--profile",
    default=c.Profile.SMALL.value,
    show_default=True,
    help="Profile for the installation.",
    type=click.Choice([p.value for p in c.Profile]),
)
@click.option(
    "--name",
    default="genesis-core",
    help="Name of the installation",
)
# It's a temporary option, will be removed in the future but now it's
# convenient to run elements and cores slightly differently
@click.option(
    "-m",
    "--launch-mode",
    default="element",
    type=click.Choice([s for s in tp.get_args(LaunchModeType)]),
    show_default=True,
    help="Launch mode for start element, core or custom configuration",
)
@click.option(
    "-s",
    "--stand-spec",
    default=None,
    type=click.Path(exists=True),
    help="Additional stand specification for core mode.",
)
@click.option(
    "--cidr",
    default=GC_CIDR,
    help="The main network CIDR",
    show_default=True,
    type=ipaddress.IPv4Network,
)
@click.option(
    "--core-ip",
    default=None,
    help=(
        "The IP address for the core VM. If `None` is provided, "
        "second IP address from the main network will be used."
    ),
    show_default=True,
    type=ipaddress.IPv4Address,
)
@click.option(
    "--bridge",
    default=None,
    help=(
        "Name of the linux bridge for the main network, it will be created if not set."
    ),
)
@click.option(
    "--boot-cidr",
    default=GC_BOOT_CIDR,
    help="The bootstrap network CIDR",
    show_default=True,
    type=ipaddress.IPv4Network,
)
@click.option(
    "--boot-bridge",
    default=None,
    help=(
        "Name of the linux bridge for the bootstrap network, "
        "it will be created if not set."
    ),
)
@click.option(
    "-f",
    "--force",
    show_default=True,
    is_flag=True,
    help="Rebuild if the output already exists",
)
@click.option(
    "--no-wait",
    show_default=True,
    is_flag=True,
    help="Cancel waiting for the installation to start",
)
@click.option(
    "-r",
    "--repository",
    default=f"{c.GENESIS_REPO_URL}/",
    type=str,
    help="Default element repository",
    show_default=True,
)
@click.option(
    "--admin-password",
    default=None,
    type=str,
    help=(
        "A password for the admin user in. If not provided, "
        "the password will be generated."
    ),
    show_default=True,
)
@click.option(
    "--save-admin-password-file",
    default=None,
    type=str,
    help=(
        "If the option is specified the admin password is saved "
        "to the file. Otherwise it's printed to the console."
    ),
    show_default=True,
)
@click.option(
    "--hyper-connection-uri",
    default="",
    type=str,
    help=(
        "Connection URI for the hypervisor, "
        "e.g. 'qemu+tcp://10.0.0.1/system' or "
        "'qemu+ssh://user@10.0.0.1/system'. If not set, "
        "the first address of the network(--cidr option) will be used. "
    ),
)
@click.option(
    "--hyper-storage-pool",
    default="default",
    type=str,
    help="Storage pool for the hypervisor.",
    show_default=True,
)
@click.option(
    "--hyper-machine-prefix",
    default="vm-",
    type=str,
    help="A prefix for new VMs.",
    show_default=True,
)
@click.option(
    "--hyper-iface-rom-file",
    default="/usr/share/qemu/1af41041.rom",
    type=str,
    help="A path to the custom ROM file of a network interface.",
    show_default=True,
)
@click.option(
    "--no-start",
    show_default=True,
    is_flag=True,
    help="Do not start the stand after creation",
)
# Ecosystem
@click.option(
    "--no-registration",
    is_flag=True,
    envvar="NO_REGISTRATION",
    help="Don't register in ecosystem.",
)
@click.option(
    "--disable-telemetry",
    is_flag=True,
    envvar="DISABLE_TELEMETRY",
    help="Disable telemetry. Anonymized data only is sent by default.",
)
@click.option(
    "--org-token",
    prompt=False,
    hide_input=True,
    type=str,
    envvar="ORG_TOKEN",
    help="Organization token, used to register stand in ecosystem",
)
@click.option(
    "--ecosystem-endpoint",
    default="https://console.genesis-core.tech",
    type=str,
    envvar="ECOSYSTEM_ENDPOINT",
    help="Ecosystem's endpoint to connect to",
)
def bootstrap_cmd(
    inventory: str,
    profile: str,
    name: str,
    launch_mode: LaunchModeType,
    stand_spec: str | None,
    cidr: ipaddress.IPv4Network,
    core_ip: ipaddress.IPv4Address | None,
    bridge: str | None,
    boot_cidr: ipaddress.IPv4Network,
    boot_bridge: str | None,
    force: bool,
    no_wait: bool,
    repository: str,
    admin_password: str | None,
    save_admin_password_file: str | None,
    hyper_connection_uri: str,
    hyper_storage_pool: str,
    hyper_machine_prefix: str,
    hyper_iface_rom_file: str,
    no_start: bool,
    no_registration: bool,
    disable_telemetry: bool,
    org_token: str | None,
    ecosystem_endpoint: str,
) -> None:
    if not inventory or not os.path.exists(inventory):
        raise click.UsageError("No inventory specified or not found")

    profile = c.Profile[profile.upper()]

    # Determine the IP address for the core VM
    if core_ip is None:
        core_ip = cidr[2]

    if core_ip not in cidr:
        raise click.UsageError("Core IP is not in the main network")

    # Generate admin password if not provided
    if not admin_password:
        import secrets

        admin_password = secrets.token_urlsafe(16)

    # Load inventory and get image path and image URI.
    inventory = base_builder.ElementInventory.load(pathlib.Path(inventory))

    if not inventory.images:
        raise click.UsageError("No images found in the inventory")

    if not inventory.manifests:
        raise click.UsageError("No manifests found in the inventory")

    # NOTE(akremenetsky): The core element has one image and manifest at the moment
    image_path = str(inventory.images[0])
    manifest_path = str(inventory.manifests[0])
    image_uri = _get_core_image_uri_from_manifest(manifest_path)

    if launch_mode not in ("element", "core"):
        raise click.UsageError(f"Unknown launch mode {launch_mode}")

    if image_path and not os.path.isabs(image_path):
        image_path = os.path.abspath(image_path)

    # DEPRECATED(akremenetsky): The 'element' mode is deprecated
    if launch_mode == "element":
        if stand_spec is not None:
            raise click.UsageError("Stand spec is not supported in 'element' mode")

        return _bootstrap_element(
            image_path=image_path,
            cores=profile.cores,
            memory=profile.ram,
            name=name,
            force=force,
            no_wait=no_wait,
            cidr=cidr,
        )

    # Validate org-token requirement based on no-registration flag
    if no_registration:
        org_token = None
    elif not org_token:
        click.secho(
            click.style(
                """\

Register your realm in the Genesis ecosystem to get access to additional features and support.
You can skip registration by using --no-registration flag.

""",
                bold=True,
                fg="yellow",
            ),
            bold=True,
            # Underline makes the text more visible
            underline=True,
        )

        org_token = click.prompt("Organization token", hide_input=True)

    if stand_spec is not None:
        with open(stand_spec) as f:
            stand_spec = yaml.safe_load(f)

    net_name = utils.installation_net_name(name)
    stand_main_network = stand_models.Network(
        name=bridge if bridge else net_name,
        cidr=cidr,
        managed_network=False if bridge else True,
    )
    boot_net_name = utils.installation_boot_net_name(name)
    stand_boot_network = stand_models.Network(
        name=boot_bridge if boot_bridge else boot_net_name,
        cidr=boot_cidr,
        managed_network=False if boot_bridge else True,
    )

    hypervisors = []

    if not hyper_connection_uri:
        hyper_connection_uri = f"qemu+tcp://{cidr[1]}/system"

    # Single hypervisor at bootstrap time is supported at the moment
    hypervisor = stand_models.Hypervisor(
        network=stand_main_network.name,
        network_type="bridge" if bridge else "network",
        connection_uri=hyper_connection_uri,
        storage_pool=hyper_storage_pool,
        machine_prefix=hyper_machine_prefix,
        iface_rom_file=hyper_iface_rom_file,
    )
    hypervisors.append(hypervisor)

    realm_uuid, realm_secret, realm_tokens = _register_core(
        ecosystem_endpoint=ecosystem_endpoint,
        disable_telemetry=disable_telemetry,
        org_token=org_token,
    )

    return _bootstrap_core(
        image_path=image_path,
        image_uri=image_uri,
        profile=profile,
        name=name,
        stand_spec=stand_spec,
        stand_main_network=stand_main_network,
        stand_boot_network=stand_boot_network,
        force=force,
        core_ip=core_ip,
        repository=repository,
        admin_password=admin_password,
        save_admin_password_file=save_admin_password_file,
        manifest_path=manifest_path,
        hypervisors=hypervisors,
        no_start=no_start,
        ecosystem_endpoint=ecosystem_endpoint,
        disable_telemetry=disable_telemetry,
        realm_uuid=realm_uuid,
        realm_secret=realm_secret,
        realm_tokens=realm_tokens,
    )


@genesis.command("get-version", help="Return the version of the project")
@click.argument("element_dir", type=click.Path())
def get_project_version_cmd(element_dir: str) -> None:
    logger = ClickLogger()
    version = utils.get_project_version(element_dir)
    logger.important(version)


def _start_validation_type(start: str | None) -> time.struct_time | None:
    if start is None:
        return None

    try:
        return time.strptime(start, "%H:%M:%S")
    except ValueError:
        raise click.UsageError("Invalid '--start' format. Use HH:MM:SS, e.g., 16:00:00")


@genesis.command("backup", help="Backup the current installation")
@click.option(
    "--config",
    default=None,
    type=click.Path(),
    help="Path to the backuper configuration file",
)
@click.option(
    "-n",
    "--name",
    default=None,
    multiple=True,
    help="Name of the libvirt domain, if not provided, all will be backed up",
)
@click.option(
    "-d",
    "--backup-dir",
    default=".",
    type=click.Path(),
    help="Directory where backups will be stored",
)
@click.option(
    "-p",
    "--period",
    default=c.BackupPeriod.D1.value,
    type=click.Choice([p.value for p in c.BackupPeriod]),
    show_default=True,
    help="the regularity of backups",
)
@click.option(
    "-o",
    "--offset",
    default=None,
    type=click.Choice([p.value for p in c.BackupPeriod]),
    show_default=True,
    help=(
        "The time offset of the first backup. If not provided, "
        "the same value as the period will be used"
    ),
)
@click.option(
    "--start",
    default=None,
    type=_start_validation_type,
    help=(
        "Time of day to start backup in format HH:MM:SS. "
        "Cannot be used together with --offset. If provided, "
        "period must be >= 1d."
    ),
)
@click.option(
    "--oneshot",
    show_default=True,
    is_flag=True,
    help="Do a backup once and exit",
)
@click.option(
    "-c",
    "--compress",
    show_default=True,
    is_flag=True,
    help="Compress the backup.",
)
@click.option(
    "-e",
    "--encrypt",
    show_default=True,
    is_flag=True,
    help=(
        "Encrypt the backup. Works only with the compress flag. "
        "Use environment variable to specify the encryption key "
        "and the initialization vector: "
        "GEN_DEV_BACKUP_KEY and GEN_DEV_BACKUP_IV"
    ),
)
@click.option(
    "-s",
    "--min-free-space",
    default=50,
    type=int,
    show_default=True,
    help=(
        "Free disk space shouldn't be lower than this threshold. "
        "If the space becomes lower, the backup process is stopped. "
        "The value is in GB."
    ),
)
@click.option(
    "-r",
    "--rotate",
    default=5,
    type=int,
    show_default=True,
    help=(
        "Maximum number of backups to keep. The oldest backups are deleted. "
        "`0` means no rotation."
    ),
)
@click.option(
    "--no",
    "--exclude-name",
    "exclude_name",
    multiple=True,
    help="Name or pattern of libvirt domains to exclude from backup",
)
def backup_cmd(
    config: str | None,
    name: tp.List[str] | None,
    exclude_name: tp.List[str] | None,
    backup_dir: str,
    period: str,
    offset: str | None,
    start: time.struct_time | None,
    oneshot: bool,
    compress: bool,
    encrypt: bool,
    min_free_space: int,
    rotate: int,
) -> None:
    period = c.BackupPeriod(period)
    if offset:
        offset = c.BackupPeriod(offset)

    # Forbid using both include and exclude options
    if name and exclude_name:
        raise click.UsageError(
            "Cannot specify both --name and --no/--exclude-name options at the same time."
        )

    # Default local backuper if no config is provided
    if config is None:
        backuper = backup_local.LocalQcowBackuper(
            backup_dir=backup_dir,
            min_free_disk_space_gb=min_free_space,
        )
    else:
        backuper = utils.load_driver(config)

    # Need to specify encryption key and initialization vector via
    # environment variables.
    if encrypt:
        try:
            backup_base.EncryptionCreds.validate_env()
        except ValueError:
            raise click.UsageError(
                (
                    "Define environment variables GEN_DEV_BACKUP_KEY "
                    "and GEN_DEV_BACKUP_IV. "
                    "Key and IV must be greater or equal than "
                    f"{backup_base.EncryptionCreds.MIN_LEN} bytes and less "
                    f"or equal to {backup_base.EncryptionCreds.LEN} bytes."
                )
            )

        encryption = backup_base.EncryptionCreds.from_env()
    else:
        encryption = None

    # Do a single backup and exit
    if oneshot:
        domains = _domains_for_backup(name, exclude_name, raise_on_domain_absence=True)
        backuper.backup(domains, compress, encryption)
        return

    # Do periodic backups
    click.secho(f"Current time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # The `start` option validation
    if start is None:
        # Default behavior: use offset (or period if offset not provided)
        offset = offset or period
        ts = time.time() + offset.timeout
        click.secho(
            f"Next backup at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))}"
        )
        time.sleep(offset.timeout)
    else:
        # Validate mutually exclusive options: --start and --offset
        if offset is not None:
            raise click.UsageError(
                "Options '--start' and '--offset' cannot be used together. "
                "Choose one. By default, --offset is used."
            )

        # If --start is specified, period must be at least daily
        if period.timeout < c.BackupPeriod.D1.timeout:
            raise click.UsageError(
                "The '--start' option requires the period to be at least 1 day (1d)."
            )

        start_sec = start.tm_hour * 3600 + start.tm_min * 60 + start.tm_sec
        now_ts = time.time()
        now = time.localtime(now_ts)
        now_sec = now.tm_hour * 3600 + now.tm_min * 60 + now.tm_sec

        if now_sec < start_sec:
            delta = start_sec - now_sec
        else:
            delta = 24 * 3600 - now_sec + start_sec

        ts = now_ts + delta
        click.secho(
            f"Next backup at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))}"
        )
        time.sleep(delta)

    # Next runs happen every 'period' seconds from the aligned start
    next_ts = time.time() + period.timeout

    # Do periodic backups
    while True:
        # Need to refresh the list of domains since it could have changed
        domains = _domains_for_backup(name, exclude_name)

        click.secho(f"Backup started at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        backuper.backup(domains, compress, encryption)
        click.secho(
            "Next backup at: "
            f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(next_ts))}"
        )

        # Rotate old backups
        backuper.rotate(rotate)

        timeout = next_ts - time.time()
        timeout = 0 if timeout < 0 else timeout
        next_ts += period.timeout

        time.sleep(timeout)


@genesis.command("backup-decrypt", help="Decrypt a backup file")
@click.argument("path", type=click.Path(exists=True))
def backup_decrypt_cmd(path: str) -> None:
    # Need to specify encryption key and initialization vector via
    # environment variables.

    try:
        backup_base.EncryptionCreds.validate_env()
    except ValueError:
        raise click.UsageError(
            (
                "Define environment variables GEN_DEV_BACKUP_KEY "
                "and GEN_DEV_BACKUP_IV. "
                "Key and IV must be greater or equal than "
                f"{backup_base.EncryptionCreds.MIN_LEN} bytes and less or "
                f"equal to {backup_base.EncryptionCreds.LEN} bytes."
            )
        )

    encryption = backup_base.EncryptionCreds.from_env()

    if os.path.isdir(path):
        for file in os.listdir(path):
            _path = os.path.join(path, file)
            utils.decrypt_file(
                _path,
                encryption.key,
                encryption.iv,
            )
            click.secho(f"The {_path} file has been decrypted.", fg="green")
        return

    utils.decrypt_file(
        path,
        encryption.key,
        encryption.iv,
    )
    click.secho(f"The {path} file has been decrypted.", fg="green")


@genesis.command(help="tool for creating docs files for cli commands", hidden=True)
def dumphelp() -> None:
    from genesis_devtools.common.md_click import dump_helper  # type: ignore

    dump_helper(genesis)
    return None


@genesis.command(
    name="openapi", help="tool for creating openapi spec files", hidden=True
)
@click.option(
    "-u",
    "--url",
    type=click.STRING,
    required=False,
    default=None,
    help="openapi url",
)
@click.option(
    "-e",
    "--endpoint",
    required=False,
    default=None,
)
@click.argument(
    "path",
    required=False,
    type=click.Path(exists=False, dir_okay=False),
    help="Path to target file",
)
@click.pass_context
def openapi_spec(ctx: click.Context, url: str, endpoint: str, path: str) -> None:
    from genesis_devtools.clients.base_client import get_user_api_client
    import ruamel.yaml

    if url:
        response = requests.get(url, timeout=10).json()
        response.raise_for_status()
        data = response.json()
    else:
        auth_data = ctx.obj.auth_data
        if endpoint:
            auth_data["endpoint"] = endpoint
        client = get_user_api_client(auth_data)
        data = client.filter("specifications/3.0.3")

    path = path or os.path.expanduser("~/.openapi.yaml")
    with open(path, "w") as f:
        yaml = ruamel.yaml.YAML()
        yaml.indent(sequence=4, offset=2)
        yaml.dump(data, f)
    click.secho(f"OpenAPI spec written to {path}", fg="green")
    return None


def _domains_for_backup(
    names: tp.List[str] | None = None,
    exclude_names: tp.List[str] | None = None,
    raise_on_domain_absence: bool = False,
) -> tp.List[str]:
    domains = set(libvirt.list_domains())
    names = set(names or [])
    exclude_names = set(exclude_names or [])

    # Check if the specified domains exist
    if raise_on_domain_absence and (names - domains):
        diff = ", ".join(names - domains)
        raise click.UsageError(f"Domains {diff} not found")

    if names:
        domains &= names

    if exclude_names:
        domains = {
            d
            for d in domains
            if not any(fnmatch.fnmatch(d, pattern) for pattern in exclude_names)
        }

    return list(domains)


def _bootstrap_element(
    image_path: tp.Optional[str],
    cores: int,
    memory: int,
    name: str,
    cidr: ipaddress.IPv4Network,
    force: bool,
    no_wait: bool,
) -> None:
    logger = ClickLogger()

    net_name = utils.installation_net_name(name)
    default_stand_network = stand_models.Network(
        name=net_name,
        cidr=cidr,
        managed_network=True,
        dhcp=True,
    )

    bootstrap_domain_name = utils.installation_bootstrap_name(name)

    # Single bootstrap stand
    dev_stand = stand_models.Stand.single_bootstrap_stand(
        name=name,
        image=image_path,
        cores=cores,
        memory=memory,
        network=default_stand_network,
        bootstrap_name=bootstrap_domain_name,
    )

    if not dev_stand.is_valid():
        logger.error("Invalid stand for element")
        return

    infra = libvirt_infra.LibvirtInfraDriver()

    # Check if the target stand already exists
    for stand in infra.list_stands():
        if stand.name != dev_stand.name:
            continue

        # Without `force` flag, unable to proceed with the installation
        if not force:
            logger.warn(
                f"Genesis element {dev_stand.name} is already running. "
                "Use '--force' flag to forcely rerun genesis element.",
            )
            return

        infra.delete_stand(stand)
        logger.info(f"Destroyed old genesis element: {dev_stand.name}")

    infra.create_stand(dev_stand)
    logger.info(f"Launched genesis element {name}")

    # Wait for the installation to start
    if no_wait:
        return

    utils.wait_for(
        lambda: bool(libvirt.get_domain_ip(bootstrap_domain_name)),
        title=f"Waiting for element {name}",
    )

    ip = libvirt.get_domain_ip(bootstrap_domain_name)
    logger.important(f"The element {name} is ready at:\nssh ubuntu@{ip}")


def _register_core(
    ecosystem_endpoint: str,
    disable_telemetry: bool,
    org_token: str | None,
) -> tuple[str, str, str]:
    from genesis_devtools.clients import ecosystem

    logger = ClickLogger()
    logger.info("Registering realm in ecosystem...")

    realm_uuid, realm_secret, tokens_dict = ecosystem.register_realm(
        ecosystem_endpoint=ecosystem_endpoint,
        org_token=org_token,
    )

    if tokens_dict:
        logger.info("Realm registered successfully")
    else:
        logger.info("Realm registered successfully in anonymous mode")

    return realm_uuid, realm_secret, tokens_dict


def _bootstrap_core(
    image_path: str | None,
    image_uri: str | None,
    profile: c.Profile,
    name: str,
    stand_spec: tp.Dict[str, tp.Any] | None,
    stand_main_network: stand_models.Network,
    stand_boot_network: stand_models.Network,
    force: bool,
    core_ip: ipaddress.IPv4Address,
    repository: str,
    admin_password: str,
    save_admin_password_file: str | None,
    manifest_path: str,
    hypervisors: tp.Collection[stand_models.Hypervisor],
    no_start: bool,
    ecosystem_endpoint: str,
    disable_telemetry: bool,
    realm_uuid: str,
    realm_secret: str,
    realm_tokens: dict,
) -> None:
    logger = ClickLogger()
    logger.info("Starting genesis bootstrap in 'core' mode")

    if not hypervisors:
        logger.error("No hypervisors provided")
        return

    # Single bootstrap stand
    if stand_spec is None:
        bootstrap_domain_name = utils.installation_bootstrap_name(name)
        dev_stand = stand_models.Stand.single_bootstrap_stand(
            name=name,
            image=image_path,
            image_uri=image_uri,
            cores=profile.cores,
            memory=profile.ram,
            core_ip=core_ip,
            network=stand_main_network,
            boot_network=stand_boot_network,
            bootstrap_name=bootstrap_domain_name,
            hypervisors=hypervisors,
        )
    else:
        dev_stand = stand_models.Stand.from_spec(stand_spec)
        if dev_stand.network.is_dummy:
            dev_stand.network = stand_main_network

        if dev_stand.boot_network.is_dummy:
            dev_stand.boot_network = stand_boot_network

        # Assign the image to bootstraps if it wasn't specified
        # in the specification.
        for b in dev_stand.bootstraps:
            if b.image is None:
                b.image = image_path

    if not dev_stand.is_valid():
        logger.error(f"Invalid stand {dev_stand} from spec {stand_spec}")
        return

    infra = libvirt_infra.LibvirtInfraDriver()

    # Check if the target stand already exists
    for stand in infra.list_stands():
        if stand.name != dev_stand.name:
            continue

        # Without `force` flag, unable to proceed with the installation
        if not force:
            logger.warn(
                f"Genesis installation {dev_stand.name} is already running. "
                "Use '--force' flag to forcely rerun genesis installation.",
            )
            return

        infra.delete_stand(stand)
        logger.info(f"Destroyed old genesis installation: {dev_stand.name}")

    try:
        infra.create_stand(
            dev_stand,
            manifest_path=manifest_path,
            no_start=no_start,
            repository=repository,
            admin_password=admin_password,
            profile=profile.value,
            ecosystem_endpoint=ecosystem_endpoint,
            disable_telemetry=disable_telemetry,
            realm_uuid=realm_uuid,
            realm_secret=realm_secret,
            realm_tokens=realm_tokens,
        )
        logger.info(f"Launched genesis installation in `{profile.value}` profile")

        if save_admin_password_file:
            # Basic security check to prevent path traversal.
            if ".." in pathlib.Path(save_admin_password_file).parts:
                logger.error(
                    "Invalid password file path (contains '..'). Skipping save."
                )
            else:
                try:
                    # Ensure parent directory exists.
                    pathlib.Path(save_admin_password_file).parent.mkdir(
                        parents=True, exist_ok=True
                    )
                    # Use exclusive creation ('x' mode) to prevent race conditions
                    # and accidental overwrites.
                    with open(save_admin_password_file, "x") as f:
                        f.write(admin_password)
                    logger.info(f"Admin password saved to {save_admin_password_file}")
                except FileExistsError:
                    logger.warn(
                        f"Admin password file {save_admin_password_file} "
                        "already exists. Skipping saving the password."
                    )
                except OSError as e:
                    logger.error(
                        "Failed to save admin password to "
                        f"{save_admin_password_file}: {e}"
                    )
        else:
            logger.important(f"Admin password: {admin_password}")
    except Exception:
        infra.delete_stand(dev_stand)
        logger.error(f"Failed to launch genesis installation {dev_stand.name}")
        raise

    cidr = dev_stand.network.cidr
    if not no_start:
        logger.important(
            f"The stand {name} will be ready soon at:\nssh ubuntu@{cidr[2]}",
        )
    else:
        logger.info(
            f"The stand {name} is created but not started. You can start it manually."
        )


def check_latest_version(echo_on_latest: bool = False) -> None:
    """Check for the latest version on GitHub and warn if newer version exists."""
    try:
        response = requests.get(f"{c.GITHUB_RELEASES_URL}/latest", timeout=1)
        response.raise_for_status()
        latest_tag = response.json()["tag_name"]

        from genesis_devtools import version as genesis_version

        # Сравниваем версии
        from packaging import version

        if version.parse(latest_tag) > version.parse(genesis_version.version_info):
            click.secho(
                f"New version available: {latest_tag} (current: {genesis_version.version_info}) "
                f"Update by:\ncurl -fsSL {c.GENESIS_REPO_URL}/install.sh | sudo sh",
                fg="yellow",
            )
        else:
            if echo_on_latest:
                click.secho(
                    f"You are using the latest version: {genesis_version.version_info}",
                    fg="green",
                )
    except Exception as err:
        click.secho(
            f"Failed to check for the latest version on GitHub: {err}", fg="red"
        )


def should_check_version():
    """Check if we should perform a version check."""
    try:
        # Check if file exists and is not empty
        if not os.path.exists(c.LAST_CHECK_FILE):
            return True

        # Read the last check time
        with open(c.LAST_CHECK_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return True

            last_check = float(content)

        # Check if enough time has passed
        if time.time() - last_check > c.UPDATE_CHECK_INTERVAL:
            return True
        return False
    except Exception:
        return False  # Default to no checking if we can't read the file


def save_last_check_time():
    """Save the current timestamp to the version check file."""
    try:
        os.makedirs(os.path.dirname(c.LAST_CHECK_FILE), exist_ok=True)
        with open(c.LAST_CHECK_FILE, "w") as f:
            f.write(str(time.time()))
    except Exception:
        # Silently ignore write errors
        pass


@genesis.command(name="version", help=f"Prints the {c.PKG_NAME} version")
def version_cmd() -> None:
    from genesis_devtools import version

    click.echo(version.version_info)


@genesis.command(name="latest", help="Check for the latest version on GitHub")
def latest_cmd() -> None:
    check_latest_version(echo_on_latest=True)


@genesis.command("cowsay", help="Display a cow message")
def cowsay_cmd() -> None:
    import cowsay

    cowsay.cow("I am genesis-cli")


@genesis.command("hello", help="Display a genesis message")
def hello() -> None:
    msg = """
▄▖        ▘
▌ █▌▛▌█▌▛▘▌▛▘
▙▌▙▖▌▌▙▖▄▌▌▄▌
"""
    click.echo(msg)


@genesis.command("autocomplete_help", help="Display a autocomplete help")
def autocomplete_help() -> None:
    from genesis_devtools.utils import PROJECT_PATH

    with open(
        os.path.join(
            PROJECT_PATH, "genesis_devtools", "autocomplete", "autocomplete_help"
        ),
        "r",
    ) as f:
        autocomplete_data = f.read()
    click.echo(autocomplete_data)


@genesis.command("autocomplete", help="update genesis autocomplete for your shell")
@click.option(
    "-s",
    "--shell",
    type=click.Choice(["bash", "zsh"]),
    required=False,
    default=None,
    help="shell kind",
)
def autocomplete(shell: str | None) -> None:
    from genesis_devtools.utils import PROJECT_PATH

    if shell is None:
        import psutil

        shell = psutil.Process(os.getppid()).parent().name()

    if shell == "bash":
        project_complete_path = "genesis-complete.bash"
        rc_complete_path = "bashrc-complete"
        rc_file = "~/.bashrc"
    elif shell == "zsh":
        project_complete_path = "genesis-complete.zsh"
        rc_complete_path = "zshrc-complete"
        rc_file = "~/.zshrc"
    else:
        click.echo(f"autocomplete not supported for this shell {shell}")
        return
    with open(
        os.path.join(PROJECT_PATH, c.PKG_NAME, "autocomplete", project_complete_path),
        "r",
    ) as f:
        autocomplete_data = f.read()
    os.makedirs(os.path.expanduser(c.CONFIG_DIR), exist_ok=True)
    with open(os.path.expanduser(f"{c.CONFIG_DIR}/.{project_complete_path}"), "w") as f:
        f.write(autocomplete_data)
    with open(
        os.path.join(PROJECT_PATH, c.PKG_NAME, "autocomplete", rc_complete_path),
        "r",
    ) as f:
        rc_data = f.read()
    with open(os.path.expanduser(rc_file), "a+") as f:
        f.seek(0)
        if rc_data not in f.read():
            f.write(rc_data)
    click.echo("autocomplete updated. Restart your shell")


genesis.add_command(auth_commands.auth_group)  # noqa

genesis.add_command(iam_group)  # noqa
genesis.add_command(secret_group)  # noqa
genesis.add_command(compute_group, aliases=["c"])  # noqa
genesis.add_command(vs_group)  # noqa
genesis.add_command(realms_group)  # noqa

genesis.add_command(manifests_commands.manifests_group)  # noqa
genesis.add_command(elements_commands.elements_group, aliases=["e"])  # noqa
genesis.add_command(services_commands.services_group)  # noqa

genesis.add_command(configs_commands.configs_group)  # noqa
genesis.add_command(settings_commands.settings_group)  # noqa
genesis.add_command(repo_commands.repository_group)  # noqa
genesis.add_command(resources_commands.resources_group, aliases=["r"])  # noqa

genesis.add_command(initialization_commands.init_cmd)  # noqa


if __name__ == "__main__":
    try:
        genesis()
    except bazooka_exc.BaseHTTPException as e:
        click.secho(f"Error: [{e.code}] {e.cause.response.text}", fg="red")
    except RequestException as e:
        if e.response is not None:
            click.secho(
                f"Error: [{e.response.status_code}] {e.response.text}", fg="red"
            )
        click.secho(f"Error: {e}", fg="red")
    except ValueError as e:
        click.secho(f"Error: {e}", fg="red")
