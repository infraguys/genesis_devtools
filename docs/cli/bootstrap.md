
# bootstrap

Bootstrap genesis locally

## Usage

```console
Usage: genesis bootstrap [OPTIONS]
```

## Options

*   `inventory`:
    *   Type: STRING
    *   Default: `sentinel.unset`
    *   Usage: `-i
--inventory`

  Path to the genesis inventory file or directory with inventory.json

*   `profile`:
    * Type: Choice(['develop', 'small', 'medium', 'large', 'legacy'])
    * Default: `small`
    * Usage: `--profile`

  Profile for the installation.

*   `name`:
    * Type: STRING
    * Default: `genesis-core`
    * Usage: `--name`

  Name of the installation

*   `launch_mode`:
    *   Type: Choice(['core', 'element', 'custom'])
    *   Default: `element`
    *   Usage: `-m
--launch-mode`

  Launch mode for start element, core or custom configuration

*   `stand_spec`:
    *   Type: <click.types.Path object at 0x7cb005f3a2d0>
    *   Default: `none`
    *   Usage: `-s
--stand-spec`

  Additional stand specification for core mode.

*   `cidr`:
    * Type: <click.types.FuncParamType object at 0x7cb005f3a4b0>
    * Default: `10.20.0.0/22`
    * Usage: `--cidr`

  The genesis network CIDR

*   `core_ip`:
    * Type: <click.types.FuncParamType object at 0x7cb005f3a5a0>
    * Default: `none`
    * Usage: `--core-ip`

  The IP address for the core VM. If `None` is provided, second IP address from the genesis network will be used.

*   `bridge`:
    * Type: STRING
    * Default: `none`
    * Usage: `--bridge`

  Name of the linux bridge for the genesis network, it will be created if not set.

*   `boot_cidr`:
    * Type: <click.types.FuncParamType object at 0x7cb005f3a660>
    * Default: `10.30.0.0/24`
    * Usage: `--boot-cidr`

  The bootstrap network CIDR

*   `boot_bridge`:
    * Type: STRING
    * Default: `none`
    * Usage: `--boot-bridge`

  Name of the linux bridge for the bootstrap network, it will be created if not set.

*   `force`:
    *   Type: BOOL
    *   Default: `false`
    *   Usage: `-f
--force`

  Rebuild if the output already exists

*   `no_wait`:
    * Type: BOOL
    * Default: `false`
    * Usage: `--no-wait`

  Cancel waiting for the installation to start

*   `repository`:
    *   Type: STRING
    *   Default: `https://repository.genesis-core.tech/`
    *   Usage: `-r
--repository`

  Default element repository

*   `admin_password`:
    * Type: STRING
    * Default: `none`
    * Usage: `--admin-password`

  A password for the admin user in. If not provided, the password will be generated.

*   `save_admin_password_file`:
    * Type: STRING
    * Default: `none`
    * Usage: `--save-admin-password-file`

  If the option is specified the admin password is saved to the file. Otherwise it's printed to the console.

*   `hyper_connection_uri`:
    * Type: STRING
    * Default: ``
    * Usage: `--hyper-connection-uri`

  Connection URI for the hypervisor, e.g. 'qemu+tcp://10.0.0.1/system' or 'qemu+ssh://user@10.0.0.1/system'. If not set, the first address of the network(--cidr option) will be used.

*   `hyper_storage_pool`:
    * Type: STRING
    * Default: `default`
    * Usage: `--hyper-storage-pool`

  Storage pool for the hypervisor.

*   `hyper_machine_prefix`:
    * Type: STRING
    * Default: `vm-`
    * Usage: `--hyper-machine-prefix`

  A prefix for new VMs.

*   `hyper_iface_rom_file`:
    * Type: STRING
    * Default: `/usr/share/qemu/1af41041.rom`
    * Usage: `--hyper-iface-rom-file`

  A path to the custom ROM file of a network interface.

*   `no_start`:
    * Type: BOOL
    * Default: `false`
    * Usage: `--no-start`

  Do not start the stand after creation

*   `help`:
    * Type: BOOL
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
Usage: genesis bootstrap [OPTIONS]

  Bootstrap genesis locally

Options:
  -i, --inventory TEXT            Path to the genesis inventory file or
                                  directory with inventory.json
  --profile [develop|small|medium|large|legacy]
                                  Profile for the installation.  [default:
                                  small]
  --name TEXT                     Name of the installation
  -m, --launch-mode [core|element|custom]
                                  Launch mode for start element, core or custom
                                  configuration  [default: element]
  -s, --stand-spec PATH           Additional stand specification for core mode.
  --cidr IPV4NETWORK              The genesis network CIDR  [default:
                                  10.20.0.0/22]
  --core-ip IPV4ADDRESS           The IP address for the core VM. If `None` is
                                  provided, second IP address from the genesis
                                  network will be used.
  --bridge TEXT                   Name of the linux bridge for the genesis
                                  network, it will be created if not set.
  --boot-cidr IPV4NETWORK         The bootstrap network CIDR  [default:
                                  10.30.0.0/24]
  --boot-bridge TEXT              Name of the linux bridge for the bootstrap
                                  network, it will be created if not set.
  -f, --force                     Rebuild if the output already exists
  --no-wait                       Cancel waiting for the installation to start
  -r, --repository TEXT           Default element repository  [default:
                                  https://repository.genesis-core.tech/]
  --admin-password TEXT           A password for the admin user in. If not
                                  provided, the password will be generated.
  --save-admin-password-file TEXT
                                  If the option is specified the admin password
                                  is saved to the file. Otherwise it's printed
                                  to the console.
  --hyper-connection-uri TEXT     Connection URI for the hypervisor, e.g.
                                  'qemu+tcp://10.0.0.1/system' or
                                  'qemu+ssh://user@10.0.0.1/system'. If not set,
                                  the first address of the network(--cidr
                                  option) will be used.
  --hyper-storage-pool TEXT       Storage pool for the hypervisor.  [default:
                                  default]
  --hyper-machine-prefix TEXT     A prefix for new VMs.  [default: vm-]
  --hyper-iface-rom-file TEXT     A path to the custom ROM file of a network
                                  interface.  [default:
                                  /usr/share/qemu/1af41041.rom]
  --no-start                      Do not start the stand after creation
  --help                          Show this message and exit.
```
