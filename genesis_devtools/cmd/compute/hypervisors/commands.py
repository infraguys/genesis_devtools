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
import typing as tp

import rich_click as click
from genesis_devtools.common.table import get_table, print_table, show_data

from genesis_devtools.logger import ClickLogger
from genesis_devtools.clients import base_client
from genesis_devtools.common.run import runsh, run_command
from genesis_devtools import utils
from genesis_devtools import constants as c

ENTITY = "hypervisor"
ENTITY_COLLECTION = c.HYPERVISOR_COLLECTION


@click.group(f"{ENTITY}s", help=f"Manage {ENTITY}s in the Genesis installation")
def hypervisors_group():
    pass


@hypervisors_group.command("list", help=f"List {ENTITY}s")
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


@hypervisors_group.command("show", help=f"Show {ENTITY}")
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
    data = base_client.get_entity(client, ENTITY_COLLECTION, uuid)
    show_data(data)


@hypervisors_group.command("delete", help=f"Delete {ENTITY}")
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
    base_client.delete_entity(client, ENTITY_COLLECTION, uuid)


def _print_entities(hypervisors: tp.List[dict]) -> None:
    table = get_table()
    table.add_column("UUID")
    table.add_column("Name")
    table.add_column("MachineType")
    table.add_column("All Cores")
    table.add_column("Avail Cores")
    table.add_column("All Ram")
    table.add_column("Avail Ram")
    table.add_column("Status")

    for hypervisor in hypervisors:
        table.add_row(
            hypervisor["uuid"],
            hypervisor["name"],
            hypervisor["machine_type"],
            str(hypervisor["all_cores"]),
            str(hypervisor["avail_cores"]),
            str(hypervisor["all_ram"]),
            str(hypervisor["avail_ram"]),
            hypervisor["status"],
        )

    print_table(table)


def _is_superuser() -> bool:
    """Check if running with superuser privileges."""
    return os.geteuid() == 0


def _install_packages() -> None:
    """Install required Debian packages."""
    packages = [
        "qemu-system-x86",
        "qemu-utils",
        "libvirt-daemon-system",
        "libvirt-dev",
        "genisoimage",
    ]
    cmd = ["apt-get", "update"]
    run_command(cmd)
    cmd = ["apt-get", "install", "-y"]
    cmd.extend(packages)
    run_command(cmd)


def _add_user_to_groups() -> None:
    """Add current user to libvirt and kvm groups."""
    username = os.environ.get("USER")
    if not username:
        raise click.ClickException("Cannot determine current username")
    else:
        click.echo(f"Current username: {username}")

    cmd = ["usermod", "-a", "-G", "libvirt", username]
    run_command(cmd)
    cmd = ["usermod", "-a", "-G", "kvm", username]
    run_command(cmd)


def _create_storage_pool(pool_name: str) -> None:
    """Create libvirt storage pool if it doesn't exist."""
    # Check if pool exists
    result = runsh("virsh pool-list --all").raise_on_result()
    if pool_name not in result.output:
        # Create storage pool
        cmd = [
            "virsh",
            "pool-define-as",
            pool_name,
            "dir",
            "--target",
            "/var/lib/libvirt/images",
        ]
        run_command(cmd)
        cmd = ["virsh", "pool-build", pool_name]
        run_command(cmd)
        cmd = ["virsh", "pool-start", pool_name]
        run_command(cmd)
        cmd = ["virsh", "pool-autostart", pool_name]
        run_command(cmd)


def _download_rom_file(version: str) -> None:
    """Download ROM file if it doesn't exist."""
    rom_filename = "1af41041.rom"
    rom_path = f"/usr/share/qemu/{rom_filename}"
    if not os.path.exists(rom_path):
        runsh(
            f"wget -O {rom_path} https://repository.genesis-core.tech/seed_os/{version}/{rom_filename}"
        ).raise_on_result()

    else:
        click.echo(f"ROM file {rom_path} already exists")


def _configure_libvirt() -> None:
    """Configure libvirt to enable TCP connection."""
    config_file = "/etc/libvirt/libvirtd.conf"

    # Read existing config
    try:
        with open(config_file, "r") as f:
            content = f.read()
    except FileNotFoundError:
        raise click.ClickException(f"Config file not found: {config_file}")

    # Add required lines if not present
    required_lines = ["listen_tcp = 1", 'listen_addr = "0.0.0.0"', 'auth_tcp = "none"']

    for line in required_lines:
        if line not in content:
            content += f"\n{line}"

    # Write back to file
    with open(config_file, "w") as f:
        f.write(content)

    # Restart services
    cmd = ["systemctl", "stop", "libvirtd"]
    run_command(cmd)
    cmd = ["systemctl", "enable", "--now", "libvirtd-tcp.socket"]
    run_command(cmd)
    cmd = ["systemctl", "start", "libvirtd"]
    run_command(cmd)


def _check_debian_like():
    """Check if the OS is Debian-like."""
    try:
        with open("/etc/os-release", "r") as f:
            content = f.read()
            if "Debian" in content or "Ubuntu" in content or "Kali" in content:
                return True
    except FileNotFoundError:
        pass

    try:
        with open("/etc/debian_version", "r") as f:
            f.read()
            return True
    except FileNotFoundError:
        pass

    return False


def _install_packer() -> None:
    """Install packer."""

    try:
        run_command(["which", "packer"])
        click.echo("Packer is already installed")
        return None
    except Exception:
        pass

    cmd = ["mkdir", "-p", "/opt/packer"]
    run_command(cmd)
    # Version 1.9.2 is the latest free
    cmd = [
        "wget",
        "https://hashicorp-releases.yandexcloud.net/packer/1.9.2/packer_1.9.2_linux_amd64.zip",
        "-P",
        "/opt/packer",
    ]
    run_command(cmd)
    cmd = ["unzip", "/opt/packer/packer_1.9.2_linux_amd64.zip", "-d", "/opt/packer"]
    run_command(cmd)
    cmd = ["mv", "/opt/packer/packer", "/usr/local/bin/"]
    run_command(cmd)
    cmd = ["/usr/local/bin/packer", "-version"]
    run_command(cmd)
    return None


@hypervisors_group.command("init", help="Initialize hypervisor")
@click.option(
    "--romfile_version",
    type=str,
    default="latest",
    help="version of the rom file",
)
@click.option(
    "--pool_name",
    type=str,
    default="latest",
    help="storage pool name",
)
@click.option(
    "-p",
    "--packer",
    show_default=True,
    is_flag=True,
    default=False,
    help="Install packer",
)
def init_cmd(romfile_version: str, pool_name: str, packer: bool) -> None:
    """Initialize hypervisor with all required components."""

    if not _check_debian_like():
        raise click.ClickException(
            "This command is only supported on Debian-based systems."
        )

    if not _is_superuser():
        raise click.ClickException(
            "This command requires superuser privileges. Please run with sudo."
        )

    log = ClickLogger()

    log.info("Installing required packages...")
    _install_packages()

    log.info("Adding user to required groups...")
    _add_user_to_groups()

    log.info("Setting up storage pool...")
    _create_storage_pool(pool_name)

    log.info("Checking ROM file...")
    _download_rom_file(romfile_version)

    log.info("Configuring libvirt...")
    _configure_libvirt()

    if packer:
        log.info("Configuring packer...")
        _install_packer()

    log.important("Hypervisor environment initialized successfully")
