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
import subprocess
import typing as tp
import shutil
from importlib.resources import files

from genesis_devtools.builder import base
from genesis_devtools.logger import AbstractLogger, DummyLogger
from genesis_devtools import constants as c


file_provisioner_tmpl = """
  provisioner "file" {{
      source      = "{source}"
      destination = "{tmp_destination}"
  }}
  provisioner "shell" {{
    inline = [
      "sudo mkdir -p {destination_dir}",
      "sudo mv {tmp_destination} {destination}",
    ]
  }}
"""


dev_keys_provisioner_tmpl = """
  provisioner "file" {{
      source      = "{source}"
      destination = "/tmp/__dev_keys"
  }}
"""


packer_build_tmpl = """
variable "output_directory" {{
  type    = string
  default = "{output_directory}"
}}

build {{
  source "qemu.{profile}" {{
    name = "{name}"
  }}

  {file_provisioners}

  provisioner "shell" {{
    execute_command = "sudo -S env {{{{ .Vars }}}} {{{{ .Path }}}}"
    script          = "{script}"
    env             = {{
      {envs}
    }}
  }}

  {developer_keys}
}}
"""


class PackerVariable(tp.NamedTuple):
    name: str
    value: str | int | float | list | dict | None = ""
    var_tmpl: str = "{name} = {value}"

    def render(self) -> str:
        data = self._asdict()
        data.pop("var_tmpl", None)

        # Need quotes for strings in HCL
        if isinstance(self.value, str):
            data["value"] = f'"{self.value}"'

        return self.var_tmpl.format(**data)

    @classmethod
    def variable_file_content(cls, overrides: dict[str, tp.Any]) -> str:
        if not overrides:
            return ""

        variables = []
        for k, v in overrides.items():
            variables.append(cls(name=k, value=v))

        return "\n".join([v.render() for v in variables])


def _get_profile_files(base: str) -> str:
    """Get base files for the image."""
    profile_files = []
    for bfile in files(f"{c.PKG_NAME}.packer.{base}").iterdir():
        profile_files.append(bfile)

    return profile_files


class PackerBuilder(base.DummyImageBuilder):
    """Packer image builder.

    Packer image builder that uses Packer tools to build images.
    """

    def __init__(self, logger: AbstractLogger | None = None) -> None:
        super().__init__()
        self._logger = logger or DummyLogger()

    def _resolve_envs(self, envs: list[str]) -> str:
        if len(envs) == 0:
            return ""

        result = []

        for env in envs:
            # Check if the env is a wildcard
            if env.endswith("*"):
                for _env in (e for e in os.environ if e.startswith(env[:-1])):
                    result.append(f'{_env}="{os.environ[_env]}"')
                continue
            # Check if there a default value for the env
            elif "=" in env:
                name, value = tuple(e.strip() for e in env.split("="))
            else:
                name, value = env.strip(), ""

            result.append(f'{name}="{os.environ.get(name, value)}"')

        return "\n".join(result)

    def pre_build(
        self,
        image_dir: str,
        image: base.Image,
        deps: list[base.AbstractDependency],
        developer_keys: str | None = None,
        output_dir: str = c.DEF_GEN_OUTPUT_DIR_NAME,
    ) -> None:
        """Actions to prepare the environment for building the image."""

        # Prepare the packer build file
        # Data provisioners
        provisioners = []
        for i, dep in enumerate(deps):
            if not dep.local_path:
                self._logger.warn(
                    f"Dependency {dep.img_dest} has no local path "
                    "and will be skipped"
                )
                continue

            tmp_dest = os.path.join(
                "/tmp/", os.path.basename(dep.img_dest) + f"_{i}"
            )
            provisioners.append(
                file_provisioner_tmpl.format(
                    source=dep.local_path,
                    destination_dir=os.path.dirname(dep.img_dest),
                    destination=dep.img_dest,
                    tmp_destination=tmp_dest,
                )
            )

        # Prepare developer
        if developer_keys:
            dev_key_path = os.path.join(image_dir, "__dev_keys")
            with open(dev_key_path, "w") as f:
                f.write(developer_keys)
            developer_keys_prov = dev_keys_provisioner_tmpl.format(
                source=dev_key_path
            )
        else:
            developer_keys_prov = ""

        # Prepare envs
        envs = f'GEN_IMAGE_PROFILE = "{image.profile}"\n'
        if image.envs:
            envs += self._resolve_envs(image.envs)

        profile = image.profile.replace("_", "-")
        packer_build = packer_build_tmpl.format(
            profile=profile,
            name=image.name or profile,
            file_provisioners="\n".join(provisioners),
            script=image.script,
            developer_keys=developer_keys_prov,
            output_directory=output_dir,
            envs=envs,
        )

        # Write the packer build file
        main_path = os.path.join(image_dir, "main.pkr.hcl")
        with open(main_path, "w") as f:
            f.write(packer_build)

        # Copy profile files to the image directory
        profile_files = _get_profile_files(image.profile)
        for bfile in profile_files:
            shutil.copy(bfile, image_dir)

        # Override variables
        override = image.override or {}

        # Enrich with the image format
        override["img_format"] = image.format

        # Write the packer variables
        variables = PackerVariable.variable_file_content(override)
        with open(
            os.path.join(image_dir, "overrides.auto.pkrvars.hcl"), "w"
        ) as f:
            f.write(variables)

        subprocess.run(["packer", "init", image_dir], check=True)

    def build(
        self,
        image_dir: str,
        image: base.Image,
        developer_keys: str | None = None,
    ) -> None:
        """Actions to build the image."""
        self._logger.important(f"Build image: {image.name}")
        subprocess.run(
            ["packer", "build", "-parallel-builds=1", image_dir], check=True
        )
