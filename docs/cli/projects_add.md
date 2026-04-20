
# projects_add

Add a new project to the Genesis installation

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: genesis iam projects add [OPTIONS]                                                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the project

* `name`:
    * Type: text
    * Default: `test-project`
    * Usage: `-n
--name`

  Name of the project

* `description`:
    * Type: text
    * Default: ``
    * Usage: `-D
--description`

  Description of the project

* `organization` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-o
--organization`

  uuid of parent organization

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: genesis iam projects add [OPTIONS]                                                                                                                                                                                                                                                                 
                                                                                                                                                                                                                                                                                                           
 Add a new project to the Genesis installation                                                                                                                                                                                                                                                             
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    --uuid          -u  UUID  UUID of the project                                                                                                                                                                                                                                                        │
│    --name          -n  TEXT  Name of the project                                                                                                                                                                                                                                                        │
│    --description   -D  TEXT  Description of the project                                                                                                                                                                                                                                                 │
│ *  --organization  -o  UUID  uuid of parent organization [required]                                                                                                                                                                                                                                     │
│    --help                    Show this message and exit.                                                                                                                                                                                                                                                │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
