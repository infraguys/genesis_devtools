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
from unittest.mock import MagicMock

import pytest
import yaml

from genesis_devtools.builder.builder import SimpleBuilder
from genesis_devtools.builder.base import (
    AbstractDependency,
    AbstractImageBuilder,
    Element,
)
from genesis_devtools.logger import DummyLogger
from genesis_devtools.builder.dependency import LocalPathDependency


@pytest.fixture
def simple_builder() -> SimpleBuilder:
    work_dir = "/tmp/work_dir"
    deps = [MagicMock(spec=AbstractDependency) for _ in range(2)]
    elements = [MagicMock(spec=Element) for _ in range(2)]
    image_builder = MagicMock(spec=AbstractImageBuilder)
    logger = DummyLogger()
    return SimpleBuilder(work_dir, deps, elements, image_builder, logger)


@pytest.fixture
def dep_local_path_factory():
    def factory(path: str, img_path: str) -> LocalPathDependency:
        return LocalPathDependency(path, img_path)

    return factory


@pytest.fixture
def build_config() -> tp.Dict[str, tp.Any]:
    fixture = """
build:
  deps:
    - dst: /opt/genesis_core
      path:
        src: /tmp/genesis_core_test_dir
    - dst: /opt/undionly.kpxe
      http:
        src: http://repository.genesis-core.tech:8081/ipxe/latest/undionly.kpxe
  elements:
    - images:
      - name: genesis-core
        format: raw
        profile: ubuntu_24
        script: images/install.sh
"""
    cfg = yaml.safe_load(fixture)
    return cfg["build"]


@pytest.fixture
def build_git_config() -> tp.Dict[str, tp.Any]:
    fixture = """
build:
  deps:
    - dst: /opt/genesis_templates
      git:
        src: https://github.com/infraguys/genesis_templates.git
        branch: master
  elements:
    - images:
      - name: genesis-core
        format: raw
        profile: ubuntu_24
        script: images/install.sh
"""
    cfg = yaml.safe_load(fixture)
    return cfg["build"]


@pytest.fixture
def build_env_config() -> tp.Dict[str, tp.Any]:
    fixture = """
build:
  deps:
    - dst: /opt/genesis_devtools
      optional: false
      path:
        env: PATH_FROM_ENV
  elements:
    - images:
      - name: genesis-core
        format: raw
        profile: ubuntu_24
        script: images/install.sh
"""
    cfg = yaml.safe_load(fixture)
    return cfg["build"]
