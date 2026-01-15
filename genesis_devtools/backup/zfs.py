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

import abc
import os
import subprocess
import time
import typing as tp

import prettytable

from genesis_devtools.backup import base
from genesis_devtools import logger as logger_base
from genesis_devtools.infra.libvirt import libvirt
from genesis_devtools import utils


def volume_from_disk_path(disk_path: str) -> str:
    """Return ZFS volume name for a given disk path.

    The most common layout for libvirt on ZFS is using zvols under
    ``/dev/zvol/<pool>/<zvol>``. In this case the volume name is the
    path component after ``/dev/zvol/``.

    For any other path we fallback to the basename, which allows using
    plain datasets referenced by mount points, at the cost of relying on
    the caller to provide a correct mapping between disks and datasets.
    """

    if disk_path.startswith("/dev/zvol/"):
        return disk_path[len("/dev/zvol/") :]

    return os.path.basename(disk_path)


def create_snapshot(volume: str, snapshot_name: str) -> None:
    subprocess.run(
        ["sudo", "zfs", "snapshot", f"{volume}@{snapshot_name}"],
        check=True,
    )


def destroy_snapshot(volume: str, snapshot_name: str) -> None:
    subprocess.run(
        ["sudo", "zfs", "destroy", f"{volume}@{snapshot_name}"],
        check=True,
    )


def volume_used_bytes(volume: str) -> int:
    out = subprocess.check_output(
        ["sudo", "zfs", "list", "-Hp", "-o", "used", volume]
    )
    return int(out.decode().strip())


class AbstractZfsBackuper(base.AbstractBackuper):

    ENCRYPTED_SUFFIX = ".encrypted"

    def __init__(
        self,
        snapshot_name: str = "backup",
        logger: logger_base.AbstractLogger | None = None,
    ) -> None:
        self._snapshot_name = snapshot_name
        self._logger = logger or logger_base.ClickLogger()

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
        volumes: tp.Collection[str],
        domain_backup_path: str,
        encryption: base.EncryptionCreds | None = None,
    ) -> None:
        """Backup domain disks for the given ZFS volumes."""

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

        volumes = [volume_from_disk_path(d) for d in disks]

        volumes_with_snapshots = []
        try:
            for volume in volumes:
                create_snapshot(volume, self._snapshot_name)
                volumes_with_snapshots.append(volume)

            self.backup_domain_disks(
                volumes,
                domain_backup_path,
                encryption=encryption,
            )
            status = "success"
        finally:
            for volume in volumes_with_snapshots:
                try:
                    destroy_snapshot(volume, self._snapshot_name)
                except Exception as e:
                    self._logger.error(
                        f"Failed to destroy snapshot for {volume}: {e}"
                    )

            end = time.monotonic()
            duration = f"{end - start:.2f}"
            self._logger.info(
                f"Backup of {domain} done with status {status} ({duration} s)"
            )

        total_size = 0
        for volume in volumes:
            try:
                total_size += volume_used_bytes(volume)
            except Exception:
                continue

        size = utils.human_readable_size(total_size)
        te = time.strftime("%Y-%m-%d %H:%M:%S")

        return domain, ts, te, duration, size, status

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
