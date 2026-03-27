
# vars_select

Select variable

## Usage

```console
                                                                                
 Usage: genesis vars select [OPTIONS] UUID                                      
                                                                                
```

## Options

* `uuid` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `uuid`

* `value` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-v
--value`

  Uuid of the value to select as the value of the variable

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                
 Usage: genesis vars select [OPTIONS] UUID                                      
                                                                                
 Select variable                                                                
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ *  --value  -v  UUID  Uuid of the value to select as the value of the        │
│                       variable [required]                                    │
│    --help             Show this message and exit.                            │
╰──────────────────────────────────────────────────────────────────────────────╯
```
