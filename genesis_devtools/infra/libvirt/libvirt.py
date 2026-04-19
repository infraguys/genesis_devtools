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

import json
import os
import re
import tempfile
import itertools
import subprocess
import ipaddress
import typing as tp
import uuid as sys_uuid
from xml.etree import ElementTree as ET

from genesis_devtools.stand import models
from genesis_devtools import constants as c
from genesis_devtools.infra.libvirt import constants as vc

CONFIG_DRIVES_DIR = "/var/lib/genesis/config-drives"

domain_template = """
<domain type="kvm">
  <name>{name}</name>
  <uuid>{uuid}</uuid>
  <metadata>
    <genesis:genesis xmlns:genesis="https://github.com/infraguys">
      {meta_tags}
    </genesis:genesis>
  </metadata>
  <memory>{memory}</memory>
  <currentMemory>{memory}</currentMemory>
  <vcpu>{cores}</vcpu>
  <os>
    <type arch="x86_64" machine="q35">hvm</type>
    <loader readonly="yes" type="pflash">/usr/share/OVMF/OVMF_CODE_4M.fd</loader>
    <nvram template="/usr/share/OVMF/OVMF_VARS_4M.fd"/>
    {boot}
  </os>
  <features>
    <acpi/>
    <apic/>
    <vmport state="off"/>
  </features>
  <cpu mode="host-passthrough"/>
  <clock offset="utc">
    <timer name="rtc" tickpolicy="catchup"/>
    <timer name="pit" tickpolicy="delay"/>
    <timer name="hpet" present="no"/>
  </clock>
  <pm>
    <suspend-to-mem enabled="no"/>
    <suspend-to-disk enabled="no"/>
  </pm>
  <devices>
    <emulator>/usr/bin/qemu-system-x86_64</emulator>
    {disks}
    <controller type="usb" model="qemu-xhci" ports="5"/>
    <controller type="pci" model="pcie-root"/>
    <!-- For hotplug devices -->
    <controller type="pci" model="pcie-root-port"/>
    <controller type="pci" model="pcie-root-port"/>
    <controller type="pci" model="pcie-root-port"/>
    <controller type="pci" model="pcie-root-port"/>
    <controller type="pci" model="pcie-root-port"/>
    <controller type="pci" model="pcie-root-port"/>
    <controller type="pci" model="pcie-root-port"/>
    <controller type="pci" model="pcie-root-port"/>
    <controller type="pci" model="pcie-root-port"/>
    {net_ifaces}
    <console type="pty"/>
    <channel type="unix">
      <source mode="bind"/>
      <target type="virtio" name="org.qemu.guest_agent.0"/>
    </channel>
    <channel type="spicevmc">
      <target type="virtio" name="com.redhat.spice.0"/>
    </channel>
    <input type="tablet" bus="usb"/>
    <graphics type="spice" port="-1" tlsPort="-1" autoport="yes">
      <image compression="off"/>
    </graphics>
    <video>
      <model type="qxl"/>
    </video>
    <redirdev bus="usb" type="spicevmc"/>
    <memballoon model="virtio"/>
    <rng model="virtio">
      <backend model="random">/dev/urandom</backend>
    </rng>
  </devices>
</domain>
"""


nat_network_template = """
<network>
  <name>{name}</name>
  <forward mode="nat"/>
  <domain name="{name}"/>
  <ip address="{ip}" netmask="{netmask}">
    <dhcp>
      <range start="{range_start}" end="{range_end}"/>
    </dhcp>
  </ip>
</network>
"""


nat_network_no_dhcp_template = """
<network>
  <name>{name}</name>
  <forward mode="nat"/>
  <domain name="network"/>
  <ip address="{ip}" netmask="{netmask}"/>
</network>
"""


isolated_network_no_dhcp_template = """
<network>
  <name>{name}</name>
  <domain name="{name}"/>
</network>
"""


network_iface_template = """
    <interface type="network">
      <source network="{network}"/>
      <mac address="{mac}"/>
      <model type="virtio"/>
    </interface>
"""


bridge_iface_template = """
    <interface type="bridge">
      <source bridge="{network}"/>
      <mac address="{mac}"/>
      <model type="virtio"/>
    </interface>
"""

disk_file_template = """
    <disk type="file" device="disk">
      <driver name="qemu" type="qcow2"/>
      <source file="{image}"/>
      <target dev="{device}" bus="virtio"/>
    </disk>
"""

disk_zfs_dev_template = """
    <disk type="block" device="disk">
      <driver name="qemu" type="raw" discard="unmap"/>
      <source dev="{image}"/>
      <target dev="{device}" bus="virtio"/>
    </disk>
"""

cdrom_template = """
    <disk type="file" device="cdrom">
      <driver name="qemu" type="raw"/>
      <source file="{config_drive_path}"/>
      <target dev="sda" bus="sata"/>
      <readonly/>
    </disk>
"""


def list_domains(
    meta_tag: str | None = None, state: c.DomainState = "all"
) -> tp.List[str]:
    """List all domains."""
    out = subprocess.check_output(["sudo", "virsh", "list", f"--{state}", "--name"])
    out = out.decode().strip()
    names = [o for o in out.split("\n") if o]

    if not meta_tag:
        return names

    # FIXME(akremenetsky): Need more optimization here
    # Find all domains with the corresponding meta tag
    domains = []
    for name in names:
        out = subprocess.check_output(["sudo", "virsh", "dumpxml", name])
        out = out.decode().strip()
        if meta_tag in out:
            domains.append(name)

    return domains


def list_xml_domains(
    meta_tag: str | None = None, state: c.DomainState = "all"
) -> tp.List[str]:
    """List all domains."""
    out = subprocess.check_output(["sudo", "virsh", "list", f"--{state}", "--name"])
    out = out.decode().strip()
    names = [o for o in out.split("\n") if o]

    # FIXME(akremenetsky): Need more optimization here
    # Find all domains with the corresponding meta tag
    domains = []
    for name in names:
        out = subprocess.check_output(["sudo", "virsh", "dumpxml", name])
        out = out.decode().strip()
        if meta_tag and meta_tag in out:
            domains.append(out)
        elif not meta_tag:
            domains.append(out)

    return domains


def is_active_domain(name: str) -> bool:
    return name not in list_domains(state="inactive")


def list_nets():
    """List all networks."""
    out = subprocess.check_output(["sudo", "virsh", "net-list", "--all", "--name"])
    out = out.decode().strip()
    return out.split("\n")


def list_pool():
    """List all pools."""
    out = subprocess.check_output(["sudo", "virsh", "pool-list", "--all", "--name"])
    out = out.decode().strip()
    return out.split("\n")


def define_network(name: str, net_xml: str):
    with tempfile.TemporaryDirectory() as temp_dir:
        network_path = os.path.join(temp_dir, f"{name}.xml")
        with open(network_path, "w") as f:
            f.write(net_xml)

        subprocess.check_call(
            ["sudo", "virsh", "net-define", network_path],
            stdout=subprocess.DEVNULL,
        )
        subprocess.check_call(
            ["sudo", "virsh", "net-start", name],
            stdout=subprocess.DEVNULL,
        )
        subprocess.check_call(
            ["sudo", "virsh", "net-autostart", name],
            stdout=subprocess.DEVNULL,
        )


def create_nat_network(
    name: str, cidr: ipaddress.IPv4Network, dhcp_enabled: bool = True
):
    net_params = {
        "name": name,
        "netmask": str(cidr.netmask),
        "ip": str(cidr[1]),
        "range_start": str(cidr[10]),
        "range_end": str(cidr[100]),
    }

    if dhcp_enabled:
        network = nat_network_template.format(**net_params)
    else:
        network = nat_network_no_dhcp_template.format(**net_params)

    define_network(name, network)


def create_isolated_network(name: str):
    net_params = {"name": name}
    network = isolated_network_no_dhcp_template.format(**net_params)
    define_network(name, network)


def create_domain(
    uuid: sys_uuid.UUID,
    name: str,
    cores: str,
    memory: int,
    networks: tp.Collection[models.Network],
    ports: tp.Collection[models.Port],
    pool: str,
    image: str | None = None,
    disks: tp.Collection[models.Disk] = (),
    meta_tags: tp.Collection[str] = (),
    boot: vc.BootMode = "hd",
    config_drive: str | None = None,
    start: bool = True,
):
    disks_xml = ""
    ifaces_xml = ""
    disk_paths = []
    index = 0

    if not disks:
        raise ValueError("At least one disk must be provided")

    pool_info = get_pool_info(pool)
    pool_path = pool_info["path"]
    img_format, img_suffix, disk_template = (
        ("qcow2", ".qcow2", disk_file_template)
        if pool_info["type"] == "dir"
        else ("raw", "", disk_zfs_dev_template)
    )

    # Use image if it is provided or create empty disk if it is not
    if image is not None:
        image_name = f"{disks[0].uuid(uuid)}{img_suffix}"
        tgt_image_path = os.path.join(pool_path, image_name)
        delete_volume(pool, image_name)
        create_volume(
            pool, image_name, disks[0].size, source_path=image, fmt=img_format
        )
        disks_xml = disk_template.format(
            device="vda",
            image=tgt_image_path,
        )
        index += 1

    for i, disk in enumerate(disks[index:], index):
        disk_name = f"{disk.uuid(uuid)}{img_suffix}"
        disk_path = os.path.join(pool_path, disk_name)
        disk_paths.append(disk_path)
        create_volume(pool, disk_name, disk.size, fmt=img_format)
        disks_xml += disk_template.format(
            device=f"vd{chr(ord('a') + i)}",
            image=disk_path,
        )

    for network, port in itertools.zip_longest(networks, ports):
        if not network:
            continue

        mac = port.mac if port else models.Port.gen_mac()
        if network.managed_network:
            network_iface = network_iface_template.format(network=network.name, mac=mac)
        else:
            network_iface = bridge_iface_template.format(network=network.name, mac=mac)
        ifaces_xml += network_iface

    meta_tags_xml = "\n\t\t".join(tag for tag in meta_tags)

    if boot == "hd":
        boot = f'<boot dev="{boot}"/>'
    else:
        boot = '<boot dev="network"/><boot dev="hd"/>'

    # Copy config drive
    if config_drive is not None:
        subprocess.check_call(
            ["sudo", "mkdir", "-p", CONFIG_DRIVES_DIR],
            stdout=subprocess.DEVNULL,
        )
        config_drive_path = os.path.join(CONFIG_DRIVES_DIR, f"{name}-config-drive.iso")
        subprocess.check_call(
            ["sudo", "cp", config_drive, config_drive_path],
            stdout=subprocess.DEVNULL,
        )
        disks_xml += cdrom_template.format(
            config_drive_path=config_drive_path,
        )

    memory <<= 10
    domain = domain_template.format(
        name=name,
        cores=cores,
        memory=memory,
        net_ifaces=ifaces_xml,
        disks=disks_xml,
        uuid=uuid,
        meta_tags=meta_tags_xml,
        boot=boot,
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        domain_path = os.path.join(temp_dir, f"{name}.xml")
        with open(domain_path, "w") as f:
            f.write(domain)

        try:
            subprocess.check_call(
                ["sudo", "virsh", "define", domain_path],
                stdout=subprocess.DEVNULL,
            )
            subprocess.check_call(
                ["sudo", "virsh", "autostart", name],
                stdout=subprocess.DEVNULL,
            )
            if start:
                subprocess.check_call(
                    ["sudo", "virsh", "start", name],
                    stdout=subprocess.DEVNULL,
                )
        except Exception:
            # Unable to create domain, delete disks
            for disk_path in disk_paths:
                subprocess.check_call(["sudo", "rm", "-f", disk_path])


def get_domain_ip(name: str) -> tp.Optional[str]:
    out = subprocess.check_output(["sudo", "virsh", "dumpxml", name])
    out = out.decode().strip()

    mac_addresses = re.findall(r"<mac address='(.*?)'", out)
    networs = re.findall(r"<source network='(.*?)'", out)
    # Instance without network interfaces ?
    if not mac_addresses:
        return

    # Actually it's not right solution but for simplicity keep it.
    for mac, net in zip(mac_addresses, networs):
        out = subprocess.check_output(
            ["sudo", "virsh", "net-dhcp-leases", net],
        )
        out = out.decode().strip()
        for line in out.split("\n"):
            if mac in line:
                return re.findall(r"\d+\.\d+\.\d+\.\d+", line)[0]


def get_domain_disk(name: str) -> str | None:
    out = subprocess.check_output(["sudo", "virsh", "dumpxml", name])
    out = out.decode().strip()

    # The simplest implementation, take first disk
    if disks := re.findall(r"<source file='(.*?)'", out):
        return disks[0]


def get_domain_disks(name: str) -> tp.List[str]:
    out = subprocess.check_output(["sudo", "virsh", "dumpxml", name])
    out = out.decode().strip()

    # The simplest implementation, take first disk
    return re.findall(r"<source file='(.*?)'", out)


def has_domain(name: str) -> bool:
    return name in list_domains()


def has_net(name: str) -> bool:
    return name in list_nets()


def destroy_domain(name: str) -> None:
    """Delete domain."""
    domain_disks = get_domain_disks(name)

    if is_active_domain(name):
        try:
            subprocess.check_call(
                ["sudo", "virsh", "destroy", name],
                stdout=subprocess.DEVNULL,
            )
        except subprocess.CalledProcessError:
            # Nothing to do, the domain is already destroyed
            pass

    try:
        subprocess.run(
            ["sudo", "virsh", "undefine", "--nvram", "--remove-all-storage", name],
            stdout=subprocess.DEVNULL,
            check=True,
        )
    except subprocess.CalledProcessError:
        # Nothing to do, the domain is already undefined
        pass

    # Remove leftover disks not managed by a pool (e.g. config drive ISOs)
    for disk_path in domain_disks:
        subprocess.check_call(
            ["sudo", "rm", "-f", disk_path],
            stdout=subprocess.DEVNULL,
        )


def destroy_net(name: str) -> None:
    """Delete network."""
    try:
        subprocess.check_call(
            ["sudo", "virsh", "net-destroy", name],
            stdout=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        # Nothing to do, the network is already destroyed
        pass

    try:
        subprocess.check_call(
            ["sudo", "virsh", "net-undefine", name],
            stdout=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        # Nothing to do, the network is already undefined
        pass


def domain_xml(name: str) -> str:
    out = subprocess.check_output(["sudo", "virsh", "dumpxml", name])
    return out.decode().strip()


def backup_domain(name: str, backup_path: str) -> None:
    disks = get_domain_disks(name)

    # Save domain xml
    out = subprocess.check_output(["sudo", "virsh", "dumpxml", name])
    out = out.decode().strip()

    with open(os.path.join(backup_path, "domain.xml"), "w") as f:
        f.write(out)

    # Not active domain
    if not is_active_domain(name):
        for disk in disks:
            disk_name = os.path.basename(disk)
            backup_disk_path = os.path.join(backup_path, disk_name)
            subprocess.check_call(["sudo", "cp", disk, backup_disk_path])
        return

    # Active domain
    try:
        subprocess.check_call(
            ["sudo", "virsh", "suspend", name],
            stdout=subprocess.DEVNULL,
        )

        for disk in disks:
            disk_name = os.path.basename(disk)
            backup_disk_path = os.path.join(backup_path, disk_name)
            subprocess.check_call(["sudo", "cp", disk, backup_disk_path])

    finally:
        subprocess.check_call(
            ["sudo", "virsh", "resume", name],
            stdout=subprocess.DEVNULL,
        )


def create_snapshot(domain: str, snap_name: str = "snapshot") -> None:
    # Create a snapshot
    subprocess.check_call(
        [
            "sudo",
            "virsh",
            "snapshot-create-as",
            domain,
            snap_name,
            "--disk-only",
            "--quiesce",
            "--atomic",
        ],
        stdout=subprocess.DEVNULL,
    )


def delete_snapshot(domain: str, snap_name: str = "snapshot") -> None:
    subprocess.check_call(
        [
            "sudo",
            "virsh",
            "snapshot-delete",
            domain,
            snap_name,
            "--metadata",
        ],
        stdout=subprocess.DEVNULL,
    )


def merge_disk_snapshot(
    domain: str, device: str, disk_path: str, snapshot_path: str
) -> None:
    subprocess.check_call(
        [
            "sudo",
            "virsh",
            "blockcommit",
            "--domain",
            domain,
            device,
            "--top",
            snapshot_path,
            "--base",
            disk_path,
            "--wait",
            "--pivot",
        ],
        stdout=subprocess.DEVNULL,
    )


def resume_domain(name: str) -> None:
    subprocess.check_call(
        ["sudo", "virsh", "resume", name],
        stdout=subprocess.DEVNULL,
    )


def get_pool_info(pool: str) -> dict[str, int | str]:
    out = subprocess.check_output(["sudo", "virsh", "pool-dumpxml", pool])
    xml_str = out.decode().strip()
    xml = ET.fromstring(xml_str)

    def _find_int(tag: str) -> int:
        elem = xml.find(tag)
        if elem is None or elem.text is None:
            raise ValueError(f"Unable to find '{tag}' in pool xml")
        return int(elem.text)

    path_elem = xml.find("./target/path")
    if path_elem is None or path_elem.text is None:
        raise ValueError("Unable to find 'target/path' in pool xml")

    return {
        "capacity": _find_int("capacity"),
        "allocation": _find_int("allocation"),
        "available": _find_int("available"),
        "path": path_elem.text,
        "type": xml.get("type"),
    }


def _get_vol_path(pool: str, name: str) -> str:
    out = subprocess.check_output(["sudo", "virsh", "vol-path", "--pool", pool, name])
    return out.decode().strip()


def _get_image_format(path: str) -> str:
    out = subprocess.check_output(["sudo", "qemu-img", "info", "--output=json", path])
    info = json.loads(out.decode().strip())
    return info["format"]


def create_volume(
    pool: str,
    name: str,
    size_gb: int,
    fmt: str = "qcow2",
    source_path: str | None = None,
) -> None:
    args = [
        "sudo",
        "virsh",
        "vol-create-as",
        pool,
        name,
        f"{size_gb}G",
        "--allocation",
        "0",
        "--format",
        fmt,
    ]
    subprocess.check_call(args, stdout=subprocess.DEVNULL)

    if source_path is not None:
        if fmt == "raw":
            # vol-upload copies raw bytes without format conversion,
            # so we must use qemu-img convert to handle any source format.
            vol_path = _get_vol_path(pool, name)
            src_fmt = _get_image_format(source_path)
            subprocess.check_call(
                [
                    "sudo",
                    "qemu-img",
                    "convert",
                    "-f",
                    src_fmt,
                    "-O",
                    "raw",
                    source_path,
                    vol_path,
                ],
                stdout=subprocess.DEVNULL,
            )
        else:
            subprocess.check_call(
                ["sudo", "virsh", "vol-upload", "--pool", pool, name, source_path],
                stdout=subprocess.DEVNULL,
            )


def update_volume(
    pool: str,
    name: str,
    size_gb: int | None = None,
    source_path: str | None = None,
) -> None:
    if size_gb is not None:
        subprocess.check_call(
            ["sudo", "virsh", "vol-resize", "--pool", pool, name, f"{size_gb}G"],
            stdout=subprocess.DEVNULL,
        )

    if source_path is not None:
        subprocess.check_call(
            ["sudo", "virsh", "vol-upload", "--pool", pool, name, source_path],
            stdout=subprocess.DEVNULL,
        )


def delete_volume(pool: str, name: str) -> None:
    try:
        subprocess.check_call(
            ["sudo", "virsh", "vol-delete", "--pool", pool, name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        pass
