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

import os
import shutil
import typing as tp

from genesis_devtools.builder import base


class LocalPathDependency(base.AbstractDependency):
    """Local path dependency item."""

    def __init__(self, path: str, img_dest: str) -> None:
        super().__init__()
        self._path = path
        self._img_dest = img_dest
        self._local_path = None

    @property
    def img_dest(self) -> tp.Optional[str]:
        """Destination for the image."""
        return self._img_dest

    @property
    def local_path(self) -> tp.Optional[str]:
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
