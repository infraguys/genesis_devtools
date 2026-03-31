
# vars_set

Create variable if missing and set its value by creating a new value record

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: genesis vs vars set [OPTIONS] VAR_UUID_OR_NAME VALUE                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                                                           
```

## Options

* `var_uuid_or_name` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `var_uuid_or_name`

* `value` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `value`

* `project_id`:
    * Type: uuid
    * Default: `none`
    * Usage: `-p
--project-id`

  UUID of the project in which to deploy the variable

* `name`:
    * Type: text
    * Default: `none`
    * Usage: `--name`

  Name of the variable to create if it does not exist

* `description`:
    * Type: text
    * Default: `none`
    * Usage: `--description`

  Description of the variable to create if it does not exist

* `rotate`:
    * Type: boolean
    * Default: `false`
    * Usage: `--rotate`

  Delete all existing values for the variable before creating the new one

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: genesis vs vars set [OPTIONS] VAR_UUID_OR_NAME VALUE                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                                                           
 Create variable if missing and set its value by creating a new value record                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --project-id   -p  UUID  UUID of the project in which to deploy the variable                                                                                                                                                                                                                            │
│ --name             TEXT  Name of the variable to create if it does not exist                                                                                                                                                                                                                            │
│ --description      TEXT  Description of the variable to create if it does not exist                                                                                                                                                                                                                     │
│ --rotate                 Delete all existing values for the variable before creating the new one                                                                                                                                                                                                        │
│ --help                   Show this message and exit.                                                                                                                                                                                                                                                    │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
