
# elements_install

Install element from a manifest (YAML file)

## Usage

```console
                                                                                
 Usage: genesis elements install [OPTIONS] PATH_OR_NAME                         
                                                                                
```

## Options

* `repository`:
    * Type: text
    * Default: `https://repository.genesis-core.tech/genesis-elements/`
    * Usage: `-r
--repository`

  Repository endpoint

* `path_or_name` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `path_or_name`

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                
 Usage: genesis elements install [OPTIONS] PATH_OR_NAME                         
                                                                                
 Install element from a manifest (YAML file)                                    
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --repository  -r  TEXT  Repository endpoint [default:                        │
│                         https://repository.genesis-core.tech/genesis-element │
│                         s/]                                                  │
│ --help                  Show this message and exit.                          │
╰──────────────────────────────────────────────────────────────────────────────╯
```
