
# services_add

Add a new service to the Genesis installation

## Usage

```console
Usage: genesis services add [OPTIONS]
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
Usage: genesis services add [OPTIONS]

  Add a new service to the Genesis installation

Options:
  -u, --uuid UUID         UUID of the service
  -p, --project-id UUID   Name of the project in which to deploy the service
                          [required]
  -n, --name TEXT         Name of the service
  -D, --description TEXT  Description of the service
  --help                  Show this message and exit.
```
