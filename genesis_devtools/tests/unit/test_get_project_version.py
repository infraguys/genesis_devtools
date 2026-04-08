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
import pytest
import tempfile
from unittest.mock import patch
from git import Repo
from genesis_devtools.utils import get_project_version


def test_version_with_tag():
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Repo.init(tmpdir)
        with open(os.path.join(tmpdir, "test.txt"), "w") as f:
            f.write("test")
        repo.index.add([os.path.join(tmpdir, "test.txt")])
        commit = repo.index.commit("Initial commit")

        repo.create_tag("1.2.3", commit)

        repo.head.commit = commit

        version = get_project_version(tmpdir)
        assert version == "1.2.3"


def test_version_without_tag():
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Repo.init(tmpdir)
        with open(os.path.join(tmpdir, "test.txt"), "w") as f:
            f.write("test")
        repo.index.add([os.path.join(tmpdir, "test.txt")])
        commit = repo.index.commit("Initial commit")

        repo.create_tag("1.2.2", commit)

        with open(os.path.join(tmpdir, "test2.txt"), "w") as f:
            f.write("test2")
        repo.index.add([os.path.join(tmpdir, "test2.txt")])
        repo.index.commit("Second commit")

        version = get_project_version(tmpdir)

        assert version.startswith("1.2.3-rc")


def test_version_empty_repo():
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Repo.init(tmpdir)
        with open(os.path.join(tmpdir, "test.txt"), "w") as f:
            f.write("test")
        repo.index.add([os.path.join(tmpdir, "test.txt")])
        repo.index.commit("Initial commit")
        hexsha = repo.active_branch.commit.hexsha

        version = get_project_version(tmpdir)

        assert version.startswith("0.0.1")
        assert version.endswith(f".{hexsha[:8]}")


def test_rc_branch():
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Repo.init(tmpdir)
        with open(os.path.join(tmpdir, "test.txt"), "w") as f:
            f.write("test")
        repo.index.add([os.path.join(tmpdir, "test.txt")])
        commit = repo.index.commit("Initial commit")

        repo.head.commit = commit

        with patch("git.Repo.active_branch") as mock_branch:
            mock_branch.name = "release-candidate"

            version = get_project_version(tmpdir, rc_branches=["release-candidate"])
            assert version.startswith("0.0.1-rc")


def test_tag_name_invalid():
    with tempfile.TemporaryDirectory() as tmpdir:
        repo = Repo.init(tmpdir)
        with open(os.path.join(tmpdir, "test.txt"), "w") as f:
            f.write("test")
        repo.index.add([os.path.join(tmpdir, "test.txt")])
        commit = repo.index.commit("Initial commit")

        repo.create_tag("invalid", commit)

        repo.head.commit = commit

        version = get_project_version(tmpdir)
        assert version == "invalid"


def test_path_not_exists():
    with pytest.raises(FileNotFoundError, match="File .* not found"):
        get_project_version("/non/existent/path")


def test_path_not_directory():
    with tempfile.NamedTemporaryFile() as tmpfile:
        with pytest.raises(ValueError, match="Path .* is not a directory"):
            get_project_version(tmpfile.name)
