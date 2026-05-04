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
import time

import rich_click as click

import genesis_devtools.constants as c
from genesis_devtools.common.version import get_project_version


def check_latest_version(echo_on_latest: bool = False) -> None:
    """Check for the latest version on GitHub and warn if newer version exists."""
    try:
        response = requests.get(f"{c.GITHUB_RELEASES_URL}/latest", timeout=1)
        response.raise_for_status()
        latest_tag = response.json()["tag_name"]

        from genesis_devtools import version as genesis_version

        # Сравниваем версии
        from packaging import version

        if version.parse(latest_tag) > version.parse(genesis_version.version_info):
            click.secho(
                f"New version available: {latest_tag} (current: {genesis_version.version_info}) "
                f"Update by:\ncurl -fsSL {c.GENESIS_REPO_URL}/install.sh | sudo sh",
                fg="yellow",
            )
        else:
            if echo_on_latest:
                click.secho(
                    f"You are using the latest version: {genesis_version.version_info}",
                    fg="green",
                )
    except Exception as err:
        click.secho(
            f"Failed to check for the latest version on GitHub: {err}", fg="red"
        )


def should_check_version():
    """Check if we should perform a version check."""
    try:
        # Check if file exists and is not empty
        if not os.path.exists(c.LAST_CHECK_FILE):
            return True

        # Read the last check time
        with open(c.LAST_CHECK_FILE, "r") as f:
            content = f.read().strip()
            if not content:
                return True

            last_check = float(content)

        # Check if enough time has passed
        if time.time() - last_check > c.UPDATE_CHECK_INTERVAL:
            return True
        return False
    except Exception:
        return False  # Default to no checking if we can't read the file


def save_last_check_time():
    """Save the current timestamp to the version check file."""
    try:
        os.makedirs(os.path.dirname(c.LAST_CHECK_FILE), exist_ok=True)
        with open(c.LAST_CHECK_FILE, "w") as f:
            f.write(str(time.time()))
    except Exception:
        # Silently ignore write errors
        pass


@click.command(name="version", help=f"Prints the {c.PKG_NAME} version")
def version_cmd() -> None:
    from genesis_devtools import version

    click.echo(version.version_info)


@click.command(name="latest", help="Check for the latest version on GitHub")
def latest_cmd() -> None:
    check_latest_version(echo_on_latest=True)


@click.command("get-version", help="Return the version of the project")
@click.argument("element_dir", type=click.Path())
def get_project_version_cmd(element_dir: str) -> None:
    version = get_project_version(element_dir)
    click.secho(version, fg="green")
