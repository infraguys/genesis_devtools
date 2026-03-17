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
import typing as tp

from genesis_devtools.wizards import exceptions
from genesis_devtools.wizards import constants as c


SimpleType = tp.Union[int, str, bool, float]
ActionValueType = tp.Union[SimpleType, "Scenario"]


@dataclasses.dataclass
class Action:
    """Base action class.

    TODO: Add long description
    """

    prompt: str
    result: tp.Optional[ActionValueType] = None
    default: tp.Optional[ActionValueType] = None
    required: bool = False
    choices: tp.Optional[list[ActionValueType]] = None
    description: tp.Optional[str] = None
    sensitive: bool = False

    def handle_result(self, result: ActionValueType) -> None:
        """Handle the result of the action."""
        self.result = result


@dataclasses.dataclass
class ConfirmationAction(Action):
    """Asks the user to confirm proceeding with the scenario.

    Stores the boolean answer and aborts the scenario when the user declines.
    """

    prompt: str
    result: tp.Optional[bool] = None
    default: tp.Optional[bool] = None
    required: bool = False

    def handle_result(self, result: bool) -> None:
        """Handle the result of the action."""
        self.result = result

        if not result:
            raise exceptions.CanceledScenarioError("Scenario cancelled by user")


@dataclasses.dataclass
class Scenario:
    """Base scenario class.

    TODO: Add long description
    How it related to engines and wizards?
    """

    name: str
    description: str = ""
    welcome: str | tp.Callable[[], str] = ""
    summary: str | tp.Callable[[], str] = ""
    actions: dict[str, Action] = dataclasses.field(default_factory=dict)

    def __iter__(self) -> tp.Iterator[tp.Tuple[str, Action]]:
        return iter(self.actions.items())

    def flatten(self) -> list["Scenario"]:
        """Flatten the scenario and its children."""
        result = [self]
        for action in self.actions.values():
            if isinstance(action.result, Scenario):
                result.extend(action.result.flatten())
        return result


@dataclasses.dataclass
class TemplateScenario(Scenario):
    """Scenario for template-based project generation.

    TODO: Add long description
    """

    template: str = c.EMPTY_TEMPLATE

    def __post_init__(self):
        """Initialize the template scenario."""
        self.template = self.template or self.name
