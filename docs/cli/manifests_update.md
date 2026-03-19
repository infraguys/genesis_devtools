
# manifests_update

Update manifest from a YAML file

## Usage

```console
Usage: genesis manifests update [OPTIONS] PATH_OR_NAME
```

## Options

* `repository`:
    * Type: text
    * Default: `http://10.20.0.1:8080/genesis-elements/`
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
Usage: genesis manifests update [OPTIONS] PATH_OR_NAME

  Update manifest from a YAML file

Options:
  -r, --repository TEXT  Repository endpoint  [default:
                         http://10.20.0.1:8080/genesis-elements/]
  --help                 Show this message and exit.
```
