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

import os
import tempfile
import typing as tp
import shutil

import rich_click as click


from genesis_devtools.builder import builder as simple_builder
from genesis_devtools.builder.packer import PackerBuilder
from genesis_devtools import utils

import genesis_devtools.constants as c
from genesis_devtools.logger import ClickLogger


@click.command(
    "build",
    help=(
        "Build a Genesis element. The command build all images, manifests "
        "and other artifacts required for the element. The manifest in the "
        "project may be a raw YAML file or a template using Jinja2 "
        "templates. For Jinja2 templates, the following variables are "
        "available by default: \n\n"
        "- {{ version }}: version of the element \n\n"
        "- {{ name }}: name of the element \n\n"
        "- {{ images }}: list of images \n\n"
        "- {{ manifests }}: list of manifests \n\n"
        "\n\n"
        "Additional variables can be passed using the --manifest-var "
        "options."
    ),
)
@click.option(
    "-c",
    "--genesis-cfg-file",
    default=c.DEF_GEN_CFG_FILE_NAME,
    help="Name of the project configuration file",
)
@click.option(
    "--deps-dir",
    default=None,
    help="Directory where dependencies will be fetched",
)
@click.option(
    "--build-dir",
    default=None,
    help="Directory where temporary build artifacts will be stored",
)
@click.option(
    "-o",
    "--output-dir",
    default=c.DEF_GEN_OUTPUT_DIR_NAME,
    help="Directory where output artifacts will be stored",
)
@click.option(
    "-i",
    "--developer-key-path",
    default=None,
    help="Path to developer public key",
)
@click.option(
    "-s",
    "--version-suffix",
    default="none",
    type=click.Choice([s for s in tp.get_args(c.VersionSuffixType)]),
    show_default=True,
    help="Version suffix will be used for the build",
)
@click.option(
    "-f",
    "--force",
    show_default=True,
    is_flag=True,
    help="Rebuild if the output already exists",
)
@click.option(
    "--inventory",
    show_default=True,
    is_flag=True,
    help="Build using the inventory format",
)
@click.option(
    "--manifest-var",
    multiple=True,
    help=(
        "Additional variables to pass to the manifest template. "
        "The format is 'key=value'. For example: --manifest-var "
        "key1=value1 --manifest-var key2=value2"
    ),
)
@click.argument("project_dir", type=click.Path())
@click.pass_context
def build_cmd(
    ctx: click.Context,
    genesis_cfg_file: str,
    deps_dir: str | None,
    build_dir: str | None,
    output_dir: str | None,
    developer_key_path: str | None,
    version_suffix: c.VersionSuffixType,
    force: bool,
    project_dir: str,
    inventory: bool,
    manifest_var: tuple[str, ...],
) -> None:
    if not project_dir:
        raise click.UsageError("No project directories specified")

    manifest_vars = utils.convert_input_multiply(manifest_var)

    # Leave 'none' for backward compatibility
    if version_suffix == "none" and inventory:
        version_suffix = "element"
        click.secho(
            "Inventory mode is not supported for 'none' version suffix, "
            "using 'element' instead",
            fg="yellow",
        )

    if os.path.exists(output_dir) and not force:
        click.secho(
            f"The '{output_dir}' directory already exists. Use '--force' "
            "flag to remove current artifacts and new build.",
            fg="yellow",
        )
        return
    elif os.path.exists(output_dir) and force:
        shutil.rmtree(output_dir)

    # Developer keys
    developer_keys = utils.get_keys_by_path_or_env(
        developer_key_path, ctx.obj.developer_key_path
    )

    # Find path to genesis configuration
    try:
        gen_config = utils.get_genesis_config(project_dir, genesis_cfg_file)
    except FileNotFoundError:
        raise click.ClickException(
            f"Genesis configuration file not found in {project_dir}"
        )

    # NOTE(slashburygin): openapi_schema_validator is very heavy for cli, need replace it to simple validator
    spec = utils.load_spec()
    utils.validate_config(gen_config, spec)
    # Take all build sections from the configuration
    builds = {k: v for k, v in gen_config.items() if k.startswith("build")}
    if not builds:
        click.secho("No builds found in the configuration", fg="yellow")
        return

    logger = ClickLogger()
    packer_image_builder = PackerBuilder(logger)

    # Path where genesis.yaml configuration file is located
    work_dir = os.path.abspath(os.path.join(project_dir, c.DEF_GEN_WORK_DIR_NAME))

    # Prepare a build suffix
    build_suffix = utils.get_version_suffix(version_suffix, project_dir=project_dir)

    for _, build in builds.items():
        builder = simple_builder.SimpleBuilder.from_config(
            work_dir, build, packer_image_builder, logger, output_dir
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            builder.fetch_dependency(deps_dir or temp_dir)
            builder.build(
                build_dir,
                developer_keys,
                build_suffix,
                inventory,
                manifest_vars,
            )
