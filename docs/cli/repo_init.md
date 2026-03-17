
# repo_init

Initialize the repository

## Usage

```console
Usage: genesis repo init [OPTIONS] [PROJECT_DIR]
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

* `force`:
    * Type: boolean
    * Default: `false`
    * Usage: `-f
--force`

  Force init even if the repo already exists

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
Usage: genesis repo init [OPTIONS] [PROJECT_DIR]

  Initialize the repository

Options:
  -c, --genesis-cfg-file TEXT  Name of the project configuration file
  -t, --target TEXT            Target repository to push to
  -f, --force                  Force init even if the repo already exists
  --help                       Show this message and exit.
```
