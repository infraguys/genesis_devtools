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
import shutil
import typing as tp
import tempfile
import ipaddress
import fnmatch

import yaml
import click
import prettytable

import genesis_devtools.constants as c
from genesis_devtools import utils
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


BOOTSTRAP_TAG = "bootstrap"
LaunchModeType = tp.Literal["core", "element", "custom"]
GC_CIDR = ipaddress.IPv4Network("10.20.0.0/22")


@click.group(invoke_without_command=True)
def main() -> None:
    pass


def _convert_manifest_vars(manifest_vars: tuple[str, ...]) -> dict[str, str]:
    result = {}
    for var in manifest_vars:
        if "=" not in var:
            raise click.UsageError(
                f"Invalid manifest variable format: '{var}'. "
                "Expected 'key=value'."
            )
        key, value = var.split("=", 1)
        result[key] = value
    return result


@main.command(
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
def build_cmd(
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

    manifest_vars = _convert_manifest_vars(manifest_var)

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
    developer_keys = utils.get_keys_by_path_or_env(developer_key_path)

    # Find path to genesis configuration
    try:
        gen_config = utils.get_genesis_config(project_dir, genesis_cfg_file)
    except FileNotFoundError:
        raise click.ClickException(
            f"Genesis configuration file not found in {project_dir}"
        )

    # Take all build sections from the configuration
    builds = {k: v for k, v in gen_config.items() if k.startswith("build")}
    if not builds:
        click.secho("No builds found in the configuration", fg="yellow")
        return

    logger = ClickLogger()
    packer_image_builder = PackerBuilder(logger)

    # Path where genesis.yaml configuration file is located
    work_dir = os.path.abspath(
        os.path.join(project_dir, c.DEF_GEN_WORK_DIR_NAME)
    )

    # Prepare a build suffix
    build_suffix = utils.get_version_suffix(
        version_suffix, project_dir=project_dir
    )

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


@main.command("push", help="Push the element to the repository")
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
@click.argument("project_dir", type=click.Path(), default=".")
def push_cmd(
    genesis_cfg_file: str,
    target: str | None,
    force: bool,
    element_dir: str,
    project_dir: str,
) -> None:
    driver = repo_utils.load_repo_driver(genesis_cfg_file, target, project_dir)

    # Push the element
    element = base_builder.ElementInventory.load(element_dir)
    try:
        driver.push(element)
    except base_repo.ElementAlreadyExistsError:
        if force:
            driver.remove(element)
            driver.push(element)
            return

        click.secho(
            f"Element {element.name} version {element.version} already exists.",
            fg="red",
        )


@main.command("bootstrap", help="Bootstrap genesis locally")
@click.option(
    "-i",
    "--image-path",
    default=None,
    help="Path to the genesis image",
)
@click.option(
    "--cores",
    default=2,
    show_default=True,
    help="Number of cores for the bootstrap VM",
)
@click.option(
    "--memory",
    default=4096,
    show_default=True,
    help="Memory in Mb for the bootstrap VM",
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
    default="192.168.4.0/22",
    help="Network CIDR",
    show_default=True,
    type=ipaddress.IPv4Network,
)
@click.option(
    "--bridge",
    default=None,
    help="Name of the linux bridge, it will be created if not set.",
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
    "--use-image-inplace",
    show_default=True,
    is_flag=True,
    help="Don't copy image, use specified file as is (warning - destructive!)",
)
def bootstrap_cmd(
    image_path: tp.Optional[str],
    cores: int,
    memory: int,
    name: str,
    launch_mode: LaunchModeType,
    stand_spec: str | None,
    cidr: ipaddress.IPv4Network,
    bridge: str | None,
    force: bool,
    no_wait: bool,
    use_image_inplace: bool,
) -> None:
    if image_path is None or not os.path.exists(image_path):
        raise click.UsageError("No image path specified or not found")

    if image_path and not os.path.isabs(image_path):
        image_path = os.path.abspath(image_path)

    # DEPRECATED(akremenetsky): The 'element' mode is deprecated
    if launch_mode == "element":
        if stand_spec is not None:
            raise click.UsageError(
                "Stand spec is not supported in 'element' mode"
            )

        return _bootstrap_element(
            image_path=image_path,
            cores=cores,
            memory=memory,
            name=name,
            force=force,
            no_wait=no_wait,
            cidr=cidr,
            use_image_inplace=use_image_inplace,
        )

    if launch_mode == "core":
        if stand_spec is not None:
            with open(stand_spec) as f:
                stand_spec = yaml.safe_load(f)

        return _bootstrap_core(
            image_path=image_path,
            cores=cores,
            memory=memory,
            name=name,
            stand_spec=stand_spec,
            bridge=bridge,
            force=force,
            use_image_inplace=use_image_inplace,
        )

    raise click.UsageError("Unknown launch mode")


@main.group("repo", help="Manager Genesis repository")
def repository_group():
    pass


@repository_group.command("init", help="Initialize the repository")
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
    "-f",
    "--force",
    show_default=True,
    is_flag=True,
    help="Force init even if the repo already exists",
)
@click.argument("project_dir", type=click.Path(), default=".")
def repo_init_cmd(
    genesis_cfg_file: str,
    target: str | None,
    force: bool,
    project_dir: str,
) -> None:
    driver = repo_utils.load_repo_driver(genesis_cfg_file, target, project_dir)

    try:
        driver.init_repo()
    except base_repo.RepoAlreadyExistsError:
        if force:
            driver.delete_repo()
            driver.init_repo()
            return

        click.secho(
            f"Repository already exists.",
            fg="red",
        )


@repository_group.command("delete", help="Delete the repository")
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
@click.argument("project_dir", type=click.Path(), default=".")
def repo_delete_cmd(
    genesis_cfg_file: str,
    target: str | None,
    project_dir: str,
) -> None:
    driver = repo_utils.load_repo_driver(genesis_cfg_file, target, project_dir)
    driver.delete_repo()


@repository_group.command("list", help="List the repository")
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
    "--element",
    default=None,
    help="Element to list",
)
@click.argument("project_dir", type=click.Path(), default=".")
def repo_list_cmd(
    genesis_cfg_file: str,
    target: str | None,
    element: str | None,
    project_dir: str,
) -> None:
    table = prettytable.PrettyTable()

    driver = repo_utils.load_repo_driver(genesis_cfg_file, target, project_dir)
    try:
        elements = driver.list()
    except base_repo.RepoNotFoundError:
        click.secho("Repository not found", fg="red")
        return

    if element is not None:
        if element not in elements:
            raise click.UsageError(f"Element {element} not found")

        table.field_names = [
            "version",
        ]

        for version in sorted(elements[element]):
            table.add_row([version])

        click.echo(table)
        return

    table.field_names = [
        "name",
        "last version",
        "versions",
    ]

    for element in elements:
        table.add_row(
            [element, sorted(elements[element])[-1], len(elements[element])]
        )

    click.echo(table)


@main.command("ssh", help="Connect to genesis stand/element")
@click.option(
    "-s",
    "--stand",
    default=None,
    help="Stand to connect to",
)
@click.option(
    "-u",
    "--username",
    default="ubuntu",
    help="Default username",
)
def conn_cmd(stand: str | None, username: str) -> None:
    logger = ClickLogger()
    infra = libvirt_infra.LibvirtInfraDriver()
    stands = infra.list_stands()

    if len(stands) == 0:
        logger.warn("No genesis stands found")
        return

    if len(stands) > 1 and stand is None:
        logger.warn("Multiple genesis stands found, please specify one")
        return

    # If the stand is not specified, use the first one
    for dev_stand in stands:
        if stand is None:
            break

        if dev_stand.name == stand:
            break
    else:
        raise click.UsageError("No genesis stand found")

    if dev_stand.network.dhcp:
        ip_address = libvirt.get_domain_ip(dev_stand.bootstraps[0].name)
    else:
        ip_address = dev_stand.network.cidr[2]

    os.system(f"ssh {username}@{ip_address}")


@main.command("ps", help="List of running genesis installation")
def ps_cmd() -> None:
    table = prettytable.PrettyTable()
    table.field_names = [
        "name",
        "nodes",
        "IP",
    ]

    infra = libvirt_infra.LibvirtInfraDriver()

    for stand in infra.list_stands():
        if stand.network.dhcp:
            ip = libvirt.get_domain_ip(stand.bootstraps[0].name)
        else:
            ip = stand.network.cidr[2]

        nodes = len(stand.bootstraps) + len(stand.baremetals)
        table.add_row([stand.name, nodes, ip])

    click.echo("Genesis installations:")
    click.echo(table)


@main.command("delete", help="Delete the genesis stand/element")
@click.argument("name", type=str)
def delete_cmd(name: str) -> None:
    infra = libvirt_infra.LibvirtInfraDriver()

    # Check if the target stand already exists
    for stand in infra.list_stands():
        if stand.name == name:
            break
    else:
        raise click.UsageError(f"Stand {name} not found")

    infra.delete_stand(stand)


@main.command("get-version", help="Return the version of the project")
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
        raise click.UsageError(
            "Invalid '--start' format. Use HH:MM:SS, e.g., 16:00:00"
        )


@main.command("backup", help="Backup the current installation")
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
        domains = _domains_for_backup(
            name, exclude_name, raise_on_domain_absence=True
        )
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
            "Next backup at: "
            f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))}"
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
                "The '--start' option requires the period to be at "
                "least 1 day (1d)."
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


@main.command("backup-decrypt", help="Decrypt a backup file")
@click.argument("path", type=click.Path(exists=True))
def bakcup_decrypt_cmd(path: str) -> None:
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
            if not any(
                fnmatch.fnmatch(d, pattern) for pattern in exclude_names
            )
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
    use_image_inplace: bool,
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
        use_image_inplace=use_image_inplace,
        cores=cores,
        memory=memory,
        network=default_stand_network,
        bootstrap_name=bootstrap_domain_name,
    )

    if not dev_stand.is_valid():
        logger.error(f"Invalid stand for element")
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


def _bootstrap_core(
    image_path: tp.Optional[str],
    cores: int,
    memory: int,
    name: str,
    stand_spec: tp.Dict[str, tp.Any] | None,
    bridge: str | None,
    force: bool,
    use_image_inplace: bool,
) -> None:
    logger = ClickLogger()
    logger.info("Starting genesis bootstrap in 'core' mode")

    net_name = utils.installation_net_name(name)
    default_stand_network = stand_models.Network(
        name=bridge if bridge else net_name,
        cidr=ipaddress.IPv4Network(GC_CIDR),
        managed_network=False if bridge else True,
    )

    # Single bootstrap stand
    if stand_spec is None:
        bootstrap_domain_name = utils.installation_bootstrap_name(name)

        dev_stand = stand_models.Stand.single_bootstrap_stand(
            name=name,
            image=image_path,
            use_image_inplace=use_image_inplace,
            cores=cores,
            memory=memory,
            network=default_stand_network,
            bootstrap_name=bootstrap_domain_name,
        )
    else:
        dev_stand = stand_models.Stand.from_spec(stand_spec)
        if dev_stand.network.is_dummy:
            dev_stand.network = default_stand_network

        # Assign the image to bootstraps if it wasn't specified
        # in the specification.
        for b in dev_stand.bootstraps:
            if b.image is None:
                b.image = image_path
                b.use_image_inplace = use_image_inplace

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

    infra.create_stand(dev_stand)
    logger.info("Launched genesis installation")

    cidr = dev_stand.network.cidr
    logger.important(
        f"The stand {name} will be ready " f"soon at:\nssh ubuntu@{cidr[2]}",
    )
