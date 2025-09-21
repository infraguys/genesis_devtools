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
import abc
import typing as tp


class EncryptionCreds(tp.NamedTuple):
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
            cls.MIN_LEN <= len(key) <= cls.LEN
            and cls.MIN_LEN <= len(iv) <= cls.LEN
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


class AbstractBackuper(abc.ABC):
    @abc.abstractmethod
    def backup(
        self,
        domains: tp.Collection[str],
        compress: bool = False,
        encryption: EncryptionCreds | None = None,
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

    @abc.abstractmethod
    def rotate(self, limit: int) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def cleanup(self) -> None:
        raise NotImplementedError

    @abc.abstractmethod
    def restore(self, **kwargs: tp.Any) -> None:
        raise NotImplementedError
