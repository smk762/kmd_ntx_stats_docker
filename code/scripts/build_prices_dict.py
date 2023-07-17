#!/usr/bin/env python3
import requests
import sys
import json
import time
from lib_const import *
from lib_api import get_kmd_price
import datetime
from datetime import datetime as dt

try:
    with open("prices_history.json", "r") as j:
        prices = json.load(j)
except Exception as e:
    print(e)
    prices = {}

for season in ["Season_7"]:
    if season not in prices:
        prices.update({season: {}})
    season_start_dt = dt.utcfromtimestamp(SEASONS_INFO[season]["start_time"])
    season_end_dt = dt.utcfromtimestamp(SEASONS_INFO[season]["end_time"])
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
            print(api_prices['aud'])
            time.sleep(5)

        start += datetime.timedelta(days=1)
        


with open("prices_history.json", "w+") as j:
    json.dump(prices, j, indent=4)
