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

import os

from rich_click.rich_context import RichContext
import pathlib

from genesis_devtools import utils

md_base_template = """
# {command_name}

{description}

## Usage

```console
{usage}
```

## Options
{options}

## CLI Help

```console
{help}
```

"""


def recursive_help(cmd, parent=None):
    ctx = RichContext(cmd, info_name=cmd.name, parent=parent)

    yield {
        "command": cmd,
        "help": cmd.get_help(ctx),
        "parent": parent.info_name if parent else "",
        "usage": cmd.get_usage(ctx),
        "params": cmd.get_params(ctx),
        "options": cmd.collect_usage_pieces(ctx),
    }

    commands = getattr(cmd, "commands", {})
    for sub in commands.values():
        for helpdct in recursive_help(sub, ctx):
            yield helpdct


def dump_helper(base_command):
    """
    Dumping help usage files from Click Help files into an md
    """
    docs_path = pathlib.Path(os.path.join(utils.PROJECT_PATH, "docs", "cli"))
    for helpdct in recursive_help(base_command):
        command = helpdct.get("command")
        helptxt = helpdct.get("help")
        usage = helpdct.get("usage")
        parent = helpdct.get("parent", "") or ""
        options = {
            opt.name: {
                "usage": "\n".join(opt.opts),
                "prompt": getattr(opt, "prompt", None),
                "required": getattr(opt, "required", None),
                "default": getattr(opt, "default", None),
                "help": getattr(opt, "help", None),
                "type": getattr(t, "name", str(t))
                if (t := getattr(opt, "type", None))
                else "None",
            }
            for opt in helpdct.get("params", [])
        }
        full_command = command.name
        if parent:
            full_command = f"{parent}_{full_command}"
        md_template = md_base_template.format(
            command_name=full_command,
            description=command.help,
            usage=usage,
            options="\n".join(
                [
                    f"* `{name}`{' (REQUIRED)' if opt.get('required') else ''}: \n"
                    f"  * Type: {opt.get('type')} \n"
                    f"  * Default: `{str(opt.get('default')).lower()}`\n"
                    f"  * Usage: `{opt.get('usage')}`\n"
                    "\n"
                    f"  {opt.get('help') or ''}\n"
                    f"\n"
                    for name, opt in options.items()
                ]
            ),
            help=helptxt,
        )

        if not docs_path.exists():
            docs_path.mkdir(parents=True, exist_ok=False)

        md_file_path = docs_path.joinpath(
            full_command.replace(" ", "-").lower() + ".md"
        ).absolute()

        # Create the file per each command
        with open(md_file_path, "w") as md_file:
            md_file.write(md_template)
