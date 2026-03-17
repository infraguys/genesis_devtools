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

import abc
import collections
import typing as tp

from genesis_devtools.wizards import exceptions as wiz_exceptions
from genesis_devtools.wizards.scenarios import base as scenarios


class AbstractWizard(abc.ABC):
    """Abstract wizard class."""

    def play_action_with_nested_scenarios(
        self,
        key: str,
        action: scenarios.Action,
        defaults: dict[str, int | float | str | bool] | None = None,
    ) -> None:
        """Play a single action."""
        # Use default value if provided explicitly
        defaults = defaults or {}

        if key in defaults:
            result = defaults[key]

            # Check if it's a name of a scenario in choices
            if action.choices and isinstance(action.choices[0], scenarios.Scenario):
                # Find the scenario by name
                for choice in action.choices:
                    if choice.name == result:
                        result = choice
                        break
                else:
                    raise ValueError(f"Scenario '{result}' not found in choices")
            else:
                result = self.play_action(action, result)
        else:
            if callable(action.default) and not isinstance(
                action.default, scenarios.Scenario
            ):
                action.default = action.default()
            # Ask a user to provide a value

            result = self.play_action(action)

        action.handle_result(result)

        # If the result is a scenario, run it
        if isinstance(result, scenarios.Scenario):
            self.run(result, defaults)

    def run(
        self,
        scenario: scenarios.Scenario,
        defaults: dict[str, int | float | str | bool] | None = None,
    ) -> scenarios.Scenario:
        """Play the scenario and fill in the result for each action."""
        # Start the scenario
        self.welcome(scenario)

        # Use deques to have an ability to go
        # back to the previous actions
        incoming = collections.deque(scenario)
        completed = collections.deque()

        while incoming:
            action_key, action = incoming.popleft()

            # If the result is a scenario and it's not in the choices, run it
            if isinstance(action.result, scenarios.Scenario) and not action.choices:
                self.run(action.result, defaults)
            else:
                # TODO(akremenetsky): Implement return back to the previous action
                try:
                    self.play_action_with_nested_scenarios(action_key, action, defaults)
                # The user canceled the scenario, finish it
                except wiz_exceptions.CanceledScenarioError:
                    completed.append((action_key, action))
                    break

            completed.append((action_key, action))

        # Finish the scenario
        self.summary(scenario)
        return scenario

    @abc.abstractmethod
    def play_action(
        self, action: scenarios.Action, initial_value: str | None = None
    ) -> tp.Any:
        """Play a single action."""

    def welcome(self, scenario: scenarios.Scenario) -> None:
        """Display a welcome message."""
        pass

    def summary(self, scenario: scenarios.Scenario) -> None:
        """Display a summary message."""
        pass
