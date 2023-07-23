#!/usr/bin/env python3
import sys
import json
from lib_insight import InsightAPI
from os.path import dirname, realpath

INSIGHT_EXPLORERS = {
    'CCL': 'https://ccl.komodo.earth/',
    'CHIPS': 'https://chips.explorer.dexstats.info/',
    'CLC': 'https://clc.komodo.earth/',
    'DOC': 'https://doc.komodo.earth/',
    'GLEEC': 'https://gleec.komodo.earth/',
    'ILN': 'https://iln.komodo.earth/',
    'KMD': 'https://kmd.explorer.dexstats.info/',
    'KMD_3P': 'https://kmd.explorer.dexstats.info/',
    'KOIN': 'https://koin.komodo.earth/',
    'MARTY': 'https://marty.komodo.earth/',
    'MCL': 'https://mcl.explorer.dexstats.info/',
    'NINJA': 'https://ninja.komodo.earth/',
    'PIRATE': 'https://pirate.komodo.earth/',
    'SUPERNET': 'https://supernet.explorer.dexstats.info/',
    'THC': 'https://thc.explorer.dexstats.info/',
    'TOKEL': 'https://tokel.explorer.dexstats.info/',
    'VRSC': 'https://vrsc.explorer.dexstats.info/'
}

data = []
for i in INSIGHT_EXPLORERS:
    info = {
        "coin": i,
        "explorer": INSIGHT_EXPLORERS[i],
        "height": 0,
        "sync_pct": 0,
        "blockhash": "",
        "status": "unresponsive"
    }
    insight = InsightAPI(INSIGHT_EXPLORERS[i])
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
CACHE_PATH = f"{SCRIPT_PATH}/../kmd_ntx_api/cache"

json.dump(data, open(f'{CACHE_PATH}/explorer_status.json', 'w'), indent=4)
