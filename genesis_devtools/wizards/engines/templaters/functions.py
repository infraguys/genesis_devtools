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

import datetime
import typing as tp


def now(tz=None):
    """
    Returns the current date and time in the specified timezone.

    :param tz: The timezone whose current date and time to return. If None,
               the local timezone is used.
    :type tz: datetime.tzinfo or None

    :rtype: datetime.datetime
    """
    return datetime.datetime.now(tz=tz)


def csv_list(value: tp.Any, separator: str = ",") -> list[str]:
    if value is None:
        return []

    if isinstance(value, list):
        result = []
        for item in value:
            if item is None:
                continue
            item_str = str(item).strip()
            if item_str:
                result.append(item_str)
        return result

    if isinstance(value, str):
        items = value.split(separator)
    else:
        items = str(value).split(separator)

    return [item.strip() for item in items if item.strip()]


FUNCTIONS = {
    "now": now,
    "csv_list": csv_list,
}


def get_jinja_functions():
    """
    Retrieves a copy of the available Jinja functions.

    :return: A dictionary containing Jinja function names as keys and their
             corresponding callable objects as values.
    :rtype: dict
    """

    return FUNCTIONS.copy()


__all__ = ["get_jinja_functions"]
