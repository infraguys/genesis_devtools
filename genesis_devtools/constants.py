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
import enum
import typing as tp

PKG_NAME = "genesis_devtools"
LIBVIRT_DEF_POOL_PATH = "/var/lib/libvirt/images"
DEF_GEN_CFG_FILE_NAME = "genesis.yaml"
DEF_GEN_WORK_DIR_NAME = "genesis"
DEF_GEN_OUTPUT_DIR_NAME = "output"
RC_BRANCHES = ("master", "main")
ENCRYPTED_EXTENSION = ".encrypted"

# ENV vars
ENV_GEN_DEV_KEYS = "GEN_DEV_KEYS"

# Types
ImageProfileType = tp.Literal["ubuntu_24", "genesis_base"]
ImageFormatType = tp.Literal["raw", "qcow2"]
NetType = tp.Literal["network", "bridge"]
VersionSuffixType = tp.Literal["latest", "none", "element"]
DomainState = tp.Literal["all", "inactive", "state-paused"]
NodeType = tp.Literal["bootstrap", "baremetal"]


class BackupPeriod(str, enum.Enum):
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H3 = "3h"
    H6 = "6h"
    H12 = "12h"
    D1 = "1d"
    D3 = "3d"
    D7 = "7d"

    @property
    def timeout(self) -> int:
        """Return timeout in seconds based on current element in enum."""
        timeouts = {
            self.M1: 60,
            self.M5: 60 * 5,
            self.M15: 60 * 15,
            self.M30: 60 * 30,
            self.H1: 60 * 60,
            self.H3: 60 * 60 * 3,
            self.H6: 60 * 60 * 6,
            self.H12: 60 * 60 * 12,
            self.D1: 60 * 60 * 24,
            self.D3: 60 * 60 * 24 * 3,
            self.D7: 60 * 60 * 24 * 7,
        }
        return timeouts[self]
