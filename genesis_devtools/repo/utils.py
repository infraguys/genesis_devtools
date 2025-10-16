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
import json
import shutil

from genesis_devtools import utils
from genesis_devtools.repo import base as base_repo
import genesis_devtools.constants as c


def load_repo_driver(
    genesis_cfg_file: str,
    target: str | None,
    project_dir: str,
) -> base_repo.AbstractRepoDriver:
    try:
        gen_config = utils.get_genesis_config(project_dir, genesis_cfg_file)
    except FileNotFoundError:
        raise base_repo.UnableLoadDriverError(
            f"Genesis configuration file not found in {project_dir}"
        )

    if "push" not in gen_config or not gen_config["push"]:
        raise base_repo.UnableLoadDriverError(
            "No push section found in the configuration"
        )

    pushes = gen_config["push"]

    # Select push target
    if target:
        if target not in pushes:
            raise base_repo.UnableLoadDriverError(
                f"Target {target} not found in the configuration"
            )
        push: dict = pushes[target]
    elif len(pushes) == 1:
        push = next(iter(pushes.values()))
    else:
        raise base_repo.UnableLoadDriverError(
            f"Multiple push targets found ({list(pushes.keys())}) in the "
            "configuration. Please specify target."
        )

    if "driver" not in push:
        raise base_repo.UnableLoadDriverError(
            "No driver specified in the configuration"
        )

    # Load driver from entry points
    driver_name = push.pop("driver")
    driver_class = utils.load_from_entry_point(c.EP_REPO_DRIVERS, driver_name)
    driver: base_repo.AbstractRepoDriver = driver_class(**push)

    return driver
