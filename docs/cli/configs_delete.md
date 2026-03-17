
# configs_delete

Delete configuration from environment variables

## Usage

```console
Usage: genesis configs delete [OPTIONS]
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  Config UUID

* `node`:
    * Type: uuid
    * Default: `none`
    * Usage: `-n
--node`

  Delete all configs for the node

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
Usage: genesis configs delete [OPTIONS]

  Delete configuration from environment variables

Options:
  -u, --uuid UUID  Config UUID
  -n, --node UUID  Delete all configs for the node
  --help           Show this message and exit.
```
