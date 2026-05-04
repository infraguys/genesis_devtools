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
from genesis_devtools.cmd.compute.hypervisors import commands as hypervisors_commands
from genesis_devtools.cmd.compute.sets import commands as sets_commands


@click.group(
    "compute", cls=ClickAliasedGroup, help="Compute group in the Genesis installation"
)
def compute_group():
    pass


compute_group.add_command(hypervisors_commands.hypervisors_group, aliases=["h"])  # noqa
compute_group.add_command(sets_commands.sets_group, aliases=["s"])  # noqa
