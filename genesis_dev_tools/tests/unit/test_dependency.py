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
import tempfile

from genesis_dev_tools.builder.dependency import LocalPathDependency


class TestDependency:

    def test_local_path_from_config(
        self, build_config: tp.Dict[str, tp.Any]
    ) -> None:
        work_dir = "/tmp/work_dir"
        dep = LocalPathDependency.from_config(
            build_config["deps"][0],
            work_dir,
        )

        assert dep.img_dest == "/opt/genesis_core"
        assert dep._path == "/tmp/genesis_core_test_dir"
        assert dep.local_path is None

    def test_local_path_fetch(
        self, build_config: tp.Dict[str, tp.Any]
    ) -> None:
        os.makedirs("/tmp/genesis_core_test_dir", exist_ok=True)

        dep = LocalPathDependency.from_config(
            build_config["deps"][0],
            "/tmp",
        )

        os.makedirs("/tmp/___deps_dir", exist_ok=True)
        dep.fetch("/tmp/___deps_dir")

        try:
            assert os.path.exists("/tmp/___deps_dir/genesis_core_test_dir")
        finally:
            shutil.rmtree("/tmp/genesis_core_test_dir")
            shutil.rmtree("/tmp/___deps_dir")
