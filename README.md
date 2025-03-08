![Tests workflow](https://github.com/infraguys/genesis_devtools/actions/workflows/tests.yml/badge.svg)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/genesis-devtools)


# Genesis Dev Tools

The tools to manager life cycle of genesis projects

# Requirements

Before you can install and use genesis tools you need to install several requirements:
- [packer](https://www.packer.io/)
- [libvirt](https://libvirt.org/)
- [qemu](https://www.qemu.org/)

## Ubuntu

Install packages
```sh
sudo apt update
sudo apt install qemu-kvm libvirt-daemon-system libvirt-dev mkisofs
```

Add user to group
```sh
sudo adduser $USER libvirt
sudo adduser $USER kvm
```

Install packer like described in [this article](https://yandex.cloud/ru/docs/tutorials/infrastructure-management/packer-quickstart#from-y-mirror)

# Install

To install the `genesis-devtools` package, follow these steps:

1. Clone the repository:
    ```sh
    git clone https://github.com/infraguys/genesis_devtools.git
    ```

2. Navigate to the project directory:
    ```sh
    cd genesis_devtools
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Install the package using pip:
    ```sh
    pip install .
    ```

# Quickstart

## Build
Firstly you need to build the genesis project. Navigate to your project directory and run the genesis build command, specifying the path to your project root directory as an argument. This will build the project according to the configuration defined in the `genesis.yaml` file.

Here are some examples of how to use the build command:
```sh
genesis build /path/to/my/project
```

There are some useful options for the genesis build command.
- Build a Genesis project with a custom developer key path:
```sh
genesis build -i /path/to/my/developer/key /path/to/my/project
```

- Build a Genesis project with the --force option to rebuild if the output already exists:
```sh
genesis build -f /path/to/my/project
```

Look at the `genesis build --help` command for more options.

## Bootstrap

To bootstrap a Genesis installation locally, use the genesis bootstrap command. This command creates and boots a virtual machine with the specified Genesis image.

One of the key options for the bootstrap command is `--launch-mode`, which allows you to specify the launch mode for the application. There are three available modes:

- `element`: This is the default mode, which launches the installation as a single element.
- `core`: This mode launches the installation as a core.
- `custom`: This mode allows you to launch the installation with a custom configuration.

Here are some examples of how to use the `--launch-mode` option:
```sh+
genesis bootstrap -i output/genesis-element.raw
```

Launch the installation in `core` mode:
```sh
genesis bootstrap -i output/genesis-core.raw -m core
```

# Usage

The package provides a command line interface for building genesis projects, managing genesis installations and cover many other useful aspects. To use the command line interface, run the `genesis` command from the command line. For full documentation about CLI commands, run `genesis --help`.

For every genesis project the directory `genesis` should exist in the project root. The project configuration file should be named `genesis.yaml` in this directory. For example my project structure looks like this:

```sh
.
├── my_project
│   └── main.py
├── project_settings.json
├── requirements.txt
├── setup.cfg
├── setup.py
└── README.md
```

The project should be extended as follows:

```sh
.
├── my_project
│   └── main.py
├── genesis
│   └── genesis.yaml
├── README.md
├── project_settings.json
├── requirements.txt
├── setup.cfg
├── setup.py
└── README.md
```

## Genesis configuration file

The `genesis.yaml` file contains the configuration for the genesis project. It should be placed in the `genesis` directory. It consists of several sections such as build, deploy, etc.

Example of the `genesis.yaml` file:

```yaml
# Build section. It describes the build process of the project.
build:
  # Dependencies of the project
  # This section is used to specify build dependencies
  # for the project
  deps:
      # Target path in the image
    - dst: /opt/genesis_core
      # Local path of the build machine
      path:
        src: ../../genesis_core
  
  # This section describes elements of the project.
  # Images, artifacts and manifests for every element. 
  elements:
      # List of images in the element
    - images:
      - name: genesis-core
        format: raw
        
        # OS profile for the image
        profile: ubuntu_24

        # Provisioning script
        script: images/install.sh

        # Override image build parameters, for instance Packer parameters
        override:
          disk_size: "10G"

      manifest: manifests/genesis-core.yaml
      
      # List of artifacts in the element
      artifacts:
        - configs/my-cofig.yaml
        - templates/my-template.yaml
```

## Build project

The `genesis build` command builds the project. The build process is described in the `build` section of the `genesis.yaml` file. The mandatory argument is path to the project root directory.

Build a Genesis project.
```sh
genesis build my_project
```

This will build the Genesis project in the `my_project` directory using the default configuration file will be located in `my_project/genesis/genesis.yaml`.

After build the project output artifacts will be stored in the `output` directory.
For detailed information about the `genesis build` command run `genesis build --help`.

## Manager Genesis installation locally

To bootstrap genesis installation locally, run the `genesis bootstrap` command. The mandatory argument is path to the genesis image. For instance,

```sh
genesis bootstrap output/genesis-core.raw
```

This command will create and boot a virtual machine with the specified genesis image `output/genesis-core.raw`. The default name of the installation is `genesis-core`. For detailed information about the `genesis bootstrap` command run `genesis bootstrap --help`.

To connect to the genesis installation, run the `genesis ssh` command. For instance,
```sh
genesis ssh
```

To list genesis installations, run the `genesis ps` command. For instance,

```sh
genesis ps
```

To delete genesis installation, run the `genesis delete` command. For instance,

```sh
genesis delete genesis-core
```

## Versions

Semver is used for project versioning. There are three types of versions:
- stable version - format `X.Y.Z`
- release candidate version - format `X.Y.Z-rc+YYYYMMDDHHMMSS.commit_hash[:8]`
- development version - format `X.Y.Z-dev+YYYYMMDDHHMMSS.commit_hash[:8]`

Stable version looks like `1.0.0`, only three digits. Release candidate version looks like `0.0.1-rc+20250224092842.e11604e9`. Development version looks like `0.0.1-dev+20250223180245.fb195339`.

To get project version, run the `genesis get-version` with path to the project root directory as an argument to the command. For instance,

```sh
genesis get-version /path/to/my_project
```
