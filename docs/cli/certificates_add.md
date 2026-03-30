
# certificates_add

Add a new certificate to the Genesis installation

## Usage

```console
                                                                                
 Usage: genesis certificates add [OPTIONS]                                      
                                                                                
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the certificate

* `project_id` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-p
--project-id`

  Name of the project in which to deploy the certificate

* `name`:
    * Type: text
    * Default: `test_certificate`
    * Usage: `-n
--name`

  Name of the certificate

* `description`:
    * Type: text
    * Default: ``
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
                                                                                
 Usage: genesis certificates add [OPTIONS]                                      
                                                                                
 Add a new certificate to the Genesis installation                              
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│    --uuid         -u  UUID  UUID of the certificate                          │
│ *  --project-id   -p  UUID  Name of the project in which to deploy the       │
│                             certificate [required]                           │
│    --name         -n  TEXT  Name of the certificate                          │
│    --description  -D  TEXT  Description of the certificate                   │
│    --help                   Show this message and exit.                      │
╰──────────────────────────────────────────────────────────────────────────────╯
```
