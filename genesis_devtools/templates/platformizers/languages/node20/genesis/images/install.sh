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

echo "Building {{ project_name }} image"

# Install packages
# Install NodeJS from official repository (https://deb.nodesource.com/)
sudo curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -

sudo apt-get update

PACKAGES_TO_INSTALL="nodejs"
{% if project_node_install_redis %}
PACKAGES_TO_INSTALL="$PACKAGES_TO_INSTALL redis-server"
{% endif %}
{% if project_node_install_nginx %}
PACKAGES_TO_INSTALL="$PACKAGES_TO_INSTALL nginx"
{% endif %}
sudo apt-get install -y "$PACKAGES_TO_INSTALL"

{% if project_node_install_redis %}
# Configure Redis
sudo sed -i 's/^bind .*/bind 127.0.0.1/' /etc/redis/redis.conf
sudo sed -i 's/^supervised no/supervised systemd/' /etc/redis/redis.conf
sudo mkdir -p /etc/systemd/system/redis-server.service.d

sudo tee /etc/systemd/system/redis-server.service.d/override.conf > /dev/null << EOF
[Service]
Restart=on-failure
RestartSec=10s
TimeoutStopSec=10s
EOF

sudo systemctl daemon-reload
sudo systemctl enable redis-server
{% endif %}


cd "$GC_PATH"
{% if project_node_install_pm2 %}
# Install & build project
npm install -g pm2
npm install
{% endif %}


# Build and start all configured Node.js packages with PM2.
# Expected input (from template variable `project_node_packages`) is a
# comma-separated list of package names that exist under "$GC_PATH/packages".
# For each non-empty, trimmed package name:
#   - change directory to "$GC_PATH/packages/<package_name>"
#   - run `npm run build` to produce the build artifacts
#   - start the app with PM2 using `npm start`, under the {{ project_node_user }} user
#     with:
#       * --watch: automatically reload the process when source files change
#       * --ignore-watch="node_modules": avoid excessive restarts from dependency changes
#       * --restart-delay=10000: wait 10 seconds before restarting after a crash
#       * --name "<package_name>": set a stable, human-readable PM2 process name
PROJECT_NODE_PACKAGES="{{ project_node_packages | default('', true) }}"

if [ -n "${PROJECT_NODE_PACKAGES}" ]; then
    IFS=',' read -r -a NODE_PACKAGES <<< "${PROJECT_NODE_PACKAGES}"

    for PACKAGE_NAME in "${NODE_PACKAGES[@]}"; do
        PACKAGE_NAME="$(echo "${PACKAGE_NAME}" | xargs)"
        if [ -z "${PACKAGE_NAME}" ]; then
            continue
        fi

        cd "$GC_PATH/packages/${PACKAGE_NAME}"
        npm run build
        sudo -u {{ project_node_user }} pm2 start npm --watch --ignore-watch="node_modules" \
            --restart-delay=10000 --name "${PACKAGE_NAME}" -- start
    done
fi


# Startup
cd "$GC_PATH"
sudo chown -R {{ project_node_user }}:{{ project_node_user }} .
pm2 save
pm2 startup -u {{ project_node_user }}
sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u {{ project_node_user }} --hp /home/{{ project_node_user }}

{% if project_node_install_nginx %}
# Prepare application for Nginx
cd "$GC_PATH"
if [ -f "genesis/images/nginx.conf" ]; then
    sudo cp genesis/images/nginx.conf /etc/nginx/sites-available/default
fi
{% endif %}

# Copy bootstrap scripts
sudo cp "$GC_PATH/genesis/images/bootstrap.sh" /var/lib/genesis/bootstrap/scripts/
sudo chmod +x /var/lib/genesis/bootstrap/scripts/bootstrap.sh


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
