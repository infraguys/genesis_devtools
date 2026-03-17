
# list

List the repository

## Usage

```console
Usage: genesis repo list [OPTIONS] [PROJECT_DIR]
```

## Options

*   `genesis_cfg_file`:
    *   Type: STRING
    *   Default: `genesis.yaml`
    *   Usage: `-c
--genesis-cfg-file`

  Name of the project configuration file

*   `target`:
    *   Type: STRING
    *   Default: `none`
    *   Usage: `-t
--target`

  Target repository to push to

*   `element`:
    *   Type: STRING
    *   Default: `none`
    *   Usage: `-e
--element`

  Element to list

*   `project_dir`:
    * Type: <click.types.Path object at 0x7cb005f3aae0>
    * Default: `.`
    * Usage: `project_dir`

*   `help`:
    * Type: BOOL
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
Usage: genesis repo list [OPTIONS] [PROJECT_DIR]

  List the repository

Options:
  -c, --genesis-cfg-file TEXT  Name of the project configuration file
  -t, --target TEXT            Target repository to push to
  -e, --element TEXT           Element to list
  --help                       Show this message and exit.
```
