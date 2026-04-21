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

import json
import typing as tp
import re
import urllib.request
import urllib.parse

import yaml


class ManifestNotFound(Exception):
    """Raised when the requested manifest cannot be located or downloaded."""


def _join_url(*parts: str) -> str:
    # Join URL parts ensuring single slashes
    base = parts[0]
    for p in parts[1:]:
        base = urllib.parse.urljoin(base.rstrip("/") + "/", p)
    return base


def _http_get(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "genesis-devtools/1.0"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.read()


def _extract_hrefs(html: str) -> list[str]:
    # Extract href values from simple directory listings
    return re.findall(r'href=["\']([^"\']+)["\']', html, flags=re.IGNORECASE)


def download_manifest(
    repository_url: str,
    manifest_name: str,
    manifest_version: str | None = None,
) -> dict[str, tp.Any]:
    """Download latest manifest by semantic version from a simple HTTP repo.

    Directory layout example:
        <repo>/<name>/<version>/manifests/<name>.yaml

    Args:
        repository_url: Base URL of the repository
                        (e.g., http://host:port/genesis-elements/)
        manifest_name: Element name (e.g., "demo").
        manifest_version: Element version (e.g., "0.0.1").

    Returns:
        Parsed YAML manifest as a dict.

    Raises:
        ManifestNotFound: If the element or its manifest cannot be found.
    """
    try:
        # 1) List repository root to ensure element exists
        # (optional but validates repo)
        _http_get(repository_url).decode("utf-8", errors="ignore")
    except Exception as exc:
        raise ManifestNotFound(f"Failed to access repository: {repository_url}: {exc}")

    # 2) List element directory to get versions
    element_url = _join_url(repository_url, manifest_name)
    try:
        element_html = _http_get(element_url).decode("utf-8", errors="ignore")
    except Exception as exc:
        raise ManifestNotFound(
            f"Element '{manifest_name}' not found at {element_url}: {exc}"
        )

    if manifest_version is None:
        version_dirs = [h for h in _extract_hrefs(element_html)]
        if not version_dirs:
            raise ManifestNotFound(
                f"No version directories found for element '{manifest_name}' "
                f"at {element_url}"
            )

        # 3) Pick the highest semantic version
        try:
            latest_dir = max(version_dirs)
        except Exception as exc:
            raise ManifestNotFound(
                f"Failed to parse versions for '{manifest_name}' at {element_url}: {exc}"
            )
    else:
        latest_dir = manifest_version

    # 4) Build manifest URL and download YAML
    manifest_url = _join_url(
        element_url, latest_dir, "manifests/", f"{manifest_name}.yaml"
    )
    try:
        data = _http_get(manifest_url)
        manifest = yaml.safe_load(data)
        if not isinstance(manifest, dict):
            raise ManifestNotFound(f"Manifest at {manifest_url} is not a YAML mapping")
        return manifest
    except ManifestNotFound:
        raise
    except Exception as exc:
        raise ManifestNotFound(
            f"Failed to download or parse manifest at {manifest_url}: {exc}"
        )


def get_all_elements(repository_url: str) -> list[str]:
    inventory_url = _join_url(repository_url, "inventory.json")
    result = _http_get(inventory_url)
    inventory = json.loads(result)
    return sorted(inventory["elements"].keys())


def get_element_versions(repository_url: str, manifest_name: str) -> list[str]:
    try:
        # 1) List repository root to ensure element exists
        # (optional but validates repo)
        _http_get(repository_url).decode("utf-8", errors="ignore")
    except Exception as exc:
        raise ManifestNotFound(f"Failed to access repository: {repository_url}: {exc}")

    # 2) List element directory to get versions
    element_url = _join_url(repository_url, manifest_name)
    try:
        element_html = _http_get(element_url).decode("utf-8", errors="ignore")
    except Exception as exc:
        raise ManifestNotFound(
            f"Element '{manifest_name}' not found at {element_url}: {exc}"
        )

    version_dirs = [h for h in _extract_hrefs(element_html)]
    if not version_dirs:
        raise ManifestNotFound(
            f"No version directories found for element '{manifest_name}' "
            f"at {element_url}"
        )
    # Remove last slash from all versions
    version_dirs = [v.rstrip("/") for v in version_dirs]
    # Remove latest version from list if exists
    if "latest" in version_dirs:
        version_dirs.remove("latest")
    return version_dirs


def get_element_versions_by_inventory(
    repository_url: str, manifest_name: str
) -> list[str]:
    inventory_url = _join_url(repository_url, "inventory.json")
    result = _http_get(inventory_url)
    inventory = json.loads(result)
    if manifest_name not in inventory["elements"]:
        raise ManifestNotFound(
            f"Element '{manifest_name}' not found in inventory at {inventory_url}"
        )
    return sorted(inventory["elements"][manifest_name].keys())
