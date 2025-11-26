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
        # Case 1: exclude multiple exact names
        result = _domains_for_backup(
            names=None,
            exclude_names=("vm1", "vm2"),
            raise_on_domain_absence=True,
        )
        assert set(result) == {"stand-01", "stand-02"}

        # Case 2: exclude exact name and wildcard pattern
        result = _domains_for_backup(
            names=None,
            exclude_names=("vm2", "stand-*"),
            raise_on_domain_absence=True,
        )
        assert set(result) == {"vm1"}

        # Case 3: exclude a pattern that matches nothing
        result = _domains_for_backup(
            names=None,
            exclude_names=("nonexistent-*",),
            raise_on_domain_absence=True,
        )
        assert set(result) == all_domains

        # Case 4: exclude all domains
        result = _domains_for_backup(
            names=None,
            exclude_names=("vm*", "stand-*"),
            raise_on_domain_absence=True,
        )
        assert set(result) == set()
