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

from click.testing import CliRunner

from genesis_devtools.cmd import cli


class TestCli:
    def setup_method(self):
        self.runner = CliRunner()

    def test_dumphelp(self):
        result = self.runner.invoke(cli.genesis, ["dumphelp"])
        assert result.exit_code == 0
