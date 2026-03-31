
# auth_refresh

Refresh stored token using refresh token

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: genesis auth refresh [OPTIONS] PROJECT_DIR                                                                                                                                                                                                                                                         
                                                                                                                                                                                                                                                                                                           
```

## Options

* `ttl`:
    * Type: integer
    * Default: `none`
    * Usage: `--ttl`

  Access token lifetime in seconds (optional)

* `scope`:
    * Type: text
    * Default: `none`
    * Usage: `--scope`

  OAuth scope (optional)

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
                                                                                                                                                                                                                                                                                                           
 Usage: genesis auth refresh [OPTIONS] PROJECT_DIR                                                                                                                                                                                                                                                         
                                                                                                                                                                                                                                                                                                           
 Refresh stored token using refresh token                                                                                                                                                                                                                                                                  
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --ttl    INTEGER  Access token lifetime in seconds (optional)                                                                                                                                                                                                                                           │
│ --scope  TEXT     OAuth scope (optional)                                                                                                                                                                                                                                                                │
│ --help            Show this message and exit.                                                                                                                                                                                                                                                           │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
