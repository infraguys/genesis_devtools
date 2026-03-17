
# init

Initialize the repository

## Usage

```console
Usage: genesis repo init [OPTIONS] [PROJECT_DIR]
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

*   `force`:
    *   Type: BOOL
    *   Default: `false`
    *   Usage: `-f
--force`

  Force init even if the repo already exists

*   `project_dir`:
    * Type: <click.types.Path object at 0x7cb005f3a540>
    * Default: `.`
    * Usage: `project_dir`

*   `help`:
    * Type: BOOL
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
Usage: genesis repo init [OPTIONS] [PROJECT_DIR]

  Initialize the repository

Options:
  -c, --genesis-cfg-file TEXT  Name of the project configuration file
  -t, --target TEXT            Target repository to push to
  -f, --force                  Force init even if the repo already exists
  --help                       Show this message and exit.
```
