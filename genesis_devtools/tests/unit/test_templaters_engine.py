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

import pathlib

import pytest

from genesis_devtools.wizards.engines.templaters import templaters


class FakeTemplateSetting:
    def __init__(self, path: str, template_files: list[str], settings_vars: dict):
        self.path = path
        self.template_files = template_files
        self.settings_vars = settings_vars


def _make_engine(
    target_dir: pathlib.Path, force: bool
) -> templaters.JinjaTemplateEngine:
    engine = object.__new__(templaters.JinjaTemplateEngine)
    engine._target_path = target_dir
    engine._force = force
    engine._settings = []
    return engine


class TestJinjaTemplateEngine:
    def test_render_template_files_raises_if_target_exists_without_force(
        self, tmp_path: pathlib.Path
    ) -> None:
        source_dir = tmp_path / "source"
        target_dir = tmp_path / "target"
        source_dir.mkdir()
        target_dir.mkdir()

        source_file = source_dir / "settings.txt"
        source_file.write_text("name={{ name }}", encoding="utf-8")

        target_file = target_dir / "settings.txt"
        target_file.write_text("old-value", encoding="utf-8")

        engine = _make_engine(target_dir=target_dir, force=False)

        with pytest.raises(FileExistsError):
            engine._render_template_files(
                template_path=source_dir.as_posix(),
                template_files=[source_file.as_posix()],
                all_settings={"name": "genesis"},
            )

    def test_render_template_files_overwrites_if_force_enabled(
        self, tmp_path: pathlib.Path
    ) -> None:
        source_dir = tmp_path / "source"
        target_dir = tmp_path / "target"
        source_dir.mkdir()
        target_dir.mkdir()

        source_file = source_dir / "settings.txt"
        source_file.write_text("name={{ name }}", encoding="utf-8")

        target_file = target_dir / "settings.txt"
        target_file.write_text("old-value", encoding="utf-8")

        engine = _make_engine(target_dir=target_dir, force=True)

        rendered_files = engine._render_template_files(
            template_path=source_dir.as_posix(),
            template_files=[source_file.as_posix()],
            all_settings={"name": "genesis"},
        )

        assert rendered_files == [target_file.as_posix()]
        assert target_file.read_text(encoding="utf-8") == "name=genesis"

    def test_render_template_rolls_back_saved_files_on_error(
        self, tmp_path: pathlib.Path
    ) -> None:
        source_ok_dir = tmp_path / "source_ok"
        source_fail_dir = tmp_path / "source_fail"
        target_dir = tmp_path / "target"

        source_ok_dir.mkdir()
        source_fail_dir.mkdir()
        target_dir.mkdir()

        source_ok_file = source_ok_dir / "ok.txt"
        source_ok_file.write_text("ok={{ value }}", encoding="utf-8")

        source_fail_file = source_fail_dir / "conflict.txt"
        source_fail_file.write_text("bad={{ value }}", encoding="utf-8")

        (target_dir / "conflict.txt").write_text("already-exists", encoding="utf-8")

        engine = _make_engine(target_dir=target_dir, force=False)
        engine._settings = [
            FakeTemplateSetting(
                path=source_ok_dir.as_posix(),
                template_files=[source_ok_file.as_posix()],
                settings_vars={"value": "one"},
            ),
            FakeTemplateSetting(
                path=source_fail_dir.as_posix(),
                template_files=[source_fail_file.as_posix()],
                settings_vars={"value": "two"},
            ),
        ]

        with pytest.raises(FileExistsError):
            engine.render_template()

        assert not (target_dir / "ok.txt").exists()
