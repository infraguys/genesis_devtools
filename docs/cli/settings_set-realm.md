
# settings_set-realm

Set a realm entry in settings

## Usage

```console
                                                                                
 Usage: genesis settings set-realm [OPTIONS] REALM                              
                                                                                
```

## Options

* `realm` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `realm`

* `endpoint` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-e
--endpoint`

  Endpoint for the realm

* `check_updates`:
    * Type: boolean
    * Default: `true`
    * Usage: `-c
--check_updates`

  Check for updates on startup

* `skip_tls_verify`:
    * Type: boolean
    * Default: `true`
    * Usage: `-s
--skip_tls_verify`

  Skip TLS certificate verification

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                
 Usage: genesis settings set-realm [OPTIONS] REALM                              
                                                                                
 Set a realm entry in settings                                                  
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ *  --endpoint         -e  TEXT  Endpoint for the realm [required]            │
│    --check_updates    -c        Check for updates on startup                 │
│    --skip_tls_verify  -s        Skip TLS certificate verification            │
│    --help                       Show this message and exit.                  │
╰──────────────────────────────────────────────────────────────────────────────╯
```
