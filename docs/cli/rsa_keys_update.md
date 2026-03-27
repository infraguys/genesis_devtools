
# rsa_keys_update

Update rsa_key

## Usage

```console
                                                                                
 Usage: genesis rsa_keys update [OPTIONS] UUID                                  
                                                                                
```

## Options

* `uuid` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `uuid`

* `project_id`:
    * Type: uuid
    * Default: `none`
    * Usage: `-p
--project-id`

  Name of the project in which to deploy the rsa_key

* `name`:
    * Type: text
    * Default: `none`
    * Usage: `-n
--name`

  Name of the rsa_key

* `description`:
    * Type: text
    * Default: `none`
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
                                                                                
 Usage: genesis rsa_keys update [OPTIONS] UUID                                  
                                                                                
 Update rsa_key                                                                 
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --project-id   -p  UUID  Name of the project in which to deploy the rsa_key  │
│ --name         -n  TEXT  Name of the rsa_key                                 │
│ --description  -D  TEXT  Description of the rsa_key                          │
│ --help                   Show this message and exit.                         │
╰──────────────────────────────────────────────────────────────────────────────╯
```
