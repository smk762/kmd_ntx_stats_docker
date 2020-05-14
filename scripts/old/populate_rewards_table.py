#!/usr/bin/env python3
import time
import math
import table_lib
import logging
import logging.handlers
from rpclib import def_credentials
from address_lib import known_addresses

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
rpc = def_credentials("KMD")

# ~/komodo/src/komodo-cli getaddressutxos '{"addresses": ["RRfUCLxfT5NMpxsC9GHVbdfVy5WJnJFQLV"]}'
conn = table_lib.connect_db()
cursor = conn.cursor()

KOMODO_ENDOFERA = 7777777
LOCKTIME_THRESHOLD = 500000000
MIN_SATOSHIS = 1000000000
ONE_MONTH_CAP_HARDFORK = 1000000
ONE_HOUR = 60
ONE_MONTH = 31 * 24 * 60
ONE_YEAR = 365 * 24 * 60
DEVISOR = 10512000

tiptime = rpc.getinfo()['tiptime']

nn_utxos = {}
for addr in known_addresses:
    utxos = rpc.getaddressutxos({"addresses": [addr]})
    notary = known_addresses[addr]
    utxo_count = len(utxos)
    update_time = int(time.time())
    nn_utxos.update({
        addr:{
            "notary":notary,
            "utxo_count": utxo_count,
            "eligible_utxos":{},
            "update_time": update_time
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
            locktime = rpc.getrawtransaction(utxo["txid"], 1)['locktime']
            coinage = math.floor((tiptime-locktime)/ONE_HOUR)
            if coinage >= ONE_HOUR and locktime >= LOCKTIME_THRESHOLD:
                limit = ONE_YEAR
                if utxo['height'] >= ONE_MONTH_CAP_HARDFORK:
                    limit = ONE_MONTH
                reward_period = min(coinage, limit) - 59
                rewards = math.floor(utxo['satoshis']/DEVISOR)*reward_period
                if rewards < 0:
                    logger.info("Rewards should never be negative!")
                nn_utxos[addr]['eligible_utxos'].update({
                    utxo['txid']:{
                        "locktime":locktime,
                        "sat_rewards":rewards,
                        "kmd_rewards":rewards/100000000,
                        "satoshis":utxo['satoshis'],
                        "block_height":utxo['height']
                    }
                })
                total_rewards += rewards/100000000
                #logger.info(nn_utxos[addr]['eligible_utxos'][txid])
    eligible_utxo_count = len(nn_utxos[addr]['eligible_utxos'])
    if oldest_utxo_block == 99999999999:
        oldest_utxo_block = 0
    nn_utxos[addr].update({
        "eligible_utxo_count":eligible_utxo_count,
        "oldest_utxo_block":oldest_utxo_block,
        "kmd_balance":balance,
        "total_rewards":total_rewards
    })
    utxo_txids = list(nn_utxos[addr]['eligible_utxos'].keys())
    logger.info(notary+": "+str(balance)+" KMD balance, "+str(total_rewards)+" rewards")
    logger.info("Oldest block: "+str(oldest_utxo_block))
    row_data = (addr, notary, utxo_count, eligible_utxo_count,
               oldest_utxo_block, balance, total_rewards,
               update_time)

    table_lib.update_rewards_tbl(conn, cursor, row_data)

cursor.close()

conn.close()