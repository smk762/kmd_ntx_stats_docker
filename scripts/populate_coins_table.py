#!/usr/bin/env python3
import json
import requests
import logging
import logging.handlers
from notary_lib import *

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


conn = connect_db()
cursor = conn.cursor()

# Uncomment if need to clear table
# cursor.execute("DELETE FROM coins WHERE dpow_active = 1;")
# conn.commit()

dpow_coins = get_dpow_coins()
third_party_coins = []
antara_coins = []
other_coins = []

for item in dpow_coins:
    if item[6]['server'] == 'dpow-mainnet':
        if item[1] not in ['KMD', 'BTC']:
            antara_coins.append(item[1])
    elif item[6]['server'] == 'dpow-3p':
        third_party_coins.append(item[1])
    else:
        other_coins.append(item[1])

                   
before_coins = antara_coins + third_party_coins + other_coins + ['BTC', 'KMD']

dpow = {}
dpow_main = []
dpow_3p = []
r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/dPoW/master/README.md")
dpow_readme = r.text
lines = dpow_readme.splitlines()
for line in lines:
    raw_info = line.split("|")
    info = [i.strip() for i in raw_info]
    if len(info) > 4 and info[0].lower() not in ['coin', '--------', 'game']:
        coin = info[0]
        logger.info("Adding "+coin+" to dpow")
        try:
            src = info[1].split("(")[1].replace(")","")
        except:
            src = info[1]
        version = info[2]
        server = info[4].lower()
        if server == "dpow-mainnet":
            dpow_main.append(coin)
        elif server == "dpow-3p":
            dpow_3p.append(coin)
        dpow.update({
            coin:{
                "src":src,
                "version":version,
                "server":server            
            }
        })

now_coins = list(dpow.keys())
print(before_coins)
print(now_coins)
for coin in before_coins:
    if coin not in now_coins:
        print("Removing "+coin+" from dpow")
        cursor.execute("DELETE FROM coins WHERE chain = '"+coin+"';")
        conn.commit()



r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/komodo/dev/src/assetchains.json")
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
    "VRSC":"~/VerusCoin/src/verus",   
}

for chain in other_launch:
    if chain in dpow:
        dpow[chain].update({"launch_params":other_launch[chain]})
for chain in other_conf:
    if chain in dpow:
        dpow[chain].update({"conf_path":other_conf[chain]})
for chain in other_cli:
    if chain in dpow:
        dpow[chain].update({"cli":other_cli[chain]})

r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/coins/master/coins")
coins_repo = r.json()

# Some coins are named differently between dpow and coins repo...
translate_coins = { 'COQUI':'COQUICASH','HUSH':'HUSH3','OURC':'OUR','WLC':'WLC21' }

coins_info = {}
for item in coins_repo:
    coin = item['coin']
    if coin in translate_coins:
        coin = translate_coins[coin]
    coins_info.update({coin:{"coins_info":item}})
    coins_info[coin].update({"electrums":[]})
    coins_info[coin].update({"electrums_ssl":[]})
    mm2_compatible = 0
    if 'mm2' in item:
        mm2_compatible = item['mm2']
    logger.info("Getting info for ["+coin+"]")

    try:
        if coin in ['COQUICASH', 'HUSH3', 'WLC21', 'OUR']:
            r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/coins/master/electrums/"+item['coin'])
        else:
            r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/coins/master/electrums/"+coin)
        electrums = r.json()
        for electrum in electrums:
            if "protocol" in electrum:
                if electrum['protocol'] == "SSL":
                    coins_info[coin]['electrums_ssl'].append(electrum['url'])
                else:
                    coins_info[coin]['electrums'].append(electrum['url'])
            else:
                coins_info[coin]['electrums'].append(electrum['url'])
    except Exception as e:
        if r.text != "404: Not Found":
            logger.info("GET "+coin+" ELECTRUM ERROR: "+str(e)+" [RESPONSE]: "+r.text)

    try:
        coins_info[coin].update({"explorers":[]})
        if coin in ['COQUICASH', 'HUSH3', 'WLC21', 'OUR']:
            r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/coins/master/explorers/"+item['coin'])
        else:
            r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/coins/master/explorers/"+coin)
        explorers = r.json()
        for explorer in explorers:
            coins_info[coin]['explorers'].append(explorer)
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
    update_coins_tbl(conn, cursor, row_data)

# This is to cover coins with explorer/electrum but not in "coins" file

no_electrums = []
no_explorers = []
for coin in dpow:
    if coin not in coins_info:
        print("Adding "+coin+" (in dpow, but not in coins repo)")
        if coin in translate_coins:
            coin = translate_coins[coin]
        coins_info.update({coin:{"coins_info":item}})
        coins_info[coin].update({"electrums":[]})
        coins_info[coin].update({"electrums_ssl":[]})
        try:
            if coin in ['COQUICASH', 'HUSH3', 'WLC21', 'OUR']:
                r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/coins/master/electrums/"+item['coin'])
            else:
                r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/coins/master/electrums/"+coin)
            electrums = r.json()
            for electrum in electrums:
                if "protocol" in electrum:
                    if electrum['protocol'] == "SSL":
                        coins_info[coin]['electrums_ssl'].append(electrum['url'])
                    else:
                        coins_info[coin]['electrums'].append(electrum['url'])
                else:
                    coins_info[coin]['electrums'].append(electrum['url'])
        except Exception as e:
            if r.text != "404: Not Found":
                logger.info("GET "+coin+" ELECTRUM ERROR: "+str(e)+" [RESPONSE]: "+r.text)

        try:
            coins_info[coin].update({"explorers":[]})
            if coin in ['COQUICASH', 'HUSH3', 'WLC21', 'OUR']:
                r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/coins/master/explorers/"+item['coin'])
            else:
                r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/coins/master/explorers/"+coin)
            explorers = r.json()
            for explorer in explorers:
                coins_info[coin]['explorers'].append(explorer)
        except Exception as e:
            if r.text != "404: Not Found":
                logger.info("GET "+coin+" EXPLORER ERROR: "+str(e)+" [RESPONSE]: "+r.text)

        if coin in dpow:
            dpow_active = 1
            coins_info[coin].update({
                    "dpow":dpow[coin]
                })


        row_data = (coin, json.dumps({}),
                    json.dumps(coins_info[coin]['electrums']), json.dumps(coins_info[coin]['electrums_ssl']),
                    json.dumps(coins_info[coin]['explorers']), json.dumps(coins_info[coin]['dpow']),
                    1, 0)
        update_coins_tbl(conn, cursor, row_data)
        if len(coins_info[coin]['electrums']) == 0:
            no_electrums.append(coin)
        if len(coins_info[coin]['explorers']) == 0:
            no_explorers.append(coin)

print("no_electrums: "+str(no_electrums))
print("no_explorers: "+str(no_explorers))
print("dpow_main: "+str(len(dpow_main)))
print("dpow_main: "+str(dpow_main))
print("dpow_3p: "+str(len(dpow_3p)))
print("dpow_3p: "+str(dpow_3p))
logging.info("Finished!")
cursor.close()
conn.close()