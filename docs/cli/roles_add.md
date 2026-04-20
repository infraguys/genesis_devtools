
# roles_add

Add a new role to the Genesis installation

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: genesis iam roles add [OPTIONS]                                                                                                                                                                                                                                                                    
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the role

* `project_id`:
    * Type: uuid
    * Default: `none`
    * Usage: `-p
--project-id`

  uuid of the project in which to deploy the role

* `name`:
    * Type: text
    * Default: `test_role`
    * Usage: `-n
--name`

  Name of the role

* `description`:
    * Type: text
    * Default: ``
    * Usage: `-D
--description`

  Description of the role

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: genesis iam roles add [OPTIONS]                                                                                                                                                                                                                                                                    
                                                                                                                                                                                                                                                                                                           
 Add a new role to the Genesis installation                                                                                                                                                                                                                                                                
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --uuid         -u  UUID  UUID of the role                                                                                                                                                                                                                                                               │
│ --project-id   -p  UUID  uuid of the project in which to deploy the role                                                                                                                                                                                                                                │
│ --name         -n  TEXT  Name of the role                                                                                                                                                                                                                                                               │
│ --description  -D  TEXT  Description of the role                                                                                                                                                                                                                                                        │
│ --help                   Show this message and exit.                                                                                                                                                                                                                                                    │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
