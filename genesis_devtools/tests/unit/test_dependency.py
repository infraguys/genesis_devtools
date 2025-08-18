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
import pytest

from genesis_devtools.builder import dependency as deps


class TestDependency:

    def test_local_path_from_config(
        self, build_config: tp.Dict[str, tp.Any]
    ) -> None:
        work_dir = "/tmp/work_dir"
        dep = deps.LocalPathDependency.from_config(
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

        dep = deps.LocalPathDependency.from_config(
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

    def test_http_from_config(
        self, build_config: tp.Dict[str, tp.Any]
    ) -> None:
        work_dir = "/tmp/work_dir"
        dep = deps.HttpDependency.from_config(
            build_config["deps"][1],
            work_dir,
        )

        assert dep.img_dest == "/opt/undionly.kpxe"
        assert (
            dep._endpoint
            == "http://repository.genesis-core.tech:8081/ipxe/latest/undionly.kpxe"
        )
        assert dep.local_path is None

    def test_http_fetch(self, build_config: tp.Dict[str, tp.Any]) -> None:
        dep = deps.HttpDependency.from_config(
            build_config["deps"][1],
            "/tmp",
        )

        os.makedirs("/tmp/___deps_dir", exist_ok=True)
        dep.fetch("/tmp/___deps_dir")

        try:
            assert os.path.exists("/tmp/___deps_dir/undionly.kpxe")
        finally:
            shutil.rmtree("/tmp/___deps_dir")

    def test_git_from_config(
        self, build_git_config: tp.Dict[str, tp.Any]
    ) -> None:
        work_dir = "/tmp/work_dir"
        dep = deps.GitDependency.from_config(
            build_git_config["deps"][0],
            work_dir,
        )

        assert dep.img_dest == "/opt/genesis_templates"
        assert (
            dep._repo_url
            == "https://github.com/infraguys/genesis_templates.git"
        )
        assert dep.local_path is None

    def test_git_fetch(self, build_git_config: tp.Dict[str, tp.Any]) -> None:
        dep = deps.GitDependency.from_config(
            build_git_config["deps"][0],
            "/tmp",
        )

        os.makedirs("/tmp/___deps_dir", exist_ok=True)
        dep.fetch("/tmp/___deps_dir")

        try:
            assert os.path.exists("/tmp/___deps_dir/genesis_templates")
        finally:
            shutil.rmtree("/tmp/___deps_dir")

    def test_env_path_from_config(
        self, build_env_config: tp.Dict[str, tp.Any]
    ) -> None:
        work_dir = "/tmp/work_dir"
        dep = deps.LocalEnvPathDependency.from_config(
            build_env_config["deps"][0],
            work_dir,
        )

        assert dep.img_dest == "/opt/genesis_devtools"
        assert dep._env_path == "PATH_FROM_ENV"
        assert dep.local_path is None

    def test_env_path_fetch(
        self, build_env_config: tp.Dict[str, tp.Any]
    ) -> None:
        os.makedirs("/tmp/genesis_core_test_dir", exist_ok=True)
        os.environ["PATH_FROM_ENV"] = "/tmp/genesis_core_test_dir"

        dep = deps.LocalEnvPathDependency.from_config(
            build_env_config["deps"][0],
            "/tmp",
        )

        os.makedirs("/tmp/___deps_dir", exist_ok=True)
        dep.fetch("/tmp/___deps_dir")

        try:
            assert os.path.exists("/tmp/___deps_dir/genesis_core_test_dir")
        finally:
            shutil.rmtree("/tmp/genesis_core_test_dir")
            shutil.rmtree("/tmp/___deps_dir")

    def _run_local_path_dep_fetch(
        self,
        src_dir: str,
        target_dir: str,
        files: tp.List[str],
        exclude: tp.List[str],
        dep_config_base: tp.Dict[str, tp.Any],
    ) -> str:
        """
        Function helper for exclude tests set
        Creates temporary file structures, runs LocalPathDependency.fetch.
        and return path out.
        """
        # Creating all folders and files

        for file_path in files:
            full_path = os.path.join(src_dir, file_path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, "w") as f:
                f.write(f"content of {file_path}")

        # Create a target folder
        os.makedirs(target_dir, exist_ok=True)

        # Add exclude
        dep_config = dict(dep_config_base)
        dep_config["exclude"] = exclude

        dep = deps.LocalPathDependency.from_config(dep_config, "/tmp")
        dep.fetch(target_dir)

        return os.path.join(target_dir, os.path.basename(src_dir))

    def test_exclude_dir_root_lvl(self):
        # Exclude the build file from root
        src_dir = "/tmp/genesis_core_test_dir"
        target_dir = "/tmp/deps_test"
        base_dep_config = {
            "dst": "/opt/genesis_core",
            "path": {"src": src_dir},
        }

        base_target = self._run_local_path_dep_fetch(
            src_dir,
            target_dir,
            files=[
                "my_project/build",
                "build",
                "README.md",
            ],
            exclude=["build"],
            dep_config_base=base_dep_config,
        )

        try:
            assert not os.path.exists(os.path.join(base_target, "build"))
            assert os.path.exists(
                os.path.join(base_target, "my_project/build")
            )
            assert os.path.exists(os.path.join(base_target, "README.md"))

        finally:
            shutil.rmtree(src_dir)
            shutil.rmtree(target_dir)

    def test_exclude_dir_root_lvl_with_file_inside(self):
        src_dir = "/tmp/genesis_core_test_dir"
        target_dir = "/tmp/deps_test"
        base_dep_config = {
            "dst": "/opt/genesis_core",
            "path": {"src": src_dir},
        }

        base_target = self._run_local_path_dep_fetch(
            src_dir,
            target_dir,
            files=[
                "my_project/build",
                "build/main.so",
                "README.md",
            ],
            exclude=["build"],
            dep_config_base=base_dep_config,
        )

        try:
            assert not os.path.exists(os.path.join(base_target, "build"))
            assert not os.path.exists(
                os.path.join(base_target, "build/main.so")
            )
            assert os.path.exists(
                os.path.join(base_target, "my_project/build")
            )
            assert os.path.exists(os.path.join(base_target, "README.md"))

        finally:
            shutil.rmtree(src_dir)
            shutil.rmtree(target_dir)

    def test_exclude_nested_folder(self):
        src_dir = "/tmp/genesis_core_test_dir"
        target_dir = "/tmp/deps_test"
        base_dep_config = {
            "dst": "/opt/genesis_core",
            "path": {"src": src_dir},
        }

        base_target = self._run_local_path_dep_fetch(
            src_dir,
            target_dir,
            files=[
                "my_project/build",
                "build/main.so",
                "README.md",
            ],
            exclude=["my_project/build"],
            dep_config_base=base_dep_config,
        )

        try:
            assert os.path.exists(os.path.join(base_target, "my_project"))
            assert not os.path.exists(
                os.path.join(base_target, "my_project/build")
            )
            assert os.path.exists(os.path.join(base_target, "build"))
            assert os.path.exists(os.path.join(base_target, "build/main.so"))
            assert os.path.exists(os.path.join(base_target, "README.md"))

        finally:
            shutil.rmtree(src_dir)
            shutil.rmtree(target_dir)

        def test_exclude_wildcards(self):
            src_dir = "/tmp/genesis_core_test_dir"
            target_dir = "/tmp/deps_test"
            base_dep_config = {
                "dst": "/opt/genesis_core",
                "path": {"src": src_dir},
            }

            base_target = self._run_local_path_dep_fetch(
                src_dir,
                target_dir,
                files=[
                    "my_project/build/file1.txt",
                    "my_project/build/file2.txt",
                    "my_project/build/file3.txt",
                    "my_project/build/e1.txt",
                    "build/main.so",
                    "README.md",
                ],
                exclude=["my_project/build/file*"],
                dep_config_base=base_dep_config,
            )

            try:
                assert not os.path.exists(
                    os.path.join(base_target, "my_project/build/file1.txt")
                )
                assert not os.path.exists(
                    os.path.join(base_target, "my_project/build/file2.txt")
                )
                assert not os.path.exists(
                    os.path.join(base_target, "my_project/build/file3.txt")
                )
                assert os.path.exists(
                    os.path.join(base_target, "my_project/build/e1.txt")
                )
                assert os.path.exists(os.path.join(base_target, "build"))
                assert os.path.exists(
                    os.path.join(base_target, "build/main.so")
                )
                assert os.path.exists(os.path.join(base_target, "README.md"))

            finally:
                shutil.rmtree(src_dir)
                shutil.rmtree(target_dir)
