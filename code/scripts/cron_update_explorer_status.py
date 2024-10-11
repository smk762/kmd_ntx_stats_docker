#!/usr/bin/env python3.12
import sys
import json
from lib_insight import InsightAPI, INSIGHT_EXPLORERS
from os.path import dirname, realpath
from logger import logger



data = []
for coin, explorers in INSIGHT_EXPLORERS.items():
    for domain in explorers:
        info = {
            "coin": coin,
            "explorer": domain,
            "height": 0,
            "sync_pct": 0,
            "version": 0,
            "notarised": 0,
            "blockhash": "",
            "status": "unresponsive"
        }
        insight = InsightAPI(domain)
        try:
            sync = insight.sync_status()
            node = insight.node_status()
            logger.info(f"scanning {domain} for {coin}")
            logger.info(node)
            info.update({
                "height": sync['height'],
                "explorer": domain,
                
                "version": node['info']['version'],
                "sync_pct": sync['syncPercentage'],
                "blockhash": insight.block_index_info(sync['height'])['blockHash'],
                "status": sync['status']
            })
            if 'notarized' in node['info']:
                info.update({
                    "notarized": node['info']['notarized'],
                })
            logger.info(f"[{coin}] {domain} OK!")
        except Exception as e:
            info.update({"status": str(e)})
            logger.error(f"[{coin}] {domain} Failed! {e}")
        data.append(info)

SCRIPT_PATH = dirname(realpath(sys.argv[0]))
CACHE_PATH = f"{SCRIPT_PATH}/../cache"
output_file = f'{CACHE_PATH}/explorer_status.json'
logger.info(f"Saving to {output_file}")
json.dump(data, open(output_file, 'w+'), indent=4)
