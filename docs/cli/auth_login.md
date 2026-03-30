
# auth_login

Authenticate in IAM and store tokens locally

## Usage

```console
                                                                                
 Usage: genesis auth login [OPTIONS] PROJECT_DIR                                
                                                                                
```

## Options

* `iam_client_endpoint` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--iam-client-endpoint`

  Full URL of the IAM client

* `project_id` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--project-id`

  Project ID for IAM authentication

* `client_id`:
    * Type: text
    * Default: `none`
    * Usage: `--client-id`

  OAuth client id (optional)

* `client_secret`:
    * Type: text
    * Default: `none`
    * Usage: `--client-secret`

  OAuth client secret (optional)

* `scope`:
    * Type: text
    * Default: `profile`
    * Usage: `--scope`

  OAuth scope

* `ttl`:
    * Type: integer
    * Default: `900`
    * Usage: `--ttl`

  Access token lifetime in seconds

* `refresh_ttl`:
    * Type: integer
    * Default: `3600`
    * Usage: `--refresh-ttl`

  Refresh token lifetime in seconds

* `force`:
    * Type: boolean
    * Default: `false`
    * Usage: `-f
--force`

  Overwrite existing auth file

* `project_dir` (REQUIRED):
    * Type: path
    * Default: `sentinel.unset`
    * Usage: `project_dir`

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                
 Usage: genesis auth login [OPTIONS] PROJECT_DIR                                
                                                                                
 Authenticate in IAM and store tokens locally                                   
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ *  --iam-client-endpoint      TEXT     Full URL of the IAM client [required] │
│ *  --project-id               TEXT     Project ID for IAM authentication     │
│                                        [required]                            │
│    --client-id                TEXT     OAuth client id (optional)            │
│    --client-secret            TEXT     OAuth client secret (optional)        │
│    --scope                    TEXT     OAuth scope [default: profile]        │
│    --ttl                      INTEGER  Access token lifetime in seconds      │
│                                        [default: 900]                        │
│    --refresh-ttl              INTEGER  Refresh token lifetime in seconds     │
│                                        [default: 3600]                       │
│    --force                -f           Overwrite existing auth file          │
│    --help                              Show this message and exit.           │
╰──────────────────────────────────────────────────────────────────────────────╯
```
