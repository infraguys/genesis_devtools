
# repo_list

List elements in the repository

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
                                                                                                                                                                                                                                                                                                           
 List elements in the repository                                                                                                                                                                                                                                                                           
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --genesis-cfg-file  -c  TEXT  Name of the project configuration file                                                                                                                                                                                                                                    │
│ --target            -t  TEXT  Target repository to push to                                                                                                                                                                                                                                              │
│ --element           -e  TEXT  Element to list                                                                                                                                                                                                                                                           │
│ --help                        Show this message and exit.                                                                                                                                                                                                                                               │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
