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
WORK_DIR="/var/lib/genesis"

SYSTEMD_SERVICE_DIR=/etc/systemd/system/

# Install packages
sudo apt update
sudo apt install build-essential python3.12-dev python3.12-venv \
    cloud-initramfs-growroot irqbalance qemu-guest-agent -y

# Install stuff for bootstrap procedure
sudo mkdir -p "$WORK_DIR/bootstrap/scripts/"
sudo cp "$GC_PATH/artifacts/bootstrap.sh" "$WORK_DIR/bootstrap/"
sudo cp "$GC_PATH/artifacts/genesis-bootstrap.service" $SYSTEMD_SERVICE_DIR

# Clean up
sudo rm -fr "$GC_PATH"
