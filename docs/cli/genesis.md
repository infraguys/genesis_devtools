
# genesis

Genesis DevTools

## Usage

```console
Usage: genesis [OPTIONS] COMMAND [ARGS]...
```

## Options

* `config`:
    * Type: file
    * Default: `/home/user/.genesis/genesisctl.yaml`
    * Usage: `--config`

  Path to YAML config file

* `endpoint`:
    * Type: text
    * Default: `http://localhost:11010`
    * Usage: `-e
--endpoint`

  Genesis API endpoint

* `user`:
    * Type: text
    * Default: `none`
    * Usage: `-u
--user`

  Client user name

* `password`:
    * Type: text
    * Default: `none`
    * Usage: `-p
--password`

  Password for the client user

* `project_id`:
    * Type: uuid
    * Default: `none`
    * Usage: `-P
--project-id`

  Project ID for the client user

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
Usage: genesis [OPTIONS] COMMAND [ARGS]...

  Genesis DevTools

Options:
  --config FILE          Path to YAML config file  [default:
                         /home/user/.genesis/genesisctl.yaml]
  -e, --endpoint TEXT    Genesis API endpoint  [default: http://localhost:11010]
  -u, --user TEXT        Client user name
  -p, --password TEXT    Password for the client user
  -P, --project-id UUID  Project ID for the client user
  --help                 Show this message and exit.

Commands:
  auth            Authenticate and manage IAM token
  backup          Backup the current installation
  backup-decrypt  Decrypt a backup file
  bootstrap       Bootstrap genesis locally
  build           Build a Genesis element.
  configs         Manager configs in the Genesis installation
  delete          Delete the genesis stand/element
  elements        Manage elements in the Genesis installation
  get-version     Return the version of the project
  nodes           Manager nodes in the Genesis installation
  ps              List of running genesis installation
  push            Push the element to the repository
  repo            Manager Genesis repository
  ssh             Connect to genesis stand/element
```
