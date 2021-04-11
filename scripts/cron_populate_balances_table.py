#!/usr/bin/env python3
import time
import math
import lib_electrum
from lib_notary import get_season
import threading
from lib_const import *
from lib_table_select import get_notarised_seasons, get_notarised_servers, get_notarised_chains
from models import balance_row, rewards_row
from lib_electrum import get_balance
from base_58 import get_addr_from_pubkey

'''
This script checks notary balances for all dpow coins via electrum servers,
and any pending KMD rewards then stores data in db
It should be run as a cronjob every hour or so (takes about an 10 min to run).
'''

class electrum_thread(threading.Thread):
    def __init__(self, season, server, notary, coin, pubkey, address):
        threading.Thread.__init__(self)
        self.season = season
        self.server = server
        self.notary = notary
        self.chain = coin
        self.pubkey = pubkey
        self.address = address
    def run(self):
        thread_electrum(self.season, self.server, self.notary, self.chain, self.pubkey, self.address)

def thread_electrum(season, server, notary, coin, pubkey, address):
    balance = balance_row()
    balance.season = season
    balance.server = server
    balance.notary = notary
    balance.chain = coin
    balance.pubkey = pubkey
    balance.address = address

    balance.balance = get_balance(balance.chain, balance.pubkey, balance.address, balance.server)

    if balance.balance != -1:
        balance.update()

def get_balances(season):
    season_coins = requests.get(f'{THIS_SERVER}/api/info/dpow_server_coins?season={season}').json()

    if len(season_coins) > 0:
        thread_list = {}

        for pubkey_season in NOTARY_PUBKEYS:

            if pubkey_season.find(season) != -1:
                address_data = requests.get(f'{THIS_SERVER}/api/wallet/notary_addresses?season={season}').json()

                if pubkey_season.find("Third_Party") != -1:
                    coins = season_coins["Third_Party"][:]
                    server = "Third_Party"

                else:
                    coins = season_coins["Main"][:]
                    server = "Main"

                coins += ["BTC", "KMD", "LTC"]
                coins.sort()
                
                for notary in NOTARY_PUBKEYS[pubkey_season]:
                    thread_list.update({notary:[]})

                    for coin in coins:
                        
                        address = address_data[season][server][notary]["addresses"][coin]
                        pubkey = address_data[season][server][notary]["pubkey"]
                        thread_list[notary].append(electrum_thread(season, server, notary, coin, pubkey, address))

                    for thread in thread_list[notary]:
                        thread.start()
                time.sleep(4) # 4 sec sleep = 15 min runtime.

def get_kmd_rewards(season):
    nn_utxos = {}
    kmd_tiptime = RPC["KMD"].getinfo()['tiptime']
    for notary in NOTARY_PUBKEYS[season]:
        rewards = rewards_row()
        rewards.addr = get_addr_from_pubkey("KMD", NOTARY_PUBKEYS[season][notary])
        rewards.notary = notary
        utxos = RPC["KMD"].getaddressutxos({"addresses": [rewards.addr]})
        rewards.utxo_count = len(utxos)

        nn_utxos.update({
            rewards.addr:{
                "notary":notary,
                "utxo_count": rewards.utxo_count,
                "eligible_utxos":{}
            }
        })
        total_rewards = 0
        balance = 0
        oldest_utxo_block = 99999999999
        for utxo in utxos:
            balance += utxo['satoshis']/100000000
            if utxo['height'] < oldest_utxo_block:
                oldest_utxo_block = utxo['height']
            if utxo['height'] < KOMODO_ENDOFERA and utxo['satoshis'] >= MIN_SATOSHIS:
                try:
                    locktime = RPC["KMD"].getrawtransaction(utxo["txid"], 1)['locktime']
                    coinage = math.floor((kmd_tiptime-locktime)/ONE_HOUR)
                    if coinage >= ONE_HOUR and locktime >= LOCKTIME_THRESHOLD:
                        limit = ONE_YEAR
                        if utxo['height'] >= ONE_MONTH_CAP_HARDFORK:
                            limit = ONE_MONTH
                        reward_period = min(coinage, limit) - 59
                        utxo_rewards = math.floor(utxo['satoshis']/DEVISOR)*reward_period
                        if utxo_rewards < 0:
                            logger.info("Rewards should never be negative!")
                        nn_utxos[rewards.addr]['eligible_utxos'].update({
                            utxo['txid']:{
                                "locktime":locktime,
                                "sat_rewards":utxo_rewards,
                                "kmd_rewards":utxo_rewards/100000000,
                                "satoshis":utxo['satoshis'],
                                "block_height":utxo['height']
                            }
                        })
                        total_rewards += utxo_rewards/100000000
                except:
                    pass
        eligible_utxo_count = len(nn_utxos[rewards.addr]['eligible_utxos'])
        if oldest_utxo_block == 99999999999:
            oldest_utxo_block = 0
        nn_utxos[rewards.addr].update({
            "eligible_utxo_count":eligible_utxo_count,
            "oldest_utxo_block":oldest_utxo_block,
            "kmd_balance":balance,
            "total_rewards":total_rewards
        })

        rewards.eligible_utxo_count = eligible_utxo_count
        rewards.oldest_utxo_block = oldest_utxo_block
        rewards.balance = balance
        rewards.total_rewards = total_rewards

        rewards.update()

if __name__ == "__main__":

    logger.info(f"Preparing to populate [balances] table...")


    logger.info(f"Removing stale data...")
    CURSOR.execute(f"DELETE FROM balances WHERE update_time < {time.time()-24*60*60};")
    CURSOR.execute(f"DELETE FROM balances;")
    CONN.commit()

    for season in SEASONS_INFO:
        if season in EXCLUDED_SEASONS:
            logger.warning(f"Skipping season: {season}")
        else:
            get_balances(season)
            get_kmd_rewards(season)
