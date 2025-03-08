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
import shutil
import typing as tp
import tempfile
import ipaddress

import click
import prettytable

import genesis_devtools.constants as c
from genesis_devtools import utils
from genesis_devtools.logger import ClickLogger
from genesis_devtools.builder.builder import SimpleBuilder
from genesis_devtools.builder.packer import PackerBuilder
from genesis_devtools import libvirt


BOOTSTRAP_TAG = "bootstrap"
LaunchModeType = tp.Literal["core", "element", "custom"]
GC_CIDR = ipaddress.IPv4Network("10.20.0.0/22")


@click.group(invoke_without_command=True)
def main() -> None:
    pass


@main.command("build", help="Build Genesis project")
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
    default=None,
    help="Directory where output artifacts will be stored",
)
@click.option(
    "-i",
    "--developer-key-path",
    default=None,
    help="Path to developer public key",
)
@click.option(
    "-f",
    "--force",
    default=False,
    type=bool,
    show_default=True,
    is_flag=True,
    help="Rebuild if the output already exists",
)
@click.argument("project_dir", type=click.Path())
def build_cmd(
    genesis_cfg_file: str,
    deps_dir: tp.Optional[str],
    build_dir: tp.Optional[str],
    output_dir: tp.Optional[str],
    developer_key_path: tp.Optional[str],
    force: bool,
    project_dir: str,
) -> None:
    if not project_dir:
        raise click.UsageError("No project directories specified")

    output_dir = output_dir or c.DEF_GEN_OUTPUT_DIR_NAME
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
    packer_image_builder = PackerBuilder(output_dir, logger)

    # Path where genesis.yaml configuration file is located
    work_dir = os.path.abspath(
        os.path.join(project_dir, c.DEF_GEN_WORK_DIR_NAME)
    )

    for _, build in builds.items():
        builder = SimpleBuilder.from_config(
            work_dir, build, packer_image_builder, logger
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            builder.fetch_dependency(deps_dir or temp_dir)
            builder.build(build_dir, developer_keys)


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
    "--dhcp",
    default=False,
    type=bool,
    show_default=True,
    is_flag=True,
    help="Enable DHCP on 'network' network type",
)
@click.option(
    "-f",
    "--force",
    default=False,
    type=bool,
    show_default=True,
    is_flag=True,
    help="Rebuild if the output already exists",
)
@click.option(
    "--no-wait",
    default=False,
    type=bool,
    show_default=True,
    is_flag=True,
    help="Cancel waiting for the installation to start",
)
def bootstrap_cmd(
    image_path: tp.Optional[str],
    cores: int,
    memory: int,
    name: str,
    launch_mode: LaunchModeType,
    cidr: ipaddress.IPv4Network,
    bridge: str | None,
    dhcp: bool,
    force: bool,
    no_wait: bool,
) -> None:
    if image_path is None or not os.path.exists(image_path):
        raise click.UsageError("No image path specified or not found")

    if image_path and not os.path.isabs(image_path):
        image_path = os.path.abspath(image_path)

    logger = ClickLogger()

    # Modify network paramters based on the launch mode
    if launch_mode == "element":
        bridge, dhcp = None, True
        logger.info("Starting genesis bootstrap in 'element' mode")
    elif launch_mode == "core":
        bridge, dhcp, cidr = None, False, GC_CIDR
        logger.info("Starting genesis bootstrap in 'core' mode")
    else:
        # Custom launch mode, nothing to do
        logger.info("Starting genesis bootstrap in 'custom' mode")

    # KiB for libvirt
    memory = memory << 10
    net_name = utils.installation_net_name(name)
    bootstrap_domain_name = utils.installation_bootstrap_name(name)

    # Check if the any genesis installation is running
    has_domain = libvirt.has_domain(bootstrap_domain_name)

    # Don't delete the network if it was created by the user
    has_net = False if bridge else libvirt.has_net(net_name)

    if has_domain or has_net:
        if not force:
            logger.warn(
                "Genesis installation is already running. Use '--force' flag to "
                "rerun genesis installation.",
            )
            return

        # Delete old genesis installation
        _delete_installation(name, delete_net=has_net)
        logger.info("Destroyed old genesis installation")

    # The 'bridge' should be created by the user
    if not bridge:
        libvirt.create_nat_network(net_name, cidr, dhcp)

    libvirt.create_domain(
        name=bootstrap_domain_name,
        cores=cores,
        memory=memory,
        image=image_path,
        network=bridge or net_name,
        net_type="bridge" if bridge else "network",
    )
    logger.info("Launched genesis installation. Started VM: " + name)

    # Wait for the installation to start
    if no_wait:
        return

    if not dhcp:
        logger.warn("Unable to detect IP address if DHCP is disabled. Bye.")
        return

    utils.wait_for(
        lambda: bool(libvirt.get_domain_ip(bootstrap_domain_name)),
        title=f"Waiting for installation {name}",
    )

    ip = libvirt.get_domain_ip(bootstrap_domain_name)
    logger.important(f"The installation {name} is ready at:\nssh ubuntu@{ip}")


@main.command("ssh", help="Connect to genesis installation")
@click.option(
    "-i",
    "--ip-address",
    default=None,
    help="IP address of installation",
)
@click.option(
    "-u",
    "--username",
    default="ubuntu",
    help="Default username",
)
def conn_cmd(ip_address: tp.Optional[str], username: str) -> None:
    installations = _list_installations()

    if ip_address is None:
        if len(installations) == 1:
            ip_address = installations[0][1]
        elif len(installations) > 1:
            raise click.UsageError(
                "There are multiple genesis installations. "
                "You must specify IP address of the installation"
            )
        else:
            click.secho("No genesis installation found", fg="yellow")
            return

    os.system(f"ssh {username}@{ip_address}")


@main.command("ps", help="List of running genesis installation")
def ps_cmd() -> None:
    table = prettytable.PrettyTable()
    table.field_names = [
        "name",
        "IP",
    ]

    for name, ip in _list_installations():
        table.add_row([name, ip])

    click.echo("Genesis installations:")
    click.echo(table)


@main.command("delete", help="Delete the genesis installation")
@click.argument("name", type=str)
def delete_cmd(name: str) -> None:
    return _delete_installation(name)


@main.command("get-version", help="Return the version of the project")
@click.argument("element_dir", type=click.Path())
def get_project_version_cmd(element_dir: str) -> None:
    logger = ClickLogger()
    version = utils.get_project_version(element_dir)
    logger.important(version)


def _list_installations() -> tp.List[tp.Tuple[str, str]]:
    installations = []

    # Each bootstrap is a separate installation
    for domain in libvirt.list_domains():
        if BOOTSTRAP_TAG in domain:
            installation = utils.installation_name_from_bootstrap(domain)
            ip = libvirt.get_domain_ip(domain)
            installations.append((installation, str(ip)))
    return installations


def _delete_installation(name: str, delete_net: bool = True) -> None:
    logger = ClickLogger()
    destroyed = False

    net_name = utils.installation_net_name(name)

    # Multiple stands will be supported in the future
    # bootstrap_domain_name = utils.installation_bootstrap_name(name)
    genesis_domains = libvirt.list_domains(c.GENESIS_META_TAG)
    for domain in genesis_domains:
        logger.info(f"Found genesis domain: {domain}")
        libvirt.destroy_domain(domain)
        destroyed = True

    if delete_net and libvirt.has_net(net_name):
        libvirt.destroy_net(net_name)
        destroyed = True

    if not destroyed:
        logger.warn("Genesis installation not found")
        return

    logger.important(f"Destroyed genesis installation: {name}")
