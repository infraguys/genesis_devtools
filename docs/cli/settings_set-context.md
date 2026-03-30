
# settings_set-context

Set a context entry in settings

## Usage

```console
                                                                                
 Usage: genesis settings set-context [OPTIONS] REALM                            
                                                                                
```

## Options

* `realm` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `realm`

* `name` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-n
--name`

  Name of the context

* `user`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-u
--user`

  User for the context

* `password`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-p
--password`

  Password for the user in context

* `access_token`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-a
--access_token`

  Access token for the user in context

* `refresh_token`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-t
--refresh_token`

  Refresh token for the user in context

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                
 Usage: genesis settings set-context [OPTIONS] REALM                            
                                                                                
 Set a context entry in settings                                                
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ *  --name           -n  TEXT  Name of the context [required]                 │
│    --user           -u  TEXT  User for the context                           │
│    --password       -p  TEXT  Password for the user in context               │
│    --access_token   -a  TEXT  Access token for the user in context           │
│    --refresh_token  -t  TEXT  Refresh token for the user in context          │
│    --help                     Show this message and exit.                    │
╰──────────────────────────────────────────────────────────────────────────────╯
```
