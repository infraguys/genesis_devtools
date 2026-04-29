
# ssh_keys_add

Add a new ssh_key to the Genesis installation, example: `secret ssh_keys add --node 2cc70850-3df7-4234-b9c1-0e20ed3672c7 --user ubuntu --target_public_key ~/.ssh/id_rsa.pub`

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: genesis secret ssh_keys add [OPTIONS]                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the ssh_key

* `project_id`:
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

* `node`:
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `--node`

  node uuid

* `node_set`:
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `--node_set`

  node_set uuid

* `user` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--user`

  user name of the ssh_key

* `target_public_key`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--target_public_key`

  key or path to it, for example: /home/user/.ssh/id_rsa.pub

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: genesis secret ssh_keys add [OPTIONS]                                                                                                                                                                                                                                                              
                                                                                                                                                                                                                                                                                                           
 Add a new ssh_key to the Genesis installation, example: `secret ssh_keys add --node 2cc70850-3df7-4234-b9c1-0e20ed3672c7 --user ubuntu --target_public_key ~/.ssh/id_rsa.pub`                                                                                                                             
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    --uuid               -u  UUID  UUID of the ssh_key                                                                                                                                                                                                                                                   │
│    --project-id         -p  UUID  Name of the project in which to deploy the ssh_key                                                                                                                                                                                                                    │
│    --name               -n  TEXT  Name of the ssh_key                                                                                                                                                                                                                                                   │
│    --description        -D  TEXT  Description of the ssh_key                                                                                                                                                                                                                                            │
│    --node                   UUID  node uuid                                                                                                                                                                                                                                                             │
│    --node_set               UUID  node_set uuid                                                                                                                                                                                                                                                         │
│ *  --user                   TEXT  user name of the ssh_key [required]                                                                                                                                                                                                                                   │
│    --target_public_key      TEXT  key or path to it, for example: /home/user/.ssh/id_rsa.pub                                                                                                                                                                                                            │
│    --help                         Show this message and exit.                                                                                                                                                                                                                                           │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
