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
import yaml
import rich_click as click
import json

from genesis_devtools import constants as c


@click.group("settings", help="Modify genesis settings files")
def settings_group():
    pass


def load_config(cfg_path: str | None = c.CONFIG_FILE) -> dict:
    """Load configuration from file"""
    try:
        if cfg_path and os.path.exists(cfg_path):
            with open(cfg_path, "r") as f:
                config = yaml.safe_load(f) or {}
        else:
            config = {}
    except Exception as e:
        raise click.ClickException(f"Error reading settings: {e}")
    return config


def _save_config(config: dict, cfg_path: str = c.CONFIG_FILE) -> None:
    """Save configuration to file"""
    try:
        with open(cfg_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
    except Exception as e:
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
    if "contexts" not in realm:
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


@settings_group.command("view", help="Display merged genesis settings")
@click.option(
    "--raw",
    is_flag=True,
    help="Display the raw merge of the genesis config",
)
@click.pass_context
def view(ctx: click.Context, raw: bool) -> None:
    config = load_config(ctx.obj.cfg_path)

    if raw:
        click.echo(yaml.dump(config, default_flow_style=False))
        return

    click.echo(yaml.dump(config, default_flow_style=False))


@settings_group.command("current-realm", help="Display the current-realm")
@click.pass_context
def current_realm(ctx: click.Context) -> None:
    config = load_config(ctx.obj.cfg_path)
    realm = get_current_realm(config)
    click.echo(realm if realm else "No current realm set")


@settings_group.command("use-realm", help="Set the current-realm in a settings file")
@click.argument("realm", type=str, required=True)
@click.pass_context
def use_realm(ctx: click.Context, realm: str) -> None:
    config = load_config(ctx.obj.cfg_path)

    if "realms" not in config or realm not in config["realms"]:
        raise click.ClickException(f"realm '{realm}' not found")

    config["current-realm"] = realm
    _save_config(config, ctx.obj.cfg_path)
    click.echo(f"Switched to realm '{realm}'")


@settings_group.command("list-realms", help="Describe one or many realms")
@click.option(
    "-o",
    "--output",
    type=click.Choice(["json", "yaml"]),
    default="yaml",
    help="Output format",
)
@click.pass_context
def list_realms(ctx: click.Context, output: str) -> None:
    config = load_config(ctx.obj.cfg_path)

    if output == "json":
        click.echo(json.dumps(config.get("realms", {}), indent=2))
    else:
        click.echo(yaml.dump(config.get("realms", {}), default_flow_style=False))


@settings_group.command("set-realm", help="Set a realm entry in settings")
@click.argument("realm", type=str, required=True)
@click.option(
    "-e",
    "--endpoint",
    required=True,
    type=str,
    help="Endpoint for the realm",
)
@click.option(
    "-c",
    "--check_updates",
    is_flag=True,
    default=True,
    help="Check for updates on startup",
)
@click.option(
    "-s",
    "--skip_tls_verify",
    is_flag=True,
    default=True,
    help="Skip TLS certificate verification",
)
@click.pass_context
def set_realm(
    ctx: click.Context,
    realm: str,
    endpoint: str | None,
    check_updates: bool,
    skip_tls_verify: bool,
) -> None:
    config = load_config(ctx.obj.cfg_path)

    if "realms" not in config:
        config["realms"] = {}

    realm_config = {
        "endpoint": endpoint,
        "check_updates": check_updates,
        "skip_tls_verify": skip_tls_verify,
    }

    config["realms"][realm] = realm_config
    _save_config(config, ctx.obj.cfg_path)
    click.echo(f"realm '{realm}' set")


@settings_group.command(
    "delete-realm", help="Delete the specified realm from the settings"
)
@click.argument("realm", type=str, required=True)
@click.pass_context
def delete_realm(ctx: click.Context, realm: str) -> None:
    config = load_config(ctx.obj.cfg_path)

    if "realms" not in config or realm not in config["realms"]:
        raise click.ClickException(f"realm '{realm}' not found")

    del config["realms"][realm]
    _save_config(config, ctx.obj.cfg_path)
    click.echo(f"realm '{realm}' deleted")


@settings_group.command("set", help="Set an individual value in a settings file")
@click.argument("key", type=str, required=True)
@click.argument("value", type=str, required=True)
@click.pass_context
def config_set(ctx: click.Context, key: str, value: str) -> None:
    config = load_config(ctx.obj.cfg_path)
    config[key] = value
    _save_config(config, ctx.obj.cfg_path)
    click.echo(f"Set {key} to {value}")


@settings_group.command("unset", help="Unset an individual value in a settings file")
@click.argument("key", type=str, required=True)
@click.pass_context
def config_unset(ctx: click.Context, key: str) -> None:
    config = load_config(ctx.obj.cfg_path)
    if key in config:
        del config[key]
        _save_config(config, ctx.obj.cfg_path)
        click.echo(f"Unset {key}")
    else:
        raise click.ClickException(f"Key '{key}' not found in config")


@settings_group.command("get", help="Get an individual value from a settings file")
@click.argument("key", type=str, required=True)
@click.pass_context
def config_get(ctx: click.Context, key: str) -> None:
    config = load_config(ctx.obj.cfg_path)
    if key in config:
        click.echo(config[key])
    else:
        raise click.ClickException(f"Key '{key}' not found in config")


@settings_group.command("set-context", help="Set a context entry in settings")
@click.argument("realm", type=str, required=True)
@click.option(
    "-n",
    "--name",
    type=str,
    required=True,
    help="Name of the context",
)
@click.option(
    "-u",
    "--user",
    type=str,
    help="User for the context",
)
@click.option(
    "-p",
    "--password",
    type=str,
    help="Password for the user in context",
)
@click.option(
    "-a",
    "--access_token",
    type=str,
    help="Access token for the user in context",
)
@click.option(
    "-t",
    "--refresh_token",
    type=str,
    help="Refresh token for the user in context",
)
@click.pass_context
def set_context(
    ctx: click.Context,
    realm: str,
    name: str,
    user: str | None,
    password: str | None,
    access_token: str | None,
    refresh_token: str | None,
) -> None:
    config = load_config(ctx.obj.cfg_path)

    if "realms" not in config:
        config["realms"] = {}

    if not (user and password) and not (access_token and refresh_token):
        raise click.ClickException("Either user/password or tokens must be provided")

    context_config = {}
    if user:
        context_config["user"] = user
    if password:
        context_config["password"] = password
    if access_token:
        context_config["access_token"] = access_token
    if refresh_token:
        context_config["refresh_token"] = refresh_token

    config["realms"][realm]["contexts"][name] = context_config
    _save_config(config, ctx.obj.cfg_path)
    click.echo(f"Context '{name}' for realm '{realm}' set")


@settings_group.command(
    "delete-context", help="Delete the specified context from the settings"
)
@click.argument("name", type=str, required=True)
@click.option(
    "-r",
    "--realm",
    type=str,
    help="Name of the realm",
)
@click.pass_context
def delete_context(
    ctx: click.Context,
    name: str,
    realm: str | None,
) -> None:
    config = load_config(ctx.obj.cfg_path)

    if realm:
        if "realms" not in config or realm not in config["realms"]:
            raise click.ClickException(f"Realm '{realm}' not found")
        del config["realms"][realm]["contexts"][name]
    else:
        for realm in config["realms"]:
            context = config["realms"][realm]["contexts"].get(name)
            if not context:
                raise click.ClickException(f"Context '{name}' not found")
            del config["realms"][realm]["contexts"][name]

    _save_config(config, ctx.obj.cfg_path)
    click.echo(f"Context '{name}' deleted")


@settings_group.command(
    "rename-context", help="Rename a context from the settings file"
)
@click.argument("old-context", type=str, required=True)
@click.argument("new-context", type=str, required=True)
@click.option(
    "-r",
    "--realm",
    type=str,
    required=True,
    help="Name of the context",
)
@click.pass_context
def rename_context(
    ctx: click.Context, old_context: str, new_context: str, realm: str
) -> None:
    config = load_config(ctx.obj.cfg_path)

    if "realms" not in config or realm not in config["realms"]:
        raise click.ClickException(f"Realm '{realm}' not found")

    # Rename the context
    config["realms"][realm]["contexts"][new_context] = config["realms"][realm][
        "contexts"
    ].pop(old_context)

    # Update current context if needed
    if (
        "current_context" in config["realms"][realm]
        and config["realms"][realm]["current_context"] == old_context
    ):
        config["current_context"] = new_context

    _save_config(config, ctx.obj.cfg_path)
    click.echo(f"Context '{old_context}' renamed to '{new_context}'")
