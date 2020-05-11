#!/usr/bin/env python3
import json
import requests
import table_lib
import logging
import logging.handlers
from coins_lib import all_coins

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

'''
This script scans the coins and dpow repositories and updates contexual info about the chains in the "coins" table.
It should be run as a cronjob every 12-24 hours
'''


conn = table_lib.connect_db()
cursor = conn.cursor()

dpow = {}
r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/dPoW/master/README.md")
dpow_readme = r.text
lines = dpow_readme.splitlines()
for line in lines:
    raw_info = line.split("|")
    info = [i.strip() for i in raw_info]
    if info[0] in all_coins and len(info) == 5:
        coin = info[0]
        src = info[1].split("(")[1].replace(")","")
        version = info[2]
        server = info[4]
        dpow.update({
            coin:{
                "src":src,
                "version":version,
                "server":server            
            }
        })

r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/coins/master/coins")
coins_repo = r.json()

coins_info = {}
for item in coins_repo:
    coin = item['coin']
    mm2_compatible = 0
    if 'mm2' in item:
        mm2_compatible = item['mm2']
    logger.info("Getting info for ["+coin+"]")
    logger.info(item)
    coins_info.update({coin:{"coins_info":item}})
    try:
        coins_info[coin].update({"electrums":[]})
        coins_info[coin].update({"electrums_ssl":[]})
        r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/coins/master/electrums/"+coin)
        electrums = r.json()
        for item in electrums:
            if "protocol" in item:
                if item['protocol'] == "SSL":
                    coins_info[coin]['electrums_ssl'].append(item['url'])
                else:
                    coins_info[coin]['electrums'].append(item['url'])
            else:
                coins_info[coin]['electrums'].append(item['url'])
    except Exception as e:
        logger.info("GET "+coin+" ELECTRUM ERROR: "+str(e)+" [RESPONSE]: "+r.text)
    try:
        coins_info[coin].update({"explorers":[]})
        r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/coins/master/explorers/"+coin)
        explorers = r.json()
        for item in explorers:
            coins_info[coin]['explorers'].append(item)
    except Exception as e:
        logger.info("GET "+coin+" EXPLORER ERROR: "+str(e)+" [RESPONSE]: "+r.text)
    if coin in dpow:
        dpow_active = 1
        coins_info[coin].update({
                "dpow":{
                    "src":dpow[coin]['src'],
                    "version":dpow[coin]['version'],
                    "server":dpow[coin]['server']
                }
            })
    else:
        dpow_active = 0
        coins_info[coin].update({"dpow":{}})
    row_data = (coin, json.dumps(coins_info[coin]["coins_info"]),
                json.dumps(coins_info[coin]['electrums']), json.dumps(coins_info[coin]['electrums_ssl']),
                json.dumps(coins_info[coin]['explorers']), json.dumps(coins_info[coin]['dpow']),
                dpow_active, mm2_compatible)
    table_lib.update_coins_tbl(conn, cursor, row_data)

logging.info("Finished!")
cursor.close()
conn.close()