
# genesis_backup

Backup the current installation

## Usage

```console
                                                                                
 Usage: genesis backup [OPTIONS]                                                
                                                                                
```

## Options

* `config`:
    * Type: path
    * Default: `none`
    * Usage: `--config`

  Path to the backuper configuration file

* `name`:
    * Type: text
    * Default: `none`
    * Usage: `-n
--name`

  Name of the libvirt domain, if not provided, all will be backed up

* `backup_dir`:
    * Type: path
    * Default: `.`
    * Usage: `-d
--backup-dir`

  Directory where backups will be stored

* `period`:
    * Type: choice
    * Default: `1d`
    * Usage: `-p
--period`

  the regularity of backups

* `offset`:
    * Type: choice
    * Default: `none`
    * Usage: `-o
--offset`

  The time offset of the first backup. If not provided, the same value as the period will be used

* `start`:
    * Type: _start_validation_type
    * Default: `none`
    * Usage: `--start`

  Time of day to start backup in format HH:MM:SS. Cannot be used together with --offset. If provided, period must be >= 1d.

* `oneshot`:
    * Type: boolean
    * Default: `false`
    * Usage: `--oneshot`

  Do a backup once and exit

* `compress`:
    * Type: boolean
    * Default: `false`
    * Usage: `-c
--compress`

  Compress the backup.

* `encrypt`:
    * Type: boolean
    * Default: `false`
    * Usage: `-e
--encrypt`

  Encrypt the backup. Works only with the compress flag. Use environment variable to specify the encryption key and the initialization vector: GEN_DEV_BACKUP_KEY and GEN_DEV_BACKUP_IV

* `min_free_space`:
    * Type: integer
    * Default: `50`
    * Usage: `-s
--min-free-space`

  Free disk space shouldn't be lower than this threshold. If the space becomes lower, the backup process is stopped. The value is in GB.

* `rotate`:
    * Type: integer
    * Default: `5`
    * Usage: `-r
--rotate`

  Maximum number of backups to keep. The oldest backups are deleted. `0` means no rotation.

* `exclude_name`:
    * Type: text
    * Default: `sentinel.unset`
    * Usage: `--no
--exclude-name`

  Name or pattern of libvirt domains to exclude from backup

* `help`:
    * Type: boolean
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
                                                                                
 Usage: genesis backup [OPTIONS]                                                
                                                                                
 Backup the current installation                                                
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --config                 PATH                      Path to the backuper      │
│                                                    configuration file        │
│ --name               -n  TEXT                      Name of the libvirt       │
│                                                    domain, if not provided,  │
│                                                    all will be backed up     │
│ --backup-dir         -d  PATH                      Directory where backups   │
│                                                    will be stored            │
│ --period             -p  [1m|5m|15m|30m|1h|3h|6h|  the regularity of backups │
│                          12h|1d|3d|7d]             [default: 1d]             │
│ --offset             -o  [1m|5m|15m|30m|1h|3h|6h|  The time offset of the    │
│                          12h|1d|3d|7d]             first backup. If not      │
│                                                    provided, the same value  │
│                                                    as the period will be     │
│                                                    used                      │
│ --start                  _START_VALIDATION_TYPE    Time of day to start      │
│                                                    backup in format          │
│                                                    HH:MM:SS. Cannot be used  │
│                                                    together with --offset.   │
│                                                    If provided, period must  │
│                                                    be >= 1d.                 │
│ --oneshot                                          Do a backup once and exit │
│ --compress           -c                            Compress the backup.      │
│ --encrypt            -e                            Encrypt the backup. Works │
│                                                    only with the compress    │
│                                                    flag. Use environment     │
│                                                    variable to specify the   │
│                                                    encryption key and the    │
│                                                    initialization vector:    │
│                                                    GEN_DEV_BACKUP_KEY and    │
│                                                    GEN_DEV_BACKUP_IV         │
│ --min-free-space     -s  INTEGER                   Free disk space shouldn't │
│                                                    be lower than this        │
│                                                    threshold. If the space   │
│                                                    becomes lower, the backup │
│                                                    process is stopped. The   │
│                                                    value is in GB. [default: │
│                                                    50]                       │
│ --rotate             -r  INTEGER                   Maximum number of backups │
│                                                    to keep. The oldest       │
│                                                    backups are deleted. `0`  │
│                                                    means no rotation.        │
│                                                    [default: 5]              │
│ --no,--exclude-name      TEXT                      Name or pattern of        │
│                                                    libvirt domains to        │
│                                                    exclude from backup       │
│ --help                                             Show this message and     │
│                                                    exit.                     │
╰──────────────────────────────────────────────────────────────────────────────╯
```
