# Config for genesis cli

Default path for config file: `~/.genesis/genesisctl.yaml`

Example config:

```yaml
current-realm: default
realms:
  default:
    check_updates: true
    contexts:
      admin:
        password: admin
        user: admin
    current-context: admin
    endpoint: http://10.20.0.2:11010
  my_stand:
    check_updates: true
    contexts:
      base:
        password: my_password
        user: my_admin
    current-context: base
    endpoint: https://console.my_company.tech:80
  production:
    check_updates: true
    endpoint: http://10.40.0.2:11010
    skip_tls_verify: true
developer_key_path: ~/.ssh/id_rsa.pub
```

You can change the path to the config file by setting the command line argument `--config`.

Example:

```bash
genesis --config ~/.genesis.yaml elements list
```

## Realms

Realms are used to separate environments. For example, you can have production and development environments.

See the [realms](realms.md) page for more information.

## developer_key_path

The path to your ssh key.

You can change the path to the ssh key by config or by setting the command line argument `--developer_key_path` or `-i`
or by environment variable `GEN_DEV_KEYS`.

## Init

You can interactively init the config file by running the following command:

```bash
genesis settings init
```
