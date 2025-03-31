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

WORK_DIR="/var/lib/genesis/bootstrap"
DONE_PATH="$WORK_DIR/__done"
BUILD_MAC="52:54:00:12:34:56"

# Ignore image building for bootstrap scripts
for iface in $(ls /sys/class/net/) ; do
  if [ "$(cat /sys/class/net/$iface/address)" == "$BUILD_MAC" ] ; then
    echo "In the image build process, skip bootstrap scripts"
    exit 0
  fi
done


for EXECUTABLE in $(ls $WORK_DIR/scripts/ | sort)
do
  echo "Start - $WORK_DIR/scripts/$EXECUTABLE"
  "$WORK_DIR/scripts/$EXECUTABLE"
  echo "Completed - $WORK_DIR/scripts/$EXECUTABLE"
done


echo "Done" > "$DONE_PATH"