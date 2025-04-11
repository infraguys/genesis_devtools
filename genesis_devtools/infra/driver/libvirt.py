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

import itertools
import ipaddress
import typing as tp
from xml.dom import minidom

from genesis_devtools.stand import models

from genesis_devtools.infra.driver import base
from genesis_devtools.infra.libvirt import libvirt
from genesis_devtools.infra.libvirt import constants as vc


def _get_tag_value(xml: minidom.Document, tag: str) -> str | None:
    try:
        return xml.getElementsByTagName(tag)[0].firstChild.nodeValue
    except Exception:
        return None


class LibvirtInfraDriver(base.AbstractInfraDriver):
    def __init__(self, spec: tp.Dict[str, tp.Any] | None = None) -> None:
        self._spec = spec

    def _domain2node(self, domain: minidom.Document) -> models.Node:
        cores = int(_get_tag_value(domain, vc.GENESIS_META_CPU_TAG))
        ram = int(_get_tag_value(domain, vc.GENESIS_META_MEM_TAG))
        name = _get_tag_value(domain, "name")
        image = _get_tag_value(domain, vc.GENESIS_META_IMAGE_TAG)

        return models.Node(
            name=name,
            cores=cores,
            memory=ram,
            image=image,
            # TODO(akremenetsky): Add implementation for disks
            disks=[],
        )

    def _extract_net_from_bootstrap(
        self, bootstrap: minidom.Document
    ) -> models.Network:
        net = bootstrap.getElementsByTagName(vc.GENESIS_META_NET_TAG)[0]
        name = net.firstChild.nodeValue
        cidr = ipaddress.IPv4Network(net.getAttribute("cidr"))
        managed_network = bool(int(net.getAttribute("managed_network")))
        dhcp = bool(int(net.getAttribute("dhcp")))
        return models.Network(
            name=name, cidr=cidr, managed_network=managed_network, dhcp=dhcp
        )

    def _domain2bootstrap(self, domain: minidom.Document) -> models.Bootstrap:
        node = self._domain2node(domain)
        return models.Bootstrap.from_node(node)

    def _tag(
        self,
        tag: str,
        value: str | None = None,
        fields: tp.Dict[str, tp.Any] | None = None,
    ) -> str:
        fields = fields or {}
        fields_str = " ".join(f'{k}="{str(v)}"' for k, v in fields.items())
        if value is None:
            return f"<{tag} {fields_str} />"

        return f"<{tag} {fields_str} >{value}</{tag}>"

    def list_stands(self) -> tp.List[models.Stand]:
        """List stands for the current connection."""
        # NOTE(akremenetsky): Only single bootstrap stands
        # are supported for now

        stands = {}
        for d in libvirt.list_xml_domains():
            domain = minidom.parseString(d)
            stand_name = _get_tag_value(domain, vc.GENESIS_META_STAND_TAG)

            # Unable to determine the stand name.
            # It may be a payload (VM) or user machine. Just ignore it.
            if stand_name is None:
                continue

            stand: models.Stand = stands.setdefault(
                stand_name, models.Stand.empty_stand(stand_name)
            )

            node_type = _get_tag_value(domain, vc.GENESIS_META_NODE_TYPE_TAG)

            if node_type == "bootstrap":
                stand.bootstraps.append(self._domain2bootstrap(domain))
                stand.network = self._extract_net_from_bootstrap(domain)
            elif node_type == "baremetal":
                stand.baremetals.append(self._domain2node(domain))
            else:
                raise NotImplementedError(f"Unknown node type: {node_type}")

        return list(stands.values())

    def create_stand(self, stand: models.Stand) -> models.Stand:
        """Create a new stand."""
        if len(stand.bootstraps) > 1:
            raise NotImplementedError(
                "Multiple bootstraps are not supported yet"
            )

        if not stand.is_valid():
            raise ValueError(f"Stand {stand} is invalid!")

        if any(
            libvirt.has_domain(n.name)
            for n in itertools.chain(stand.bootstraps, stand.baremetals)
        ):
            raise ValueError(f"Some domain in stand {stand} already exists")

        if stand.network.managed_network and libvirt.has_net(stand.network):
            raise ValueError(f"Network {stand.network} already exists")

        if stand.network.managed_network:
            libvirt.create_nat_network(
                name=stand.network.name,
                cidr=stand.network.cidr,
                dhcp_enabled=stand.network.dhcp,
            )

        # Create bootstraps first and set metadata about network in the
        # boostarp domains.
        for bootstrap in stand.bootstraps:
            tags = (
                self._tag(vc.GENESIS_META_STAND_TAG, stand.name),
                self._tag(vc.GENESIS_META_CPU_TAG, bootstrap.cores),
                self._tag(vc.GENESIS_META_MEM_TAG, bootstrap.memory),
                self._tag(vc.GENESIS_META_IMAGE_TAG, bootstrap.image),
                self._tag(vc.GENESIS_META_NODE_TYPE_TAG, "bootstrap"),
                self._tag(
                    vc.GENESIS_META_NET_TAG,
                    stand.network.name,
                    {
                        "cidr": str(stand.network.cidr),
                        "managed_network": int(stand.network.managed_network),
                        "dhcp": int(stand.network.dhcp),
                    },
                ),
            )

            libvirt.create_domain(
                name=bootstrap.name,
                image=bootstrap.image,
                cores=bootstrap.cores,
                memory=bootstrap.memory,
                network=stand.network.name,
                net_type=(
                    "network" if stand.network.managed_network else "bridge"
                ),
                meta_tags=tags,
            )

        for node in stand.baremetals:
            tags = (
                self._tag(vc.GENESIS_META_STAND_TAG, stand.name),
                self._tag(vc.GENESIS_META_CPU_TAG, node.cores),
                self._tag(vc.GENESIS_META_MEM_TAG, node.memory),
                self._tag(vc.GENESIS_META_NODE_TYPE_TAG, "baremetal"),
            )

            # TODO(akremenetsky): Remove bootstrap nodes
            # if something goes wrong
            libvirt.create_domain(
                name=node.name,
                image=node.image,
                cores=node.cores,
                memory=node.memory,
                network=stand.network.name,
                net_type=(
                    "network" if stand.network.managed_network else "bridge"
                ),
                meta_tags=tags,
                disks=node.disks,
                boot="network",
            )

    def delete_stand(self, stand: models.Stand) -> None:
        """Delete the stand."""
        for node in itertools.chain(stand.bootstraps, stand.baremetals):
            libvirt.destroy_domain(node.name)

        if stand.network.managed_network:
            libvirt.destroy_net(stand.network.name)
