
# genesis_push

Push the element to the repository

## Usage

```console
Usage: genesis push [OPTIONS] [PROJECT_DIR]
```

## Options

* `genesis_cfg_file`:
    * Type: text
    * Default: `genesis.yaml`
    * Usage: `-c
--genesis-cfg-file`

  Name of the project configuration file

* `target`:
    * Type: text
    * Default: `none`
    * Usage: `-t
--target`

  Target repository to push to

* `element_dir`:
    * Type: path
    * Default: `output`
    * Usage: `-e
--element-dir`

  Directory where element artifacts are stored

* `force`:
    * Type: boolean
    * Default: `false`
    * Usage: `-f
--force`

  Force push even if the element already exists

* `project_dir`:
    * Type: path
    * Default: `.`
    * Usage: `project_dir`

* `help`:
    * Type: boolean
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
