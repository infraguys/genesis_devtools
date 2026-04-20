
# clients_add

Add a new client to the Genesis installation

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: genesis iam clients add [OPTIONS]                                                                                                                                                                                                                                                                  
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the client

* `name`:
    * Type: text
    * Default: `test_client`
    * Usage: `-n
--name`

  Name of the client

* `description`:
    * Type: text
    * Default: ``
    * Usage: `-D
--description`

  Description of the client

* `project_id` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-p
--project-id`

  Name of the project in which to deploy the client

* `client_id` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--client-id`

  client_id

* `secret` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--secret`

  secret

* `signature_algorithm`:
    * Type: choice
    * Default: `hs256`
    * Usage: `-s
--signature-algorithm`

  signature-algorithm

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: genesis iam clients add [OPTIONS]                                                                                                                                                                                                                                                                  
                                                                                                                                                                                                                                                                                                           
 Add a new client to the Genesis installation                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    --uuid                 -u  UUID           UUID of the client                                                                                                                                                                                                                                         │
│    --name                 -n  TEXT           Name of the client                                                                                                                                                                                                                                         │
│    --description          -D  TEXT           Description of the client                                                                                                                                                                                                                                  │
│ *  --project-id           -p  UUID           Name of the project in which to deploy the client [required]                                                                                                                                                                                               │
│ *  --client-id                TEXT           client_id [required]                                                                                                                                                                                                                                       │
│ *  --secret                   TEXT           secret [required]                                                                                                                                                                                                                                          │
│    --signature-algorithm  -s  [HS256|RS256]  signature-algorithm [default: HS256]                                                                                                                                                                                                                       │
│    --help                                    Show this message and exit.                                                                                                                                                                                                                                │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
