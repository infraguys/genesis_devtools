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

import typing as tp
import tempfile

from genesis_devtools.builder import base
from genesis_devtools.logger import AbstractLogger, DummyLogger


class SimpleBuilder:
    """Abstract element builder.

    This class defines the interface for building elements.
    """

    DEP_KEY = "deps"
    ELEMENT_KEY = "elements"

    def __init__(
        self,
        work_dir: str,
        deps: tp.List[base.AbstractDependency],
        elements: tp.List[base.Element],
        image_builder: base.AbstractImageBuilder,
        logger: tp.Optional[AbstractLogger] = None,
    ) -> None:
        super().__init__()
        self._deps = deps
        self._elements = elements
        self._image_builder = image_builder
        self._work_dir = work_dir
        self._logger = logger or DummyLogger()

    def fetch_dependency(self, deps_dir: str) -> None:
        """Fetch common dependencies for elements."""
        self._logger.important("Fetching dependencies")
        for dep in self._deps:
            self._logger.info(f"Fetching dependency: {dep}")
            dep.fetch(deps_dir)

    def build(
        self,
        build_dir: tp.Optional[str] = None,
        developer_keys: tp.Optional[str] = None,
    ) -> None:
        """Build all elements."""
        self._logger.important("Building elements")
        for e in self._elements:
            self._logger.info(f"Building element: {e}")
            for img in e.images:
                # The build_dir is used only for debugging purposes to observe
                # the content of the image. In production, the image is built
                # in a temporary directory.
                if build_dir is not None:
                    self._image_builder.run(
                        build_dir, img, self._deps, developer_keys
                    )
                else:
                    with tempfile.TemporaryDirectory() as temp_dir:
                        self._image_builder.run(
                            temp_dir, img, self._deps, developer_keys
                        )

    @classmethod
    def from_config(
        cls,
        work_dir: str,
        build_config: tp.Dict[str, tp.Any],
        image_builder: base.AbstractImageBuilder,
        logger: tp.Optional[AbstractLogger] = None,
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

        return cls(work_dir, deps, elements, image_builder, logger)
