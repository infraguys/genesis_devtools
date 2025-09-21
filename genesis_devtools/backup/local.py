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
import typing as tp
import shutil
import multiprocessing as mp

from genesis_devtools.backup import base
from genesis_devtools.backup import qcow
from genesis_devtools import logger as logger_base
from genesis_devtools.infra.libvirt import libvirt
from genesis_devtools import utils
from genesis_devtools import constants as c


class LocalQcowBackuper(qcow.AbstractQcowBackuper):

    def __init__(
        self,
        backup_dir: str,
        snapshot_name: str = "backup_snap",
        logger: logger_base.AbstractLogger | None = None,
        min_free_disk_space_gb: int = 50,
    ):
        super().__init__(backup_dir, snapshot_name, logger)
        self._min_free_disk_space_gb = min_free_disk_space_gb

    def _save_file_to_backup(
        self,
        file_path: str,
        backup_path: str,
        encryption: base.EncryptionCreds | None = None,
    ) -> None:
        shutil.copyfile(file_path, backup_path)

        if encryption:
            utils.encrypt_file(backup_path, encryption.key, encryption.iv)
            os.remove(backup_path)
            self._logger.info(f"Encryption of {backup_path} done")

    def backup_domain_spec(
        self,
        domain_spec: str,
        domain_backup_path: str,
        domain_filename: str = "domain.xml",
        encryption: base.EncryptionCreds | None = None,
    ) -> None:
        """Backup domain specification."""
        # Prepare directory for the backup
        os.makedirs(domain_backup_path, exist_ok=True)

        with open(os.path.join(domain_backup_path, domain_filename), "w") as f:
            f.write(domain_spec)

        if encryption:
            utils.encrypt_file(
                os.path.join(domain_backup_path, domain_filename),
                encryption.key,
                encryption.iv,
            )
            os.remove(os.path.join(domain_backup_path, domain_filename))
            self._logger.info(f"Encryption of {domain_backup_path} done")

    def backup_domain_disks(
        self,
        disks: tp.Collection[str],
        domain_backup_path: str,
        encryption: base.EncryptionCreds | None = None,
    ) -> None:
        """Backup domain disks."""
        for disk in disks:
            disk_name = os.path.basename(disk)
            backup_disk_path = os.path.join(domain_backup_path, disk_name)
            self._save_file_to_backup(disk, backup_disk_path, encryption)

    def backup_domain_snapshot(
        self,
        disks: tp.Collection[str],
        domain_backup_path: str,
        encryption: base.EncryptionCreds | None = None,
    ) -> None:
        """Backup domain snapshot."""
        snapshot_path = self._snapshot_path(disks[0])
        snapshot_backup_path = os.path.join(
            domain_backup_path, os.path.basename(snapshot_path)
        )
        self._save_file_to_backup(
            snapshot_path, snapshot_backup_path, encryption
        )

    def _do_backup(
        self,
        backup_path: str,
        domains: tp.List[str],
        compress: bool = False,
        encryption: base.EncryptionCreds | None = None,
    ) -> None:
        os.makedirs(backup_path, exist_ok=True)

        self.backup_domains(backup_path, domains, encryption)

        if not compress:
            return

        self._logger.info(f"Compressing {backup_path}")
        compressed_backup_path = f"{backup_path}{self.COMPRESS_SUFFIX}"
        compress_directory = os.path.dirname(backup_path)
        try:
            utils.compress_dir(backup_path, compress_directory)
        except Exception:
            self._logger.error(f"Compression of {backup_path} failed")
            if os.path.exists(compressed_backup_path):
                os.remove(compressed_backup_path)
            return

        self._logger.info(f"Compression of {backup_path} done")
        shutil.rmtree(backup_path)

    def _terminate_backup_process(self, backup_process: mp.Process) -> None:
        """Terminate the backup process and wait for it to terminate."""
        self._logger.warn("Terminating backup process")
        backup_process.terminate()
        backup_process.join(5)

        if backup_process.exitcode is None:
            self._logger.error("Backup process timed out!")
            backup_process.kill()

    def _snapshot_path(self, disk_path: str) -> str:
        return ".".join(disk_path.split(".")[:-1]) + f".{self._snapshot_name}"

    def _cleanup_after_failure(
        self, domains: tp.Collection[str], backup_path: str
    ) -> None:
        # Remove the backup directory to free up space
        shutil.rmtree(backup_path)
        compressed_backup_path = f"{backup_path}{self.COMPRESS_SUFFIX}"
        if os.path.exists(compressed_backup_path):
            os.remove(compressed_backup_path)

        # Merge snapshots and delete them
        for domain in domains:
            disks = libvirt.get_domain_disks(domain)

            if len(disks) == 0:
                self._logger.warn(f"No disks found for domain {domain}")
                continue

            snapshot_path = disks[0]

            if os.path.exists(snapshot_path):
                # Find the original disk
                for disk_format in ("raw", "qcow2"):
                    disk_path = (
                        ".".join(disks[0].split(".")[:-1]) + disk_format
                    )
                    if os.path.exists(disk_path):
                        break
                else:
                    self._logger.error(
                        "The original disk hasn't been found for domain "
                        f"{domain}"
                    )
                    continue

                try:
                    libvirt.merge_snapshot(domain, disk_path, snapshot_path)
                    os.remove(snapshot_path)
                    libvirt.delete_snapshot(domain, self._snapshot_name)
                except Exception:
                    self._logger.error(
                        f"Failed to merge snapshot {snapshot_path} "
                        f"for domain {domain}"
                    )

    def backup(
        self,
        domains: tp.Collection[str],
        compress: bool = False,
        encryption: base.EncryptionCreds | None = None,
        **kwargs: tp.Any,
    ) -> None:
        """Backup the specified domains.

        Args:
            domains: List of domain names to backup.
            compress: Whether to compress the backup.
            encryption: Encryption credentials. If it's specified,
                the backup will be encrypted.
            **kwargs: Additional keyword arguments.
        """
        backup_path = utils.backup_path(self._backup_dir)
        os.makedirs(backup_path, exist_ok=True)

        # TODO(akremenetsky): Do check if the potential backup size is
        # less than the free disk space

        free_gb = shutil.disk_usage(backup_path).free >> c.GB_SHIFT
        if free_gb < self._min_free_disk_space_gb:
            self._logger.error(
                f"Unable to start backup due to low disk space {free_gb} GB",
            )
            return

        # Run the actual backup process in another process.
        # The current process will track the free disk space.
        backup_process = mp.Process(
            target=self._do_backup,
            args=(backup_path, domains, compress, encryption),
            daemon=True,
        )
        backup_process.start()

        # Track the minimum free disk space
        # If this threshold is reached, the backup process is stopped
        while True:
            backup_process.join(2)
            if backup_process.exitcode is not None:
                break

            # Track disk space
            free_gb = shutil.disk_usage(backup_path).free >> c.GB_SHIFT
            if free_gb < self._min_free_disk_space_gb:
                self._terminate_backup_process(backup_process)
                self._cleanup_after_failure(domains, backup_path)

                # _resume_domains(domains)
                self._logger.error(
                    f"Backup process stopped due to low disk space ({free_gb} GB)",
                )
                return

        self._logger.info("Backup finished")

    def rotate(self, limit: int = 5) -> None:
        """Keep the last limit backups."""
        # Special value to disable rotation
        if limit == 0:
            return

        # List all items in the backups directory
        all_backups = [
            os.path.join(self._backup_dir, f)
            for f in os.listdir(self._backup_dir)
            if self._backup_dir_pattern.match(f)
        ]

        # Sort the backups by their creation time (older first)
        all_backups.sort(key=lambda x: os.path.getctime(x))

        # If there are more backups than limit, remove the oldest ones
        if len(all_backups) > limit:
            backups_to_remove = all_backups[:-limit]
            for backup in backups_to_remove:
                # Non compressed backups (directory)
                if os.path.isdir(backup):
                    shutil.rmtree(backup)

                # Compressed backups
                elif os.path.isfile(backup):
                    os.remove(backup)

                self._logger.info(f"The backup {backup} was rotated")

    def cleanup(self) -> None:
        raise NotImplementedError()

    def restore(self, backup_path: str) -> None:
        raise NotImplementedError()
