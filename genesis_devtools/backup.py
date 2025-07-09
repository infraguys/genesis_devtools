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
import time
import shutil
import typing as tp
import multiprocessing as mp

import click
import prettytable

from genesis_devtools import utils
from genesis_devtools.infra.libvirt import libvirt


class EnctryptionCreds(tp.NamedTuple):
    LEN = 16
    MIN_LEN = 6

    key: bytes
    iv: bytes

    @classmethod
    def validate_env(cls):
        if not os.environ.get("GEN_DEV_BACKUP_KEY") or not os.environ.get(
            "GEN_DEV_BACKUP_IV"
        ):
            raise ValueError(
                (
                    "Define environment variables GEN_DEV_BACKUP_KEY "
                    "and GEN_DEV_BACKUP_IV."
                )
            )

        key = os.environ["GEN_DEV_BACKUP_KEY"]
        iv = os.environ["GEN_DEV_BACKUP_IV"]

        if (
            cls.MIN_LEN <= len(key) < cls.LEN
            and cls.MIN_LEN <= len(iv) < cls.LEN
        ):
            return

        raise ValueError(
            f"Key and IV must be greater or equal than {cls.MIN_LEN} "
            f"bytes and less or equal to {cls.LEN} bytes."
        )

    @classmethod
    def from_env(cls):
        key = os.environ["GEN_DEV_BACKUP_KEY"]
        iv = os.environ["GEN_DEV_BACKUP_IV"]
        key = key + "0" * (cls.LEN - len(key))
        iv = iv + "0" * (cls.LEN - len(iv))

        return cls(
            key=key.encode(),
            iv=iv.encode(),
        )


def _do_backup(
    backup_path: str,
    domains: tp.List[str],
    compress: bool = False,
    encryption: EnctryptionCreds | None = None,
) -> None:
    os.makedirs(backup_path, exist_ok=True)

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
        os.makedirs(domain_backup_path, exist_ok=True)
        start, end = time.monotonic(), str(None)
        ts, te = time.strftime("%Y-%m-%d %H:%M:%S"), str(None)
        status = "failed"
        duration = str(None)
        size = str(None)

        try:
            libvirt.backup_domain(domain, domain_backup_path)
            end = time.monotonic()
            te = time.strftime("%Y-%m-%d %H:%M:%S")
            status = "success"
            duration = f"{end - start:.2f}"
            size = utils.human_readable_size(
                utils.get_directory_size(domain_backup_path)
            )
            click.secho(f"Backup of {domain} done ({duration} s)", fg="green")
        except Exception:
            click.secho(f"Backup of {domain} failed", fg="red")

        table.add_row([domain, ts, te, f"{duration}", size, status])

    click.echo(f"Summary: {backup_path}")
    click.echo(table)

    if not compress:
        return

    click.echo(f"Compressing {backup_path}")
    compressed_backup_path = f"{backup_path}.tar.gz"
    compress_directory = os.path.dirname(backup_path)
    try:
        utils.compress_dir(backup_path, compress_directory)
    except Exception:
        click.secho(f"Compression of {backup_path} failed", fg="red")
        if os.path.exists(compressed_backup_path):
            os.remove(compressed_backup_path)
        return

    click.secho(f"Compression of {backup_path} done", fg="green")

    if not encryption:
        shutil.rmtree(backup_path)
        return

    click.echo(f"Encrypting {compressed_backup_path}")
    try:
        utils.encrypt_file(
            compressed_backup_path, encryption.key, encryption.iv
        )
    except Exception:
        click.secho(f"Encryption of {compressed_backup_path} failed", fg="red")
        return
    finally:
        shutil.rmtree(backup_path)

    os.remove(compressed_backup_path)
    click.secho(f"Encryption of {compressed_backup_path} done", fg="green")


def _terminate_backup_process(backup_process: mp.Process) -> None:
    """Terminate the backup process and wait for it to terminate."""
    click.secho("Terminating backup process", fg="yellow")
    backup_process.terminate()
    backup_process.join(10)

    if backup_process.exitcode is None:
        click.secho("Backup process timed out!", fg="red")
        backup_process.kill()


def _resume_domains(domains: tp.List[str]) -> None:
    paused_domain = libvirt.list_domains(state="state-paused")

    for domain in set(domains) & set(paused_domain):
        try:
            libvirt.resume_domain(domain)
        except Exception:
            click.secho(f"Resume of {domain} failed", fg="red")


def backup(
    backup_path: str,
    domains: tp.List[str],
    compress: bool = False,
    encryption: EnctryptionCreds | None = None,
    min_free_disk_space_gb: int = 50,
) -> None:
    if not os.path.exists(backup_path):
        os.makedirs(backup_path, exist_ok=True)

    # TODO(akremenetsky): Do check if the potential backup size is
    # less than the free disk space

    free_gb = shutil.disk_usage(backup_path).free >> 30
    if free_gb < min_free_disk_space_gb:
        click.secho(
            f"Unable to start backup due to low disk space {free_gb} GB",
            fg="red",
        )
        return

    # Run the actual backup process in another process.
    # The current process will track the free disk space.
    backup_process = mp.Process(
        target=_do_backup,
        args=(backup_path, domains, compress, encryption),
        daemon=True,
    )
    backup_process.start()

    # Track the minimum free disk space
    # The this threshold is reached, the backup process is stopped
    while True:
        backup_process.join(3)
        if backup_process.exitcode is not None:
            break

        # Track disk space
        free_gb = shutil.disk_usage(backup_path).free >> 30
        if free_gb < min_free_disk_space_gb:
            _terminate_backup_process(backup_process)

            # Remove the backup directory to free up space
            shutil.rmtree(backup_path)
            compressed_backup_path = f"{backup_path}.tar.gz"
            if os.path.exists(compressed_backup_path):
                os.remove(compressed_backup_path)

            _resume_domains(domains)
            click.secho(
                f"Backup process stopped due to low disk space ({free_gb} GB)",
                fg="yellow",
            )
            return

    click.secho("Backup done", fg="green")


def rotate(backups_dir: str, max_count: int) -> None:
    """Remove the oldest backups in the backups_dir according to max_count."""
    # Special value to disable rotation
    if max_count == 0:
        return

    # Compile a regex pattern to match the backup directory or archive names
    pattern = re.compile(r"^\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}")

    # List all items in the backups directory
    all_backups = [
        os.path.join(backups_dir, f)
        for f in os.listdir(backups_dir)
        if pattern.match(f)
    ]

    # Sort the backups by their creation time (older first)
    all_backups.sort(key=lambda x: os.path.getctime(x))

    # If there are more backups than max_count, remove the oldest ones
    if len(all_backups) > max_count:
        backups_to_remove = all_backups[:-max_count]
        for backup in backups_to_remove:
            # Non compressed backups (directory)
            if os.path.isdir(backup):
                shutil.rmtree(backup)

            # Compressed backups
            elif os.path.isfile(backup):
                os.remove(backup)

            click.echo(f"The backup {backup} was rotated")
