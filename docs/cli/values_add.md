
# values_add

Add a new value to the Genesis installation

## Usage

```console
Usage: genesis values add [OPTIONS]
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the value

* `project_id` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-p
--project-id`

  Name of the project in which to deploy the value

* `name`:
    * Type: text
    * Default: `test_value`
    * Usage: `-n
--name`

  Name of the value

* `description`:
    * Type: text
    * Default: ``
    * Usage: `-D
--description`

  Description of the value

* `var`:
    * Type: text
    * Default: `none`
    * Usage: `--var`

  UUID of a variable the value belongs to

* `value`:
    * Type: text
    * Default: ``
    * Usage: `-V
--value`

  value

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
Usage: genesis values add [OPTIONS]

  Add a new value to the Genesis installation

Options:
  -u, --uuid UUID         UUID of the value
  -p, --project-id UUID   Name of the project in which to deploy the value
                          [required]
  -n, --name TEXT         Name of the value
  -D, --description TEXT  Description of the value
  --var TEXT              UUID of a variable the value belongs to
  -V, --value TEXT        value
  --help                  Show this message and exit.
```
