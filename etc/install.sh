#!/bin/sh
# This script installs Genesis DevTools on Linux and macOS.
# It detects the current operating system architecture and installs the appropriate version of Genesis DevTools.

# Wrap script in main function so that a truncated partial download doesn't end
# up executing half a script.
main() {

set -eu

red="$( (/usr/bin/tput bold || :; /usr/bin/tput setaf 1 || :) 2>&-)"
plain="$( (/usr/bin/tput sgr0 || :) 2>&-)"

status() { echo ">>> $*" >&2; }
error() { echo "${red}ERROR:${plain} $*"; exit 1; }
warning() { echo "${red}WARNING:${plain} $*"; }

TEMP_DIR=$(mktemp -d)
cleanup() { rm -rf $TEMP_DIR; }
trap cleanup EXIT

available() { command -v $1 >/dev/null; }
require() {
    local MISSING=''
    for TOOL in $*; do
        if ! available $TOOL; then
            MISSING="$MISSING $TOOL"
        fi
    done

    echo $MISSING
}

OS="$(uname -s)"
ARCH=$(uname -m)
case "$ARCH" in
    x86_64) ARCH="amd64" ;;
    # aarch64|arm64) ARCH="arm64" ;;
    *) error "Unsupported architecture: $ARCH" ;;
esac

###########################################
# macOS
###########################################

if [ "$OS" = "Darwin" ]; then
    NEEDS=$(require curl)
    if [ -n "$NEEDS" ]; then
        status "ERROR: The following tools are required but missing:"
        for NEED in $NEEDS; do
            echo "  - $NEED"
        done
        exit 1
    fi

    DOWNLOAD_URL="https://repository.genesis-core.tech/genesis-devtools/latest/genesis-macos"

    if [ -d "/Applications/genesis.app" ]; then
        status "Removing existing genesis installation..."
        rm -rf "/Applications/genesis.app"
    fi

    status "Downloading genesis for macOS..."
    curl --fail --show-error --location --progress-bar \
        -o "$TEMP_DIR/genesis-darwin.zip" "$DOWNLOAD_URL"

    status "Installing genesis to /Applications..."
    unzip -q "$TEMP_DIR/genesis-darwin.zip" -d "$TEMP_DIR"
    mv "$TEMP_DIR/genesis.app" "/Applications/"

    if [ ! -L "/usr/local/bin/genesis" ] || [ "$(readlink "/usr/local/bin/genesis")" != "/Applications/genesis.app/Contents/Resources/genesis" ]; then
        status "Adding 'genesis' command to PATH (may require password)..."
        mkdir -p "/usr/local/bin" 2>/dev/null || sudo mkdir -p "/usr/local/bin"
        ln -sf "/Applications/genesis.app/Contents/Resources/genesis" "/usr/local/bin/genesis" 2>/dev/null || \
            sudo ln -sf "/Applications/genesis.app/Contents/Resources/genesis" "/usr/local/bin/genesis"
    fi

    if [ -z "${genesis_NO_START:-}" ]; then
        status "Starting genesis..."
        open -a genesis --args hidden
    fi

    status "Install complete. You can now run 'genesis'."
    exit 0
fi

###########################################
# Linux
###########################################

[ "$OS" = "Linux" ] || error 'This script is intended to run on Linux and macOS only.'

IS_WSL2=false

KERN=$(uname -r)
case "$KERN" in
    *icrosoft*WSL2 | *icrosoft*wsl2) IS_WSL2=true;;
    *icrosoft) error "Microsoft WSL1 is not currently supported. Please use WSL2 with 'wsl --set-version <distro> 2'" ;;
    *) ;;
esac

SUDO=
if [ "$(id -u)" -ne 0 ]; then
    error "This script requires superuser permissions. Please re-run as root."
    SUDO="sudo"
fi

NEEDS=$(require curl grep xargs)
if [ -n "$NEEDS" ]; then
    status "ERROR: The following tools are required but missing:"
    for NEED in $NEEDS; do
        echo "  - $NEED"
    done
    exit 1
fi

# Function to download and extract with fallback from zst to tgz
download_and_extract() {
    local url_base="$1"
    local dest_dir="$2"
    local filename="$3"

    if curl --fail --silent --head --location "${url_base}/${filename}" >/dev/null 2>&1; then
        status "Downloading ${filename}"
        curl --fail --show-error --location --progress-bar \
            "${url_base}/${filename}" --output "${dest_dir}/genesis"
        return 0
    fi
}

for BINDIR in /usr/local/bin /usr/bin /bin; do
    echo $PATH | grep -q $BINDIR && break || continue
done

status "Installing genesis to $BINDIR"

download_and_extract "https://repository.genesis-core.tech/genesis-devtools/latest" "$BINDIR" "genesis-linux"
$SUDO chmod +x "$BINDIR"/genesis

install_success() {
    status 'Install complete. Run "genesis" from the command line.'
}
trap install_success EXIT

}

main
