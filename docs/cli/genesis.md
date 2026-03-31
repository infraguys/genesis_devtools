
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
    * Usage: `--refresh_token`

  refresh token for the client user

* `realm`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-r
--realm`

  Name of the realm

* `context`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-c
--context`

  Name of the context

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
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --config             FILE  Path to YAML config file [default: /home/user/.genesis/genesisctl.yaml]                                                                                                                                                                                                      │
│ --endpoint       -e  TEXT  Genesis API endpoint [default: http://localhost:11010]                                                                                                                                                                                                                       │
│ --user           -u  TEXT  Client user name                                                                                                                                                                                                                                                             │
│ --password       -p  TEXT  Password for the client user                                                                                                                                                                                                                                                 │
│ --access_token   -a  TEXT  access token for the client user                                                                                                                                                                                                                                             │
│ --refresh_token      TEXT  refresh token for the client user                                                                                                                                                                                                                                            │
│ --realm          -r  TEXT  Name of the realm                                                                                                                                                                                                                                                            │
│ --context        -c  TEXT  Name of the context                                                                                                                                                                                                                                                          │
│ --project-id     -P  UUID  Project ID for the client user                                                                                                                                                                                                                                               │
│ --help                     Show this message and exit.                                                                                                                                                                                                                                                  │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ auth                Authenticate and manage IAM token                                                                                                                                                                                                                                                   │
│ autocomplete_help   Display a autocomplete help                                                                                                                                                                                                                                                         │
│ backup              Backup the current installation                                                                                                                                                                                                                                                     │
│ backup-decrypt      Decrypt a backup file                                                                                                                                                                                                                                                               │
│ bootstrap           Bootstrap genesis locally                                                                                                                                                                                                                                                           │
│ build               Build a Genesis element. The command build all images, manifests and other artifacts required for the element. The manifest in the project may be a raw YAML file or a template using Jinja2 templates. For Jinja2 templates, the following variables are available by default:     │
│ compute             Compute group in the Genesis installation                                                                                                                                                                                                                                           │
│ configs             Manager configs in the Genesis installation                                                                                                                                                                                                                                         │
│ cowsay              Display a cow message                                                                                                                                                                                                                                                               │
│ delete              Delete the genesis stand/element                                                                                                                                                                                                                                                    │
│ elements            Manage elements in the Genesis installation                                                                                                                                                                                                                                         │
│ get-version         Return the version of the project                                                                                                                                                                                                                                                   │
│ hello               Display a genesis message                                                                                                                                                                                                                                                           │
│ iam                 iam group in the Genesis installation                                                                                                                                                                                                                                               │
│ init                Platformize the project                                                                                                                                                                                                                                                             │
│ latest              Check for the latest version on GitHub                                                                                                                                                                                                                                              │
│ manifests           Manage manifests in the Genesis installation                                                                                                                                                                                                                                        │
│ ps                  List of running genesis installation                                                                                                                                                                                                                                                │
│ push                Push the element to the repository                                                                                                                                                                                                                                                  │
│ repo                Manager Genesis repository                                                                                                                                                                                                                                                          │
│ resources           Manage resources in the Genesis installation                                                                                                                                                                                                                                        │
│ secret              Secret group in the Genesis installation                                                                                                                                                                                                                                            │
│ services            Manage services in the Genesis installation                                                                                                                                                                                                                                         │
│ settings            Modify genesis settings files                                                                                                                                                                                                                                                       │
│ ssh                 Connect to genesis stand/element                                                                                                                                                                                                                                                    │
│ version             Prints the genesis_devtools version                                                                                                                                                                                                                                                 │
│ vs                  vs group in the Genesis installation                                                                                                                                                                                                                                                │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
