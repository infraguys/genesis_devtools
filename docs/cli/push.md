
# push

Push the element to the repository

## Usage

```console
Usage: genesis push [OPTIONS] [PROJECT_DIR]
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

*   `element_dir`:
    *   Type: <click.types.Path object at 0x7cb005f39ca0>
    *   Default: `output`
    *   Usage: `-e
--element-dir`

  Directory where element artifacts are stored

*   `force`:
    *   Type: BOOL
    *   Default: `false`
    *   Usage: `-f
--force`

  Force push even if the element already exists

*   `project_dir`:
    * Type: <click.types.Path object at 0x7cb005f39f10>
    * Default: `.`
    * Usage: `project_dir`

*   `help`:
    * Type: BOOL
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
Usage: genesis push [OPTIONS] [PROJECT_DIR]

  Push the element to the repository

Options:
  -c, --genesis-cfg-file TEXT  Name of the project configuration file
  -t, --target TEXT            Target repository to push to
  -e, --element-dir PATH       Directory where element artifacts are stored
  -f, --force                  Force push even if the element already exists
  --help                       Show this message and exit.
```
