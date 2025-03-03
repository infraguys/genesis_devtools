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
import typing as tp
import tempfile
import subprocess
import ipaddress

from genesis_devtools import constants as c

domain_template = """
<domain type="kvm">
  <name>{name}</name>
  <metadata>
    <genesis:genesis xmlns:genesis="https://github.com/infraguys">
    </genesis:genesis>
  </metadata>
  <memory>{memory}</memory>
  <currentMemory>{memory}</currentMemory>
  <vcpu>{cores}</vcpu>
  <os>
    <type arch="x86_64" machine="q35">hvm</type>
    <boot dev="hd"/>
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
    <disk type="file" device="disk">
      <driver name="qemu" type="raw"/>
      <source file="{image}"/>
      <target dev="vda" bus="virtio"/>
    </disk>
    <controller type="usb" model="qemu-xhci" ports="5"/>
    <controller type="pci" model="pcie-root"/>
    <controller type="pci" model="pcie-root-port"/>
    {net_iface}
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


def list_domains(meta_tag: str | None = None):
    """List all domains."""
    out = subprocess.check_output("sudo virsh list --all --name", shell=True)
    out = out.decode().strip()
    names = out.split("\n")

    if not meta_tag:
        return names

    # FIXME(akremenetsky): Need more optimization here
    # Find all domains with the corresponding meta tag
    domains = []
    for name in names:
        out = subprocess.check_output(f"sudo virsh dumpxml {name}", shell=True)
        out = out.decode().strip()
        if meta_tag in out:
            domains.append(name)

    return domains


def list_nets():
    """List all networks."""
    out = subprocess.check_output(
        "sudo virsh net-list --all --name", shell=True
    )
    out = out.decode().strip()
    return out.split("\n")


def list_pool():
    """List all pools."""
    out = subprocess.check_output(
        "sudo virsh pool-list --all --name", shell=True
    )
    out = out.decode().strip()
    return out.split("\n")


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

    with tempfile.TemporaryDirectory() as temp_dir:
        network_path = os.path.join(temp_dir, f"{name}.xml")
        with open(network_path, "w") as f:
            f.write(network)

        subprocess.run(
            f"sudo virsh net-define {network_path} 1>/dev/null",
            shell=True,
            check=True,
        )
        subprocess.run(
            f"sudo virsh net-start {name} 1>/dev/null", shell=True, check=True
        )
        subprocess.run(
            f"sudo virsh net-autostart {name} 1>/dev/null",
            shell=True,
            check=True,
        )


def create_domain(
    name: str,
    cores: str,
    memory: int,
    image: str,
    network: str,
    net_type: str = "network",
    pool: str = c.LIBVIRT_DEF_POOL_PATH,
):
    # Copy the image to a pool
    image_name = os.path.basename(image)
    pool_image_path = os.path.join(pool, image_name)

    # TODO: Need default user pool
    if not os.path.exists(pool_image_path):
        subprocess.run(
            f"sudo rm -f {pool_image_path}; sudo cp {image} {pool_image_path}",
            shell=True,
            check=True,
        )

    if net_type == "network":
        network_iface = network_iface_template.format(network=network)
    else:
        network_iface = bridge_iface_template.format(network=network)

    domain = domain_template.format(
        name=name,
        cores=cores,
        memory=memory,
        image=pool_image_path,
        net_iface=network_iface,
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        domain_path = os.path.join(temp_dir, f"{name}.xml")
        with open(domain_path, "w") as f:
            f.write(domain)

        subprocess.run(
            f"sudo virsh define {domain_path} 1>/dev/null",
            shell=True,
            check=True,
        )
        subprocess.run(
            f"sudo virsh start {name} 1>/dev/null", shell=True, check=True
        )


def get_domain_ip(name: str) -> tp.Optional[str]:
    out = subprocess.check_output(f"sudo virsh dumpxml {name}", shell=True)
    out = out.decode().strip()

    mac_addresses = re.findall(r"<mac address='(.*?)'", out)
    networs = re.findall(r"<source network='(.*?)'", out)
    # Instance without network interfaces ?
    if not mac_addresses:
        return

    # Actually it's not right solution but for simplicity keep it.
    for mac, net in zip(mac_addresses, networs):
        out = subprocess.check_output(
            f"sudo virsh net-dhcp-leases {net}",
            shell=True,
        )
        out = out.decode().strip()
        for line in out.split("\n"):
            if mac in line:
                return re.findall(r"\d+\.\d+\.\d+\.\d+", line)[0]


def get_domain_disk(name: str) -> tp.Optional[str]:
    out = subprocess.check_output(f"sudo virsh dumpxml {name}", shell=True)
    out = out.decode().strip()

    # The simplest implementation, take first disk
    if disks := re.findall(r"<source file='(.*?)'", out):
        return disks[0]


def has_domain(name: str) -> bool:
    return name in list_domains()


def has_net(name: str) -> bool:
    return name in list_nets()


def destroy_domain(name: str) -> None:
    """Delete domain."""
    disk_path = get_domain_disk(name)

    try:
        subprocess.run(
            f"sudo virsh destroy {name} 1>/dev/null",
            shell=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        # Nothing to do, the domain is already destroyed
        pass

    try:
        subprocess.run(
            f"sudo virsh undefine {name} 1>/dev/null",
            shell=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        # Nothing to do, the domain is already undefined
        pass

    # Remove the disk
    if disk_path:
        subprocess.run(
            f"sudo rm -f {disk_path} 1>/dev/null", shell=True, check=True
        )


def destroy_net(name: str) -> None:
    """Delete network."""
    try:
        subprocess.run(
            f"sudo virsh net-destroy {name} 1>/dev/null",
            shell=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        # Nothing to do, the network is already destroyed
        pass

    try:
        subprocess.run(
            f"sudo virsh net-undefine {name} 1>/dev/null",
            shell=True,
            check=True,
        )
    except subprocess.CalledProcessError:
        # Nothing to do, the network is already undefined
        pass
