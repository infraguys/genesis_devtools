
# role_bindings_add

Add a new role_binding to the Genesis installation

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: genesis iam role_bindings add [OPTIONS]                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the role_binding

* `project_id` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-p
--project-id`

  Name of the project in which to deploy the role_binding

* `user` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `--user`

  role uuid

* `role` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `--role`

  user uuid

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: genesis iam role_bindings add [OPTIONS]                                                                                                                                                                                                                                                            
                                                                                                                                                                                                                                                                                                           
 Add a new role_binding to the Genesis installation                                                                                                                                                                                                                                                        
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    --uuid        -u  UUID  UUID of the role_binding                                                                                                                                                                                                                                                     │
│ *  --project-id  -p  UUID  Name of the project in which to deploy the role_binding [required]                                                                                                                                                                                                           │
│ *  --user            UUID  role uuid [required]                                                                                                                                                                                                                                                         │
│ *  --role            UUID  user uuid [required]                                                                                                                                                                                                                                                         │
│    --help                  Show this message and exit.                                                                                                                                                                                                                                                  │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
