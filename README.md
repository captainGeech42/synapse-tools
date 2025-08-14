# synapse-tools

## Usage

```
$ uv tool install -e .
```

## Sample Config

By default, the config is loaded from `~/.syn/tools.yaml`. You can override this `$SYN_TOOLS_CONFIG_PATH`.

```yaml
optic:
  # base url of the optic server
  url: https://optic.my.synapse.instance/

  # creds used to directly authenticate to optic
  username: admin
  password: hunter2

  # if true, ssl cert verification is disabled
  disable_ssl_verification: false
```

## todo

- upload file