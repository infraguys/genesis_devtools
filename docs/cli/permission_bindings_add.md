
# permission_bindings_add

Add a new permission_binding to the Genesis installation

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: genesis iam permission_bindings add [OPTIONS]                                                                                                                                                                                                                                                      
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the permission_binding

* `project_id` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-p
--project-id`

  Name of the project in which to deploy the permission_binding

* `role` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `--role`

  role uuid

* `permission` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `--permission`

  permission uuid

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: genesis iam permission_bindings add [OPTIONS]                                                                                                                                                                                                                                                      
                                                                                                                                                                                                                                                                                                           
 Add a new permission_binding to the Genesis installation                                                                                                                                                                                                                                                  
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    --uuid        -u  UUID  UUID of the permission_binding                                                                                                                                                                                                                                               │
│ *  --project-id  -p  UUID  Name of the project in which to deploy the permission_binding [required]                                                                                                                                                                                                     │
│ *  --role            UUID  role uuid [required]                                                                                                                                                                                                                                                         │
│ *  --permission      UUID  permission uuid [required]                                                                                                                                                                                                                                                   │
│    --help                  Show this message and exit.                                                                                                                                                                                                                                                  │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
