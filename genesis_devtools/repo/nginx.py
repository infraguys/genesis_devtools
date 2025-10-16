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
import tempfile
import shutil
import pathlib
import requests

from genesis_devtools.repo import base
from genesis_devtools.builder import base as builder_base
from genesis_devtools import logger as logger_base


class NginxRepoDriver(base.AbstractRepoDriver):
    """Nginx-based repository driver for storing and retrieving elements.

    This driver uses an Nginx server with WebDAV module enabled to store
    elements. Files are uploaded using HTTP PUT requests.
    """

    def __init__(
        self,
        url: str,
        auth: tuple[str, str] | None = None,
        logger: logger_base.AbstractLogger = logger_base.ClickLogger(),
    ):
        """Initialize the Nginx repo driver.

        Args:
            url: Base URL of the Nginx server (e.g., 'http://localhost:8080')
            auth: Optional tuple of (username, password) for basic auth
            logger: Logger instance for output
        """
        self._base_url = url.rstrip("/")
        self._auth = auth
        self._logger = logger
        self._session = requests.Session()
        if self._auth:
            self._session.auth = self._auth

    @property
    def elements_path(self) -> str:
        """Get the base path for elements in the repository."""
        return f"{self._base_url}/genesis-elements"

    def elements_inventory_path(
        self, element: builder_base.ElementInventory
    ) -> str:
        """Get the base path for elements in the repository."""
        return (
            f"{self._base_url}/genesis-elements"
            f"/{element.name}/{element.version}/inventory.json"
        )

    def _upload_file(self, local_path: str, remote_path: str) -> None:
        """Upload a file to the Nginx server.

        Args:
            local_path: Path to the local file
            remote_path: Remote path on the Nginx server
        """
        with open(local_path, "rb") as f:
            response = self._session.put(remote_path, data=f)
            response.raise_for_status()

    def _download_file(self, remote_path: str, local_path: str) -> None:
        """Download a file from the Nginx server.

        Args:
            remote_path: Remote path on the Nginx server
            local_path: Path to save the downloaded file
        """
        response = self._session.get(remote_path)
        response.raise_for_status()

        os.makedirs(os.path.dirname(local_path), exist_ok=True)
        with open(local_path, "wb") as f:
            f.write(response.content)

    def _delete_remote(self, remote_path: str) -> None:
        """Delete a file or directory from the Nginx server.

        Args:
            remote_path: Remote path to delete
        """
        response = self._session.delete(remote_path)
        # Ignore 404 errors as the resource might not exist
        if response.status_code != 404:
            response.raise_for_status()

    def _list_remote_directory(self, remote_path: str) -> list[str]:
        """List contents of a remote directory.

        Args:
            remote_path: Remote directory path

        Returns:
            List of items in the directory
        """
        # For Nginx with autoindex on, we need to parse the HTML response
        # or use a custom listing endpoint if available
        response = self._session.get(remote_path)
        if response.status_code == 404:
            return []
        response.raise_for_status()

        # Simple parsing for Nginx autoindex HTML
        # This is a basic implementation - might need adjustment based
        # on Nginx config
        items = []
        for line in response.text.split("\n"):
            if '<a href="' in line and "../" not in line:
                start = line.find('<a href="') + 9
                end = line.find('">', start)
                if start > 8 and end > start:
                    item = line[start:end].rstrip("/")
                    if item and item != ".":
                        items.append(item)
        return items

    def init_repo(self) -> None:
        """Initialize the repo."""
        meta_url = f"{self._base_url}/genesis-repo-meta.json"

        # Check if repo is already initialized
        response = self._session.head(meta_url)
        if response.status_code == 200:
            raise base.RepoAlreadyExistsError(
                f"Repo at {self._base_url} already initialized."
            )

        # Create metadata
        meta = base.RepoMetaV1()
        meta_data = json.dumps(meta.to_dict(), indent=2)

        # Upload metadata file
        response = self._session.put(meta_url, data=meta_data.encode("utf-8"))
        response.raise_for_status()

        # Create elements directory
        response = self._session.put(f"{self.elements_path}/.keeper")
        response.raise_for_status()

        self._logger.info(f"Initialized repo at {self._base_url}")

    def delete_repo(self) -> None:
        """Delete the repo."""
        # Delete elements directory
        self._delete_remote(self.elements_path)

        # Delete metadata file
        meta_url = f"{self._base_url}/genesis-repo-meta.json"
        self._delete_remote(meta_url)

        self._logger.info(f"Deleted repo at {self._base_url}")

    def push(self, element: builder_base.ElementInventory) -> None:
        """Push the element to the repo."""
        element_url = f"{self.elements_path}/{element.name}/{element.version}"

        # Check if element already exists
        response = self._session.head(self.elements_inventory_path(element))
        if response.status_code == 200:
            raise base.ElementAlreadyExistsError(
                f"Element {element.name} version {element.version} "
                "already exists."
            )

        for category in element.categories():
            if artifacts := getattr(element, category):
                for artifact in artifacts:
                    self._upload_file(
                        artifact,
                        f"{element_url}/{category}/"
                        f"{os.path.basename(artifact)}",
                    )
                    self._logger.info(
                        f"Uploaded {os.path.basename(artifact)} to "
                        f"{element.name}/{element.version}"
                    )

        spec = element.to_dict()
        for category in element.categories():
            spec[category] = [
                os.path.basename(artifact)
                for artifact in getattr(element, category)
            ]

        # Upload the inventory file
        response = self._session.put(
            self.elements_inventory_path(element),
            data=json.dumps(spec, indent=2).encode("utf-8"),
        )
        response.raise_for_status()

        self._logger.info(f"Pushed {element.name} version {element.version}")

    def pull(
        self, element: builder_base.ElementInventory, dst_path: str
    ) -> None:
        """Pull the element from the repo."""
        if not os.path.exists(dst_path):
            raise FileNotFoundError(f"Path {dst_path} does not exist.")

        element_url = f"{self.elements_path}/{element.name}/{element.version}"

        # Check if element exists
        response = self._session.head(self.elements_inventory_path(element))
        if response.status_code != 200:
            raise base.RepoNotFoundError(
                f"Element {element.name} version {element.version} not found."
            )

        # Download inventory file first
        inventory_path = os.path.join(dst_path, "inventory.json")
        self._download_file(
            self.elements_inventory_path(element), inventory_path
        )

        # Load inventory to get the list of files
        loaded_element = builder_base.ElementInventory.load(
            pathlib.Path(dst_path)
        )

        # Download all artifacts
        for category in loaded_element.categories():
            if artifacts := getattr(loaded_element, category):
                category_dir = os.path.join(dst_path, category)
                os.makedirs(category_dir, exist_ok=True)

                for artifact_path in artifacts:
                    artifact_name = os.path.basename(artifact_path)
                    remote_file = f"{element_url}/{category}/{artifact_name}"
                    local_file = os.path.join(category_dir, artifact_name)

                    try:
                        self._download_file(remote_file, local_file)
                        self._logger.info(
                            f"Downloaded {artifact_name} from "
                            f"{element.name}/{element.version}"
                        )
                    except requests.HTTPError as e:
                        if e.response.status_code != 404:
                            raise
                        self._logger.warn(
                            f"File {artifact_name} not found in "
                            "remote repository"
                        )

        self._logger.info(f"Pulled {element.name} version {element.version}")

    def remove(self, element: builder_base.ElementInventory) -> None:
        """Remove the element from the repo."""
        element_url = f"{self.elements_path}/{element.name}/{element.version}"

        # First, get list of all files to delete
        # We need to delete files individually as Nginx WebDAV might
        # not support recursive directory deletion

        # Download inventory to get file list
        try:
            response = self._session.get(self.elements_inventory_path(element))
            response.raise_for_status()

            # Delete all artifact files
            for category in builder_base.ElementInventory.categories():
                if artifacts := getattr(element, category):
                    for artifact in artifacts:
                        artifact_name = os.path.basename(artifact)
                        file_url = f"{element_url}/{category}/{artifact_name}"
                        self._delete_remote(file_url)

            # Delete category directories
            for category in builder_base.ElementInventory.categories():
                self._delete_remote(f"{element_url}/{category}")

            # Delete inventory file
            self._delete_remote(self.elements_inventory_path(element))

            # Try to delete the version directory
            self._delete_remote(element_url)

            self._logger.info(
                f"Removed {element.name} version {element.version}"
            )
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                self._logger.warning(
                    f"Element {element.name} version {element.version} "
                    "not found"
                )
            else:
                raise

    def list(self) -> dict[str, list[str]]:
        """List the elements in the repo."""
        meta_url = f"{self._base_url}/genesis-repo-meta.json"
        result = {}

        # Check if repo exists
        response = self._session.head(meta_url)
        if response.status_code != 200:
            raise base.RepoNotFoundError(
                f"Repo at {self._base_url} not found."
            )

        try:
            # Get list of element names
            element_names = self._list_remote_directory(self.elements_path)

            for name in element_names:
                # Get list of versions for each element
                element_url = f"{self.elements_path}/{name}"
                versions = self._list_remote_directory(element_url)

                if versions:
                    result[name] = versions

            return result
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                raise base.RepoNotFoundError(
                    f"Repo at {self._base_url} not found."
                )
            raise
