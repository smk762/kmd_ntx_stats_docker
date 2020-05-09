#!/usr/bin/env python3
import requests
from coins_lib import all_coins

r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/coins/master/coins")
coins_repo = r.json()

coins_info = {}
for item in coins_repo:
    coin = item['coin']
    if coin in all_coins:
        print("Getting info for ["+coin+"]")
        coins_info.update({coin:{}})
        for k,v in item.items():
            if k != 'coin':
                coins_info[coin].update({k:v})
        try:
            r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/coins/master/electrums/"+coin)
            electrums = r.json()
            coins_info[coin].update({"electrums":[]})
            coins_info[coin].update({"electrums_ssl":[]})
            for item in electrums:
                if "protocol" in item:
                    if item['protocol'] == "SSL":
                        coins_info[coin]['electrums_ssl'].append(item['url'])
                    else:
                        coins_info[coin]['electrums'].append(item['url'])
                else:
                    coins_info[coin]['electrums'].append(item['url'])
        except Exception as e:
            print("GET "+coin+" ELECTRUM ERROR: "+str(e)+" [RESPONSE]: "+r.text)
        try:
            r = requests.get("https://raw.githubusercontent.com/KomodoPlatform/coins/master/explorers/"+coin)
            explorers = r.json()
            coins_info[coin].update({"explorers":[]})
            for item in explorers:
                coins_info[coin]['explorers'].append(item)
        except Exception as e:
            print("GET "+coin+" EXPLORER ERROR: "+str(e)+" [RESPONSE]: "+r.text)
print(coins_info)


