
# backup

Backup the current installation

## Usage

```console
Usage: genesis backup [OPTIONS]
```

## Options

*   `config`:
    * Type: <click.types.Path object at 0x7cb005f3af60>
    * Default: `none`
    * Usage: `--config`

  Path to the backuper configuration file

*   `name`:
    *   Type: STRING
    *   Default: `none`
    *   Usage: `-n
--name`

  Name of the libvirt domain, if not provided, all will be backed up

*   `backup_dir`:
    *   Type: <click.types.Path object at 0x7cb005f3afc0>
    *   Default: `.`
    *   Usage: `-d
--backup-dir`

  Directory where backups will be stored

*   `period`:
    *   Type: Choice(['1m', '5m', '15m', '30m', '1h', '3h', '6h', '12h', '1d', '3d', '7d'])
    *   Default: `1d`
    *   Usage: `-p
--period`

  the regularity of backups

*   `offset`:
    *   Type: Choice(['1m', '5m', '15m', '30m', '1h', '3h', '6h', '12h', '1d', '3d', '7d'])
    *   Default: `none`
    *   Usage: `-o
--offset`

  The time offset of the first backup. If not provided, the same value as the period will be used

*   `start`:
    * Type: <click.types.FuncParamType object at 0x7cb005f3b560>
    * Default: `none`
    * Usage: `--start`

  Time of day to start backup in format HH:MM:SS. Cannot be used together with --offset. If provided, period must be >= 1d.

*   `oneshot`:
    * Type: BOOL
    * Default: `false`
    * Usage: `--oneshot`

  Do a backup once and exit

*   `compress`:
    *   Type: BOOL
    *   Default: `false`
    *   Usage: `-c
--compress`

  Compress the backup.

*   `encrypt`:
    *   Type: BOOL
    *   Default: `false`
    *   Usage: `-e
--encrypt`

  Encrypt the backup. Works only with the compress flag. Use environment variable to specify the encryption key and the initialization vector: GEN_DEV_BACKUP_KEY and GEN_DEV_BACKUP_IV

*   `min_free_space`:
    *   Type: INT
    *   Default: `50`
    *   Usage: `-s
--min-free-space`

  Free disk space shouldn't be lower than this threshold. If the space becomes lower, the backup process is stopped. The value is in GB.

*   `rotate`:
    *   Type: INT
    *   Default: `5`
    *   Usage: `-r
--rotate`

  Maximum number of backups to keep. The oldest backups are deleted. `0` means no rotation.

*   `exclude_name`:
    *   Type: STRING
    *   Default: `sentinel.unset`
    *   Usage: `--no
--exclude-name`

  Name or pattern of libvirt domains to exclude from backup

*   `help`:
    * Type: BOOL
    * Default: `false`
    * Usage: `--help`

  Show this message and exit.

## CLI Help

```console
Usage: genesis backup [OPTIONS]

  Backup the current installation

Options:
  --config PATH                   Path to the backuper configuration file
  -n, --name TEXT                 Name of the libvirt domain, if not
                                  provided, all will be backed up
  -d, --backup-dir PATH           Directory where backups will be stored
  -p, --period [1m|5m|15m|30m|1h|3h|6h|12h|1d|3d|7d]
                                  the regularity of backups  [default: 1d]
  -o, --offset [1m|5m|15m|30m|1h|3h|6h|12h|1d|3d|7d]
                                  The time offset of the first backup. If not
                                  provided, the same value as the period will be
                                  used
  --start _START_VALIDATION_TYPE  Time of day to start backup in format
                                  HH:MM:SS. Cannot be used together with
                                  --offset. If provided, period must be >= 1d.
  --oneshot                       Do a backup once and exit
  -c, --compress                  Compress the backup.
  -e, --encrypt                   Encrypt the backup. Works only with the
                                  compress flag. Use environment variable to
                                  specify the encryption key and the
                                  initialization vector: GEN_DEV_BACKUP_KEY and
                                  GEN_DEV_BACKUP_IV
  -s, --min-free-space INTEGER    Free disk space shouldn't be lower than this
                                  threshold. If the space becomes lower, the
                                  backup process is stopped. The value is in GB.
                                  [default: 50]
  -r, --rotate INTEGER            Maximum number of backups to keep. The oldest
                                  backups are deleted. `0` means no rotation.
                                  [default: 5]
  --no, --exclude-name TEXT       Name or pattern of libvirt domains to
                                  exclude from backup
  --help                          Show this message and exit.
```
