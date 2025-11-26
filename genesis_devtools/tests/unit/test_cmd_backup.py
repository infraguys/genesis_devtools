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
from unittest.mock import MagicMock, patch

import click
import pytest

from genesis_devtools.cmd.cli import backup_cmd


class TestCmdBackup:

    def test_oneshot_uses_local_backuper_when_no_config(
        self,
    ) -> None:
        # Arrange
        domains = ["vm1", "vm2"]

        backuper_mock = MagicMock()
        # Local backuper constructor should return our mock instance
        with patch(
            "genesis_devtools.cmd.cli.backup_local.LocalQcowBackuper",
            return_value=backuper_mock,
        ) as local_backuper_ctor, patch(
            "genesis_devtools.cmd.cli._domains_for_backup",
            return_value=domains,
        ) as domains_for_backup, patch(
            "genesis_devtools.cmd.cli.utils.load_driver"
        ) as load_driver:
            # Act
            backup_cmd.callback(
                config=None,
                name=("vm1", "vm2"),
                exclude_name=None,
                backup_dir="/tmp/backups",
                period="1d",
                offset=None,
                start=None,
                oneshot=True,
                compress=True,
                encrypt=False,
                min_free_space=123,
                rotate=7,
            )

        # Assert
        local_backuper_ctor.assert_called_once_with(
            backup_dir="/tmp/backups", min_free_disk_space_gb=123
        )
        load_driver.assert_not_called()
        domains_for_backup.assert_called_once_with(
            ("vm1", "vm2"), None, raise_on_domain_absence=True
        )
        backuper_mock.backup.assert_called_once()
        # backup(domains, compress, encryption)
        called_args, called_kwargs = backuper_mock.backup.call_args
        assert called_args[0] == domains
        assert called_args[1] is True
        assert called_args[2] is None

    def test_oneshot_uses_configured_driver_when_config_path_provided(
        self,
    ) -> None:
        # Arrange
        domains = ["vmX"]
        backuper_mock = MagicMock()

        with patch(
            "genesis_devtools.cmd.cli.utils.load_driver",
            return_value=backuper_mock,
        ) as load_driver, patch(
            "genesis_devtools.cmd.cli._domains_for_backup",
            return_value=domains,
        ) as domains_for_backup, patch(
            "genesis_devtools.cmd.cli.backup_local.LocalQcowBackuper"
        ) as local_backuper_ctor:
            # Act
            backup_cmd.callback(
                config="/path/to/config.yaml",
                name=("vmX",),
                exclude_name=None,
                backup_dir=".",
                period="1d",
                offset=None,
                start=None,
                oneshot=True,
                compress=False,
                encrypt=False,
                min_free_space=50,
                rotate=5,
            )

        # Assert configured driver used, not local backuper
        load_driver.assert_called_once_with("/path/to/config.yaml")
        local_backuper_ctor.assert_not_called()
        domains_for_backup.assert_called_once_with(
            ("vmX",), None, raise_on_domain_absence=True
        )
        backuper_mock.backup.assert_called_once_with(domains, False, None)

    def test_oneshot_with_exclude_names_filters_domains(self) -> None:
        # Arrange
        filtered_domains = ["vm1"]
        backuper_mock = MagicMock()

        with patch(
            "genesis_devtools.cmd.cli.backup_local.LocalQcowBackuper",
            return_value=backuper_mock,
        ) as local_backuper_ctor, patch(
            "genesis_devtools.cmd.cli._domains_for_backup",
            return_value=filtered_domains,
        ) as domains_for_backup, patch(
            "genesis_devtools.cmd.cli.utils.load_driver"
        ) as load_driver:
            # Act
            backup_cmd.callback(
                config=None,
                name=None,
                exclude_name=("vm2", "stand-*"),
                backup_dir="/tmp/backups",
                period="1d",
                offset=None,
                start=None,
                oneshot=True,
                compress=True,
                encrypt=False,
                min_free_space=50,
                rotate=5,
            )

        # Assert
        local_backuper_ctor.assert_called_once_with(
            backup_dir="/tmp/backups", min_free_disk_space_gb=50
        )
        load_driver.assert_not_called()
        domains_for_backup.assert_called_once_with(
            None, ("vm2", "stand-*"), raise_on_domain_absence=True
        )
        backuper_mock.backup.assert_called_once_with(
            filtered_domains, True, None
        )

    def test_oneshot_raises_if_name_and_exclude_name_given(self) -> None:
        # Act / Assert
        with pytest.raises(
            click.UsageError,
            match="Cannot specify both --name and --no/--exclude-name",
        ):
            backup_cmd.callback(
                config=None,
                name=("vm1",),
                exclude_name=("vm2",),
                backup_dir="/tmp/backups",
                period="1d",
                offset=None,
                start=None,
                oneshot=True,
                compress=True,
                encrypt=False,
                min_free_space=50,
                rotate=5,
            )

    def test_encrypt_env_missing_raises_usage_error_before_backup(
        self,
    ) -> None:
        # Arrange: local backuper returned but backup should never be called
        backuper_mock = MagicMock()
        with patch(
            "genesis_devtools.cmd.cli.backup_local.LocalQcowBackuper",
            return_value=backuper_mock,
        ), patch(
            "genesis_devtools.cmd.cli.backup_base.EncryptionCreds.validate_env",
            side_effect=ValueError("invalid env"),
        ):
            # Act / Assert
            with pytest.raises(click.UsageError):
                backup_cmd.callback(
                    config=None,
                    name=(),
                    exclude_name=None,
                    backup_dir="/tmp/backups",
                    period="1d",
                    offset=None,
                    start=None,
                    oneshot=True,
                    compress=True,
                    encrypt=True,
                    min_free_space=50,
                    rotate=5,
                )

        backuper_mock.backup.assert_not_called()

    def test_encrypt_env_ok_passes_encryption_object_to_backup(self) -> None:
        # Arrange
        domains = ["vm1"]
        backuper_mock = MagicMock()
        encryption_obj = MagicMock()

        with patch(
            "genesis_devtools.cmd.cli.backup_local.LocalQcowBackuper",
            return_value=backuper_mock,
        ), patch(
            "genesis_devtools.cmd.cli._domains_for_backup",
            return_value=domains,
        ), patch(
            "genesis_devtools.cmd.cli.backup_base.EncryptionCreds.validate_env",
            return_value=None,
        ), patch(
            "genesis_devtools.cmd.cli.backup_base.EncryptionCreds.from_env",
            return_value=encryption_obj,
        ):
            # Act
            backup_cmd.callback(
                config=None,
                name=("vm1",),
                exclude_name=None,
                backup_dir="/tmp/backups",
                period="1d",
                offset=None,
                start=None,
                oneshot=True,
                compress=False,
                encrypt=True,
                min_free_space=50,
                rotate=5,
            )

        # Assert encryption object passed as third positional arg
        backuper_mock.backup.assert_called_once()
        args, _ = backuper_mock.backup.call_args
        assert args[0] == domains
        assert args[1] is False
        assert args[2] == encryption_obj

    def test_periodic_with_start_runs_once_and_waits_until_start(self) -> None:
        # Arrange fixed times: now = 09:59:00, start = 10:00:00 -> delta = 60s
        import time as _time

        now_struct = _time.strptime("2025-01-01 09:59:00", "%Y-%m-%d %H:%M:%S")
        now_ts = int(_time.mktime(now_struct))

        start_struct = _time.strptime("10:00:00", "%H:%M:%S")

        domains = ["vmA"]
        backuper_mock = MagicMock()

        with patch(
            "genesis_devtools.cmd.cli.backup_local.LocalQcowBackuper",
            return_value=backuper_mock,
        ), patch(
            "genesis_devtools.cmd.cli._domains_for_backup",
            return_value=domains,
        ) as domains_for_backup, patch(
            "genesis_devtools.cmd.cli.time.time",
            side_effect=[now_ts, now_ts],
        ), patch(
            "genesis_devtools.cmd.cli.time.localtime",
            return_value=now_struct,
        ), patch(
            "genesis_devtools.cmd.cli.time.sleep"
        ) as sleep_mock:
            # Make rotate raise to stop after first iteration
            backuper_mock.rotate.side_effect = SystemExit

            # Act
            with pytest.raises(SystemExit):
                backup_cmd.callback(
                    config=None,
                    name=("vmA",),
                    exclude_name=None,
                    backup_dir="/tmp/backups",
                    period="1d",
                    offset=None,
                    start=start_struct,
                    oneshot=False,
                    compress=False,
                    encrypt=False,
                    min_free_space=50,
                    rotate=1,
                )

        # Assert: waited 60 seconds until start time
        sleep_mock.assert_any_call(60)
        # And then it attempted one backup cycle
        domains_for_backup.assert_called_with(("vmA",), None)
        backuper_mock.backup.assert_called_once_with(domains, False, None)
