
# profiles_add

Add a new profile to the Genesis installation

## Usage

```console
                                                                                                                                                                                                                                                                                                           
 Usage: genesis vs profiles add [OPTIONS]                                                                                                                                                                                                                                                                  
                                                                                                                                                                                                                                                                                                           
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
                                                                                                                                                                                                                                                                                                           
 Usage: genesis vs profiles add [OPTIONS]                                                                                                                                                                                                                                                                  
                                                                                                                                                                                                                                                                                                           
 Add a new profile to the Genesis installation                                                                                                                                                                                                                                                             
                                                                                                                                                                                                                                                                                                           
╭─ Options ───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│    --uuid          -u  UUID  UUID of the profile                                                                                                                                                                                                                                                        │
│ *  --project-id    -p  UUID  Name of the project in which to deploy the profile [required]                                                                                                                                                                                                              │
│    --name          -n  TEXT  Name of the profile                                                                                                                                                                                                                                                        │
│    --description   -D  TEXT  Description of the profile                                                                                                                                                                                                                                                 │
│    --profile_type  -t  TEXT  Profile_type (ELEMENT, GLOBAL)                                                                                                                                                                                                                                             │
│    --help                    Show this message and exit.                                                                                                                                                                                                                                                │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
