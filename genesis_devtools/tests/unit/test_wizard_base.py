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

import pytest

from genesis_devtools.wizards.scenarios import base as scenarios
from genesis_devtools.wizards.wizards import base as wizard_base


class DummyWizard(wizard_base.AbstractWizard):
    def __init__(self, values=None):
        self.play_calls = []
        self.summary_calls = []
        self.welcome_calls = []
        self._values = list(values or [])

    def play_action(self, action: scenarios.Action, initial_value: str | None = None):
        self.play_calls.append(
            {
                "prompt": action.prompt,
                "initial_value": initial_value,
                "default": action.default,
            }
        )
        if self._values:
            return self._values.pop(0)
        if initial_value is not None:
            return initial_value
        return f"value:{action.prompt}"

    def welcome(self, scenario: scenarios.Scenario) -> None:
        self.welcome_calls.append(scenario.name)

    def summary(self, scenario: scenarios.Scenario) -> None:
        self.summary_calls.append(scenario.name)


class TestAbstractWizard:
    def test_play_action_with_unknown_scenario_name_raises_value_error(self) -> None:
        wizard = DummyWizard()

        action = scenarios.Action(
            prompt="Project type",
            choices=[
                scenarios.Scenario(name="generic"),
                scenarios.Scenario(name="python"),
            ],
        )

        with pytest.raises(ValueError, match="Scenario 'go' not found in choices"):
            wizard.play_action_with_nested_scenarios(
                "project_type",
                action,
                defaults={"project_type": "go"},
            )

    def test_play_action_with_nested_scenario_default_by_name(self) -> None:
        wizard = DummyWizard()

        python_scenario = scenarios.Scenario(name="python")
        generic_scenario = scenarios.Scenario(name="generic")

        action = scenarios.Action(
            prompt="Project type",
            choices=[generic_scenario, python_scenario],
        )

        wizard.play_action_with_nested_scenarios(
            "project_type",
            action,
            defaults={"project_type": "python"},
        )

        assert action.result is python_scenario
        assert wizard.play_calls == []
        assert wizard.welcome_calls == ["python"]
        assert wizard.summary_calls == ["python"]

    def test_play_action_with_callable_default(self) -> None:
        wizard = DummyWizard()
        action = scenarios.Action(
            prompt="Project name",
            default=lambda: "demo-project",
        )

        wizard.play_action_with_nested_scenarios("project_name", action, defaults={})

        assert action.default == "demo-project"
        assert action.result == "value:Project name"
        assert wizard.play_calls[0]["initial_value"] is None

    def test_run_stops_on_canceled_scenario(self) -> None:
        wizard = DummyWizard(values=[False, "should-not-be-used"])
        scenario = scenarios.Scenario(
            name="root",
            actions={
                "confirm": scenarios.ConfirmationAction(prompt="Continue"),
                "next": scenarios.Action(prompt="Next step"),
            },
        )

        wizard.run(scenario)

        assert scenario.actions["confirm"].result is False
        assert scenario.actions["next"].result is None
        assert [c["prompt"] for c in wizard.play_calls] == ["Continue"]
        assert wizard.summary_calls == ["root"]
