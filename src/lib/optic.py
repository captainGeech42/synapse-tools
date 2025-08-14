import logging
import json
import pprint
from typing import Any

import requests

import lib.config as config

LOG = logging.getLogger(__name__)

class Client:
    def __init__(self):
        self._config = config.load_config()
        self._base_url = str(self._config.get("optic.url")).rstrip("/")
        self._danger_ssl = bool(self._config.get("optic.disable_ssl_verification"))
        if self._danger_ssl:
            LOG.debug("ssl verification is disabled")

        self._session = requests.Session()
        self._auth()
    
    def _auth(self):
        u = self._config.get("optic.username")
        p = self._config.get("optic.password")
        
        r = self._post("/api/v1/optic/login", json={"user": u, "passwd": p})
        j = r.json()
        if j.get("status") != "ok":
            raise RuntimeError(f"failed to authenticate to optic: {pprint.pformat(j)}")

        LOG.debug("successfully authenticated as %s to %s", u, self._base_url)

    def _get(self, path: str, *args, **kwargs) -> requests.Response:
        return self._session.get(self._base_url+path, *args, verify=(not self._danger_ssl), **kwargs)

    def _post(self, path: str, *args, **kwargs) -> requests.Response:
        return self._session.post(self._base_url+path, *args, verify=(not self._danger_ssl), **kwargs)

    def _put(self, path: str, *args, **kwargs) -> requests.Response:
        return self._session.put(self._base_url+path, *args, verify=(not self._danger_ssl), **kwargs)

    def _delete(self, path: str, *args, **kwargs) -> requests.Response:
        return self._session.delete(self._base_url+path, *args, verify=(not self._danger_ssl), **kwargs)
    
    def _patch(self, path: str, *args, **kwargs) -> requests.Response:
        return self._session.patch(self._base_url+path, *args, verify=(not self._danger_ssl), **kwargs)
    
    def _head(self, path: str, *args, **kwargs) -> requests.Response:
        return self._session.head(self._base_url+path, *args, verify=(not self._danger_ssl), **kwargs)
    
    def axon_files_put(self, content: bytes) -> dict[str, str | int]:
        """/api/v1/axon/files/put request"""

        r = self._post("/api/v1/axon/files/put", data=content)
        r.raise_for_status()
        j = r.json()
        if j.get("status") != "ok":
            raise RuntimeError(f"failed to upload file: {j}")
        return j["result"]

    def axon_files_by_sha256(self, sha256: str) -> bytes:
        """/api/v1/axon/files/by/sha256/<SHA-256> request"""

        r = self._get(f"/api/v1/axon/files/by/sha256/{sha256}")
        r.raise_for_status()
        return r.content
    
    def cortex_storm(self, query: str, opts: dict[str, Any] | None = None) -> list[list[Any]]:
        """/api/v1/storm request"""

        j: dict[str, Any] = {
            "query": query
        }
        if opts:
            j["opts"] = opts

        r = self._get("/api/v1/storm", stream=True, json=j)
        ret = []
        for chunk in r.iter_content(chunk_size=None, decode_unicode=True):
            msg = json.loads(chunk)
            ret.append(msg)
        return ret