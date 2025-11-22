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
from unittest.mock import patch

from genesis_devtools.cmd.cli import _domains_for_backup


def test_domains_for_backup_exclude_patterns():
    all_domains = {"vm1", "vm2", "stand-01", "stand-02"}

    with patch(
        "genesis_devtools.cmd.cli.libvirt.list_domains",
        return_value=all_domains,
    ):
        result = _domains_for_backup(
            ("vm1", "vm2", "stand-01", "stand-02"),
            ("vm2", "stand-*"),
            raise_on_domain_absence=True,
        )

    assert result == ["vm1"]
