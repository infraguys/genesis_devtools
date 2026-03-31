
# genesis_build

Build a Genesis element. The command build all images, manifests and other artifacts required for the element. The manifest in the project may be a raw YAML file or a template using Jinja2 templates. For Jinja2 templates, the following variables are available by default:

- {{ version }}: version of the element

- {{ name }}: name of the element

- {{ images }}: list of images

- {{ manifests }}: list of manifests

Additional variables can be passed using the --manifest-var options.

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: genesis build [OPTIONS] PROJECT_DIR                                                                                                                                                                                                                                                                
                                                                                                                                                                                                                                                                                                           
```

## Options

- `genesis_cfg_file`:
    - Type: text
    - Default: `genesis.yaml`
    - Usage: `-c
--genesis-cfg-file`

  Name of the project configuration file

- `deps_dir`:
    - Type: text
    - Default: `none`
    - Usage: `--deps-dir`

  Directory where dependencies will be fetched

- `build_dir`:
    - Type: text
    - Default: `none`
    - Usage: `--build-dir`

  Directory where temporary build artifacts will be stored

- `output_dir`:
    - Type: text
    - Default: `output`
    - Usage: `--output-dir`

  Directory where output artifacts will be stored

- `developer_key_path`:
    - Type: text
    - Default: `none`
    - Usage: `-i
--developer-key-path`

  Path to developer public key

- `version_suffix`:
    - Type: choice
    - Default: `none`
    - Usage: `-s
--version-suffix`

  Version suffix will be used for the build

- `force`:
    - Type: boolean
    - Default: `false`
    - Usage: `-f
--force`

  Rebuild if the output already exists

- `inventory`:
    - Type: boolean
    - Default: `false`
    - Usage: `--inventory`

  Build using the inventory format

- `manifest_var`:
    - Type: text
    - Default: `sentinel.unset`
    - Usage: `--manifest-var`

  Additional variables to pass to the manifest template. The format is 'key=value'. For example: --manifest-var key1=value1 --manifest-var key2=value2

- `project_dir` (REQUIRED):
    - Type: path
    - Default: `sentinel.unset`
    - Usage: `project_dir`

- `help`:
    - Type: boolean
    - Default: `false`
    - Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                                                                                                                                                                                                                                           
 Usage: genesis build [OPTIONS] PROJECT_DIR                                                                                                                                                                                                                                                                
                                                                                                                                                                                                                                                                                                           
 Build a Genesis element. The command build all images, manifests and other artifacts required for the element. The manifest in the project may be a raw YAML file or a template using Jinja2 templates. For Jinja2 templates, the following variables are available by default:                           
 - {{ version }}: version of the element                                                                                                                                                                                                                                                                   
 - {{ name }}: name of the element                                                                                                                                                                                                                                                                         
 - {{ images }}: list of images                                                                                                                                                                                                                                                                            
 - {{ manifests }}: list of manifests                                                                                                                                                                                                                                                                      
                                                                                                                                                                                                                                                                                                           
 Additional variables can be passed using the --manifest-var options.                                                                                                                                                                                                                                      
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│ --genesis-cfg-file    -c  TEXT                   Name of the project configuration file                                                                                                                                                                                                                 │
│ --deps-dir                TEXT                   Directory where dependencies will be fetched                                                                                                                                                                                                           │
│ --build-dir               TEXT                   Directory where temporary build artifacts will be stored                                                                                                                                                                                               │
│ --output-dir              TEXT                   Directory where output artifacts will be stored                                                                                                                                                                                                        │
│ --developer-key-path  -i  TEXT                   Path to developer public key                                                                                                                                                                                                                           │
│ --version-suffix      -s  [latest|none|element]  Version suffix will be used for the build [default: none]                                                                                                                                                                                              │
│ --force               -f                         Rebuild if the output already exists                                                                                                                                                                                                                   │
│ --inventory                                      Build using the inventory format                                                                                                                                                                                                                       │
│ --manifest-var            TEXT                   Additional variables to pass to the manifest template. The format is 'key=value'. For example: --manifest-var key1=value1 --manifest-var key2=value2                                                                                                   │
│ --help                                           Show this message and exit.                                                                                                                                                                                                                            │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
