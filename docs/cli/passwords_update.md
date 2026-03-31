
# passwords_update

Update password

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: genesis secret passwords update [OPTIONS] UUID                                                                                                                                                                                                                                                     
                                                                                                                                                                                                                                                                                                           
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

  Name of the project in which to deploy the password

* `name`:
    * Type: text
    * Default: `none`
    * Usage: `-n
--name`

  Name of the password

* `description`:
    * Type: text
    * Default: `none`
    * Usage: `-D
--description`

  Description of the password

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: genesis secret passwords update [OPTIONS] UUID                                                                                                                                                                                                                                                     
                                                                                                                                                                                                                                                                                                           
 Update password                                                                                                                                                                                                                                                                                           
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --project-id   -p  UUID  Name of the project in which to deploy the password                                                                                                                                                                                                                            │
│ --name         -n  TEXT  Name of the password                                                                                                                                                                                                                                                           │
│ --description  -D  TEXT  Description of the password                                                                                                                                                                                                                                                    │
│ --help                   Show this message and exit.                                                                                                                                                                                                                                                    │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
