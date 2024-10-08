#!/usr/bin/env python3.12
import requests

season = "Season_8"
url = "https://stats.kmd.io/api/wallet/notary_addresses/?season={season}"
data = requests.get(url).json()


for server in data[season]:
    balances_url = f"https://stats.kmd.io/api/table/balances/?season={season}&server={server}"
    balances_data = requests.get(balances_url).json()['results']
    for i in balances_data:
        coin = i['coin']
        nn = i['notary']
        balance = i['balance']
        if coin == "KMD":
            continue
        if coin == "LTC" and server == "Third_Party":
            continue
        print(f"{coin} ({server}) for [{nn}]: {balance}")
        if float(balance) < float("0.1000000") or coin == "CLC":
            pk = data[season][server][nn]['pubkey']
            if coin == "TOKEL":
                coin = "TKL"
            faucet_url = f"https://notaryfaucet.dragonhound.tools/faucet/{pk}/{coin}"
            print(requests.get(faucet_url).json())
            


            
        