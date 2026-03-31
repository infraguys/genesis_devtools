
# passwords_add

Add a new password to the Genesis installation

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: genesis secret passwords add [OPTIONS]                                                                                                                                                                                                                                                             
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the password

* `project_id` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-p
--project-id`

  Name of the project in which to deploy the password

* `name`:
    * Type: text
    * Default: `test_password`
    * Usage: `-n
--name`

  Name of the password

* `description`:
    * Type: text
    * Default: ``
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
                                                                                                                                                                                                                                                                                                           
 Usage: genesis secret passwords add [OPTIONS]                                                                                                                                                                                                                                                             
                                                                                                                                                                                                                                                                                                           
 Add a new password to the Genesis installation                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    --uuid         -u  UUID  UUID of the password                                                                                                                                                                                                                                                        │
│ *  --project-id   -p  UUID  Name of the project in which to deploy the password [required]                                                                                                                                                                                                              │
│    --name         -n  TEXT  Name of the password                                                                                                                                                                                                                                                        │
│    --description  -D  TEXT  Description of the password                                                                                                                                                                                                                                                 │
│    --help                   Show this message and exit.                                                                                                                                                                                                                                                 │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
