
# certificates_update

Update certificate

## Usage

```console
                                                                                
 Usage: genesis certificates update [OPTIONS] UUID                              
                                                                                
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

  Name of the project in which to deploy the certificate

* `name`:
    * Type: text
    * Default: `none`
    * Usage: `-n
--name`

  Name of the certificate

* `description`:
    * Type: text
    * Default: `none`
    * Usage: `-D
--description`

  Description of the certificate

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                
 Usage: genesis certificates update [OPTIONS] UUID                              
                                                                                
 Update certificate                                                             
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --project-id   -p  UUID  Name of the project in which to deploy the          │
│                          certificate                                         │
│ --name         -n  TEXT  Name of the certificate                             │
│ --description  -D  TEXT  Description of the certificate                      │
│ --help                   Show this message and exit.                         │
╰──────────────────────────────────────────────────────────────────────────────╯
```
