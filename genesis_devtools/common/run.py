# vim: tabstop=4 shiftwidth=4 softtabstop=4
#
# Copyright 2019 Mail.ru Group
#
# All Rights Reserved.
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

import logging
import subprocess

from genesis_devtools.exceptions import RunException

LOG = logging.getLogger(__name__)


def _stringify_command(command: list) -> str:
    return " ".join(command)


class ShellCommandResult:
    def __init__(self, command: str | list, popen: subprocess.Popen):
        super(ShellCommandResult, self).__init__()
        self.command = command
        self._popen = popen
        self._stdout_data = b""
        self._stderr_data = b""

    @property
    def ok(self) -> bool:
        return not bool(self.exit_code)

    @property
    def exit_code(self) -> int:
        self._communicate()
        return self._popen.wait()

    def _communicate(self) -> None:
        if self._popen.returncode is None:
            self._stdout_data, self._stderr_data = self._popen.communicate()

    @property
    def output(self) -> str:
        self._communicate()
        return self._stdout_data.decode()

    @property
    def stderr(self) -> str:
        self._communicate()
        return self._stderr_data.decode()

    def __repr__(self) -> str:
        return "%(class_name)s(command=%(command)s, exit_code=%(exit_code)s)" % {
            "class_name": self.__class__.__name__,
            "command": self.command,
            "exit_code": self._popen.returncode,
        }

    def raise_on_result(self) -> "ShellCommandResult":
        if self.exit_code:
            raise RunException(
                "Error has occurred during shell command execution: %s.", self.stderr
            )
        else:
            return self


def runsh(command: str | list, sudo: bool = False) -> ShellCommandResult:
    if sudo:
        command = "sudo {}".format(command)
    LOG.info("Executing [ %s ]..." % command)
    return ShellCommandResult(
        command=command,
        popen=subprocess.Popen(
            args=command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ),
    )


def run_command(cmd: str | list, check: bool = True) -> subprocess.CompletedProcess:
    """Run shell command and return result."""
    try:
        result = subprocess.run(
            cmd,
            check=check,
            capture_output=True,
            text=True,
        )
        return result
    except subprocess.CalledProcessError as e:
        raise RunException(f"Command failed: {cmd}\nError: {e.stderr}")
