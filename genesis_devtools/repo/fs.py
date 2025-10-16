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
import json
import shutil

from genesis_devtools.repo import base
from genesis_devtools.builder import base as builder_base
from genesis_devtools import logger as logger_base


class FSRepoDriver(base.AbstractRepoDriver):
    def __init__(
        self,
        path: str,
        logger: logger_base.AbstractLogger = logger_base.ClickLogger(),
    ):
        self._repo_path = path
        self._logger = logger

    def _push_directory(
        self, element: builder_base.ElementInventory, dst: str, name: str
    ) -> None:
        if artifacts := getattr(element, name):
            os.makedirs(os.path.join(dst, name), exist_ok=True)
            for artifact in artifacts:
                artifact_name = os.path.basename(artifact)
                shutil.copyfile(
                    artifact, os.path.join(dst, name, artifact_name)
                )
                self._logger.info(f"Pushed {artifact_name} to {dst}")

            self._logger.info(f"Finished pushing {name}")

    @property
    def elements_path(self) -> str:
        return os.path.join(self._repo_path, "genesis-elements")

    def elements_inventory_path(
        self, element: builder_base.ElementInventory
    ) -> str:
        """Get the base path for elements in the repository."""
        return os.path.join(
            self.elements_path, element.name, element.version, "inventory.json"
        )

    def init_repo(self) -> None:
        """Initialize the repo."""
        elements_path = self.elements_path
        meta_path = os.path.join(self._repo_path, "genesis-repo-meta.json")

        # Check if repo is already initialized
        if os.path.exists(elements_path) or os.path.exists(meta_path):
            raise base.RepoAlreadyExistsError(
                f"Repo {self._repo_path} already initialized."
            )
        os.makedirs(self.elements_path, exist_ok=True)

        meta = base.RepoMetaV1()
        with open(meta_path, "w") as f:
            json.dump(meta.to_dict(), f, indent=2)

    def delete_repo(self) -> None:
        """Delete the repo."""
        elements_path = self.elements_path
        meta_path = os.path.join(self._repo_path, "genesis-repo-meta.json")

        if os.path.exists(elements_path):
            os.rmdir(elements_path)

        if os.path.exists(meta_path):
            os.remove(meta_path)

    def push(self, element: builder_base.ElementInventory) -> None:
        """Push the element to the repo."""
        element_path = os.path.join(
            self.elements_path, element.name, element.version
        )
        if os.path.exists(element_path):
            raise base.ElementAlreadyExistsError(
                f"Element {element.name} version {element.version} already exists."
            )

        os.makedirs(element_path, exist_ok=True)

        # Push all artifacts
        for name in builder_base.ElementInventory.categories():
            self._push_directory(element, element_path, name)

        # Push inventory
        spec = element.to_dict()
        for category in element.categories():
            spec[category] = [
                os.path.basename(artifact)
                for artifact in getattr(element, category)
            ]

        with open(self.elements_inventory_path(element), "w") as f:
            json.dump(spec, f, indent=2)

    def pull(
        self, element: builder_base.ElementInventory, dst_path: str
    ) -> None:
        """Pull the element from the repo."""
        # Pull all artifacts
        shutil.copytree(
            os.path.join(self.elements_path, element.name, element.version),
            dst_path,
            dirs_exist_ok=True,
        )

        # Pull inventory
        with open(self.elements_inventory_path(element), "r") as f:
            spec = json.load(f)

        inventory_path = os.path.join(dst_path, "inventory.json")
        with open(inventory_path, "w") as f:
            json.dump(spec, f, indent=2)

        self._logger.info(f"Pulled {element.name} version {element.version}")

    def remove(self, element: builder_base.ElementInventory) -> None:
        """Remove the element from the repo."""
        element_path = os.path.join(
            self.elements_path, element.name, element.version
        )
        if os.path.exists(element_path):
            shutil.rmtree(element_path)
        self._logger.info(f"Removed {element.name} version {element.version}")

    def list(self) -> dict[str, list[str]]:
        """List the elements in the repo."""
        try:
            return {
                name: os.listdir(os.path.join(self.elements_path, name))
                for name in os.listdir(self.elements_path)
            }
        except FileNotFoundError:
            raise base.RepoNotFoundError(f"Repo {self._repo_path} not found.")
