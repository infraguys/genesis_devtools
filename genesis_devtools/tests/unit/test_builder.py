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
import typing as tp
from unittest.mock import MagicMock

from genesis_devtools.builder.builder import SimpleBuilder
from genesis_devtools.logger import DummyLogger
from genesis_devtools.builder import base


class TestBuilder:

    def test_fetch_dependency(self, simple_builder: SimpleBuilder) -> None:
        deps_dir = "/tmp/deps_dir"
        simple_builder.fetch_dependency(deps_dir)
        for dep in simple_builder._deps:
            dep.fetch.assert_called_once_with(deps_dir)

        assert len(simple_builder._deps) > 1

    def test_from_config(self, build_config: tp.Dict[str, tp.Any]) -> None:
        work_dir = "/tmp/work_dir"

        builder = SimpleBuilder.from_config(
            work_dir,
            build_config,
            MagicMock(),
            DummyLogger(),
        )

        assert len(builder._deps) == 2
        assert len(builder._elements) == 1
        assert builder._work_dir == work_dir

    def test_manifest_rendering_jinja2_variables(self, tmp_path) -> None:
        """Ensure Jinja2 variables render correctly."""
        # Arrange: temp work dir and output dir
        work_dir = tmp_path / "work"
        out_dir = tmp_path / "out"
        work_dir.mkdir()
        out_dir.mkdir()

        # Create a Jinja2 manifest template that is also valid YAML before rendering
        # so that the pre-parse with yaml.safe_load succeeds.
        manifest_rel = "myapp.yaml.j2"
        manifest_path = work_dir / manifest_rel
        manifest_content = (
            "name: my-element\n"
            'version: "{{ version }}"\n'
            "images: \"{{ images | join(',') }}\"\n"
            "metadata:\n"
            '  title: "{{ name }} v{{ version }}"\n'
            '  meta_foo: "{{ foo }}"\n'
            '  meta_bar: "{{ bar }}"\n'
        )
        manifest_path.write_text(manifest_content)

        # Prepare builder with no images to focus on manifest rendering
        builder = SimpleBuilder(
            work_dir=str(work_dir),
            deps=[],
            elements=[],
            image_builder=MagicMock(spec=base.AbstractImageBuilder),
            logger=DummyLogger(),
            elements_output_dir=str(out_dir),
        )

        element = base.Element(manifest=manifest_rel, images=[])

        # Act
        builder.build_element(
            element=element,
            build_dir=None,
            developer_keys=None,
            build_suffix="1.2.3",
            inventory_mode=True,
            manifest_vars={"foo": "FOO", "bar": "BAR"},
        )

        # Assert: rendered manifest exists without the .j2 extension
        manifests_dir = out_dir / "manifests"
        rendered_manifest = manifests_dir / "myapp.yaml"
        assert rendered_manifest.exists(), "Rendered manifest file not found"

        content = rendered_manifest.read_text()
        # Variables should be interpolated
        assert 'version: "1.2.3"' in content
        assert 'title: "my-element v1.2.3"' in content
        assert 'meta_foo: "FOO"' in content
        assert 'meta_bar: "BAR"' in content
        # images list is empty -> joined string should be empty quotes
        assert 'images: ""' in content

        # Inventory file should be created and include the manifest reference
        inventory_json = out_dir / "inventory.json"
        assert inventory_json.exists(), "inventory.json was not created"

    def test_manifest_rendering_preserves_filename_without_template_ext(
        self, tmp_path
    ) -> None:
        """Ensure the rendered manifest file drops the template extension (.j2/.jinja2)."""
        work_dir = tmp_path / "work"
        out_dir = tmp_path / "out"
        work_dir.mkdir()
        out_dir.mkdir()

        manifest_rel = "service.yaml.jinja2"
        manifest_path = work_dir / manifest_rel
        manifest_path.write_text('name: svc\nversion: "{{ version }}"\n')

        builder = SimpleBuilder(
            work_dir=str(work_dir),
            deps=[],
            elements=[],
            image_builder=MagicMock(spec=base.AbstractImageBuilder),
            logger=DummyLogger(),
            elements_output_dir=str(out_dir),
        )

        element = base.Element(manifest=manifest_rel, images=[])

        builder.build_element(
            element=element,
            build_dir=None,
            developer_keys=None,
            build_suffix="0.0.1",
            inventory_mode=True,
        )

        # The output manifest should be saved without the .jinja2 extension
        assert (out_dir / "manifests" / "service.yaml").exists()
