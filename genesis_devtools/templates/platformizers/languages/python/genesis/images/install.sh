#!/usr/bin/env bash

# Copyright {{ functions.now().strftime('%Y') }} {{ author_name }}.
#
# All Rights Reserved.
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

set -eu
set -x
set -o pipefail


GC_PATH="/opt/{{ project_name }}"
GC_CFG_DIR=/etc/{{ project_name }}
GC_ART_DIR="$GC_PATH/artifacts"
VENV_PATH="$GC_PATH/.venv"
BOOTSTRAP_PATH="/var/lib/genesis/bootstrap/scripts"
SYSTEMD_SERVICE_DIR=/etc/systemd/system/


# Install packages
sudo apt update
sudo apt install libev-dev -y
# curl -LsSf https://astral.sh/uv/install.sh | sh
curl -LsSf https://releases.astral.sh/github/uv/releases/download/0.10.12/uv-installer.sh | sh
source "$HOME/.local/bin/env"

# Install {{ project_name }}
if [ -d "$GC_PATH/etc/{{ project_name }}" ]; then
    sudo cp -r "$GC_PATH/etc/{{ project_name }}" /etc/
fi

sudo cp "$GC_PATH/genesis/images/bootstrap.sh" "$BOOTSTRAP_PATH/0900-{{ project_name }}-bootstrap.sh"
sudo chmod +x "$BOOTSTRAP_PATH/0900-{{ project_name }}-bootstrap.sh"

cd "$GC_PATH"
{% if project_python_package_manager == "uv" %}
uv sync
source "$GC_PATH/.venv/bin/activate"
{% elif project_python_package_manager == "pip" %}
python3 -m venv .venv
source "$GC_PATH/.venv/bin/activate"
pip install -e .
{% endif %}


# Create links to venv and install systemd service files
# Example input: project_systemd_services=foo-api,bar-api,baz-worker
# Example output (for foo-api):
# - ln -sf "$VENV_PATH/bin/foo-api" "/usr/bin/foo-api"
# - cp "$GC_PATH/etc/systemd/foo-api.service" "$SYSTEMD_SERVICE_DIR"
# - systemctl enable "foo-api.service"

PROJECT_SYSTEMD_SERVICES="{{ project_systemd_services | default('', true) }}"

if [ -n "${PROJECT_SYSTEMD_SERVICES}" ]; then
    IFS=',' read -r -a SYSTEMD_SERVICES <<< "${PROJECT_SYSTEMD_SERVICES}"

    for SERVICE_NAME in "${SYSTEMD_SERVICES[@]}"; do
        SERVICE_NAME="$(echo "${SERVICE_NAME}" | xargs)"
        if [ -z "${SERVICE_NAME}" ]; then
            continue
        fi

        sudo ln -sf "${VENV_PATH}/bin/${SERVICE_NAME}" "/usr/bin/${SERVICE_NAME}"
        sudo cp "${GC_PATH}/etc/systemd/${SERVICE_NAME}.service" "${SYSTEMD_SERVICE_DIR}"
        sudo systemctl enable "${SERVICE_NAME}.service"
    done
fi

cat <<EOT | sudo tee /etc/motd
▄▖        ▘  
▌ █▌▛▌█▌▛▘▌▛▘
▙▌▙▖▌▌▙▖▄▌▌▄▌


Welcome to {{ project_name }} node!

{% if project_url %}
The project page:
{{ project_url }}
{% endif %}

EOT