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
IMG_ARTS_PATH="$GC_PATH/genesis/images/genesis_base"
WORK_DIR="/var/lib/genesis"
PASSWD="${GEN_USER_PASSWD:-ubuntu}"

SYSTEMD_SERVICE_DIR=/etc/systemd/system/

# Install packages
sudo apt update
sudo apt install build-essential python3.12-dev python3.12-venv \
    cloud-guest-utils irqbalance qemu-guest-agent -y

# Install stuff for bootstrap procedure
sudo mkdir -p "$WORK_DIR/bootstrap/scripts/"
sudo cp "$IMG_ARTS_PATH/bootstrap.sh" "$WORK_DIR/bootstrap/"
sudo cp "$IMG_ARTS_PATH/root_autoresize.sh" "/usr/bin/"
sudo cp "$IMG_ARTS_PATH/genesis-bootstrap.service" $SYSTEMD_SERVICE_DIR
sudo cp "$IMG_ARTS_PATH/genesis-root-autoresize.service" $SYSTEMD_SERVICE_DIR

# Enable genesis core services
sudo systemctl enable genesis-bootstrap genesis-root-autoresize

# Set default password
cat > /tmp/__passwd <<EOF
ubuntu:$PASSWD
EOF

sudo chpasswd < /tmp/__passwd
rm -f /tmp/__passwd

# Clean up
sudo rm -fr "$GC_PATH"
