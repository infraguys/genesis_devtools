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

# Detect root partition
ROOT_PART=$(findmnt -n -o SOURCE /)
PARTITION_NAME=$(echo "$ROOT_PART" | awk -F/ '{print $NF}')

# Wait RW mode for the root partition
while [[ "$(findmnt / -o options -n | grep -E "^ro,|,ro,|,ro$")" != "" ]]
do
    echo "Waiting for root partition to be in RW mode"
    sleep 2
done

# Detect root device
for blk in $(ls /sys/block/ | grep -v loop); do
  if [ -d "/sys/block/$blk/$PARTITION_NAME" ]; then
    ROOT_DEV="/dev/$blk"
    PARTITION_NUMBER=$(cat /sys/block/$blk/$PARTITION_NAME/partition)
    break
  fi
done

if [ -z "$ROOT_DEV" ]; then
  echo "Unable to detect root device"
  exit 1
fi

echo "Detected root device: $ROOT_DEV"
echo "Detected partition name: $PARTITION_NAME"
echo "Detected partition number: $PARTITION_NUMBER"

# Grow root partition and resize filesystem 
growpart $ROOT_DEV $PARTITION_NUMBER || true
resize2fs /dev/$PARTITION_NAME
