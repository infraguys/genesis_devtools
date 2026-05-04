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

import hashlib
import json
import enum
import os
import subprocess
import time
import typing as tp
import ipaddress
import pathlib
import urllib.parse
import yaml
import fnmatch

import requests
import rich.progress
import rich.status
import rich_click as click

from genesis_devtools.builder import base as base_builder
import genesis_devtools.constants as c
from genesis_devtools.logger import ClickLogger
from genesis_devtools import utils
from genesis_devtools.stand import models as stand_models
from genesis_devtools.infra.driver import libvirt as libvirt_infra
from genesis_devtools.infra.libvirt import libvirt
from genesis_devtools.backup import base as backup_base
from genesis_devtools.backup import local as backup_local

BOOTSTRAP_TAG = "bootstrap"
LaunchModeType = tp.Literal["core", "element", "custom"]
GC_CIDR = ipaddress.IPv4Network("10.20.0.0/22")
GC_BOOT_CIDR = ipaddress.IPv4Network("10.30.0.0/24")
_INVENTORY_CACHE_BASE = pathlib.Path.home() / ".cache" / "genesis"


def _is_url(value: str) -> bool:
    """Return True if *value* looks like an HTTP(S) URL."""
    parsed = urllib.parse.urlparse(value)
    return parsed.scheme in ("http", "https")


def _is_version(value: str) -> bool:
    """Return True if *value* looks like a plain version string (e.g. '0.0.6')."""
    import re

    return bool(re.fullmatch(r"[0-9]+\.[0-9]+(\.[0-9]+)*", value.strip()))


def _inventory_cache_dir(base_url: str) -> pathlib.Path:
    """Return the local cache directory for a given inventory base URL.

    The path is ``~/.cache/genesis/<name>/<version>/`` derived from the
    last two segments of *base_url*'s path.  Falls back to a SHA-256 hash
    when the URL has fewer than two path segments.
    """
    url_parts = [
        p for p in urllib.parse.urlparse(base_url).path.split("/") if p and p != ".."
    ]
    if len(url_parts) >= 2:
        element_name = url_parts[-2]
        element_version = url_parts[-1]
    else:
        url_hash = hashlib.sha256(base_url.encode()).hexdigest()[:16]
        element_name = "unknown"
        element_version = url_hash
    return _INVENTORY_CACHE_BASE / element_name / element_version


def _download_inventory_json(session: requests.Session, base_url: str) -> dict:
    """Fetch ``inventory.json`` from *base_url* and return its parsed content."""
    inventory_url = f"{base_url}/inventory.json"
    with rich.progress.Progress(
        rich.progress.SpinnerColumn(),
        rich.progress.TextColumn("[progress.description]{task.description}"),
        rich.progress.BarColumn(),
        rich.progress.DownloadColumn(),
        rich.progress.TransferSpeedColumn(),
        rich.progress.TimeRemainingColumn(),
        transient=True,
    ) as progress:
        task = progress.add_task(
            f"Downloading inventory.json from {base_url}", total=None
        )
        response = session.get(inventory_url)
        response.raise_for_status()
        progress.update(task, completed=1, total=1)
    return response.json()


def _download_inventory_files(
    session: requests.Session,
    base_url: str,
    raw: dict,
    cache_dir: pathlib.Path,
) -> None:
    """Download all artefact files referenced in *raw* inventory to *cache_dir*.

    Remote layout:  ``base_url/<category>/<filename>``
    Local layout:   ``cache_dir/<category>/<filename>``

    Already-cached files are skipped.  On completion, *raw* is mutated in-place
    so that every category list contains absolute local paths, and the final
    ``inventory.json`` is written to *cache_dir*.
    """
    inventories = raw if isinstance(raw, list) else [raw]

    # rel_path in inventory.json is a bare filename (no category subdir).
    # Remote: base_url/<category>/<filename>  (Nginx layout with subdirs)
    # Local:  cache_dir/<category>/<filename>  (matches ElementInventory.load)
    all_files: list[tuple[str, pathlib.Path, str]] = []
    for inv in inventories:
        for category in base_builder.ElementInventory.categories():
            for rel_path in inv.get(category, []):
                file_name = pathlib.Path(rel_path).name
                remote_url = f"{base_url}/{category}/{file_name}"
                local_file = cache_dir / category / file_name
                all_files.append((remote_url, local_file, file_name))

    with rich.progress.Progress(
        rich.progress.SpinnerColumn(),
        rich.progress.TextColumn("[progress.description]{task.description}"),
        rich.progress.BarColumn(),
        rich.progress.DownloadColumn(),
        rich.progress.TransferSpeedColumn(),
        rich.progress.TimeRemainingColumn(),
    ) as progress:
        for remote_url, local_file, file_name in all_files:
            task = progress.add_task(f"Downloading {file_name}", total=None)
            local_file.parent.mkdir(parents=True, exist_ok=True)
            if local_file.exists():
                progress.update(
                    task,
                    description=f"[dim]Cached[/dim] {file_name}",
                    completed=1,
                    total=1,
                )
                continue
            temp_file = local_file.with_suffix(".tmp")
            with session.get(remote_url, stream=True) as resp:
                resp.raise_for_status()
                content_length = resp.headers.get("Content-Length")
                total = int(content_length) if content_length else None
                progress.update(task, total=total)
                downloaded = 0
                with open(temp_file, "wb") as fh:
                    for chunk in resp.iter_content(chunk_size=1024 * 64):
                        fh.write(chunk)
                        downloaded += len(chunk)
                        progress.update(task, completed=downloaded)
            temp_file.replace(local_file)

    for inv in inventories:
        for category in base_builder.ElementInventory.categories():
            inv[category] = [
                str(cache_dir / category / pathlib.Path(rel_path).name)
                for rel_path in inv.get(category, [])
            ]

    inventory_local = cache_dir / "inventory.json"
    inventory_local.write_text(json.dumps(raw, indent=2))


def _resolve_inventory_from_url(url: str) -> pathlib.Path:
    """Download inventory and all artefacts from an Nginx URL, with caching.

    Args:
        url: URL of the inventory directory or ``inventory.json`` file.

    Returns:
        Local cache directory path accepted by :py:meth:`ElementInventory.load`.
    """
    base_url = url.rstrip("/")
    if base_url.endswith("/inventory.json"):
        base_url = base_url[: -len("/inventory.json")]

    cache_dir = _inventory_cache_dir(base_url)
    inventory_local = cache_dir / "inventory.json"

    if inventory_local.exists():
        click.secho(f"Using cached inventory from {cache_dir}", fg="cyan")
        return cache_dir

    cache_dir.mkdir(parents=True, exist_ok=True)
    with requests.Session() as session:
        raw = _download_inventory_json(session, base_url)
        _download_inventory_files(session, base_url, raw, cache_dir)

    return cache_dir


class Profile(str, enum.Enum):
    DEVELOP = "develop"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    LEGACY = "legacy"

    @property
    def ram(self) -> int:
        """Return memory in Mb based on current element in enum."""
        memory = {
            self.DEVELOP: 1024,
            self.SMALL: 2048,
            self.MEDIUM: 8192,
            self.LARGE: 16384,
            self.LEGACY: 4096,
        }
        return memory[self]

    @property
    def cores(self) -> int:
        """Return CPU cores based on current element in enum."""
        cores = {
            self.DEVELOP: 1,
            self.SMALL: 2,
            self.MEDIUM: 4,
            self.LARGE: 8,
            self.LEGACY: 2,
        }
        return cores[self]


class BackupPeriod(str, enum.Enum):
    M1 = "1m"
    M5 = "5m"
    M15 = "15m"
    M30 = "30m"
    H1 = "1h"
    H3 = "3h"
    H6 = "6h"
    H12 = "12h"
    D1 = "1d"
    D3 = "3d"
    D7 = "7d"

    @property
    def timeout(self) -> int:
        """Return timeout in seconds based on current element in enum."""
        timeouts = {
            self.M1: 60,
            self.M5: 60 * 5,
            self.M15: 60 * 15,
            self.M30: 60 * 30,
            self.H1: 60 * 60,
            self.H3: 60 * 60 * 3,
            self.H6: 60 * 60 * 6,
            self.H12: 60 * 60 * 12,
            self.D1: 60 * 60 * 24,
            self.D3: 60 * 60 * 24 * 3,
            self.D7: 60 * 60 * 24 * 7,
        }
        return timeouts[self]


def _get_core_image_uri_from_manifest(manifest_path: str) -> str:
    """Get image URI from manifest file."""
    if not os.path.exists(manifest_path):
        raise click.UsageError(f"Manifest file {manifest_path} does not exist")

    with open(manifest_path, "r") as f:
        manifest = yaml.safe_load(f)

    # Determine image URI from manifest
    try:
        return manifest["resources"]["$core.compute.sets"]["core_set"]["disk_spec"][
            "disks"
        ][0]["image"]
    except (KeyError, IndexError):
        click.secho("Failed to get image URI from manifest", fg="red")
        raise


def _bootstrap_element(
    image_path: tp.Optional[str],
    cores: int,
    memory: int,
    name: str,
    cidr: ipaddress.IPv4Network,
    force: bool,
    no_wait: bool,
) -> None:
    logger = ClickLogger()

    net_name = utils.installation_net_name(name)
    default_stand_network = stand_models.Network(
        name=net_name,
        cidr=cidr,
        managed_network=True,
        dhcp=True,
    )

    bootstrap_domain_name = utils.installation_bootstrap_name(name)

    # Single bootstrap stand
    dev_stand = stand_models.Stand.single_bootstrap_stand(
        name=name,
        image=image_path,
        cores=cores,
        memory=memory,
        network=default_stand_network,
        bootstrap_name=bootstrap_domain_name,
    )

    if not dev_stand.is_valid():
        logger.error("Invalid stand for element")
        return

    infra = libvirt_infra.LibvirtInfraDriver()

    # Check if the target stand already exists
    for stand in infra.list_stands():
        if stand.name != dev_stand.name:
            continue

        # Without `force` flag, unable to proceed with the installation
        if not force:
            logger.warn(
                f"Genesis element {dev_stand.name} is already running. "
                "Use '--force' flag to forcely rerun genesis element.",
            )
            return

        infra.delete_stand(stand)
        logger.info(f"Destroyed old genesis element: {dev_stand.name}")

    infra.create_stand(dev_stand)
    logger.info(f"Launched genesis element {name}")

    # Wait for the installation to start
    if no_wait:
        return

    utils.wait_for(
        lambda: bool(libvirt.get_domain_ip(bootstrap_domain_name)),
        title=f"Waiting for element {name}",
    )

    ip = libvirt.get_domain_ip(bootstrap_domain_name)
    logger.important(f"The element {name} is ready at:\nssh ubuntu@{ip}")


def _register_core(
    ecosystem_endpoint: str,
    disable_telemetry: bool,
    org_token: str | None,
) -> tuple[str, str, str]:
    from genesis_devtools.clients import ecosystem

    logger = ClickLogger()
    logger.info("Registering realm in ecosystem...")

    realm_uuid, realm_secret, tokens_dict = ecosystem.register_realm(
        ecosystem_endpoint=ecosystem_endpoint,
        org_token=org_token,
    )

    if tokens_dict:
        logger.info("Realm registered successfully")
    else:
        logger.info("Realm registered successfully in anonymous mode")

    return realm_uuid, realm_secret, tokens_dict


def _bootstrap_core(
    image_path: str | None,
    image_uri: str | None,
    profile: Profile,
    name: str,
    stand_spec: tp.Dict[str, tp.Any] | None,
    stand_main_network: stand_models.Network,
    stand_boot_network: stand_models.Network,
    force: bool,
    core_ip: ipaddress.IPv4Address,
    repository: str,
    admin_password: str,
    save_admin_password_file: str | None,
    manifest_path: str,
    eco_manifest_path: str,
    hypervisors: tp.Collection[stand_models.Hypervisor],
    no_start: bool,
    ecosystem_endpoint: str,
    disable_telemetry: bool,
    realm_uuid: str,
    realm_secret: str,
    realm_tokens: dict,
    ssh_public_key: str | None = None,
) -> None:
    logger = ClickLogger()
    logger.info("Starting genesis bootstrap in 'core' mode")

    if not hypervisors:
        logger.error("No hypervisors provided")
        return

    # Single bootstrap stand
    if stand_spec is None:
        bootstrap_domain_name = utils.installation_bootstrap_name(name)
        dev_stand = stand_models.Stand.single_bootstrap_stand(
            name=name,
            image=image_path,
            image_uri=image_uri,
            cores=profile.cores,
            memory=profile.ram,
            core_ip=core_ip,
            network=stand_main_network,
            boot_network=stand_boot_network,
            bootstrap_name=bootstrap_domain_name,
            hypervisors=hypervisors,
        )
    else:
        dev_stand = stand_models.Stand.from_spec(stand_spec)
        if dev_stand.network.is_dummy:
            dev_stand.network = stand_main_network

        if dev_stand.boot_network.is_dummy:
            dev_stand.boot_network = stand_boot_network

        # Assign the image to bootstraps if it wasn't specified
        # in the specification.
        for b in dev_stand.bootstraps:
            if b.image is None:
                b.image = image_path

    if not dev_stand.is_valid():
        logger.error(f"Invalid stand {dev_stand} from spec {stand_spec}")
        return

    infra = libvirt_infra.LibvirtInfraDriver()

    # Check if the target stand already exists
    for stand in infra.list_stands():
        if stand.name != dev_stand.name:
            continue

        # Without `force` flag, unable to proceed with the installation
        if not force:
            logger.warn(
                f"Genesis installation {dev_stand.name} is already running. "
                "Use '--force' flag to forcely rerun genesis installation.",
            )
            return

        infra.delete_stand(stand)
        logger.info(f"Destroyed old genesis installation: {dev_stand.name}")

    try:
        infra.create_stand(
            dev_stand,
            manifest_path=manifest_path,
            eco_manifest_path=eco_manifest_path,
            no_start=no_start,
            repository=repository,
            admin_password=admin_password,
            profile=profile.value,
            ecosystem_endpoint=ecosystem_endpoint,
            disable_telemetry=disable_telemetry,
            realm_uuid=realm_uuid,
            realm_secret=realm_secret,
            realm_tokens=realm_tokens,
            developer_keys=ssh_public_key,
        )
        logger.info(f"Launched genesis installation in `{profile.value}` profile")

        if save_admin_password_file:
            # Basic security check to prevent path traversal.
            if ".." in pathlib.Path(save_admin_password_file).parts:
                logger.error(
                    "Invalid password file path (contains '..'). Skipping save."
                )
            else:
                try:
                    # Ensure parent directory exists.
                    pathlib.Path(save_admin_password_file).parent.mkdir(
                        parents=True, exist_ok=True
                    )
                    # Use exclusive creation ('x' mode) to prevent race conditions
                    # and accidental overwrites.
                    with open(save_admin_password_file, "x") as f:
                        f.write(admin_password)
                    logger.info(f"Admin password saved to {save_admin_password_file}")
                except FileExistsError:
                    logger.warn(
                        f"Admin password file {save_admin_password_file} "
                        "already exists. Skipping saving the password."
                    )
                except OSError as e:
                    logger.error(
                        "Failed to save admin password to "
                        f"{save_admin_password_file}: {e}"
                    )
        else:
            logger.important(f"Admin password: {admin_password}")
    except Exception:
        infra.delete_stand(dev_stand)
        logger.error(f"Failed to launch genesis installation {dev_stand.name}")
        raise

    cidr = dev_stand.network.cidr
    if not no_start:
        logger.important(
            f"The stand {name} will be ready soon at:\nssh ubuntu@{cidr[2]}",
        )
    else:
        logger.info(
            f"The stand {name} is created but not started. You can start it manually."
        )


@click.command("bootstrap", help="Bootstrap genesis locally")
@click.option(
    "-i",
    "--inventory",
    help=(
        "Path to the inventory directory containing inventory.json, "
        "or an HTTP(S) URL pointing to an Nginx-served directory. "
        "When a URL is given, inventory.json and all referenced artefacts are "
        "downloaded and cached under ~/.cache/genesis/<name>/<version>/. "
        "Trailing /inventory.json in the URL is accepted and treated identically "
        "to the bare directory URL. "
        "A bare version string (e.g. '0.0.6') is expanded automatically to "
        f"{c.ELEMENT_REPO_URL}/core/<version>/. "
        "Examples: "
        "0.0.6  "
        "/path/to/core/0.0.6  "
        "https://repository.example.com/genesis-elements/core/0.0.6/  "
        "https://repository.example.com/genesis-elements/core/0.0.6/inventory.json"
    ),
)
@click.option(
    "--profile",
    default=Profile.SMALL.value,
    show_default=True,
    help="Profile for the installation.",
    type=click.Choice([p.value for p in Profile]),
)
@click.option(
    "--name",
    default="genesis-core",
    help="Name of the installation",
)
# It's a temporary option, will be removed in the future but now it's
# convenient to run elements and cores slightly differently
@click.option(
    "-m",
    "--launch-mode",
    default="element",
    type=click.Choice([s for s in tp.get_args(LaunchModeType)]),
    show_default=True,
    help="Launch mode for start element, core or custom configuration",
)
@click.option(
    "-s",
    "--stand-spec",
    default=None,
    type=click.Path(exists=True),
    help="Additional stand specification for core mode.",
)
@click.option(
    "--cidr",
    default=GC_CIDR,
    help="The main network CIDR",
    show_default=True,
    type=ipaddress.IPv4Network,
)
@click.option(
    "--core-ip",
    default=None,
    help=(
        "The IP address for the core VM. If `None` is provided, "
        "second IP address from the main network will be used."
    ),
    show_default=True,
    type=ipaddress.IPv4Address,
)
@click.option(
    "--bridge",
    default=None,
    help=(
        "Name of the linux bridge for the main network, it will be created if not set."
    ),
)
@click.option(
    "--boot-cidr",
    default=GC_BOOT_CIDR,
    help="The bootstrap network CIDR",
    show_default=True,
    type=ipaddress.IPv4Network,
)
@click.option(
    "--boot-bridge",
    default=None,
    help=(
        "Name of the linux bridge for the bootstrap network, "
        "it will be created if not set."
    ),
)
@click.option(
    "-f",
    "--force",
    show_default=True,
    is_flag=True,
    help="Rebuild if the output already exists",
)
@click.option(
    "--no-wait",
    show_default=True,
    is_flag=True,
    help="Cancel waiting for the installation to start",
)
@click.option(
    "-r",
    "--repository",
    default=f"{c.GENESIS_REPO_URL}/",
    type=str,
    help="Default element repository",
    show_default=True,
)
@click.option(
    "--admin-password",
    default=None,
    type=str,
    help=(
        "A password for the admin user in. If not provided, "
        "the password will be generated."
    ),
    show_default=True,
)
@click.option(
    "--save-admin-password-file",
    default=None,
    type=str,
    help=(
        "If the option is specified the admin password is saved "
        "to the file. Otherwise it's printed to the console."
    ),
    show_default=True,
)
@click.option(
    "--hyper-connection-uri",
    default="",
    type=str,
    help=(
        "Connection URI for the hypervisor, "
        "e.g. 'qemu+tcp://10.0.0.1/system' or "
        "'qemu+ssh://user@10.0.0.1/system'. If not set, "
        "the first address of the network(--cidr option) will be used. "
    ),
)
@click.option(
    "--hyper-storage-pool",
    default="default",
    type=str,
    help="Storage pool for the hypervisor.",
    show_default=True,
)
@click.option(
    "--hyper-machine-prefix",
    default="vm-",
    type=str,
    help="A prefix for new VMs.",
    show_default=True,
)
@click.option(
    "--hyper-iface-rom-file",
    default="/usr/share/qemu/1af41041.rom",
    type=str,
    help="A path to the custom ROM file of a network interface.",
    show_default=True,
)
@click.option(
    "--no-start",
    show_default=True,
    is_flag=True,
    help="Do not start the stand after creation",
)
# Ecosystem
@click.option(
    "--no-registration",
    is_flag=True,
    envvar="NO_REGISTRATION",
    help="Don't register in ecosystem.",
)
@click.option(
    "--disable-telemetry",
    is_flag=True,
    envvar="DISABLE_TELEMETRY",
    help="Disable telemetry. Anonymized data only is sent by default.",
)
@click.option(
    "--org-token",
    prompt=False,
    hide_input=True,
    type=str,
    envvar="ORG_TOKEN",
    help="Organization token, used to register stand in ecosystem",
)
@click.option(
    "--ecosystem-endpoint",
    default="https://console.genesis-core.tech",
    type=str,
    envvar="ECOSYSTEM_ENDPOINT",
    help="Ecosystem's endpoint to connect to",
)
@click.option(
    "--settings",
    show_default=True,
    is_flag=True,
    help="Interactively create a genesis settings file",
)
@click.option(
    "--ssh-public-key",
    multiple=True,
    type=click.Path(exists=True),
    help=(
        "Path to a public SSH key file to inject into the VM "
        "after bootstrap. Can be specified multiple times. "
        "If not provided, no key will be injected."
    ),
)
@click.pass_context
def bootstrap_cmd(
    ctx: click.Context,
    inventory: str,
    profile: str,
    name: str,
    launch_mode: LaunchModeType,
    stand_spec: str | None,
    cidr: ipaddress.IPv4Network,
    core_ip: ipaddress.IPv4Address | None,
    bridge: str | None,
    boot_cidr: ipaddress.IPv4Network,
    boot_bridge: str | None,
    force: bool,
    no_wait: bool,
    repository: str,
    admin_password: str | None,
    save_admin_password_file: str | None,
    hyper_connection_uri: str,
    hyper_storage_pool: str,
    hyper_machine_prefix: str,
    hyper_iface_rom_file: str,
    no_start: bool,
    no_registration: bool,
    disable_telemetry: bool,
    org_token: str | None,
    ecosystem_endpoint: str,
    settings: bool,
    ssh_public_key: tp.Tuple[str, ...],
) -> None:
    if not inventory:
        raise click.UsageError("No inventory specified")

    if _is_version(inventory):
        inventory = f"{c.ELEMENT_REPO_URL}/core/{inventory.strip()}/"

    if _is_url(inventory):
        inventory_path = _resolve_inventory_from_url(inventory)
        inventory = str(inventory_path)
    elif not os.path.exists(inventory):
        raise click.UsageError(f"Inventory path not found: {inventory}")

    profile = Profile[profile.upper()]

    # Determine the IP address for the core VM
    if core_ip is None:
        core_ip = cidr[2]

    if core_ip not in cidr:
        raise click.UsageError("Core IP is not in the main network")

    # Generate admin password if not provided
    if not admin_password:
        import secrets

        admin_password = secrets.token_urlsafe(16)

    # Load inventory and get image path and image URI.
    inventory_instance = base_builder.ElementInventory.load(pathlib.Path(inventory))

    if not inventory_instance.images:
        raise click.UsageError("No images found in the inventory")

    if not inventory_instance.manifests:
        raise click.UsageError("No manifests found in the inventory")

    # NOTE(akremenetsky): The core element has one image and manifest at the moment
    image_path = str(inventory_instance.images[0])
    manifest_path = str(inventory_instance.manifests[0])
    image_uri = _get_core_image_uri_from_manifest(manifest_path)

    if launch_mode not in ("element", "core"):
        raise click.UsageError(f"Unknown launch mode {launch_mode}")

    if image_path and not os.path.isabs(image_path):
        image_path = os.path.abspath(image_path)

    # DEPRECATED(akremenetsky): The 'element' mode is deprecated
    if launch_mode == "element":
        if stand_spec is not None:
            raise click.UsageError("Stand spec is not supported in 'element' mode")

        return _bootstrap_element(
            image_path=image_path,
            cores=profile.cores,
            memory=profile.ram,
            name=name,
            force=force,
            no_wait=no_wait,
            cidr=cidr,
        )

    # Validate org-token requirement based on no-registration flag
    if no_registration:
        org_token = None
    # TODO: re-enable after preparations
    #     elif not org_token:
    #         click.secho(
    #             click.style(
    #                 """\

    # Register your realm in the Genesis ecosystem to get access to additional features and support.
    # You can skip registration by using --no-registration flag.

    # """,
    #                 bold=True,
    #                 fg="yellow",
    #             ),
    #             bold=True,
    #             # Underline makes the text more visible
    #             underline=True,
    #         )

    #         org_token = click.prompt("Organization token", hide_input=True)

    if stand_spec is not None:
        with open(stand_spec) as f:
            stand_spec = yaml.safe_load(f)

    net_name = utils.installation_net_name(name)
    stand_main_network = stand_models.Network(
        name=bridge if bridge else net_name,
        cidr=cidr,
        managed_network=False if bridge else True,
    )
    boot_net_name = utils.installation_boot_net_name(name)
    stand_boot_network = stand_models.Network(
        name=boot_bridge if boot_bridge else boot_net_name,
        cidr=boot_cidr,
        managed_network=False if boot_bridge else True,
    )

    hypervisors = []

    if not hyper_connection_uri:
        hyper_connection_uri = f"qemu+tcp://{cidr[1]}/system"

    # Single hypervisor at bootstrap time is supported at the moment
    hypervisor = stand_models.Hypervisor(
        network=stand_main_network.name,
        network_type="bridge" if bridge else "network",
        connection_uri=hyper_connection_uri,
        storage_pool=hyper_storage_pool,
        machine_prefix=hyper_machine_prefix,
        iface_rom_file=hyper_iface_rom_file,
    )
    hypervisors.append(hypervisor)

    with rich.status.Status("Registering realm in ecosystem...", spinner="dots"):
        realm_uuid, realm_secret, realm_tokens = _register_core(
            ecosystem_endpoint=ecosystem_endpoint,
            disable_telemetry=disable_telemetry,
            org_token=org_token,
        )

    inventory_eco_instance = base_builder.ElementInventory.load(
        pathlib.Path(inventory), 1
    )
    eco_manifest_path = str(inventory_eco_instance.manifests[0])

    ssh_public_key_content = None
    if ssh_public_key:
        key_parts = []
        for key_path in ssh_public_key:
            with open(key_path) as f:
                key_content = f.read().strip()
                key_parts.append(key_content + "\n")
        ssh_public_key_content = "".join(key_parts)

    if subprocess.call(["sudo", "-n", "true"], stderr=subprocess.DEVNULL) != 0:
        click.secho("Sudo privileges are required to proceed.", fg="yellow")
        if subprocess.call(["sudo", "-v"]) != 0:
            raise click.ClickException("Failed to obtain sudo privileges. Aborting.")

    with rich.status.Status(
        f"Launching genesis installation '{name}'... ", spinner="dots"
    ):
        _bootstrap_core(
            image_path=image_path,
            image_uri=image_uri,
            profile=profile,
            name=name,
            stand_spec=stand_spec,
            stand_main_network=stand_main_network,
            stand_boot_network=stand_boot_network,
            force=force,
            core_ip=core_ip,
            repository=repository,
            admin_password=admin_password,
            save_admin_password_file=save_admin_password_file,
            manifest_path=manifest_path,
            eco_manifest_path=eco_manifest_path,
            hypervisors=hypervisors,
            no_start=no_start,
            ecosystem_endpoint=ecosystem_endpoint,
            disable_telemetry=disable_telemetry,
            realm_uuid=realm_uuid,
            realm_secret=realm_secret,
            realm_tokens=realm_tokens,
            ssh_public_key=ssh_public_key_content,
        )
    if settings:
        from genesis_devtools.cmd.settings.commands import init_config

        ctx.invoke(
            init_config,
        )
    return None


def _start_validation_type(start: str | None) -> time.struct_time | None:
    if start is None:
        return None

    try:
        return time.strptime(start, "%H:%M:%S")
    except ValueError:
        raise click.UsageError("Invalid '--start' format. Use HH:MM:SS, e.g., 16:00:00")


def _domains_for_backup(
    names: tp.List[str] | None = None,
    exclude_names: tp.List[str] | None = None,
    raise_on_domain_absence: bool = False,
) -> tp.List[str]:
    domains = set(libvirt.list_domains())
    names = set(names or [])
    exclude_names = set(exclude_names or [])

    # Check if the specified domains exist
    if raise_on_domain_absence and (names - domains):
        diff = ", ".join(names - domains)
        raise click.UsageError(f"Domains {diff} not found")

    if names:
        domains &= names

    if exclude_names:
        domains = {
            d
            for d in domains
            if not any(fnmatch.fnmatch(d, pattern) for pattern in exclude_names)
        }

    return list(domains)


@click.command("backup", help="Backup the current installation")
@click.option(
    "--config",
    default=None,
    type=click.Path(),
    help="Path to the backuper configuration file",
)
@click.option(
    "-n",
    "--name",
    default=None,
    multiple=True,
    help="Name of the libvirt domain, if not provided, all will be backed up",
)
@click.option(
    "-d",
    "--backup-dir",
    default=".",
    type=click.Path(),
    help="Directory where backups will be stored",
)
@click.option(
    "-p",
    "--period",
    default=BackupPeriod.D1.value,
    type=click.Choice([p.value for p in BackupPeriod]),
    show_default=True,
    help="the regularity of backups",
)
@click.option(
    "-o",
    "--offset",
    default=None,
    type=click.Choice([p.value for p in BackupPeriod]),
    show_default=True,
    help=(
        "The time offset of the first backup. If not provided, "
        "the same value as the period will be used"
    ),
)
@click.option(
    "--start",
    default=None,
    type=_start_validation_type,
    help=(
        "Time of day to start backup in format HH:MM:SS. "
        "Cannot be used together with --offset. If provided, "
        "period must be >= 1d."
    ),
)
@click.option(
    "--oneshot",
    show_default=True,
    is_flag=True,
    help="Do a backup once and exit",
)
@click.option(
    "-c",
    "--compress",
    show_default=True,
    is_flag=True,
    help="Compress the backup.",
)
@click.option(
    "-e",
    "--encrypt",
    show_default=True,
    is_flag=True,
    help=(
        "Encrypt the backup. Works only with the compress flag. "
        "Use environment variable to specify the encryption key "
        "and the initialization vector: "
        "GEN_DEV_BACKUP_KEY and GEN_DEV_BACKUP_IV"
    ),
)
@click.option(
    "-s",
    "--min-free-space",
    default=50,
    type=int,
    show_default=True,
    help=(
        "Free disk space shouldn't be lower than this threshold. "
        "If the space becomes lower, the backup process is stopped. "
        "The value is in GB."
    ),
)
@click.option(
    "-r",
    "--rotate",
    default=5,
    type=int,
    show_default=True,
    help=(
        "Maximum number of backups to keep. The oldest backups are deleted. "
        "`0` means no rotation."
    ),
)
@click.option(
    "--no",
    "--exclude-name",
    "exclude_name",
    multiple=True,
    help="Name or pattern of libvirt domains to exclude from backup",
)
def backup_cmd(
    config: str | None,
    name: tp.List[str] | None,
    exclude_name: tp.List[str] | None,
    backup_dir: str,
    period: str,
    offset: str | None,
    start: time.struct_time | None,
    oneshot: bool,
    compress: bool,
    encrypt: bool,
    min_free_space: int,
    rotate: int,
) -> None:
    period = BackupPeriod(period)
    if offset:
        offset = BackupPeriod(offset)

    # Forbid using both include and exclude options
    if name and exclude_name:
        raise click.UsageError(
            "Cannot specify both --name and --no/--exclude-name options at the same time."
        )

    # Default local backuper if no config is provided
    if config is None:
        backuper = backup_local.LocalQcowBackuper(
            backup_dir=backup_dir,
            min_free_disk_space_gb=min_free_space,
        )
    else:
        backuper = utils.load_driver(config)

    # Need to specify encryption key and initialization vector via
    # environment variables.
    if encrypt:
        try:
            backup_base.EncryptionCreds.validate_env()
        except ValueError:
            raise click.UsageError(
                (
                    "Define environment variables GEN_DEV_BACKUP_KEY "
                    "and GEN_DEV_BACKUP_IV. "
                    "Key and IV must be greater or equal than "
                    f"{backup_base.EncryptionCreds.MIN_LEN} bytes and less "
                    f"or equal to {backup_base.EncryptionCreds.LEN} bytes."
                )
            )

        encryption = backup_base.EncryptionCreds.from_env()
    else:
        encryption = None

    # Do a single backup and exit
    if oneshot:
        domains = _domains_for_backup(name, exclude_name, raise_on_domain_absence=True)
        backuper.backup(domains, compress, encryption)
        return

    # Do periodic backups
    click.secho(f"Current time: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    # The `start` option validation
    if start is None:
        # Default behavior: use offset (or period if offset not provided)
        offset = offset or period
        ts = time.time() + offset.timeout
        click.secho(
            f"Next backup at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))}"
        )
        time.sleep(offset.timeout)
    else:
        # Validate mutually exclusive options: --start and --offset
        if offset is not None:
            raise click.UsageError(
                "Options '--start' and '--offset' cannot be used together. "
                "Choose one. By default, --offset is used."
            )

        # If --start is specified, period must be at least daily
        if period.timeout < BackupPeriod.D1.timeout:
            raise click.UsageError(
                "The '--start' option requires the period to be at least 1 day (1d)."
            )

        start_sec = start.tm_hour * 3600 + start.tm_min * 60 + start.tm_sec
        now_ts = time.time()
        now = time.localtime(now_ts)
        now_sec = now.tm_hour * 3600 + now.tm_min * 60 + now.tm_sec

        if now_sec < start_sec:
            delta = start_sec - now_sec
        else:
            delta = 24 * 3600 - now_sec + start_sec

        ts = now_ts + delta
        click.secho(
            f"Next backup at: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(ts))}"
        )
        time.sleep(delta)

    # Next runs happen every 'period' seconds from the aligned start
    next_ts = time.time() + period.timeout

    # Do periodic backups
    while True:
        # Need to refresh the list of domains since it could have changed
        domains = _domains_for_backup(name, exclude_name)

        click.secho(f"Backup started at {time.strftime('%Y-%m-%d %H:%M:%S')}")
        backuper.backup(domains, compress, encryption)
        click.secho(
            "Next backup at: "
            f"{time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(next_ts))}"
        )

        # Rotate old backups
        backuper.rotate(rotate)

        timeout = next_ts - time.time()
        timeout = 0 if timeout < 0 else timeout
        next_ts += period.timeout

        time.sleep(timeout)


@click.command("backup-decrypt", help="Decrypt a backup file")
@click.argument("path", type=click.Path(exists=True))
def backup_decrypt_cmd(path: str) -> None:
    # Need to specify encryption key and initialization vector via
    # environment variables.

    try:
        backup_base.EncryptionCreds.validate_env()
    except ValueError:
        raise click.UsageError(
            (
                "Define environment variables GEN_DEV_BACKUP_KEY "
                "and GEN_DEV_BACKUP_IV. "
                "Key and IV must be greater or equal than "
                f"{backup_base.EncryptionCreds.MIN_LEN} bytes and less or "
                f"equal to {backup_base.EncryptionCreds.LEN} bytes."
            )
        )

    encryption = backup_base.EncryptionCreds.from_env()

    if os.path.isdir(path):
        for file in os.listdir(path):
            _path = os.path.join(path, file)
            utils.decrypt_file(
                _path,
                encryption.key,
                encryption.iv,
            )
            click.secho(f"The {_path} file has been decrypted.", fg="green")
        return

    utils.decrypt_file(
        path,
        encryption.key,
        encryption.iv,
    )
    click.secho(f"The {path} file has been decrypted.", fg="green")
