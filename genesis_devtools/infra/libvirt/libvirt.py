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
import re
import tempfile
import subprocess
import ipaddress
import typing as tp
import uuid as sys_uuid

from genesis_devtools.stand import models
from genesis_devtools import constants as c
from genesis_devtools.infra.libvirt import constants as vc

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
      <model type="virtio"/>
    </interface>
"""


bridge_iface_template = """
    <interface type="bridge">
      <source bridge="{network}"/>
      <model type="virtio"/>
    </interface>
"""


disk_template = """
    <disk type="file" device="disk">
      <driver name="qemu" type="{image_format}"/>
      <source file="{image}"/>
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
    name: str,
    cores: str,
    memory: int,
    networks: tp.Collection[models.Network],
    pool: str = c.LIBVIRT_DEF_POOL_PATH,
    image: str | None = None,
    use_image_inplace: bool = False,
    disks: tp.Collection[int] = (),
    meta_tags: tp.Collection[str] = (),
    boot: vc.BootMode = "hd",
    config_drive: str | None = None,
):
    uuid = str(sys_uuid.uuid4())
    disks_xml = ""
    ifaces_xml = ""
    disk_paths = []
    index = 0

    if not disks:
        raise ValueError("At least one disk must be provided")

    # Use image if it is provided or create empty disk if it is not
    if image is not None:
        tgt_image_path = os.path.abspath(image)
        image_name = os.path.basename(image)
        image_format = "qcow2" if image_name.endswith("qcow2") else "raw"
        if not use_image_inplace:
            tgt_image_path = os.path.join(pool, image_name)
            # Copy the image to the pool and delete the old one
            subprocess.run(
                ["sudo", "rm", "-f", tgt_image_path],
                check=True,
            )
            subprocess.run(
                ["sudo", "cp", image, tgt_image_path],
                check=True,
            )
        disks_xml = disk_template.format(
            device="vda",
            image=tgt_image_path,
            image_format=image_format,
        )
        index += 1

    for i, disk in enumerate(disks[index:], index):
        disk_name = f"{uuid}-{i}.qcow2"
        disk_path = os.path.join(pool, disk_name)
        disk_paths.append(disk_path)
        subprocess.check_call(
            [
                "sudo",
                "qemu-img",
                "create",
                "-f",
                "qcow2",
                disk_path,
                f"{disk}G",
            ],
            stdout=subprocess.DEVNULL,
        )
        disks_xml += disk_template.format(
            device=f"vd{chr(ord('a') + i)}",
            image=disk_path,
            image_format="qcow2",
        )

    for network in networks:
        if network.managed_network:
            network_iface = network_iface_template.format(network=network.name)
        else:
            network_iface = bridge_iface_template.format(network=network.name)
        ifaces_xml += network_iface

    meta_tags_xml = "\n\t\t".join(tag for tag in meta_tags)

    if boot == "hd":
        boot = f'<boot dev="{boot}"/>'
    else:
        boot = '<boot dev="network"/><boot dev="hd"/>'

    # Copy config drive
    if config_drive is not None:
        config_drive_path = os.path.join(pool, f"{uuid}-config-drive.iso")
        subprocess.run(
            ["sudo", "cp", config_drive, config_drive_path],
            check=True,
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
            ["sudo", "virsh", "undefine", "--nvram", name],
            stdout=subprocess.DEVNULL,
            check=True,
        )
    except subprocess.CalledProcessError:
        # Nothing to do, the domain is already undefined
        pass

    # Remove the disk
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
