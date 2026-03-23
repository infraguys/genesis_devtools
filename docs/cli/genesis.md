
# genesis

Provides all the necessary tools for work with Genesis Platform

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

* `access_token`:
    * Type: text
    * Default: `none`
    * Usage: `-a
--access_token`

  access token for the client user

* `refresh_token`:
    * Type: text
    * Default: `none`
    * Usage: `-r
--refresh_token`

  refresh token for the client user

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

  Provides all the necessary tools for work with Genesis Platform

Options:
  --config FILE             Path to YAML config file  [default:
                            /home/user/.genesis/genesisctl.yaml]
  -e, --endpoint TEXT       Genesis API endpoint  [default:
                            http://localhost:11010]
  -u, --user TEXT           Client user name
  -p, --password TEXT       Password for the client user
  -a, --access_token TEXT   access token for the client user
  -r, --refresh_token TEXT  refresh token for the client user
  -P, --project-id UUID     Project ID for the client user
  --help                    Show this message and exit.

Commands:
  auth                 Authenticate and manage IAM token
  backup               Backup the current installation
  backup-decrypt       Decrypt a backup file
  bootstrap            Bootstrap genesis locally
  build                Build a Genesis element.
  clients              Manager clients in the Genesis installation
  configs              Manager configs in the Genesis installation
  cowsay               Display a cow message
  delete               Delete the genesis stand/element
  elements             Manage elements in the Genesis installation
  get-version          Return the version of the project
  hello                Display a genesis message
  hypervisors          Manager hypervisors in the Genesis installation
  idps                 Manager idps in the Genesis installation
  latest               Check for the latest version on GitHub
  manifests            Manage manifests in the Genesis installation
  nodes                Manager nodes in the Genesis installation
  organizations        Manager organizations in the Genesis installation
  permission_bindings  Manager permission_bindings in the Genesis installation
  permissions          Manager permissions in the Genesis installation
  profiles             Manage profiles in the Genesis installation
  projects             Manager projects in the Genesis installation
  ps                   List of running genesis installation
  push                 Push the element to the repository
  repo                 Manager Genesis repository
  resources            Manage resources in the Genesis installation
  role_bindings        Manager role_bindings in the Genesis installation
  roles                Manager roles in the Genesis installation
  services             Manage services in the Genesis installation
  ssh                  Connect to genesis stand/element
  users                Manager users in the Genesis installation
  values               Manage values in the Genesis installation
  vars                 Manage variables in the Genesis installation
  version              Prints the genesis_devtools version
```
