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

import abc
import typing as tp

from genesis_devtools import exceptions
from genesis_devtools.builder import base as builder_base


class RepoAlreadyExistsError(exceptions.DevToolsException):
    """Repo already exists."""


class RepoNotFoundError(exceptions.DevToolsException):
    """Repo not found."""


class ElementAlreadyExistsError(exceptions.DevToolsException):
    """Element already exists in the repo."""


class UnableLoadDriverError(exceptions.DevToolsException):
    """Unable to load driver."""


class RepoMetaV1(tp.NamedTuple):
    schema_version: int = 1
    name: str = "genesis-elements"

    def to_dict(self) -> dict[str, tp.Any]:
        return {"schema_version": self.schema_version, "name": self.name}

    @classmethod
    def from_dict(cls, data: dict[str, tp.Any]) -> "RepoMetaV1":
        return cls(schema_version=data["schema_version"], name=data["name"])


class AbstractRepoDriver(abc.ABC):
    @abc.abstractmethod
    def init_repo(self) -> None:
        """Initialize the repo."""

    @abc.abstractmethod
    def delete_repo(self) -> None:
        """Delete the repo."""

    @abc.abstractmethod
    def push(self, element: builder_base.ElementInventory) -> None:
        """Push the element to the repo."""

    @abc.abstractmethod
    def pull(
        self, element: builder_base.ElementInventory, dst_path: str
    ) -> None:
        """Pull the element from the repo."""

    @abc.abstractmethod
    def remove(self, element: builder_base.ElementInventory) -> None:
        """Remove the element from the repo."""

    @abc.abstractmethod
    def list(self) -> dict[str, list[str]]:
        """List the elements in the repo."""
