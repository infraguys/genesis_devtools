
# settings_rename-context

Rename a context from the settings file

## Usage

```console
                                                                                
 Usage: genesis settings rename-context [OPTIONS] OLD_CONTEXT NEW_CONTEXT       
                                                                                
```

## Options

* `old_context` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `old-context`

* `new_context` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `new-context`

* `realm` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-r
--realm`

  Name of the context

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                
 Usage: genesis settings rename-context [OPTIONS] OLD_CONTEXT NEW_CONTEXT       
                                                                                
 Rename a context from the settings file                                        
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ *  --realm  -r  TEXT  Name of the context [required]                         │
│    --help             Show this message and exit.                            │
╰──────────────────────────────────────────────────────────────────────────────╯
```
