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

import typing as tp
import tempfile
import shutil
import os
import gzip
import jinja2

import yaml

from genesis_devtools.builder import base
from genesis_devtools.logger import AbstractLogger, DummyLogger
from genesis_devtools import constants as c


class SimpleBuilder:
    """Simple element builder."""

    DEP_KEY = "deps"
    ELEMENT_KEY = "elements"

    def __init__(
        self,
        work_dir: str,
        deps: tp.List[base.AbstractDependency],
        elements: tp.List[base.Element],
        image_builder: base.AbstractImageBuilder,
        logger: tp.Optional[AbstractLogger] = None,
        elements_output_dir: str = c.DEF_GEN_OUTPUT_DIR_NAME,
    ) -> None:
        super().__init__()
        self._deps = deps
        self._elements = elements
        self._image_builder = image_builder
        self._work_dir = work_dir
        self._logger = logger or DummyLogger()
        self._elements_output_dir = elements_output_dir

        if not os.path.exists(self._elements_output_dir):
            os.makedirs(self._elements_output_dir)

    def _build_image(
        self,
        img: base.Image,
        build_dir: str | None,
        output_dir: str,
        developer_keys: str,
        inventory_mode: bool = False,
    ) -> str:

        # Determine images output directory
        if inventory_mode:
            images_output_dir = os.path.join(
                self._elements_output_dir, "images"
            )
        else:
            images_output_dir = self._elements_output_dir

        # The build_dir is used only for debugging purposes to observe
        # the content of the image. In production, the image is built
        # in a temporary directory.
        if build_dir is not None:
            self._image_builder.run(
                build_dir,
                img,
                self._deps,
                developer_keys,
                output_dir,
            )
        else:
            with tempfile.TemporaryDirectory() as temp_dir:
                self._image_builder.run(
                    temp_dir,
                    img,
                    self._deps,
                    developer_keys,
                    output_dir,
                )

        # Move the image to the final location
        if not os.path.exists(images_output_dir):
            os.makedirs(images_output_dir)

        # Determine source path to move. If gzip was requested,
        # compress RAW -> GZ first.
        if img.format == "gz":
            self._logger.info(f"Compressing {img.name} to {img.name}.raw.gz")
            # Source RAW image produced by Packer
            raw_src = os.path.join(output_dir, f"{img.name}.raw")
            gz_tgt = os.path.join(images_output_dir, f"{img.name}.raw.gz")
            # Compress using standard library (gzip uses zlib) with level 5
            with open(raw_src, "rb") as f_in, gzip.open(
                gz_tgt, "wb", compresslevel=5
            ) as f_out:
                shutil.copyfileobj(f_in, f_out)
            return os.path.abspath(gz_tgt)
        else:
            src_path = os.path.join(output_dir, f"{img.name}.{img.format}")
            shutil.move(src_path, images_output_dir)
            return os.path.abspath(
                os.path.join(images_output_dir, f"{img.name}.{img.format}")
            )

    def fetch_dependency(self, deps_dir: str) -> None:
        """Fetch common dependencies for elements."""
        self._logger.important("Fetching dependencies")
        for dep in self._deps:
            self._logger.info(f"Fetching dependency: {dep}")
            dep.fetch(deps_dir)

    def build_element(
        self,
        element: base.Element,
        build_dir: str | None = None,
        developer_keys: str | None = None,
        build_suffix: str = "",
        inventory_mode: bool = False,
        manifest_vars: dict[str, tp.Any] | None = None,
    ) -> None:
        """Build an element."""
        self._logger.info(f"Building element: {element}")
        image_paths = []

        # Build images
        for img in element.images:
            if build_suffix and not inventory_mode:
                img.name = f"{img.name}.{build_suffix}"
            tmp_img_output = f"_tmp_{img.name}-output"

            try:
                _path = self._build_image(
                    img,
                    build_dir,
                    tmp_img_output,
                    developer_keys,
                    inventory_mode,
                )
                image_paths.append(_path)
            finally:
                if os.path.exists(tmp_img_output):
                    shutil.rmtree(tmp_img_output)

        # Save files in the inventory format
        if inventory_mode:
            if not element.manifest:
                raise ValueError("Element must have a manifest")

            with open(
                os.path.join(self._work_dir, element.manifest), "r"
            ) as f:
                manifest = yaml.safe_load(f)

            version = build_suffix

            if manifest_vars:
                manifest_vars = manifest_vars.copy()
            else:
                manifest_vars = {}
            manifest_vars["version"] = version

            name = (manifest_vars.get("name") or manifest["name"]).strip()

            if name.startswith("{"):
                raise ValueError(
                    "Specify manifest name using --manifest-var name=value"
                )
            manifest_vars["name"] = name

            # TODO(akremenetsky): This part should be refactored when we
            # support building of multiple elements.
            inventory_path = self._elements_output_dir

            manifests_path = os.path.join(inventory_path, "manifests")
            orig_manifest_path = os.path.join(self._work_dir, element.manifest)

            # Render templated manifests
            jinja2_extensions = (".jinja2", ".j2")
            if element.manifest.endswith(jinja2_extensions):
                # Render Jinja2 manifest
                with open(orig_manifest_path) as f:
                    template = jinja2.Template(f.read())
                rendered_manifest = template.render(
                    images=[os.path.basename(p) for p in image_paths],
                    manifests=[os.path.basename(element.manifest)],
                    **manifest_vars,
                )

                # Remove extension from the manifest name
                manifest_name = ".".join(
                    os.path.basename(element.manifest).split(".")[:-1]
                )
                manifest_path = os.path.join(manifests_path, manifest_name)

                # Save rendered manifest
                os.makedirs(manifests_path, exist_ok=True)
                with open(manifest_path, "w") as f:
                    f.write(rendered_manifest)
            else:
                manifest_name = os.path.basename(element.manifest)
                manifest_path = os.path.join(manifests_path, manifest_name)
                os.makedirs(manifests_path, exist_ok=True)
                shutil.copyfile(orig_manifest_path, manifest_path)

            manifests = [os.path.abspath(manifest_path)]

            inventory = base.ElementInventory(
                name=name,
                version=version,
                images=image_paths,
                manifests=manifests,
            )
            inventory.save(inventory_path)

    def build(
        self,
        build_dir: str | None = None,
        developer_keys: str | None = None,
        build_suffix: str = "",
        inventory_mode: bool = False,
        manifest_vars: dict[str, tp.Any] | None = None,
    ) -> None:
        """Build all elements."""
        self._logger.important("Building elements")
        for e in self._elements:
            self.build_element(
                e,
                build_dir,
                developer_keys,
                build_suffix,
                inventory_mode,
                manifest_vars,
            )

    @classmethod
    def from_config(
        cls,
        work_dir: str,
        build_config: tp.Dict[str, tp.Any],
        image_builder: base.AbstractImageBuilder,
        logger: tp.Optional[AbstractLogger] = None,
        elements_output_dir: str = c.DEF_GEN_OUTPUT_DIR_NAME,
    ) -> "SimpleBuilder":
        """Create a builder from configuration."""
        # Prepare dependencies entries but do not fetch them
        deps = []
        dep_configs = build_config.get(cls.DEP_KEY, [])
        for dep in dep_configs:
            dep_item = base.AbstractDependency.find_dependency(dep, work_dir)
            if dep_item is None:
                raise ValueError(
                    f"Unable to handle dependency: {dep}. Unknown type."
                )
            deps.append(dep_item)

        # Prepare elements
        element_configs = build_config.get(cls.ELEMENT_KEY, [])
        elements = [
            base.Element.from_config(elem, work_dir)
            for elem in element_configs
        ]

        if not elements:
            raise ValueError("No elements found in configuration")

        return cls(
            work_dir,
            deps,
            elements,
            image_builder,
            logger,
            elements_output_dir,
        )
