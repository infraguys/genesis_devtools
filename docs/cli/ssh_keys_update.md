
# ssh_keys_update

Update ssh_key

## Usage

```console
Usage: genesis ssh_keys update [OPTIONS] UUID
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

  Name of the project in which to deploy the ssh_key

* `name`:
    * Type: text
    * Default: `none`
    * Usage: `-n
--name`

  Name of the ssh_key

* `description`:
    * Type: text
    * Default: `none`
    * Usage: `-D
--description`

  Description of the ssh_key

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
Usage: genesis ssh_keys update [OPTIONS] UUID

  Update ssh_key

Options:
  -p, --project-id UUID   Name of the project in which to deploy the ssh_key
  -n, --name TEXT         Name of the ssh_key
  -D, --description TEXT  Description of the ssh_key
  --help                  Show this message and exit.
```
