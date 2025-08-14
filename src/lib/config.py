import logging
import os
import pprint

import yaml

LOG = logging.getLogger(__name__)

_CONFIG_ENV_VAR = "SYN_TOOLS_CONFIG_PATH"
_CONFIG_DEFAULT_PATH = "~/.syn/tools.yaml"

class Config:
    def __init__(self, path: str):
        with open(path, "r") as f:
            self._doc = yaml.safe_load(f)
            LOG.debug("config doc: %s", pprint.pformat(self._doc))
    
    def get(self, key: str) -> str | list | int | bool:
        v = self._doc
        for k in key.split("."):
            if not isinstance(v, dict):
                raise ValueError(f"invalid config key: {key} - no dict when handling key part {k}")
            if k not in v.keys():
                raise KeyError(f"invalid config key: {key} - key part {k} not found in current dict layer")
            v = v[k]
        return v

_CONFIG: Config | None = None

def _get_config_path():
    return os.path.expanduser(os.getenv(_CONFIG_ENV_VAR, _CONFIG_DEFAULT_PATH))

def load_config() -> Config:
    global _CONFIG
    if _CONFIG:
        LOG.debug("reusing existing config: %s", _CONFIG)
        return _CONFIG

    fp = _get_config_path()
    LOG.debug("initializing new config from %s", fp)
    _CONFIG = Config(fp)
    return _CONFIG