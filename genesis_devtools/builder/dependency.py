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
import shutil
import typing as tp

import bazooka

from genesis_devtools.builder import base


class LocalPathDependency(base.AbstractDependency):
    """Local path dependency item."""

    def __init__(self, path: str, img_dest: str) -> None:
        super().__init__()
        self._path = path
        self._img_dest = img_dest
        self._local_path = None

    @property
    def img_dest(self) -> str | None:
        """Destination for the image."""
        return self._img_dest

    @property
    def local_path(self) -> str | None:
        """Local path to the dependency."""
        return self._local_path

    def fetch(self, output_dir: str) -> None:
        """Fetch the dependency."""
        path = self._path
        if os.path.isdir(path):
            name = os.path.basename(path)
            shutil.copytree(path, os.path.join(output_dir, name))
            self._local_path = os.path.join(output_dir, name)
        else:
            shutil.copy(path, output_dir)
            self._local_path = os.path.join(output_dir, os.path.basename(path))

    def __str__(self):
        return f"Local path -> {self._path}"

    @classmethod
    def from_config(
        cls, dep_config: tp.Dict[str, tp.Any], work_dir: str
    ) -> "LocalPathDependency":
        """Create a dependency item from configuration."""
        if "path" not in dep_config or "src" not in dep_config["path"]:
            raise ValueError("Path not found in dependency configuration")

        path = dep_config["path"]["src"]
        img_dest = dep_config["dst"]

        if not os.path.isabs(path):
            path = os.path.join(work_dir, path)

        return cls(path, img_dest)


class HttpDependency(base.AbstractDependency):
    """HTTP dependency item."""

    CHUNK_SIZE = 8192

    def __init__(self, endpoint: str, img_dest: str) -> None:
        super().__init__()
        self._endpoint = endpoint
        self._img_dest = img_dest
        self._local_path = None

    @property
    def img_dest(self) -> str | None:
        """Destination for the image."""
        return self._img_dest

    @property
    def local_path(self) -> str | None:
        """Local path to the dependency."""
        return self._local_path

    def fetch(self, output_dir: str) -> None:
        """Fetch the dependency."""
        filename = os.path.basename(self._endpoint)
        output_path = os.path.join(output_dir, filename)

        with bazooka.get(self._endpoint, stream=True) as r:
            r.raise_for_status()
            with open(output_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=self.CHUNK_SIZE):
                    f.write(chunk)

        self._local_path = output_path

    def __str__(self):
        return f"URL -> {self._endpoint}"

    @classmethod
    def from_config(
        cls, dep_config: tp.Dict[str, tp.Any], work_dir: str
    ) -> "LocalPathDependency":
        """Create a dependency item from configuration."""
        if "http" not in dep_config or "src" not in dep_config["http"]:
            raise ValueError("URL not found in dependency configuration")

        endpoint = dep_config["http"]["src"]
        img_dest = dep_config["dst"]

        return cls(endpoint, img_dest)
