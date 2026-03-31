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

from genesis_devtools.cmd.iam.client import commands as client_commands
from genesis_devtools.cmd.iam.idp import commands as idp_commands
from genesis_devtools.cmd.iam.organization import commands as organization_commands
from genesis_devtools.cmd.iam.permission import commands as permission_commands
from genesis_devtools.cmd.iam.permission_binding import (
    commands as permission_binding_commands,
)
from genesis_devtools.cmd.iam.project import commands as project_commands
from genesis_devtools.cmd.iam.role import commands as role_commands
from genesis_devtools.cmd.iam.role_binding import commands as role_binding_commands
from genesis_devtools.cmd.iam.user import commands as user_commands


@click.group("iam", help="iam group in the Genesis installation")
def iam_group():
    pass


iam_group.add_command(client_commands.clients_group)  # noqa
iam_group.add_command(idp_commands.idps_group)  # noqa
iam_group.add_command(organization_commands.organizations_group)  # noqa
iam_group.add_command(permission_commands.permissions_group)  # noqa
iam_group.add_command(permission_binding_commands.permission_bindings_group)  # noqa
iam_group.add_command(project_commands.projects_group)  # noqa
iam_group.add_command(role_commands.roles_group)  # noqa
iam_group.add_command(role_binding_commands.role_bindings_group)  # noqa
iam_group.add_command(user_commands.users_group)  # noqa
