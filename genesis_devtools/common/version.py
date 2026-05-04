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
import time

import git

import genesis_devtools.constants as c


def get_project_version(
    path: str, rc_branches=c.RC_BRANCHES, start_version=(0, 0, 0)
) -> str:
    if not os.path.exists(path):
        raise FileNotFoundError(f"File {path} not found")

    if not os.path.isdir(path):
        raise ValueError(f"Path {path} is not a directory")

    # Open the git repo
    repo = git.Repo(path)

    # If a tag is set, return it as version
    for tag in repo.tags:
        if tag.commit == repo.head.commit:
            return tag.name

    # Find the nearest tag
    nearest_tag = None
    for commit in repo.iter_commits(max_count=100):
        for tag in repo.tags:
            if tag.commit == commit:
                nearest_tag = tag
                break

        if nearest_tag:
            break

    # Get the current version
    if nearest_tag:
        try:
            major, minor, patch = (int(i) for i in nearest_tag.name.split("."))
        except ValueError:
            raise ValueError(
                f"Invalid format for tag {nearest_tag.name}, "
                "expected major.minor.patch version format"
            )
    # Empty repo, start from 0.0.0
    else:
        major, minor, patch = start_version

    # Increment the version
    patch += 1

    hexsha = repo.head.commit.hexsha

    try:
        branch = repo.active_branch.name
    except Exception:
        # Detached head
        branch = None

    date = repo.head.commit.committed_date
    date_repr = time.strftime("%Y%m%d%H%M%S", time.gmtime(date))

    # Determine the prefix
    if branch in rc_branches:
        prefix = "rc"
    else:
        prefix = "dev"

    return f"{major}.{minor}.{patch}-{prefix}+{date_repr}.{hexsha[:8]}"
