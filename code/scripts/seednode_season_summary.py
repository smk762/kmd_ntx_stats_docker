#!/usr/bin/env python3.12
import json
import requests
from logger import logger


BASEURL = "https://test-stats.dragonhound.info/api/atomicdex/seednode_version_month_table"

def get_url(year, month, season):
    return f"{BASEURL}/?year={year}&month={month}&season={season}"

summary = {}
season = "Season_8"
for year in [2023, 2024]:
    if year == 2023:
        start_month = 6
        end_month = 12
    else:
        start_month = 1
        end_month = 5
        
    for month in range(start_month,end_month + 1):
        data = requests.get(get_url(year, month, season)).json()
        max_day = max([int(i) for i in data["scores"].keys()])
        for day in range(1, max_day + 1):
            day = str(day)
            if len(day) == 1:
                day = f"0{day}"
            for notary in data["scores"][day]:
                logger.info(f"Scanning {day}-{month}-{year} ({notary})")
                if notary not in summary:
                    summary.update({notary: {}})
                score = data["scores"][day][notary]["score"]
                date_str = f"{day}-{month}-{year}"
                summary[notary].update({date_str: score})
summary_mini = {}
for notary in summary:
    if sum(summary[notary].values()) > 0:
        summary_mini.update({notary: summary[notary]})

with open(f"seednode_summary_{season}.json", 'w+') as f:
    json.dump(summary_mini, f, indent=4)
    logger.merge(summary_mini.keys())
