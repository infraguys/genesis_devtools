
# permissions_add

Add a new permission to the Genesis installation

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: genesis iam permissions add [OPTIONS]                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the permission

* `name`:
    * Type: text
    * Default: `test_permission`
    * Usage: `-n
--name`

  Name of the permission

* `description`:
    * Type: text
    * Default: ``
    * Usage: `-D
--description`

  Description of the permission

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: genesis iam permissions add [OPTIONS]                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                           
 Add a new permission to the Genesis installation                                                                                                                                                                                                                                                          
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --uuid         -u  UUID  UUID of the permission                                                                                                                                                                                                                                                         │
│ --name         -n  TEXT  Name of the permission                                                                                                                                                                                                                                                         │
│ --description  -D  TEXT  Description of the permission                                                                                                                                                                                                                                                  │
│ --help                   Show this message and exit.                                                                                                                                                                                                                                                    │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
