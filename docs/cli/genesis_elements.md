
# genesis_elements

Manage elements in the Genesis installation

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: genesis elements [OPTIONS] COMMAND [ARGS]...                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                           
```

## Options

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: genesis elements [OPTIONS] COMMAND [ARGS]...                                                                                                                                                                                                                                                       
                                                                                                                                                                                                                                                                                                           
 Manage elements in the Genesis installation                                                                                                                                                                                                                                                               
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --help  Show this message and exit.                                                                                                                                                                                                                                                                     │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ available   Print available elements in repository                                                                                                                                                                                                                                                      │
│ build       Build a Genesis element. The command build all images, manifests and other artifacts required for the element. The manifest in the project may be a raw YAML file or a template using Jinja2 templates. For Jinja2 templates, the following variables are available by default:             │
│ i           Install element from a manifest (YAML file)                                                                                                                                                                                                                                                 │
│ install     Install element from a manifest (YAML file)                                                                                                                                                                                                                                                 │
│ ips         Show element ips                                                                                                                                                                                                                                                                            │
│ list        List elements                                                                                                                                                                                                                                                                               │
│ show        Show element general information                                                                                                                                                                                                                                                            │
│ uninstall   Uninstall manifest by UUID, path or name                                                                                                                                                                                                                                                    │
│ update      Update element from a YAML file                                                                                                                                                                                                                                                             │
│ versions    Print available elements in repository                                                                                                                                                                                                                                                      │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
