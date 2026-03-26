
# vars_add

Add a new variable to the Genesis installation

## Usage

```console
                                                                                
 Usage: genesis vars add [OPTIONS]                                              
                                                                                
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the variable

* `project_id` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-p
--project-id`

  Name of the project in which to deploy the variable

* `name`:
    * Type: text
    * Default: `example_variable`
    * Usage: `-n
--name`

  Name of the variable

* `description`:
    * Type: text
    * Default: ``
    * Usage: `-D
--description`

  Description of the variable

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                
 Usage: genesis vars add [OPTIONS]                                              
                                                                                
 Add a new variable to the Genesis installation                                 
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│    --uuid         -u  UUID  UUID of the variable                             │
│ *  --project-id   -p  UUID  Name of the project in which to deploy the       │
│                             variable [required]                              │
│    --name         -n  TEXT  Name of the variable                             │
│    --description  -D  TEXT  Description of the variable                      │
│    --help                   Show this message and exit.                      │
╰──────────────────────────────────────────────────────────────────────────────╯
```
