
# profiles_add

Add a new profile to the Genesis installation

## Usage

```console
Usage: genesis profiles add [OPTIONS]
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the profile

* `project_id` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-p
--project-id`

  Name of the project in which to deploy the profile

* `name`:
    * Type: text
    * Default: `profile`
    * Usage: `-n
--name`

  Name of the profile

* `description`:
    * Type: text
    * Default: ``
    * Usage: `-D
--description`

  Description of the profile

* `profile_type`:
    * Type: text
    * Default: `global`
    * Usage: `-t
--profile_type`

  Profile_type (ELEMENT, GLOBAL)

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
Usage: genesis profiles add [OPTIONS]

  Add a new profile to the Genesis installation

Options:
  -u, --uuid UUID          UUID of the profile
  -p, --project-id UUID    Name of the project in which to deploy the profile
                           [required]
  -n, --name TEXT          Name of the profile
  -D, --description TEXT   Description of the profile
  -t, --profile_type TEXT  Profile_type (ELEMENT, GLOBAL)
  --help                   Show this message and exit.
```
