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
from __future__ import annotations

import os
import re
import abc
import typing as tp
import time

import prettytable

from genesis_devtools.backup import base
from genesis_devtools import logger as logger_base
from genesis_devtools.infra.libvirt import libvirt
from genesis_devtools import utils


class AbstractQcowBackuper(base.AbstractBackuper):

    COMPRESS_SUFFIX = ".tar.gz"
    ENCRYPTED_SUFFIX = ".encrypted"

    # Compile a regex pattern to match the backup directory or
    # archive names
    _backup_dir_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}")

    def __init__(
        self,
        backup_dir: str,
        snapshot_name: str = "backup_snap",
        logger: logger_base.AbstractLogger | None = None,
    ):
        self._backup_dir = backup_dir
        self._logger = logger or logger_base.ClickLogger()
        self._snapshot_name = snapshot_name

    def _snapshot_path(self, disk_path: str) -> str:
        return ".".join(disk_path.split(".")[:-1]) + f".{self._snapshot_name}"

    def _backup_domain(
        self,
        domain: str,
        domain_backup_path: str,
        encryption: base.EncryptionCreds | None = None,
    ) -> tuple[str, str, str, str, str, str]:
        start, end = time.monotonic(), str(None)
        ts, te = time.strftime("%Y-%m-%d %H:%M:%S"), str(None)
        status = "failed"
        duration = str(None)

        domain_spec = libvirt.domain_xml(domain)
        self.backup_domain_spec(
            domain_spec,
            domain_backup_path,
            encryption=encryption,
        )

        disks = libvirt.get_domain_disks(domain)

        if len(disks) == 0:
            self._logger.error(f"No disks found for domain {domain}")
            return domain, ts, te, duration, "0", status

        # If the domain is active, create a snapshot to have an ability
        # to copy disks for running domain.
        if libvirt.is_active_domain(domain):
            libvirt.create_snapshot(domain, self._snapshot_name)
            has_snapshot = True
        else:
            has_snapshot = False

        try:
            # Copy disks
            self.backup_domain_disks(
                disks,
                domain_backup_path,
                encryption=encryption,
            )

            status = "success"
        finally:
            if has_snapshot:
                for i, disk in enumerate(disks):
                    device = "vd" + chr(ord("a") + i)
                    snapshot_path = self._snapshot_path(disk)
                    libvirt.merge_disk_snapshot(
                        domain, device, disk, snapshot_path
                    )

                # Copy snapshot
                self.backup_domain_snapshot(
                    disks,
                    domain_backup_path,
                    encryption=encryption,
                )

                for disk in disks:
                    snapshot_path = self._snapshot_path(disk)
                    os.remove(snapshot_path)
                libvirt.delete_snapshot(domain, self._snapshot_name)
            end = time.monotonic()
            duration = f"{end - start:.2f}"
            self._logger.info(
                f"Backup of {domain} done with status {status} ({duration} s)"
            )

        total_size = 0
        for disk in disks:
            total_size += os.path.getsize(disk)

        size = utils.human_readable_size(total_size)
        te = time.strftime("%Y-%m-%d %H:%M:%S")

        return domain, ts, te, duration, size, status

    @abc.abstractmethod
    def backup_domain_spec(
        self,
        domain_spec: str,
        domain_backup_path: str,
        domain_filename: str = "domain.xml",
        encryption: base.EncryptionCreds | None = None,
    ) -> None:
        """Backup domain specification."""

    @abc.abstractmethod
    def backup_domain_disks(
        self,
        disks: tp.Collection[str],
        domain_backup_path: str,
        encryption: base.EncryptionCreds | None = None,
    ) -> None:
        """Backup domain disks."""

    def backup_domain_snapshot(
        self,
        disks: tp.Collection[str],
        domain_backup_path: str,
        encryption: base.EncryptionCreds | None = None,
    ) -> None:
        """Backup domain snapshot."""
        # Nothing to do by default. It's not a mandatory step.
        pass

    def backup_domains(
        self,
        backup_path: str,
        domains: tp.List[str],
        encryption: base.EncryptionCreds | None = None,
    ) -> None:
        table = prettytable.PrettyTable()
        table.field_names = [
            "domain",
            "time start",
            "time end",
            "duration (s)",
            "size",
            "status",
        ]

        for domain in domains:
            domain_backup_path = os.path.join(backup_path, domain)

            try:
                domain, ts, te, duration, size, status = self._backup_domain(
                    domain,
                    domain_backup_path,
                    encryption=encryption,
                )
            except Exception as e:
                self._logger.error(f"Failed to backup domain {domain}: {e}")
                continue

            table.add_row([domain, ts, te, duration, size, status])

        self._logger.info(f"Summary: {backup_path}")
        self._logger.info(table)
