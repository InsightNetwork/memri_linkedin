import hashlib
import json
import os

import requests
from py2store import QuickStore


class CachedSession(requests.Session):
    def __init__(self, cache_path="cache", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache = QuickStore(cache_path)

        adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
        self.mount("http://", adapter)

    def request(self, method, url, *args, **kwargs):
        key = hashlib.sha256((method + url).encode()).hexdigest()

        if key not in self.cache:
            response = super().request(method, url, *args, **kwargs)
            if response.status_code != 200:
                raise ConnectionError(f"Got {response.status_code}: {response.text}")
            self.cache[key] = response
        return self.cache[key]


class JsonCachedSession(requests.Session):
    """A session that caches the json responses in a directory"""

    def __init__(self, cache_path="cache", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cache_path = cache_path
        os.makedirs(cache_path, exist_ok=True)
        adapter = requests.adapters.HTTPAdapter(pool_connections=100, pool_maxsize=100)
        self.mount("http://", adapter)

    def request(self, method, url, *args, **kwargs):
        key = method + url

        key = key.replace("/", "_")

        path_key = f"{self.cache_path}/{key}.json"
        with open(path_key, "wt") as f:
            response = super().request(method, url, *args, **kwargs)
            response_json = response.json()
            json.dump(response_json, f, indent=2)
            return response
