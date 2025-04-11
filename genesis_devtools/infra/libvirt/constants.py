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

import typing as tp


GENESIS_META_TAG = "genesis:genesis"
GENESIS_META_NODE_TYPE_TAG = "genesis:node_type"
GENESIS_META_STAND_TAG = "genesis:stand"
GENESIS_META_CPU_TAG = "genesis:vcpu"
GENESIS_META_MEM_TAG = "genesis:mem"
GENESIS_META_IMAGE_TAG = "genesis:image"
GENESIS_META_NET_TAG = "genesis:network"

BootMode = tp.Literal["hd", "network"]
