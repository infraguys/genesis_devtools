
# elements_update

Update element from a YAML file

## Usage

```console
Usage: genesis elements update [OPTIONS] PATH_OR_NAME
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
Usage: genesis elements update [OPTIONS] PATH_OR_NAME

  Update element from a YAML file

Options:
  -r, --repository TEXT  Repository endpoint  [default:
                         http://10.20.0.1:8080/genesis-elements/]
  --help                 Show this message and exit.
```
