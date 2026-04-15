
# users_add

Add a new user to the Genesis installation

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: genesis iam users add [OPTIONS]                                                                                                                                                                                                                                                                    
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the user

* `name`:
    * Type: text
    * Default: `test_user`
    * Usage: `-n
--name`

  Name of the user

* `password`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-p
--password`

  Password of the user

* `description`:
    * Type: text
    * Default: ``
    * Usage: `-D
--description`

  Description of the user

* `first_name`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--first_name`

* `last_name`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--last_name`

* `surname`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--surname`

* `phone`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--phone`

* `email` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--email`

* `email_verified`:
    * Type: boolean
    * Default: `false`
    * Usage: `--email_verified`

* `confirmation_code`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--confirmation_code`

* `confirmation_code_made_at`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--confirmation_code_made_at`

* `otp_secret`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--otp_secret`

* `otp_enabled`:
    * Type: boolean
    * Default: `false`
    * Usage: `--otp_enabled`

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: genesis iam users add [OPTIONS]                                                                                                                                                                                                                                                                    
                                                                                                                                                                                                                                                                                                           
 Add a new user to the Genesis installation                                                                                                                                                                                                                                                                
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    --uuid                       -u  UUID  UUID of the user                                                                                                                                                                                                                                              │
│    --name                       -n  TEXT  Name of the user                                                                                                                                                                                                                                              │
│    --password                   -p  TEXT  Password of the user                                                                                                                                                                                                                                          │
│    --description                -D  TEXT  Description of the user                                                                                                                                                                                                                                       │
│    --first_name                     TEXT                                                                                                                                                                                                                                                                │
│    --last_name                      TEXT                                                                                                                                                                                                                                                                │
│    --surname                        TEXT                                                                                                                                                                                                                                                                │
│    --phone                          TEXT                                                                                                                                                                                                                                                                │
│ *  --email                          TEXT  [required]                                                                                                                                                                                                                                                    │
│    --email_verified                                                                                                                                                                                                                                                                                     │
│    --confirmation_code              TEXT                                                                                                                                                                                                                                                                │
│    --confirmation_code_made_at      TEXT                                                                                                                                                                                                                                                                │
│    --otp_secret                     TEXT                                                                                                                                                                                                                                                                │
│    --otp_enabled                                                                                                                                                                                                                                                                                        │
│    --help                                 Show this message and exit.                                                                                                                                                                                                                                   │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
