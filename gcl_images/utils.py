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
import typing as tp
from importlib.metadata import entry_points
import yaml

import gcl_images.constants as c


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
