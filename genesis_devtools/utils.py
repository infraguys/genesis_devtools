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

import os
import time
import shutil
import itertools
import typing as tp
from importlib.metadata import entry_points
import yaml

import git

import genesis_devtools.constants as c


def load_from_entry_point(group: str, name: str) -> tp.Any:
    """Load class from entry points."""
    for ep in entry_points():
        if ep.group == group and ep.name == name:
            return ep.load()

    raise RuntimeError(f"No class '{name}' found in entry points {group}")


def get_genesis_config(
    project_dir: str, genesiss_cfg_file: str = c.DEF_GEN_CFG_FILE_NAME
) -> tp.Dict[str, tp.Any]:
    """Find the project configuration file."""
    alternatives = [
        os.path.join(project_dir, genesiss_cfg_file),
        os.path.join(project_dir, c.DEF_GEN_WORK_DIR_NAME, genesiss_cfg_file),
    ]

    for alt in alternatives:
        if os.path.exists(alt):
            with open(alt, "r") as f:
                return yaml.safe_load(f)

    raise FileNotFoundError("Genesis configuration file not found")


def get_keys_by_path_or_env(path: tp.Optional[str]) -> tp.Optional[str]:
    # Keys by path has the first priority
    if path is not None:
        if not os.path.exists(path) or not os.path.isfile(path):
            raise ValueError(f"Invalid path to the developer keys: {path}")

        with open(path) as f:
            return f.read()
    # The second priority is the developer key by env
    elif developer_keys := os.environ.get(c.ENV_GEN_DEV_KEYS):
        return developer_keys

    return


def installation_net_name(name: str) -> str:
    return f"{name}-net"


def installation_bootstrap_name(name: str) -> str:
    return f"{name}-bootstrap"


def installation_name_from_bootstrap(bootstrap_name: str) -> str:
    return bootstrap_name.replace("-bootstrap", "")


def get_project_version(
    path: str, rc_branches=c.RC_BRANCHES, start_version=(0, 0, 0)
) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f"File {path} not found")

    if not os.path.isdir(path):
        raise ValueError(f"Path {path} is not a directory")

    # Open the git repo
    repo = git.Repo(path)

    # If a tag is set, return it as version
    for tag in repo.tags:
        if tag.commit == repo.head.commit:
            return tag.name

    # Find the nearest tag
    nearest_tag = None
    for commit in repo.iter_commits(max_count=100):
        for tag in repo.tags:
            if tag.commit == commit:
                nearest_tag = tag
                break

        if nearest_tag:
            break

    # Get the current version
    if nearest_tag:
        try:
            major, minor, patch = (int(i) for i in nearest_tag.name.split("."))
        except ValueError:
            raise ValueError(
                f"Invalid format for tag {nearest_tag.name}, "
                "expected major.minor.patch version format"
            )
    # Empty repo, start from 0.0.0
    else:
        major, minor, patch = start_version

    # Increment the version
    patch += 1

    hexsha = repo.head.commit.hexsha

    try:
        branch = repo.active_branch.name
    except Exception:
        # Detached head
        branch = None

    date = repo.head.commit.committed_date
    date_repr = "{}{:02}{:02}{:02}{:02}{:02}".format(
        time.gmtime(date).tm_year,
        time.gmtime(date).tm_mon,
        time.gmtime(date).tm_mday,
        time.gmtime(date).tm_hour,
        time.gmtime(date).tm_min,
        time.gmtime(date).tm_sec,
    )

    # Determine the prefix
    if branch in rc_branches:
        prefix = "rc"
    else:
        prefix = "dev"

    return f"{major}.{minor}.{patch}-{prefix}+{date_repr}.{hexsha[:8]}"


def wait_for(
    predicate: tp.Callable,
    timeout: float = 120.0,
    step: float = 0.5,
    title: str | None = None,
) -> None:
    spinner = itertools.cycle(("-", "\\", "|", "/"))
    start = time.monotonic()
    print(f"{title} ... ", end="")
    while not predicate():
        # Print the title and interactive spinner
        if title:
            print(f"\r{title} ... {next(spinner)}", end="")

        if time.monotonic() - start > timeout:
            raise TimeoutError(f"Timeout after {timeout} seconds")
        time.sleep(step)

    print(f"\r{title} ... ok")


def get_version_suffix(version_type: c.VersionSuffixType, **kwargs) -> str:
    if version_type == "latest":
        return "latest"
    elif version_type == "none":
        return ""
    elif version_type == "element":
        if "project_dir" not in kwargs:
            raise ValueError(
                "project_dir is required for element version type"
            )
        project_dir = kwargs["project_dir"]
        return get_project_version(project_dir)

    raise ValueError(f"Invalid version type {version_type}")


def get_directory_size(directory: str) -> int:
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)

        for d in dirnames:
            total_size += get_directory_size(os.path.join(dirpath, d))

    return total_size


def human_readable_size(size: int, decimal_places: int = 2):
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024.0:
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"


def backup_path(backup_dir: str) -> str:
    backup_relative_path = time.strftime("%Y-%m-%d-%H-%M-%S")
    return os.path.join(backup_dir, backup_relative_path)


def compress_dir(
    directory: str, output_dir: str, compression_format: str = "gztar"
) -> None:
    """
    Compresses the specified directory and places the archive in the
    output directory.

    :param directory: The path to the directory to be compressed.
    :param output_dir: The path to the directory where the compressed
                       archive will be placed.
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Define the base name for the archive (without extension)
    archive_base_name = os.path.join(output_dir, os.path.basename(directory))

    # Create a zip archive of the directory
    shutil.make_archive(archive_base_name, compression_format, directory)
