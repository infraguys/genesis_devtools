# Adding and installing a new realm

## Adding and installing a new realm as current realm

```console
genesis settings set-realm <realm_name> \
  --endpoint <endpoint_url> \
  --check_updates \
  --current
```

Example:

```console
genesis settings set-realm production --endpoint http://10.40.0.2:11010 --current
```

## Adding and installing a new realm without setting it as current realm

```console
genesis settings set-realm <realm_name> \
  --endpoint <endpoint_url> \
  --check_updates \
  --skip_tls_verify
```

Example:

```console
genesis settings set-realm production --endpoint http://10.40.0.2:11010
```

## Get current realm

```console
genesis settings current-realm
```

## List all realms

```console
genesis settings list-realms
```

Example:

```console
user@user:~$ genesis settings list-realms
default:
  check_updates: true
  contexts:
    admin:
      password: admin
      user: admin
  current-context: admin
  endpoint: http://10.20.0.2:11010
production:
  check_updates: true
  endpoint: http://10.40.0.2:11010
  skip_tls_verify: true
```

## Set current realm

```console
genesis settings use-realm production
```

## Display genesis settings

```console
genesis settings view
```

Example:

```console
user@user:~$ genesis settings view
current-realm: production
endpoint: http://10.20.0.2:11010
realms:
  default:
    check_updates: true
    contexts:
      admin:
        password: admin
        user: admin
    current-context: admin
    endpoint: http://10.20.0.2:11010
  production:
    check_updates: true
    endpoint: http://10.40.0.2:11010
    skip_tls_verify: true
schema_version: 1
```

## Set authorization context

```console
genesis settings set-context <context_name> \
  --user <user> \
  --password <password> \
  --access_token <access_token> \
  --refresh_token <refresh_token> \
  <realm_name>
```

Example:

```console
genesis settings set-context --name "Admin Token" --access_token "...56riyO2U_gMjfYDwg" \
  --refresh_token "...bZ1BENYKg" City
```
