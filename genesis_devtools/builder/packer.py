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
      EXAMPLE_VARIABLE = "example_value"
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
    def variable_file_content(cls, overrides: tp.Dict[str, tp.Any]) -> str:
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

    def __init__(
        self, output_dir: str, logger: AbstractLogger | None = None
    ) -> None:
        super().__init__()
        self._logger = logger or DummyLogger()
        self._output_dir = output_dir

    def pre_build(
        self,
        image_dir: str,
        image: base.Image,
        deps: tp.List[base.AbstractDependency],
        developer_keys: str | None = None,
    ) -> None:
        """Actions to prepare the environment for building the image."""

        # Prepare the packer build file
        # Data provisioners
        provisioners = []
        for i, dep in enumerate(deps):
            tmp_dest = os.path.join(
                "/tmp/", os.path.basename(dep.img_dest) + f"_{i}"
            )
            provisioners.append(
                file_provisioner_tmpl.format(
                    source=dep.local_path,
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

        profile = image.profile.replace("_", "-")
        packer_build = packer_build_tmpl.format(
            profile=profile,
            name=image.name or profile,
            file_provisioners="\n".join(provisioners),
            script=image.script,
            developer_keys=developer_keys_prov,
            output_directory=self._output_dir,
        )

        # Write the packer build file
        main_path = os.path.join(image_dir, "main.pkr.hcl")
        with open(main_path, "w") as f:
            f.write(packer_build)

        # Copy profile files to the image directory
        profile_files = _get_profile_files(image.profile)
        for bfile in profile_files:
            shutil.copy(bfile, image_dir)

        # Override variables if they are provided
        if variables := PackerVariable.variable_file_content(
            image.override or ()
        ):
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
