
# nodes_add

Add a new node to the Genesis installation

## Usage

```console
Usage: genesis nodes add [OPTIONS]
```

## Options

* `uuid`:
    * Type: uuid
    * Default: `none`
    * Usage: `-u
--uuid`

  UUID of the node

* `project_id` (REQUIRED):
    * Type: uuid
    * Default: `sentinel.unset`
    * Usage: `-p
--project-id`

  Name of the project in which to deploy the node

* `cores`:
    * Type: integer
    * Default: `1`
    * Usage: `-c
--cores`

  Number of cores to allocate for the node

* `ram`:
    * Type: integer
    * Default: `1024`
    * Usage: `-r
--ram`

  Amount of RAM in Mb to allocate for the node

* `root_disk`:
    * Type: integer
    * Default: `10`
    * Usage: `-d
--root-disk`

  Number of GiB of root disk to allocate for the node

* `image` (REQUIRED):
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `-i
--image`

  Name of the image to deploy

* `name`:
    * Type: text
    * Default: `node`
    * Usage: `-n
--name`

  Name of the node

* `description`:
    * Type: text
    * Default: ``
    * Usage: `-D
--description`

  Description of the node

* `wait`:
    * Type: boolean
    * Default: `false`
    * Usage: `--wait`

  Wait until the node is running

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
Usage: genesis nodes add [OPTIONS]

  Add a new node to the Genesis installation

Options:
  -u, --uuid UUID          UUID of the node
  -p, --project-id UUID    Name of the project in which to deploy the node
                           [required]
  -c, --cores INTEGER      Number of cores to allocate for the node  [default:
                           1]
  -r, --ram INTEGER        Amount of RAM in Mb to allocate for the node
                           [default: 1024]
  -d, --root-disk INTEGER  Number of GiB of root disk to allocate for the node
                           [default: 10]
  -i, --image TEXT         Name of the image to deploy  [required]
  -n, --name TEXT          Name of the node
  -D, --description TEXT   Description of the node
  --wait                   Wait until the node is running
  --help                   Show this message and exit.
```
