
# services_add

Add a new service to the Genesis installation

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: genesis e services add [OPTIONS]                                                                                                                                                                                                                                                                   
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the service

* `project_id` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-p
--project-id`

  Name of the project in which to deploy the service

* `name`:
    * Type: text
    * Default: `test_service`
    * Usage: `-n
--name`

  Name of the service

* `description`:
    * Type: text
    * Default: ``
    * Usage: `-D
--description`

  Description of the service

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: genesis e services add [OPTIONS]                                                                                                                                                                                                                                                                   
                                                                                                                                                                                                                                                                                                           
 Add a new service to the Genesis installation                                                                                                                                                                                                                                                             
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    --uuid         -u  UUID  UUID of the service                                                                                                                                                                                                                                                         │
│ *  --project-id   -p  UUID  Name of the project in which to deploy the service [required]                                                                                                                                                                                                               │
│    --name         -n  TEXT  Name of the service                                                                                                                                                                                                                                                         │
│    --description  -D  TEXT  Description of the service                                                                                                                                                                                                                                                  │
│    --help                   Show this message and exit.                                                                                                                                                                                                                                                 │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
