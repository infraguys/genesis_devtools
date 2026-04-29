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

import rich_click as click

from genesis_devtools.cmd.aliases import ClickAliasedGroup
from genesis_devtools.cmd.em.exports import commands as exports_commands
from genesis_devtools.cmd.em.imports import commands as imports_commands
from genesis_devtools.cmd.em.resources import commands as resources_commands
from genesis_devtools.cmd.em.services import commands as services_commands


@click.group(
    "e", cls=ClickAliasedGroup, help="Element group in the Genesis installation"
)
def elements_group():
    pass


elements_group.add_command(exports_commands.exports_group)
elements_group.add_command(imports_commands.imports_group, aliases=["i"])
elements_group.add_command(resources_commands.resources_group, aliases=["r"])
elements_group.add_command(services_commands.services_group, aliases=["s"])
