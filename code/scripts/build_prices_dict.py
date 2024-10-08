#!/usr/bin/env python3.12
import requests
import sys
import json
import time
from const_seasons import SEASONS_INFO
from lib_const import *
from lib_api import get_kmd_price
import datetime
from datetime import datetime as dt
from logger import logger

try:
    with open("prices_history.json", "r") as j:
        prices = json.load(j)
except Exception as e:
    logger.info(e)
    prices = {}

for season in ["Season_8"]:
    if season not in prices:
        prices.update({season: {}})
    season_start_dt = dt.fomtimestamp(SEASONS_INFO[season]["start_time"], datetime.UTC)
    season_end_dt = dt.fromtimestamp(SEASONS_INFO[season]["end_time"], datetime.UTC)
    start = season_start_dt.date()
    end = datetime.date.today()

    if time.time() > SEASONS_INFO[season]["end_time"]:
        end = season_end_dt.date()

    while start <= end:
        if f"{start}" not in prices[season] or start >= end - datetime.timedelta(days=1):
            prices[season].update({f"{start}":{}})
            logger.info(f"Updating [kmd_price] for {start}")
            date = f"{start}".split("-")
            date.reverse()
            date = "-".join(date)
            api_prices = get_kmd_price(date)
            prices[season][f"{start}"].update(api_prices)
            logger.info(api_prices['aud'])
            time.sleep(5)

        start += datetime.timedelta(days=1)
        


with open("prices_history.json", "w+") as j:
    json.dump(prices, j, indent=4)
