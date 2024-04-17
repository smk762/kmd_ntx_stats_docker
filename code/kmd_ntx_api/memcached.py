#!/usr/bin/env python3
import os
import json
from dotenv import load_dotenv
from pymemcache.client.base import PooledClient
from kmd_ntx_api.logger import logger
from kmd_ntx_api.const import MEMCACHE_LIMIT

load_dotenv()

class JsonSerde(object):  # pragma: no cover
    def serialize(self, key, value):
        if isinstance(value, str):
            return value.encode("utf-8"), 1
        return json.dumps(value).encode("utf-8"), 2

    def deserialize(self, key, value, flags):
        if flags == 1:
            return value.decode("utf-8")
        if flags == 2:
            return json.loads(value.decode("utf-8"))
        raise Exception("Unknown serialization format")


try:  # pragma: no cover
    MEMCACHE = PooledClient(
        ("memcached", 11211),
        serde=JsonSerde(),
        timeout=10,
        max_pool_size=50,
        ignore_exc=True,
    )
    MEMCACHE.set("foo", "bar", 60)
    if os.getenv("IS_TESTING") == "True":
        MEMCACHE.set("testing", True, 3600)
    logger.info("Connected to memcached docker container")

except Exception as e:  # pragma: no cover
    logger.muted(e)
    MEMCACHE = PooledClient(
        ("localhost", 11211),
        serde=JsonSerde(),
        timeout=10,
        max_pool_size=50,
        ignore_exc=True,
    )
    logger.info("Connected to memcached on localhost")
    if os.getenv("IS_TESTING") == "True":
        MEMCACHE.set("testing", True, 3600)

MEMCACHE.cache_memlimit = MEMCACHE_LIMIT
MEMCACHE.flush_all()


class Cache:
    def __init__(self) -> None:
        pass
    