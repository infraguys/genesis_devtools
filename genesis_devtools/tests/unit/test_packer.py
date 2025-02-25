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

from genesis_devtools.builder import packer


class TestPackerVariable:

    def test_packer_var_int(self) -> None:
        var = packer.PackerVariable(name="cpus", value=1)
        assert var.render() == "cpus = 1"

    def test_packer_var_str(self) -> None:
        var = packer.PackerVariable(name="disk_size", value="10G")
        assert var.render() == 'disk_size = "10G"'

    def test_packer_content(self) -> None:
        content = packer.PackerVariable.variable_file_content(
            {"disk_size": "10G", "cpus": 1, "memory": 1024}
        )
        assert content == 'disk_size = "10G"\ncpus = 1\nmemory = 1024'
