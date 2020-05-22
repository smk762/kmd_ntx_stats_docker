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
    if info[0] in all_coins:
        coin = info[0]
        try:
            src = info[1].split("(")[1].replace(")","")
        except:
            src = info[1]
        version = info[2]
        server = info[4]
        dpow.update({
            coin:{
                "src":src,
                "version":version,
                "server":server            
            }
        })

r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/komodo/master/src/assetchains.json")
ac_json = r.json()
for item in ac_json:
    chain = item['ac_name']
    params = "~/komodo/src/komodod"
    for k,v in item.items():
        if k == 'addnode':
            for ip in v:
                params += " -"+k+"="+ip
        else:
            params += " -"+k+"="+str(v)
    if chain in dpow:
        dpow[chain].update({"launch_params":params})
        dpow[chain].update({"cli":'~/komodo/src/komodo-cli -ac_name='+chain})
        dpow[chain].update({"conf_path":'~/.komodo/'+chain+'/'+chain+'.conf'})

    else:
        logger.info(chain+" not in dpow list")

other_launch = {
    "BTC":"~/bitcoin/src/bitcoind",
    "KMD":"~/komodo/src/komodod", 
    "HUSH3":"~/hush3/src/hushd",   
    "AYA":"~/AYAv2/src/aryacoind",
    "CHIPS":"~/chips3/src/chipsd",
    "GAME":"~/GameCredits/src/gamecreditsd",
    "EMC2":"~/einsteinium/src/einsteiniumd",
    "GIN":"~/gincoin-core/src/gincoind",  
    "VRSC":"~/VerusCoin/src/verusd",   
}
other_conf = {
    "BTC":"~/.bitcoin/bitcoin.conf",
    "KMD":"~/.komodo/komodo.conf", 
    "HUSH3":"~/.komodo/HUSH3/HUSH3.conf",   
    "AYA":"~/.aryacoin/aryacoin.conf",
    "CHIPS":"~/.chips/chips.conf",
    "GAME":"~/.gamecredits/gamecredits.conf",
    "EMC2":"~/.einsteinium/einsteinium.conf",
    "GIN":"~/.gincoincore/gincoin.conf",  
    "VRSC":"~/.komodo/VRSC/VRSC.conf",   
}
other_cli = {
    "BTC":"~/bitcoin/src/bitcoin-cli",
    "KMD":"~/komodo/src/komodo-cli", 
    "HUSH3":"~/hush3/src/hush-cli",   
    "AYA":"~/AYAv2/src/aryacoin-cli",
    "CHIPS":"~/chips3/src/chips-cli",
    "GAME":"~/GameCredits/src/gamecredits-cli",
    "EMC2":"~/einsteinium/src/einsteinium-cli",
    "GIN":"~/gincoin-core/src/gincoin-cli",  
    "VRSC":"~/VerusCoin/src/verus",   
}

for chain in other_launch:
    dpow[chain].update({"launch_params":other_launch[chain]})
for chain in other_conf:
    dpow[chain].update({"conf_path":other_conf[chain]})
for chain in other_cli:
    dpow[chain].update({"cli":other_cli[chain]})

r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/coins/master/coins")
coins_repo = r.json()

coins_info = {}
for item in coins_repo:
    coin = item['coin']
    mm2_compatible = 0
    if 'mm2' in item:
        mm2_compatible = item['mm2']
    logger.info("Getting info for ["+coin+"]")
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
        if r.text != "404: Not Found":
            logger.info("GET "+coin+" ELECTRUM ERROR: "+str(e)+" [RESPONSE]: "+r.text)
    try:
        coins_info[coin].update({"explorers":[]})
        r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/coins/master/explorers/"+coin)
        explorers = r.json()
        for item in explorers:
            coins_info[coin]['explorers'].append(item)
    except Exception as e:
        if r.text != "404: Not Found":
            logger.info("GET "+coin+" EXPLORER ERROR: "+str(e)+" [RESPONSE]: "+r.text)
    if coin in dpow:
        dpow_active = 1
        coins_info[coin].update({
                "dpow":dpow[coin]
            })
    else:
        dpow_active = 0
        coins_info[coin].update({"dpow":{}})
    row_data = (coin, json.dumps(coins_info[coin]["coins_info"]),
                json.dumps(coins_info[coin]['electrums']), json.dumps(coins_info[coin]['electrums_ssl']),
                json.dumps(coins_info[coin]['explorers']), json.dumps(coins_info[coin]['dpow']),
                dpow_active, mm2_compatible)
    table_lib.update_coins_tbl(conn, cursor, row_data)

for coin in dpow:
    if coin not in coins_info:
        print("Adding "+coin+" (in dpow, but not in coins repo)")
        row_data = (coin, json.dumps({}),
                    json.dumps([]), json.dumps([]),
                    json.dumps([]), json.dumps(dpow[coin]),
                    1, 0)
        table_lib.update_coins_tbl(conn, cursor, row_data)


logging.info("Finished!")
cursor.close()
conn.close()