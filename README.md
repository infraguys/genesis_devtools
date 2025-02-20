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
sudo apt install qemu-kvm libvirt-daemon-system mkisofs
```

Add user to group
```sh
sudo adduser $USER libvirt
```

Install packer like described in [this article](https://yandex.cloud/ru/docs/tutorials/infrastructure-management/packer-quickstart#from-y-mirror)
```sh

```

# Install

To install the `genesis-dev-tools` package, follow these steps:

1. Clone the repository:
    ```sh
    git clone https://github.com/infraguys/genesis_dev_tools.git
    ```

2. Navigate to the project directory:
    ```sh
    cd genesis_dev_tools
    ```

3. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Install the package using pip:
    ```sh
    pip install .
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
