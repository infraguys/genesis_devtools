
# elements_edit

Edit manifest

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: genesis elements edit [OPTIONS] UUID_NAME                                                                                                                                                                                                                                                          
                                                                                                                                                                                                                                                                                                           
```

## Options

* `uuid_name` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `uuid_name`

* `editor`:
    * Type: choice
    * Default: `nano`
    * Usage: `-e
--editor`

  Editor (nano or vim)

* `repository`:
    * Type: text
    * Default: `https://repository.genesis-core.tech/genesis-elements/`
    * Usage: `-r
--repository`

  Repository endpoint

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: genesis elements edit [OPTIONS] UUID_NAME                                                                                                                                                                                                                                                          
                                                                                                                                                                                                                                                                                                           
 Edit manifest                                                                                                                                                                                                                                                                                             
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --editor      -e  [nano|vim]  Editor (nano or vim)                                                                                                                                                                                                                                                      │
│ --repository  -r  TEXT        Repository endpoint [default: https://repository.genesis-core.tech/genesis-elements/]                                                                                                                                                                                     │
│ --help                        Show this message and exit.                                                                                                                                                                                                                                               │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
