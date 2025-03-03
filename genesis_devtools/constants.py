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

PKG_NAME = "genesis_devtools"
LIBVIRT_DEF_POOL_PATH = "/var/lib/libvirt/images"
DEF_GEN_CFG_FILE_NAME = "genesis.yaml"
DEF_GEN_WORK_DIR_NAME = "genesis"
DEF_GEN_OUTPUT_DIR_NAME = "output"
RC_BRANCHES = ("master", "main")
GENESIS_META_TAG = "genesis:genesis"

# ENV vars
ENV_GEN_DEV_KEYS = "GEN_DEV_KEYS"

# Types
ImageProfileType = tp.Literal["ubuntu_24"]
ImageFormatType = tp.Literal["raw"]
NetType = tp.Literal["network", "bridge"]
