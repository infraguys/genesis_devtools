#    Copyright 2026 Genesis Corporation.
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

import dataclasses
import json
import os
import typing as tp

import requests

from genesis_devtools import exceptions
from genesis_devtools import constants


class IAMClientError(exceptions.DevToolsException):
    pass


class TokenFileAlreadyExistsError(exceptions.DevToolsException):
    pass


class TokenFileNotFoundError(exceptions.DevToolsException):
    pass


@dataclasses.dataclass(frozen=True)
class Token:
    url: str
    project_id: str
    token: str
    refresh_token: str
    ttl: int = constants.DEFAULT_IAM_TTL
    scope: str = constants.DEFAULT_IAM_SCOPE

    @staticmethod
    def file_path(project_dir: str) -> str:
        return os.path.join(os.path.abspath(project_dir), ".genesis", "auth.json")

    @classmethod
    def exists(cls, project_dir: str) -> bool:
        return os.path.exists(cls.file_path(project_dir))

    def to_dict(self) -> dict[str, tp.Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, tp.Any]) -> "Token":
        return cls(**data)

    @classmethod
    def load(cls, project_dir: str) -> "Token":
        auth_file = cls.file_path(project_dir)
        if not os.path.exists(auth_file):
            raise TokenFileNotFoundError(f"Token file not found: {auth_file}")

        with open(auth_file, "r") as f:
            data = json.load(f)

        return cls.from_dict(data)

    def save(self, project_dir: str, force: bool = False) -> None:
        auth_file = self.file_path(project_dir)
        auth_dir = os.path.dirname(auth_file)

        if os.path.exists(auth_file) and not force:
            raise TokenFileAlreadyExistsError(f"Token file already exists: {auth_file}")

        os.makedirs(auth_dir, exist_ok=True)
        with open(auth_file, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        os.chmod(auth_file, 0o600)


class IAMClient:
    def __init__(
        self,
        iam_client_endpoint: str,
        project_id: str,
        client_id: str | None = None,
        client_secret: str | None = None,
        scope: str = constants.DEFAULT_IAM_SCOPE,
        ttl: int = constants.DEFAULT_IAM_TTL,
        refresh_ttl: int = constants.DEFAULT_IAM_REFRESH_TTL,
        timeout_s: int | float = 30,
    ):
        self._iam_client_endpoint = iam_client_endpoint.rstrip("/")
        self._project_id = project_id
        self._client_id = client_id
        self._client_secret = client_secret
        self._scope = scope
        self._ttl = ttl
        self._refresh_ttl = refresh_ttl
        self._timeout_s = timeout_s

    def _request_json(
        self,
        method: str,
        url: str,
        error_prefix: str,
        **kwargs: tp.Any,
    ) -> dict[str, tp.Any]:
        try:
            response = requests.request(
                method,
                url,
                timeout=self._timeout_s,
                **kwargs,
            )
        except requests.RequestException as exc:
            raise IAMClientError(f"Unable to call IAM endpoint: {exc}")

        if not response.ok:
            raise IAMClientError(
                f"{error_prefix} ({response.status_code}): {response.text}"
            )

        try:
            return response.json()
        except ValueError:
            raise IAMClientError("IAM returned non-JSON response")

    @staticmethod
    def _extract_tokens(
        response_payload: dict[str, tp.Any],
    ) -> tuple[str, str]:
        try:
            access_token = response_payload["access_token"]
            refresh_token = response_payload["refresh_token"]
        except KeyError as exc:
            raise IAMClientError(f"IAM response missing field: {exc}")

        return access_token, refresh_token

    @property
    def iam_client_endpoint(self) -> str:
        return self._iam_client_endpoint

    @property
    def token_endpoint(self) -> str:
        return f"{self._iam_client_endpoint}/actions/get_token/invoke"

    @property
    def me_endpoint(self) -> str:
        return f"{self._iam_client_endpoint}/actions/me"

    def get_token_by_password(self, username: str, password: str) -> Token:
        data_payload: dict[str, str] = {
            "grant_type": "password",
            "username": username,
            "password": password,
            "scope": self._scope,
            "ttl": str(self._ttl),
            "refresh_ttl": str(self._refresh_ttl),
        }

        if self._client_id is not None:
            data_payload["client_id"] = self._client_id
        if self._client_secret is not None:
            data_payload["client_secret"] = self._client_secret

        response_payload = self._request_json(
            "POST",
            self.token_endpoint,
            "IAM authentication failed",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=data_payload,
        )
        access_token, refresh_token = self._extract_tokens(response_payload)

        return Token(
            url=self.iam_client_endpoint,
            project_id=self._project_id,
            token=access_token,
            refresh_token=refresh_token,
            ttl=self._ttl,
            scope=self._scope,
        )

    def refresh(
        self,
        token: Token,
        ttl: int | None = None,
        scope: str | None = None,
    ) -> Token:
        effective_ttl = token.ttl if ttl is None else ttl
        effective_scope = token.scope if scope is None else scope

        data_payload: dict[str, str] = {
            "grant_type": "refresh_token",
            "refresh_token": token.refresh_token,
            "ttl": str(effective_ttl),
            "refresh_ttl": str(self._refresh_ttl),
            "scope": effective_scope,
        }

        if self._client_id is not None:
            data_payload["client_id"] = self._client_id
        if self._client_secret is not None:
            data_payload["client_secret"] = self._client_secret

        response_payload = self._request_json(
            "POST",
            self.token_endpoint,
            "IAM refresh failed",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=data_payload,
        )
        access_token, refresh_token = self._extract_tokens(response_payload)

        return Token(
            url=self.iam_client_endpoint,
            project_id=self._project_id,
            token=access_token,
            refresh_token=refresh_token,
            ttl=effective_ttl,
            scope=effective_scope,
        )

    def me(self, token: Token) -> dict[str, tp.Any]:
        return self._request_json(
            "GET",
            self.me_endpoint,
            "IAM token validation failed",
            headers={"Authorization": f"Bearer {token.token}"},
        )
