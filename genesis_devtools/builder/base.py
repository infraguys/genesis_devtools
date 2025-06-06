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
import os
import typing as tp
import dataclasses

from genesis_devtools import constants as c


@dataclasses.dataclass
class Image:
    """Image representation."""

    script: str
    profile: c.ImageProfileType = "ubuntu_24"
    format: c.ImageFormatType = "raw"
    name: str | None = None
    envs: list[str] | None = None
    override: dict[str, tp.Any] | None = None

    @classmethod
    def from_config(
        cls, image_config: tp.Dict[str, tp.Any], work_dir: str
    ) -> "Image":
        """Create an image from configuration."""
        script = image_config.pop("script")
        if not os.path.isabs(script):
            script = os.path.join(work_dir, script)
        return cls(script=script, **image_config)


class Element(tp.NamedTuple):
    """Element representation."""

    manifest: tp.Optional[str] = None
    images: tp.Optional[tp.List[Image]] = None
    artifacts: tp.Optional[tp.List[str]] = None

    def __str__(self):
        if self.manifest:
            # TODO: Add implementation where manifest is used.
            return "<Element manifest=...>"

        if self.images and len(self.images) > 0:
            name = ", ".join([f"{i.profile}" for i in self.images])
            return f"<Element images={name}>"

        return f"<Element {str(self)}>"

    @classmethod
    def from_config(
        cls, element_config: tp.Dict[str, tp.Any], work_dir: str
    ) -> "Element":
        """Create an element from configuration."""
        image_configs = element_config.pop("images", [])
        images = [Image.from_config(img, work_dir) for img in image_configs]
        return cls(images=images, **element_config)


class AbstractDependency(abc.ABC):
    """Abstract dependency item.

    This class defines the interface for a dependency item.
    """

    dependencies_store: tp.List["AbstractDependency"] = []

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__()
        cls.dependencies_store.append(cls)

    @abc.abstractproperty
    def img_dest(self) -> tp.Optional[str]:
        """Destination for the image."""

    @property
    def local_path(self) -> tp.Optional[str]:
        """Local path to the dependency."""
        return None

    @abc.abstractmethod
    def fetch(self, output_dir: str) -> None:
        """Fetch the dependency."""

    @abc.abstractclassmethod
    def from_config(
        cls, dep_config: tp.Dict[str, tp.Any], work_dir: str
    ) -> "AbstractDependency":
        """Create a dependency item from configuration."""

    @classmethod
    def find_dependency(
        cls, dep_config: tp.Dict[str, tp.Any], work_dir: str
    ) -> tp.Optional["AbstractDependency"]:
        """Probe all dependencies to find the right one."""
        for dep in cls.dependencies_store:
            try:
                return dep.from_config(dep_config, work_dir)
            except Exception:
                pass

        return None


class AbstractImageBuilder(abc.ABC):
    """Abstract image builder.

    This class defines the interface for building images.
    """

    @abc.abstractmethod
    def pre_build(
        self,
        image_dir: str,
        image: Image,
        deps: tp.List[AbstractDependency],
        developer_keys: tp.Optional[str] = None,
        output_dir: str = c.DEF_GEN_OUTPUT_DIR_NAME,
    ) -> None:
        """Actions to prepare the environment for building the image."""

    @abc.abstractmethod
    def build(
        self,
        image_dir: str,
        image: Image,
        developer_keys: tp.Optional[str] = None,
    ) -> None:
        """Actions to build the image."""

    @abc.abstractmethod
    def post_build(
        self,
        image_dir: str,
        image: Image,
    ) -> None:
        """Actions to perform after building the image."""

    def run(
        self,
        image_dir: str,
        image: Image,
        deps: tp.List[AbstractDependency],
        developer_keys: tp.Optional[str] = None,
        output_dir: str = c.DEF_GEN_OUTPUT_DIR_NAME,
    ) -> None:
        """Run the image builder."""
        self.pre_build(image_dir, image, deps, developer_keys, output_dir)
        self.build(image_dir, image, developer_keys)
        self.post_build(image_dir, image)


class DummyImageBuilder(AbstractImageBuilder):
    """Dummy image builder.

    Dummy builder that does nothing.
    """

    def pre_build(
        self,
        image_dir: str,
        image: Image,
        deps: tp.List[AbstractDependency],
        developer_keys: tp.Optional[str] = None,
        output_dir: str = c.DEF_GEN_OUTPUT_DIR_NAME,
    ) -> None:
        """Actions to prepare the environment for building the image."""
        return None

    def build(
        self,
        image_dir: str,
        image: Image,
        developer_keys: tp.Optional[str] = None,
    ) -> None:
        """Actions to build the image."""
        return None

    def post_build(
        self,
        image_dir: str,
        image: Image,
    ) -> None:
        """Actions to perform after building the image."""
        return None
