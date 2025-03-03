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

from genesis_devtools.builder.builder import SimpleBuilder
from genesis_devtools.logger import DummyLogger


class TestBuilder:

    def test_fetch_dependency(self, simple_builder: SimpleBuilder) -> None:
        deps_dir = "/tmp/deps_dir"
        simple_builder.fetch_dependency(deps_dir)
        for dep in simple_builder._deps:
            dep.fetch.assert_called_once_with(deps_dir)

        assert len(simple_builder._deps) > 1

    def test_from_config(self, build_config: tp.Dict[str, tp.Any]) -> None:
        work_dir = "/tmp/work_dir"

        builder = SimpleBuilder.from_config(
            work_dir,
            build_config,
            MagicMock(),
            DummyLogger(),
        )

        assert len(builder._deps) == 2
        assert len(builder._elements) == 1
        assert builder._work_dir == work_dir
