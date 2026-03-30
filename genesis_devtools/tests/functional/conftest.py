#    Copyright 2025-2026 Genesis Corporation.
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
#    under the License

import os
from click.testing import CliRunner
import pytest
import yaml

from genesis_devtools.common import utils


@pytest.fixture(scope="session")
def cli_runner():
    return CliRunner()


@pytest.fixture(scope="session")
def cli_config_path():
    return os.path.join(
        utils.PROJECT_PATH,
        "genesis_devtools",
        "tests",
        "functional",
        "utils",
        "genesisctl.yaml",
    )


@pytest.fixture(scope="session")
def cli_config_data(cli_config_path):
    with open(cli_config_path, "r") as f:
        return yaml.safe_load(f)
