
# ssh_keys_add

Add a new ssh_key to the Genesis installation

## Usage

```console
                                                                                
 Usage: genesis ssh_keys add [OPTIONS]                                          
                                                                                
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the ssh_key

* `project_id` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-p
--project-id`

  Name of the project in which to deploy the ssh_key

* `name`:
    * Type: text
    * Default: `test_ssh_key`
    * Usage: `-n
--name`

  Name of the ssh_key

* `description`:
    * Type: text
    * Default: ``
    * Usage: `-D
--description`

  Description of the ssh_key

* `node` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `--node`

  node uuid of the ssh_key

* `user` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--user`

  user uuid of the ssh_key

* `target_public_key`:
    * Type: text
    * Default: `none`
    * Usage: `--target_public_key`

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                
 Usage: genesis ssh_keys add [OPTIONS]                                          
                                                                                
 Add a new ssh_key to the Genesis installation                                  
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│    --uuid               -u  UUID  UUID of the ssh_key                        │
│ *  --project-id         -p  UUID  Name of the project in which to deploy the │
│                                   ssh_key [required]                         │
│    --name               -n  TEXT  Name of the ssh_key                        │
│    --description        -D  TEXT  Description of the ssh_key                 │
│ *  --node                   UUID  node uuid of the ssh_key [required]        │
│ *  --user                   TEXT  user uuid of the ssh_key [required]        │
│    --target_public_key      TEXT                                             │
│    --help                         Show this message and exit.                │
╰──────────────────────────────────────────────────────────────────────────────╯
```
