
# services_update

Update service

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: genesis services update [OPTIONS] UUID                                                                                                                                                                                                                                                             
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `uuid`

* `project_id`:
    * Type: uuid
    * Default: `none`
    * Usage: `-p
--project-id`

  Name of the project in which to deploy the service

* `name`:
    * Type: text
    * Default: `none`
    * Usage: `-n
--name`

  Name of the service

* `description`:
    * Type: text
    * Default: `none`
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
                                                                                                                                                                                                                                                                                                           
 Usage: genesis services update [OPTIONS] UUID                                                                                                                                                                                                                                                             
                                                                                                                                                                                                                                                                                                           
 Update service                                                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --project-id   -p  UUID  Name of the project in which to deploy the service                                                                                                                                                                                                                             │
│ --name         -n  TEXT  Name of the service                                                                                                                                                                                                                                                            │
│ --description  -D  TEXT  Description of the service                                                                                                                                                                                                                                                     │
│ --help                   Show this message and exit.                                                                                                                                                                                                                                                    │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
