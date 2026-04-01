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

import rich_click as click
from genesis_devtools.common.table import get_table, print_table


from genesis_devtools.infra.driver import libvirt as libvirt_infra
from genesis_devtools.infra.libvirt import libvirt
from genesis_devtools.logger import ClickLogger


@click.group("realms", help="Manage Genesis realms")
def realms_group():
    pass


@realms_group.command("ssh", help="Connect to genesis realm")
@click.option(
    "-r",
    "--realm",
    default=None,
    help="Realm to connect to",
)
@click.option(
    "-u",
    "--username",
    default="ubuntu",
    help="Default username",
)
def ssh_cmd(realm: str | None, username: str) -> None:
    logger = ClickLogger()
    infra = libvirt_infra.LibvirtInfraDriver()
    stands = infra.list_stands()

    if len(stands) == 0:
        logger.warn("No genesis realms found")
        return

    if len(stands) > 1 and realm is None:
        logger.warn("Multiple genesis realms found, please specify one")
        return

    # If the stand is not specified, use the first one
    for dev_stand in stands:
        if realm is None:
            break

        if dev_stand.name == realm:
            break
    else:
        raise click.UsageError("No genesis realm found")

    if dev_stand.network.dhcp:
        ip_address = libvirt.get_domain_ip(dev_stand.bootstraps[0].name)
    else:
        ip_address = dev_stand.network.cidr[2]

    os.system(f"ssh {username}@{ip_address}")


@realms_group.command("list", help="List of running genesis realms")
def list_cmd() -> None:
    table = get_table()
    table.add_column("name")
    table.add_column("nodes")
    table.add_column("IP")

    infra = libvirt_infra.LibvirtInfraDriver()

    for stand in infra.list_stands():
        if stand.network.dhcp:
            ip = libvirt.get_domain_ip(stand.bootstraps[0].name)
        else:
            ip = stand.network.cidr[2]

        nodes = len(stand.bootstraps) + len(stand.baremetals)
        table.add_row(stand.name, str(nodes), str(ip))

    print_table(table)


@realms_group.command("delete", help="Delete the genesis realm")
@click.argument("name", type=str)
def delete_cmd(name: str) -> None:
    infra = libvirt_infra.LibvirtInfraDriver()

    # Check if the target stand already exists
    for stand in infra.list_stands():
        if stand.name == name:
            break
    else:
        raise click.UsageError(f"Realm {name} not found")

    infra.delete_stand(stand)
