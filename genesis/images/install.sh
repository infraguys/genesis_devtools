#!/usr/bin/env bash

# Copyright 2025 Genesis Corporation
#
# All Rights Reserved.
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

set -eu
set -x
set -o pipefail

GC_PATH="/opt/genesis_devtools"
GC_CFG_DIR=/etc/genesis_devtools
VENV_PATH="$GC_PATH/.venv"

GC_PG_USER="genesis_core"
GC_PG_PASS="genesis_core"
GC_PG_DB="genesis_core"

SYSTEMD_SERVICE_DIR=/etc/systemd/system/

# Install packages
sudo apt update
sudo apt install build-essential python3.12-dev python3.12-venv -y

# Install genesis devtools
sudo mkdir -p $GC_CFG_DIR
mkdir -p "$VENV_PATH"
python3 -m venv "$VENV_PATH"
source "$GC_PATH"/.venv/bin/activate
pip install pip --upgrade
pip install -r "$GC_PATH"/requirements.txt
pip install -e "$GC_PATH"

# Create links to venv
sudo ln -sf "$VENV_PATH/bin/genesis" "/usr/bin/genesis"
