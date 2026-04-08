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

import requests
import secrets
import uuid as sys_uuid

import rich_click as click

from bazooka import client as bazooka_client
from bazooka import exceptions as bazooka_exc


def register_realm(
    ecosystem_endpoint: str,
    org_token: str | None = None,
) -> tuple[str, str, dict[str, str] | None]:
    """
    Register stand in ecosystem.

    Args:
        ecosystem_endpoint: Ecosystem API endpoint
        org_token: Optional organization token for authorization

    Returns:
        Tuple of (stand_uuid, stand_secret, tokens_dict)
        tokens_dict contains access_token and refresh_token if org_token was provided,
        otherwise None

    Raises:
        bazooka_exc.BazookaError: If registration fails and org_token is provided
    """
    # Generate UUID and secret
    stand_uuid = str(sys_uuid.uuid4())
    stand_secret = secrets.token_hex(64)  # 128 characters

    # Prepare request data
    request_data = {
        "uuid": stand_uuid,
        "secret": stand_secret,
    }

    # Prepare headers
    headers = {
        "Content-Type": "application/json",
    }

    # Add authorization header if org_token is provided
    if org_token:
        headers["Authorization"] = f"Bearer {org_token}"

    # Create bazooka client with appropriate timeout
    # Use 10 seconds timeout when no org_token, otherwise use default 300 seconds
    timeout = 10 if not org_token else 300
    client = bazooka_client.Client(default_timeout=timeout)

    # Make registration request
    try:
        response = client.post(
            f"{ecosystem_endpoint}/api/ecosystem/v1/realms/",
            json=request_data,
            headers=headers,
        )
    except bazooka_exc.UnauthorizedError:
        if org_token:
            raise click.ClickException(
                "Invalid or expired organization token. Please check your org_token and try again."
            )
        else:
            # If no org_token, registration is non-critical
            return stand_uuid, stand_secret, {}
    except (bazooka_exc.BaseHTTPException, requests.exceptions.ConnectionError):
        if org_token:
            raise
        else:
            # If no org_token, registration is non-critical
            return stand_uuid, stand_secret, {}

    # Parse response
    tokens_dict = {}
    if org_token:
        tokens_dict = {
            "access_token": response.json().get("access_token"),
            "refresh_token": response.json().get("refresh_token"),
        }

    return stand_uuid, stand_secret, tokens_dict
