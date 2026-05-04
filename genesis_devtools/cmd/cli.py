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

from requests.exceptions import RequestException
import typing as tp
import uuid as sys_uuid

import rich_click as click

from bazooka import exceptions as bazooka_exc

import genesis_devtools.constants as c
from genesis_devtools.common.cmd_context import ContextObject

from genesis_devtools.cmd.iam.auth import commands as auth_commands

from genesis_devtools.cmd.iam import iam_group
from genesis_devtools.cmd.secret import secret_group
from genesis_devtools.cmd.vs import vs_group
from genesis_devtools.cmd.compute import compute_group
from genesis_devtools.cmd.compute.nodes import commands as nodes_commands
from genesis_devtools.cmd.realms.commands import realms_group
from genesis_devtools.cmd.version import commands as version_commands
from genesis_devtools.cmd.stand import commands as stand_commands
from genesis_devtools.cmd.stand import utils_commands

from genesis_devtools.cmd.em import elements_group
from genesis_devtools.cmd.em.builder import commands as builder_commands
from genesis_devtools.cmd.em.manifests import commands as manifests_commands
from genesis_devtools.cmd.em.elements import commands as elements_commands

from genesis_devtools.cmd.initialization import commands as initialization_commands
from genesis_devtools.cmd.configs import commands as configs_commands
from genesis_devtools.cmd.repo import commands as repo_commands

from genesis_devtools.cmd.settings import commands as settings_commands
from genesis_devtools.cmd.settings import config as settings_config

from genesis_devtools.cmd.aliases import ClickAliasedGroup


@click.group(
    cls=ClickAliasedGroup,
    invoke_without_command=True,
    help="Provides all the necessary tools for work with Genesis Platform",
)
@click.option(
    "--config",
    default=c.CONFIG_FILE,
    show_default=True,
    type=click.Path(exists=False, dir_okay=False),
    help="Path to YAML config file",
)
@click.option(
    "-e",
    "--endpoint",
    default="http://localhost:11010",
    show_default=True,
    help="Genesis API endpoint",
)
@click.option(
    "-u",
    "--user",
    default=None,
    help="Client user name",
)
@click.option(
    "-p",
    "--password",
    default=None,
    help="Password for the client user",
)
@click.option(
    "-a",
    "--access_token",
    default=None,
    help="access token for the client user",
)
@click.option(
    "--refresh_token",
    default=None,
    help="refresh token for the client user",
)
@click.option(
    "-r",
    "--realm",
    type=str,
    help="Name of the realm",
)
@click.option(
    "-c",
    "--context",
    type=str,
    help="Name of the context",
)
@click.option(
    "-P",
    "--project-id",
    default=None,
    type=click.UUID,
    help="Project ID for the client user",
)
@click.option(
    "-vvv",
    "--verbose",
    show_default=True,
    is_flag=True,
    help="Verbose logs",
)
@click.option(
    "-i",
    "--developer-key-path",
    default=None,
    help="Path to developer public key",
)
@click.option(
    "-s",
    "--silent",
    show_default=True,
    is_flag=True,
    help="Do not print messages, warnings or errors",
)
@click.pass_context
def genesis(
    ctx: click.Context,
    config: str,
    endpoint: str,
    user: str | None,
    password: str | None,
    access_token: str | None,
    refresh_token: str | None,
    realm: str | None,
    context: str | None,
    project_id: sys_uuid.UUID | None,
    verbose: bool | None,
    developer_key_path: str | None,
    silent: bool | None,
) -> None:
    if not ctx.invoked_subcommand:
        click.echo(ctx.get_help())
        return
    if verbose:
        import logging

        logging.basicConfig(level=logging.DEBUG)
    # Load configuration from file (if exists)
    cfg_path = config if config else None
    cfg = settings_config.load_config(ctx, cfg_path, silent)

    realm_conf = settings_config.get_realm(cfg, realm)
    context_conf = settings_config.get_context(realm_conf, context)

    def _get_final_value(
        param_name: str, cli_value: tp.Any, base_conf: dict, direct_conf: dict
    ) -> tp.Any:
        if (
            ctx.get_parameter_source(param_name)
            == click.core.ParameterSource.COMMANDLINE
        ):
            return cli_value
        return direct_conf.get(param_name, base_conf.get(param_name, cli_value))

    final_endpoint = _get_final_value("endpoint", endpoint, cfg, realm_conf)
    final_check_updates = _get_final_value("check_updates", False, cfg, realm_conf)
    final_user = _get_final_value("user", user, cfg, context_conf)
    final_password = _get_final_value("password", password, cfg, context_conf)
    final_access_token = _get_final_value(
        "access_token", access_token, cfg, context_conf
    )
    final_refresh_token = _get_final_value(
        "refresh_token", refresh_token, cfg, context_conf
    )
    final_developer_key_path = _get_final_value(
        "developer_key_path", developer_key_path, cfg, {}
    )
    if final_check_updates and version_commands.should_check_version():
        version_commands.check_latest_version()
        version_commands.save_last_check_time()

    final_project_id = _get_final_value("project_id", project_id, cfg, context_conf)
    scope = f"project:{final_project_id}" if final_project_id else None

    auth_data = dict(
        endpoint=final_endpoint,
        username=final_user,
        password=final_password,
        access_token=final_access_token,
        refresh_token=final_refresh_token,
        scope=scope,
    )
    ctx.obj = ContextObject(auth_data, config, final_developer_key_path, cfg)


@genesis.command(help="tool for creating docs files for cli commands", hidden=True)
def dumphelp() -> None:
    from genesis_devtools.common.md_click import dump_helper  # type: ignore

    dump_helper(genesis)
    return None


genesis.add_command(auth_commands.auth_group)  # noqa

genesis.add_command(iam_group)  # noqa
genesis.add_command(secret_group, aliases=["s"])  # noqa
genesis.add_command(compute_group, aliases=["c"])  # noqa
genesis.add_command(nodes_commands.nodes_group, aliases=["n"])  # noqa

genesis.add_command(vs_group)  # noqa
genesis.add_command(realms_group)  # noqa

genesis.add_command(elements_group)  # noqa
genesis.add_command(manifests_commands.manifests_group, aliases=["m"])  # noqa
genesis.add_command(elements_commands.elements_group, aliases=["e"])  # noqa
genesis.add_command(builder_commands.build_cmd)  # noqa

genesis.add_command(configs_commands.configs_group)  # noqa
genesis.add_command(settings_commands.settings_group)  # noqa
genesis.add_command(repo_commands.repository_group)  # noqa
genesis.add_command(repo_commands.push_cmd)  # noqa

genesis.add_command(initialization_commands.init_cmd)  # noqa

genesis.add_command(version_commands.version_cmd)  # noqa
genesis.add_command(version_commands.latest_cmd)  # noqa
genesis.add_command(version_commands.get_project_version_cmd)  # noqa

genesis.add_command(stand_commands.bootstrap_cmd)  # noqa
genesis.add_command(stand_commands.backup_cmd)  # noqa
genesis.add_command(stand_commands.backup_decrypt_cmd)  # noqa

genesis.add_command(utils_commands.openapi_spec)  # noqa
genesis.add_command(utils_commands.hello)  # noqa
genesis.add_command(utils_commands.autocomplete_help)  # noqa
genesis.add_command(utils_commands.autocomplete)  # noqa
genesis.add_command(utils_commands.sync)  # noqa


if __name__ == "__main__":
    try:
        genesis()
    except bazooka_exc.BaseHTTPException as e:
        click.secho(f"Error: [{e.code}] {e.cause.response.text}", fg="red")
    except RequestException as e:
        if e.response is not None:
            click.secho(
                f"Error: [{e.response.status_code}] {e.response.text}", fg="red"
            )
        click.secho(f"Error: {e}", fg="red")
    except (ValueError, FileNotFoundError) as e:
        click.secho(f"Error: {e}", fg="red")
