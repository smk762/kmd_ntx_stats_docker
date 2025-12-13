
#!/usr/bin/env python3.12
import os
import time
import json
import requests
from decimal import Decimal
from dotenv import load_dotenv
from pathlib import Path
from pymemcache.client.base import PooledClient
from typing import Any, Optional, Dict, Union

from kmd_ntx_api.logger import logger

load_dotenv()

HOME = Path.home()
SCRIPT_PATH: Path = Path(__file__).resolve().parent.resolve().parent
CACHE_PATH: Path = SCRIPT_PATH / "cache"
CACHE_PATH.mkdir(exist_ok=True)
CACHE_TIMEOUT = 86400  # 1 day in seconds
CACHE_SIZE_LIMIT = 250 * 1024 * 1024  # 250 MB
CACHE_EXPIRY = 600  # 10 minutes in seconds

CACHE_SOURCE_URLS: Dict[str, Optional[str]] = {
    "b58_params_cache": None,
    "coins_config_cache": "https://raw.githubusercontent.com/gleecbtc/coins/master/utils/coins_config.json",
    "coin_icons_cache": None,
    "coins_info_cache": None,
    "ecosystem_links_cache": "https://raw.githubusercontent.com/gcharang/data/master/info/ecosystem.json",
    "get_electrum_status_cache": "https://electrum-status.dragonhound.info/api/v1/electrums_status",
    "explorers_cache": None,
    "launch_params_cache": "https://raw.githubusercontent.com/gleecbtc/coins/refs/heads/master/launch/smartchains.json",
    "notary_icons": None,
    "version_timespans_cache": "https://raw.githubusercontent.com/KomodoPlatform/dPoW/dev/doc/seed_version_epochs.json",
    "navigation": None,
    "notary_pubkeys_cache": None,
    "notary_seasons": None,
    "notary_faucet_coins": "https://notaryfaucet.dragonhound.tools/faucet_coins",
    "notary_faucet_balances": "https://notaryfaucet.dragonhound.tools/faucet_balances",
    "notary_faucet_pending_tx": "https://notaryfaucet.dragonhound.tools/show_pending_tx",
    "notary_faucet_db": "https://notaryfaucet.dragonhound.tools/faucet_history"
}



class JsonSerde(object):  # pragma: no coverhttps://notaryfaucet.dragonhound.tools/show_faucet_db

    @staticmethod
    def _json_default(obj):
        if isinstance(obj, Decimal):
            return float(obj)
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

    def serialize(self, key, value: Any) -> tuple[bytes, int]:
        if isinstance(value, str):
            return value.encode("utf-8"), 1
        return json.dumps(value, default=self._json_default).encode("utf-8"), 2

    def deserialize(self, key, value: bytes, flags: int) -> Any:
        if flags == 1:
            return value.decode("utf-8")
        if flags == 2:
            return json.loads(value.decode("utf-8"))
        raise Exception("Unknown serialization format")


class Cache:

    def __init__(self, host: str = 'memcached', port: int = 11211, timeout: int = 10, pool: int = 50) -> None:
        self.host = os.getenv('MEMCACHE_HOST', host)
        self.port = int(os.getenv('MEMCACHE_PORT', port))
        self.timeout = int(os.getenv('MEMCACHE_TIMEOUT', timeout))
        self.pool_size = int(os.getenv('MEMCACHE_POOL_SIZE', pool))
        self.limit = CACHE_SIZE_LIMIT
        self._client: Optional[PooledClient] = None

    @property
    def client(self) -> PooledClient:
        if self._client is None:
            try:  # pragma: no cover
                self._client = PooledClient(
                    (self.host, self.port),
                    serde=JsonSerde(),
                    timeout=self.timeout,
                    max_pool_size=self.pool_size,
                    ignore_exc=True,
                )
                self.ping()
                if os.getenv("IS_TESTING") == "True":
                    self._client.set("testing", True, 3600)
                logger.info("Connected to memcached docker container")
            except Exception as e:  # pragma: no cover
                logger.muted(e)
                # During tests, we might need localhost
                self._client = PooledClient(
                    ('localhost', self.port),
                    serde=JsonSerde(),
                    timeout=self.timeout,
                    max_pool_size=self.pool_size,
                    ignore_exc=True,
                )
                logger.info("Connected to memcached on localhost")
                if os.getenv("IS_TESTING") == "True":
                    self._client.set("testing", True, 3600)
            self._client.cache_memlimit = self.limit
        return self._client

    def flush(self):
        self.client.flush_all()

    # -------- Namespaced cache helpers --------
    def _epoch_key(self, namespace: str) -> str:
        return f"epoch::{namespace}".lower()

    def get_epoch(self, namespace: str) -> int:
        """Return the current cache epoch for a namespace (defaults to 0)."""
        try:
            val = self.client.get(self._epoch_key(namespace))
            return int(val) if val is not None else 0
        except Exception:
            return 0

    def bump_epoch(self, namespace: str) -> int:
        """Increment the cache epoch to invalidate namespaced keys."""
        try:
            key = self._epoch_key(namespace)
            val = self.client.get(key)
            if val is None:
                self.client.set(key, 1, CACHE_TIMEOUT)
                return 1
            new_val = int(val) + 1
            self.client.set(key, new_val, CACHE_TIMEOUT)
            return new_val
        except Exception as e:
            logger.warning(f"Failed to bump cache epoch for {namespace}: {e}")
            return 0

    def namespaced_key(self, namespace: str, key: str) -> str:
        """Attach namespace epoch to the key for targeted invalidation."""
        return f"{self.get_epoch(namespace)}::{key}".lower()

    def data_path(self, key: str) -> Path:
        """Returns the cache file path based on the key."""
        # Strip namespace epoch prefix (e.g. "3::key") so we keep one file per logical key.
        base_key = key.split("::", 1)[-1]
        path: Path = CACHE_PATH / f"{base_key}.json"
        return path

    def is_expired(self, path: Path, expire: int) -> bool:
        """Checks if the cache file is expired."""
        if not path.exists():
            return True
        return time.time() - path.stat().st_mtime > expire

    def ping(self) -> bool:
        """Tests connection to Memcached."""
        try:
            self.client.set("foo", "bar", 60)
            return True
        except Exception as e:
            logger.warning(f"Failed to ping Memcached: {e}")
            return False
    
    def get_data(self, key: str, expire: int = CACHE_EXPIRY) -> Optional[Union[dict, list, str]]:
        """Fetch data from Memcached or file cache, treating empty payloads as valid.
        Avoid redundant refetches by using on-disk cache when memcache evicts."""
        logger.info(f"Getting {key} from cache")
        key = key.lower()
        data = self.client.get(key)
        if data is None:
            path = self.data_path(key)
            # Rehydrate memcache from file if still fresh
            if path.exists() and not self.is_expired(path, expire):
                data = self.file_data(key)
                if data is not None:
                    self.client.set(key, data, expire)
            if data is None:
                data = self.refresh(key=key, expire=expire, force=False)
        if data is None and not str(self.data_path(key)).endswith("_summary.json"):
            data = self.file_data(key)
        return data

    def source_data(self, key: str) -> Optional[Union[dict, list]]:
        """Fetches data from the source URL."""
        url = CACHE_SOURCE_URLS.get(key)
        if url:
            try:
                logger.info(f"Getting {key} from {url}")
                response = requests.get(url)
                response.raise_for_status()
                data = response.json()
                if isinstance(data, dict) and "results" in data:
                    data = data["results"]
                return data
            except requests.RequestException as e:
                logger.warning(f"Failed to fetch data from {url}: {e}")
        return None

    def file_data(self, key: str) -> Optional[Union[dict, list, str]]:
        """Loads data from file cache."""
        try:
            path = self.data_path(key)
            logger.info(f"Getting {key} from {path}")
            with open(path, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as e:
            logger.error(f"Failed to read from cache file {path}: {e}")
            return None

    def refresh(self, key: str, expire: int = CACHE_TIMEOUT, force: bool = False, data: Optional[Union[dict, list, str]] = None) -> Optional[Union[dict, list, str]]:
        """Refreshes the cache file and updates Memcached.
        Empty lists/dicts are written to avoid stale data."""
        key = key.lower()
        path = self.data_path(key)
        # Ensure cache directory exists before attempting to write files
        path.parent.mkdir(parents=True, exist_ok=True)
        # Only fetch from remote source if caller did not supply data
        if data is None and (self.is_expired(path, expire) or force):
            data = self.source_data(key)
        existing = self.client.get(key)
        if data is None:
            return existing

        self.client.set(key, data, expire)
        logger.info(f"{key} updated in mem {path}")
        if not str(path).endswith("_summary.json"):
            # Use the same Decimal-safe serializer as Memcached writes
            path.write_text(json.dumps(data, indent=4, default=JsonSerde._json_default))
            logger.saved(f"{path} updated!")
        return self.client.get(key)

cached = Cache()
