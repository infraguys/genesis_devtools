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

import os
import yaml
import rich_click as click
import tempfile

from genesis_devtools import constants as c


def load_config(
    ctx: click.Context, cfg_path: str | None = c.CONFIG_FILE, silent: bool = False
) -> dict:
    """Load configuration from file"""
    try:
        if cfg_path and os.path.exists(cfg_path):
            with open(cfg_path, "r") as f:
                config = yaml.safe_load(f) or {}
        else:
            if not silent:
                endpoint_provided = (
                    ctx.get_parameter_source("endpoint")
                    == click.core.ParameterSource.COMMANDLINE
                )
                user_provided = (
                    ctx.get_parameter_source("user")
                    == click.core.ParameterSource.COMMANDLINE
                )
                password_provided = (
                    ctx.get_parameter_source("password")
                    == click.core.ParameterSource.COMMANDLINE
                )
                access_token_provided = (
                    ctx.get_parameter_source("access_token")
                    == click.core.ParameterSource.COMMANDLINE
                )
                refresh_token_provided = (
                    ctx.get_parameter_source("refresh_token")
                    == click.core.ParameterSource.COMMANDLINE
                )
                if endpoint_provided and (
                    (user_provided and password_provided)
                    or (access_token_provided and refresh_token_provided)
                ):
                    silent = True
            if not silent:
                click.echo(
                    f"You don't have a configuration file {cfg_path}. "
                    f"Please, read the docs https://infraguys.github.io/genesis_devtools/config/"
                )
            config = {}
    except Exception as e:
        raise click.ClickException(f"Error reading settings: {e}")
    return config


def save_config(config: dict, cfg_path: str = c.CONFIG_FILE) -> None:
    """Save configuration to file atomically"""
    try:
        dir_name = os.path.dirname(cfg_path) or "."
        os.makedirs(dir_name, exist_ok=True)

        with tempfile.NamedTemporaryFile(
            mode="w", dir=dir_name, delete=False, suffix=".tmp"
        ) as tmp_f:
            tmp_path = tmp_f.name
            yaml.dump(config, tmp_f, default_flow_style=False)
            tmp_f.flush()
            os.fsync(tmp_f.fileno())

        # Atomically replace the original file
        os.replace(tmp_path, cfg_path)
        os.chmod(cfg_path, 0o600)
    except Exception as e:
        if "tmp_path" in locals() and os.path.exists(tmp_path):
            os.unlink(tmp_path)
        raise click.ClickException(f"Error writing settings: {e}")


def get_current_realm(config: dict) -> dict | None:
    return config.get("current-realm")


def get_realm(config: dict, realm: str | None = None) -> dict:
    if not realm:
        realm = get_current_realm(config)
        if not realm:
            return {}
    if "realms" not in config or realm not in config["realms"]:
        return {}
    return config["realms"][realm]


def get_context(realm: dict, context: str | None = None) -> dict:
    if not realm.get("contexts"):
        return {}
    if not context:
        context = realm.get("current-context")
        if not context:
            raise click.ClickException("No current context")
    if context not in realm["contexts"]:
        raise click.ClickException(
            f"context '{context}' not found for realm '{realm['name']}'"
        )
    return realm["contexts"][context]
