
# rsa_keys_add

Add a new rsa_key to the Genesis installation

## Usage

```console
                                                                                
 Usage: genesis rsa_keys add [OPTIONS]                                          
                                                                                
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the rsa_key

* `project_id` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-p
--project-id`

  Name of the project in which to deploy the rsa_key

* `name`:
    * Type: text
    * Default: `test_rsa_key`
    * Usage: `-n
--name`

  Name of the rsa_key

* `description`:
    * Type: text
    * Default: ``
    * Usage: `-D
--description`

  Description of the rsa_key

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                
 Usage: genesis rsa_keys add [OPTIONS]                                          
                                                                                
 Add a new rsa_key to the Genesis installation                                  
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│    --uuid         -u  UUID  UUID of the rsa_key                              │
│ *  --project-id   -p  UUID  Name of the project in which to deploy the       │
│                             rsa_key [required]                               │
│    --name         -n  TEXT  Name of the rsa_key                              │
│    --description  -D  TEXT  Description of the rsa_key                       │
│    --help                   Show this message and exit.                      │
╰──────────────────────────────────────────────────────────────────────────────╯
```
