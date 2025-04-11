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

import ipaddress
import typing as tp
import dataclasses


@dataclasses.dataclass
class Network:
    name: str
    cidr: ipaddress.IPv4Network
    dhcp: bool = False

    # Is an user's network bridge
    managed_network: bool = True

    @classmethod
    def dummy(cls) -> Network:
        return cls(
            name="dummy",
            cidr=ipaddress.IPv4Network("0.0.0.0/24"),
            managed_network=False,
        )

    @property
    def is_dummy(self) -> bool:
        return self.name == "dummy"

    @classmethod
    def from_spec(cls, spec: tp.Dict[str, tp.Any]) -> Network:
        spec = spec.copy()
        spec["cidr"] = ipaddress.IPv4Network(spec["cidr"])
        return cls(**spec)


@dataclasses.dataclass
class Node:
    name: str = "genesis-node"
    memory: int = 1024
    cores: int = 1
    disks: tp.List[int] = dataclasses.field(default_factory=lambda: [10])
    image: str | None = None

    @classmethod
    def from_spec(cls, spec: tp.Dict[str, tp.Any]) -> Node:
        return cls(**spec)


@dataclasses.dataclass
class Bootstrap(Node):
    name: str = "genesis-bootstrap"

    @classmethod
    def from_node(cls, node: Node) -> Bootstrap:
        return cls(**dataclasses.asdict(node))


@dataclasses.dataclass
class Stand:
    network: Network
    bootstraps: tp.List[Bootstrap]
    baremetals: tp.List[Node]
    name: str = "dev-stand"

    def is_valid(self) -> bool:
        if self.network.is_dummy or not self.bootstraps:
            return False

        if all(b.image is None for b in self.bootstraps):
            return False

        return True

    def has_bootstrap_image(self) -> bool:
        return any(b.image for b in self.bootstraps)

    def set_bootstrap_image(self, image: str):
        for b in self.bootstraps:
            b.image = image

    @classmethod
    def single_bootstrap_stand(
        cls,
        image: str,
        network: Network,
        cores: int = 1,
        memory: int = 1024,
        name: str = "dev-stand",
        bootstrap_name: str = "bootstrap",
    ) -> Stand:
        return cls(
            name=name,
            network=network,
            bootstraps=[
                Bootstrap(
                    name=bootstrap_name,
                    image=image,
                    cores=cores,
                    memory=memory,
                )
            ],
            baremetals=[],
        )

    @classmethod
    def empty_stand(
        cls, name: str = "dev-stand", network: Network | None = None
    ) -> Stand:
        if network is None:
            network = Network.dummy()

        return cls(name=name, bootstraps=[], baremetals=[], network=network)

    @classmethod
    def from_spec(cls, spec: tp.Dict[str, tp.Any]) -> Stand:
        spec = spec.copy()
        bootstraps = [
            Bootstrap.from_spec(b) for b in spec.pop("bootstraps", [])
        ]
        baremetals = [Node.from_spec(n) for n in spec.pop("baremetals", [])]

        if "network" not in spec:
            network = Network.dummy()
        else:
            network = Network.from_spec(spec.pop("network"))

        return cls(
            bootstraps=bootstraps,
            baremetals=baremetals,
            network=network,
            **spec,
        )
