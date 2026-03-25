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
import os
import typing as tp
import uuid


def is_valid_uuid(uuid_to_test: tp.Any, version: int = 4) -> bool:
    try:
        uuid.UUID(uuid_to_test, version=version)
        return True
    except (ValueError, AttributeError):
        return False


def get_project_path() -> str:
    # Repository path
    return os.sep.join(__file__.split(os.sep)[:-3])


def convert_to_nearest_type(value: str) -> bool | int | float | list | dict | str:
    lower_value = value.lower()
    if lower_value in ("true", "false"):
        return lower_value == "true"

    try:
        return int(value)
    except ValueError:
        pass

    try:
        return float(value)
    except ValueError:
        pass

    if (value.startswith("[") and value.endswith("]")) or (
        value.startswith("{") and value.endswith("}")
    ):
        try:
            parsed = json.loads(value)
            if isinstance(parsed, (list, dict)):
                return parsed
        except (ValueError, TypeError):
            pass

    return value


PROJECT_PATH = get_project_path()
