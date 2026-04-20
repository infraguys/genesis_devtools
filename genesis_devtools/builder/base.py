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
import json
import pathlib
import typing as tp
import dataclasses

from genesis_devtools import constants as c


@dataclasses.dataclass
class Image:
    """Image representation."""

    ENV_IMG_PREFIX = "GEN_IMG_FORMAT"
    DEF_IMG_FORMAT = "raw"

    script: str
    profile: c.ImageProfileType = "ubuntu_24"
    format: c.ImageFormatType = DEF_IMG_FORMAT
    name: str | None = None
    envs: list[str] | None = None
    override: dict[str, tp.Any] | None = None

    @classmethod
    def from_config(cls, image_config: dict[str, tp.Any], work_dir: str) -> "Image":
        """Create an image from configuration."""
        image_config = image_config.copy()
        script = image_config.pop("script")
        if not os.path.isabs(script):
            script = os.path.join(work_dir, script)

        # Determine the image format
        img_format = image_config.pop("format")
        if img_format.startswith(cls.ENV_IMG_PREFIX):
            format_def = None

            # Handle case if there is a default value
            if "=" in img_format:
                img_format, format_def = [i.strip() for i in img_format.split("=", 1)]

            try:
                img_format = os.environ[img_format]
            except KeyError:
                if not format_def:
                    raise ValueError(
                        f"Image format {img_format} is not found in the environment "
                        f"and no default value is provided"
                    )
                img_format = format_def

        # Validate the image format
        if img_format not in c.ImageFormatType.__args__:
            raise ValueError(
                f"Invalid image format: {img_format}, "
                f"expected one of {c.ImageFormatType.__args__}"
            )

        return cls(script=script, format=img_format, **image_config)


@dataclasses.dataclass
class Config:
    """Config representation."""

    abs_path: str
    path: str

    @classmethod
    def from_config(cls, config: dict[str, tp.Any], work_dir: str) -> "Config":
        """Create a config from configuration."""
        abs_path = os.path.join(work_dir, config["path"])
        return cls(abs_path=abs_path, path=config["path"])


@dataclasses.dataclass
class Artifact:
    """Artifact representation."""

    abs_path: str
    path: str

    @classmethod
    def from_config(cls, config: dict[str, tp.Any], work_dir: str) -> "Artifact":
        """Create an artifact from configuration."""
        abs_path = os.path.join(work_dir, config["path"])
        return cls(abs_path=abs_path, path=config["path"])


class Element(tp.NamedTuple):
    """Element representation."""

    manifest: tp.Optional[str] = None
    images: tp.Optional[tp.List[Image]] = None
    artifacts: tp.Optional[tp.List[Artifact]] = None
    configs: tp.Optional[tp.List[Config]] = None

    def __str__(self):
        if self.manifest:
            return f"<Element manifest={self.manifest}>"

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

        config_configs = element_config.pop("configs", [])
        configs = [Config.from_config(config, work_dir) for config in config_configs]

        artifacts_configs = element_config.pop("artifacts", [])
        artifacts = [
            Artifact.from_config(artifact, work_dir) for artifact in artifacts_configs
        ]
        return cls(
            images=images, configs=configs, artifacts=artifacts, **element_config
        )


class ElementInventory(tp.NamedTuple):
    """Element inventory."""

    file_name = pathlib.Path("inventory.json")

    name: str
    version: str
    images: tp.Collection[pathlib.Path] = tuple()
    manifests: tp.Collection[pathlib.Path] = tuple()
    configs: tp.Collection[pathlib.Path] = tuple()
    templates: tp.Collection[pathlib.Path] = tuple()
    artifacts: tp.Collection[pathlib.Path] = tuple()

    @classmethod
    def categories(cls) -> tuple[str, str, str, str, str]:
        return "images", "manifests", "configs", "templates", "artifacts"

    def to_dict(self) -> dict[str, tp.Any]:
        data = {
            "name": self.name,
            "version": self.version,
        }
        for category in self.categories():
            data[category] = [str(p) for p in getattr(self, category)]
        return data

    def save(self, path: pathlib.Path) -> None:
        """Save the element inventory to a path."""
        with open(path / self.file_name, "w") as f:
            json.dump(self.to_dict(), f, indent=2, sort_keys=True)

    @classmethod
    def load(cls, path: pathlib.Path, index: int = 0) -> "ElementInventory":
        """Create an element inventory from a path."""
        if path.is_dir():
            path = path / cls.file_name

        with open(path, "r") as f:
            inventory = json.load(f)

        # Backward compatibility: support both single
        # inventory and list of inventories
        if isinstance(inventory, list):
            try:
                inventory = inventory[index]
            except IndexError:
                raise ValueError(
                    f"Inventory index {index} not found in list of "
                    f"{len(inventory)} inventories"
                )

        kwargs = {
            "name": inventory["name"],
            "version": inventory["version"],
        }
        for category in cls.categories():
            kwargs[category] = [pathlib.Path(p) for p in inventory.get(category, [])]

        return cls(**kwargs)

    @classmethod
    def from_dict(cls, data: dict[str, tp.Any]) -> "ElementInventory":
        """Create an element inventory from a dictionary."""
        kwargs = {
            "name": data["name"],
            "version": data["version"],
        }
        for category in cls.categories():
            kwargs[category] = [pathlib.Path(p) for p in data.get(category, [])]
        return cls(**kwargs)


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
