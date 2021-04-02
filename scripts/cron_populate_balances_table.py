#!/usr/bin/env python3
import time
import math
import lib_electrum
import logging
import logging.handlers
from lib_notary import get_season
import threading
from lib_const import *
from models import balance_row, rewards_row
from lib_electrum import get_balance
from base_58 import get_addr_from_pubkey

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s',
                               datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

kmd_tiptime = RPC["KMD"].getinfo()['tiptime']


'''
This script checks notary balances for all dpow coins via electrum servers,
and any pending KMD rewards then stores data in db
It should be run as a cronjob every hour or so (takes about an 10 min to run).
'''

class electrum_thread(threading.Thread):
    def __init__(self, notary, chain, pubkey, addr, season):
        threading.Thread.__init__(self)
        self.notary = notary
        self.chain = chain
        self.pubkey = pubkey
        self.addr = addr
        self.season = season
    def run(self):
        thread_electrum(self.notary, self.chain, self.pubkey,
                        self.addr, self.season)

def thread_electrum(notary, chain, pubkey, addr, season):
    balance = balance_row()
    balance.notary = notary
    balance.chain = chain
    balance.pubkey = pubkey
    balance.address = addr
    balance.season = season
    balance.node = get_node(season)
    balance.balance = get_balance(balance.chain, balance.pubkey, balance.address, balance.notary, balance.node)

    if balance.balance != -1:
        balance.update()

def get_node(season):
    if season.find("Third_Party") != -1:
        return 'third party'
    else:
        return 'main'

def get_season_num(season):
    season = season.replace("Third_Party", "")
    season = season.replace("Testnet", "")
    return season

def get_kmd_rewards(season):
    nn_utxos = {}
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

def get_balances(this_season):
    thread_list = {}

    for season in NOTARY_PUBKEYS:

        # update only current season
        if season.find(this_season) != -1:

            for notary in NOTARY_PUBKEYS[season]:
                thread_list.update({notary:[]})

                for chain in NOTARY_ADDRESSES_DICT[season][notary]:
                    addr = NOTARY_ADDRESSES_DICT[season][notary][chain]
                    pubkey = NOTARY_PUBKEYS[season][notary]

                    check_bal = False
                    if chain == "KMD":
                        check_bal = True
                    elif season.find("Third_Party") != -1 and chain in THIRD_PARTY_COINS:
                        check_bal = True
                    elif  season.find("Third_Party") == -1 and chain not in THIRD_PARTY_COINS:
                        check_bal = True

                    if check_bal:
                        thread_list[notary].append(electrum_thread(notary, chain, pubkey, addr, season))

                for thread in thread_list[notary]:
                    thread.start()
                time.sleep(4) # 4 sec sleep = 15 min runtime.

season = get_season(int(time.time()))

get_balances(season)
get_kmd_rewards(season)

CURSOR.close()
CONN.close()
