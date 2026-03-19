
# values_update

Update value

## Usage

```console
Usage: genesis values update [OPTIONS] UUID
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

  Name of the project in which to deploy the value

* `name`:
    * Type: text
    * Default: `none`
    * Usage: `-n
--name`

  Name of the value

* `description`:
    * Type: text
    * Default: `none`
    * Usage: `-D
--description`

  Description of the value

* `value`:
    * Type: text
    * Default: `none`
    * Usage: `-V
--value`

  value

* `variable`:
    * Type: text
    * Default: `none`
    * Usage: `-v
--variable`

  uuid of the variable

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
Usage: genesis values update [OPTIONS] UUID

  Update value

Options:
  -p, --project-id UUID   Name of the project in which to deploy the value
  -n, --name TEXT         Name of the value
  -D, --description TEXT  Description of the value
  -V, --value TEXT        value
  -v, --variable TEXT     uuid of the variable
  --help                  Show this message and exit.
```
