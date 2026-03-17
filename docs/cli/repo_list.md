
# repo_list

List the repository

## Usage

```console
Usage: genesis repo list [OPTIONS] [PROJECT_DIR]
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

* `element`:
    * Type: text
    * Default: `none`
    * Usage: `-e
--element`

  Element to list

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
Usage: genesis repo list [OPTIONS] [PROJECT_DIR]

  List the repository

Options:
  -c, --genesis-cfg-file TEXT  Name of the project configuration file
  -t, --target TEXT            Target repository to push to
  -e, --element TEXT           Element to list
  --help                       Show this message and exit.
```
