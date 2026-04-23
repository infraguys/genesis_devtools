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
import tempfile

from genesis_devtools import constants as c


@click.group("settings", help="Modify genesis settings files")
def settings_group():
    pass


def load_config(cfg_path: str | None = c.CONFIG_FILE, silent: bool = False) -> dict:
    """Load configuration from file"""
    try:
        if cfg_path and os.path.exists(cfg_path):
            with open(cfg_path, "r") as f:
                config = yaml.safe_load(f) or {}
        else:
            if not silent:
                click.echo(
                    f"You don't have a configuration file {cfg_path}. "
                    f"Please, read the docs https://infraguys.github.io/genesis_devtools/config/"
                )
            config = {}
    except Exception as e:
        raise click.ClickException(f"Error reading settings: {e}")
    return config


def _save_config(config: dict, cfg_path: str = c.CONFIG_FILE) -> None:
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


@settings_group.command("use-realm", help="Use the current-realm in a settings file")
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
# add flag show-sensitive
@click.option(
    "--show-sensitive",
    is_flag=True,
    default=False,
    help="Show sensitive data",
)
@click.pass_context
def list_realms(ctx: click.Context, output: str, show_sensitive: bool) -> None:
    config = load_config(ctx.obj.cfg_path)

    if not show_sensitive:
        for realm in config.get("realms", {}).values():
            for context in realm.get("contexts", {}).values():
                context["password"] = "*"
                context["user"] = "*"

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
@click.option(
    "--current",
    is_flag=True,
    default=False,
    help="Set as current realm",
)
@click.pass_context
def set_realm(
    ctx: click.Context,
    realm: str,
    endpoint: str | None,
    check_updates: bool,
    skip_tls_verify: bool,
    current: bool,
) -> None:
    config = load_config(ctx.obj.cfg_path)

    if "realms" not in config:
        config["realms"] = {}

    realm_config = {
        "endpoint": endpoint,
        "check_updates": check_updates,
        "skip_tls_verify": skip_tls_verify,
        "contexts": {},
    }
    if realm in config["realms"]:
        realm_config["contexts"] = config["realms"][realm].get("contexts", {})
    config["realms"][realm] = realm_config

    if current or len(config["realms"]) == 1:
        config["current-realm"] = realm

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
@click.option(
    "--current",
    is_flag=True,
    default=False,
    help="Set as current context",
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
    current: bool,
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

    if "contexts" not in config["realms"][realm]:
        config["realms"][realm]["contexts"] = {}
    config["realms"][realm]["contexts"][name] = context_config
    if current or len(config["realms"][realm]["contexts"]) == 1:
        config["realms"][realm]["current-context"] = name
        config["current-realm"] = realm
    _save_config(config, ctx.obj.cfg_path)
    click.echo(f"Context '{name}' for realm '{realm}' set")


@settings_group.command(
    "use-context", help="Use the current-context in a settings file"
)
@click.argument("name", type=str, required=True)
@click.option(
    "-r",
    "--realm",
    type=str,
    required=True,
    help="Name of the realm",
)
@click.pass_context
def use_context(
    ctx: click.Context,
    name: str,
    realm: str,
) -> None:
    config = load_config(ctx.obj.cfg_path)

    if "realms" not in config or realm not in config["realms"]:
        raise click.ClickException(f"Realm '{realm}' not found")

    if (
        "contexts" not in config["realms"][realm]
        or name not in config["realms"][realm]["contexts"]
    ):
        raise click.ClickException(f"Context '{name}' not found")

    config["realms"][realm]["current-context"] = name
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


def _prompt_required_text(
    prompt: str,
    default: str | None = None,
    hide_input: bool = False,
) -> str:
    while True:
        value = click.prompt(
            prompt,
            type=str,
            default=default,
            show_default=default is not None,
            hide_input=hide_input,
        )
        if hide_input:
            if value:
                return value
        else:
            value = value.strip()
            if value:
                return value

        click.echo("Value cannot be empty. Please try again.", err=True)


def _build_interactive_config() -> dict:
    realm_name = _prompt_required_text("Realm name", default="default-realm")
    endpoint = _prompt_required_text("Endpoint", default="http://localhost:11010")
    check_updates = click.confirm("Check for updates on startup?", default=True)
    skip_tls_verify = click.confirm(
        "Skip TLS certificate verification?",
        default=False,
    )
    context_name = _prompt_required_text("Context name", default="default")
    use_tokens = click.confirm("Use access token authentication?", default=False)

    context_config: dict[str, str] = {}
    if use_tokens:
        context_config["access_token"] = _prompt_required_text(
            "Access token",
            hide_input=True,
        )
        context_config["refresh_token"] = _prompt_required_text(
            "Refresh token",
            hide_input=True,
        )
    else:
        context_config["user"] = _prompt_required_text("User")
        context_config["password"] = _prompt_required_text(
            "Password",
            hide_input=True,
        )

    return {
        "schema_version": 1,
        "realms": {
            realm_name: {
                "endpoint": endpoint,
                "check_updates": check_updates,
                "skip_tls_verify": skip_tls_verify,
                "contexts": {
                    context_name: context_config,
                },
                "current-context": context_name,
            }
        },
        "current-realm": realm_name,
    }


@settings_group.command("init", help="Interactively create a genesis settings file")
@click.pass_context
def init_config(ctx: click.Context) -> None:
    cfg_path = ctx.obj.cfg_path or c.CONFIG_FILE

    if os.path.exists(cfg_path):
        should_write = click.confirm(
            f"Config file '{cfg_path}' already exists. Overwrite it?",
            default=False,
        )
    else:
        should_write = click.confirm(
            f"Create config file '{cfg_path}'?",
            default=True,
        )

    if not should_write:
        click.echo("Config initialization cancelled")
        return

    config = _build_interactive_config()
    _save_config(config, cfg_path)
    click.echo(f"Config saved to '{cfg_path}'")
