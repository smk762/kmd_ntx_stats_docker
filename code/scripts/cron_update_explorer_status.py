#!/usr/bin/env python3
import sys
import json
from lib_insight import InsightAPI, INSIGHT_EXPLORERS
from os.path import dirname, realpath



data = []
for i in INSIGHT_EXPLORERS:
    info = {
        "coin": i,
        "explorer": "",
        "height": 0,
        "sync_pct": 0,
        "blockhash": "",
        "status": "unresponsive"
    }
    for j in INSIGHT_EXPLORERS[i]:
        insight = InsightAPI(j)
        try:
            sync = insight.sync()
            info.update({
                "height": sync['height'],
                "sync_pct": sync['syncPercentage'],
                "blockhash": insight.blockindex_info(sync['height'])['blockHash'],
                "status": sync['status']
            })
        except:
            pass
        data.append(info)

SCRIPT_PATH = dirname(realpath(sys.argv[0]))
CACHE_PATH = f"{SCRIPT_PATH}/../cache"

json.dump(data, open(f'{CACHE_PATH}/explorer_status.json', 'w+'), indent=4)
