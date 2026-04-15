
# idps_add

Add a new idp to the Genesis installation

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: genesis iam idps add [OPTIONS]                                                                                                                                                                                                                                                                     
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the idp

* `name`:
    * Type: text
    * Default: `test_idp`
    * Usage: `-n
--name`

  Name of the idp

* `description`:
    * Type: text
    * Default: ``
    * Usage: `-D
--description`

  Description of the idp

* `project_id` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-p
--project-id`

  Uuid of the project

* `iam_client` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-i
--iam-client`

  Uuid of iam_client

* `scope`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--scope`

  scope

* `nonce_required`:
    * Type: boolean
    * Default: `true`
    * Usage: `--nonce_required`

* `callback` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--callback`

  JSON string for callbacks

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: genesis iam idps add [OPTIONS]                                                                                                                                                                                                                                                                     
                                                                                                                                                                                                                                                                                                           
 Add a new idp to the Genesis installation                                                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    --uuid            -u  UUID  UUID of the idp                                                                                                                                                                                                                                                          │
│    --name            -n  TEXT  Name of the idp                                                                                                                                                                                                                                                          │
│    --description     -D  TEXT  Description of the idp                                                                                                                                                                                                                                                   │
│ *  --project-id      -p  UUID  Uuid of the project [required]                                                                                                                                                                                                                                           │
│ *  --iam-client      -i  UUID  Uuid of iam_client [required]                                                                                                                                                                                                                                            │
│    --scope               TEXT  scope                                                                                                                                                                                                                                                                    │
│    --nonce_required                                                                                                                                                                                                                                                                                     │
│ *  --callback            TEXT  JSON string for callbacks [required]                                                                                                                                                                                                                                     │
│    --help                      Show this message and exit.                                                                                                                                                                                                                                              │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
