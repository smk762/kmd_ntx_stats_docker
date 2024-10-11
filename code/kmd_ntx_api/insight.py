#!/usr/bin/env python3.12
import requests
from functools import cached_property

from kmd_ntx_api.helper import get_or_none
from kmd_ntx_api.query import get_coins_data
from kmd_ntx_api.logger import logger

# Grabs data from Dexstats explorer APIs
# e.g. https://kmd.explorer.dexstats.info/insight-api-komodo

KNOWN_INSIGHT_API = [
    "https://explorer.marmara.io/insight-api-komodo",
    "https://explorer.gleec.com/insight-api-komodo",
    "https://gleec.explorer.dexstats.info/insight-api-komodo",
]
