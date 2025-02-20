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

import abc
import click


class AbstractLogger(abc.ABC):
    """Abstract logger."""

    @abc.abstractmethod
    def error(self, msg: str) -> None:
        """Log an error message."""

    @abc.abstractmethod
    def warn(self, msg: str) -> None:
        """Log a warning message."""

    @abc.abstractmethod
    def info(self, msg: str) -> None:
        """Log an information message."""

    def important(self, msg: str) -> None:
        """Log an important message."""
        self.info(msg)


class ClickLogger(AbstractLogger):
    """Logger based on Click."""

    def error(self, msg: str) -> None:
        """Log an error message."""
        click.secho(msg, fg="red")

    def warn(self, msg: str) -> None:
        """Log a warning message."""
        click.secho(msg, fg="yellow")

    def info(self, msg: str) -> None:
        """Log an information message."""
        click.echo(msg)

    def important(self, msg: str) -> None:
        """Log an important message."""
        click.secho(msg, fg="green")


class DummyLogger(AbstractLogger):
    """Dummy logger."""

    def error(self, msg: str) -> None:
        """Log an error message."""
        pass

    def warn(self, msg: str) -> None:
        """Log a warning message."""
        pass

    def info(self, msg: str) -> None:
        """Log an information message."""
        pass

    def important(self, msg: str) -> None:
        """Log an important message."""
        pass
