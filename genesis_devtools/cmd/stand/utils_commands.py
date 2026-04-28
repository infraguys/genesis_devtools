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
import requests
import subprocess
import typing as tp

import rich_click as click

import genesis_devtools.constants as c
from genesis_devtools import utils

if tp.TYPE_CHECKING:
    from genesis_devtools.common.cmd_context import ContextObject


@click.command(name="openapi", help="tool for creating openapi spec files", hidden=True)
@click.option(
    "-u",
    "--url",
    type=click.STRING,
    required=False,
    default=None,
    help="openapi url",
)
@click.option(
    "-e",
    "--endpoint",
    required=False,
    default=None,
)
@click.argument(
    "path",
    required=False,
    type=click.Path(exists=False, dir_okay=False),
    help="Path to target file",
)
@click.pass_context
def openapi_spec(ctx: click.Context, url: str, endpoint: str, path: str) -> None:
    from genesis_devtools.clients.base_client import get_user_api_client
    import ruamel.yaml

    if url:
        response = requests.get(url, timeout=10).json()
        response.raise_for_status()
        data = response.json()
    else:
        auth_data = ctx.obj.auth_data
        if endpoint:
            auth_data["endpoint"] = endpoint
        client = get_user_api_client(auth_data)
        data = client.filter("specifications/3.0.3")

    path = path or os.path.expanduser("~/.openapi.yaml")
    with open(path, "w") as f:
        yaml = ruamel.yaml.YAML()
        yaml.indent(sequence=4, offset=2)
        yaml.dump(data, f)
    click.secho(f"OpenAPI spec written to {path}", fg="green")
    return None


@click.command("cowsay", help="Display a cow message")
def cowsay_cmd() -> None:
    import cowsay

    cowsay.cow("I am genesis-cli")


@click.command("hello", help="Display a genesis message")
def hello() -> None:
    msg = """
▄▖        ▘  
▌ █▌▛▌█▌▛▘▌▛▘
▙▌▙▖▌▌▙▖▄▌▌▄▌
"""
    click.echo(msg)


@click.command("autocomplete_help", help="Display a autocomplete help")
def autocomplete_help() -> None:
    from genesis_devtools.utils import PROJECT_PATH

    with open(
        os.path.join(
            PROJECT_PATH, "genesis_devtools", "autocomplete", "autocomplete_help"
        ),
        "r",
    ) as f:
        autocomplete_data = f.read()
    click.echo(autocomplete_data)


@click.command("autocomplete", help="update genesis autocomplete for your shell")
@click.option(
    "-s",
    "--shell",
    type=click.Choice(["bash", "zsh"]),
    required=False,
    default=None,
    help="shell kind",
)
def autocomplete(shell: str | None) -> None:
    from genesis_devtools.utils import PROJECT_PATH

    if shell is None:
        import psutil

        shell = psutil.Process(os.getppid()).parent().name()

    if shell == "bash":
        project_complete_path = "genesis-complete.bash"
        rc_complete_path = "bashrc-complete"
        rc_file = "~/.bashrc"
    elif shell == "zsh":
        project_complete_path = "genesis-complete.zsh"
        rc_complete_path = "zshrc-complete"
        rc_file = "~/.zshrc"
    else:
        click.echo(f"autocomplete not supported for this shell {shell}")
        return
    with open(
        os.path.join(PROJECT_PATH, c.PKG_NAME, "autocomplete", project_complete_path),
        "r",
    ) as f:
        autocomplete_data = f.read()
    os.makedirs(os.path.expanduser(c.CONFIG_DIR), exist_ok=True)
    with open(os.path.expanduser(f"{c.CONFIG_DIR}/.{project_complete_path}"), "w") as f:
        f.write(autocomplete_data)
    with open(
        os.path.join(PROJECT_PATH, c.PKG_NAME, "autocomplete", rc_complete_path),
        "r",
    ) as f:
        rc_data = f.read()
    with open(os.path.expanduser(rc_file), "a+") as f:
        f.seek(0)
        if rc_data not in f.read():
            f.write(rc_data)
    click.echo("autocomplete updated. Restart your shell")


@click.command(help="copy genesis core from local git repo to bootstrap")
@click.option(
    "-t",
    "--target-dir",
    required=False,
    type=click.Path(),
    help="Directory to copy genesis core to",
)
@click.argument("project_dir", type=click.Path(), required=False)
@click.pass_obj
def sync(obj: "ContextObject", target_dir: str | None, project_dir: str | None) -> None:
    repo = utils.get_repo(project_dir or ".")
    project_name = os.path.basename(repo.working_dir)
    if project_name != "genesis_core":
        raise ValueError("project name must be genesis_core")
    bootstrap_ip = utils.get_ip_from_url(obj.auth_data["endpoint"])
    target = target_dir or "/opt"
    dest = f"{c.BOOTSTRAP_USER}@{bootstrap_ip}:{target}"
    cmd = [
        "rsync",
        "-avzr",
        "--exclude=.*",
        "--exclude=__pycache__",
        "--exclude=output",
        repo.working_dir,
        dest,
    ]
    subprocess.run(cmd, check=True)
    return None
