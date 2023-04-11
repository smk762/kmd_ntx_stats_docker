#!/usr/bin/env python3
import os
import time
import json
from decimal import *
from random import shuffle, choice
from datetime import datetime as dt
from filelock import Timeout, FileLock

import lib_api as api
import lib_validate
from lib_urls import *
from lib_const import *
from lib_update import *
from decorators import *
from lib_rpc import RPC
import lib_query
from lib_helper import get_pubkeys
from models import addresses_row, rewards_tx_row, kmd_supply_row
from lib_threads import update_notary_balances_thread


script_path = os.path.abspath(os.path.dirname(sys.argv[0]))


@print_runtime
def get_balances(season):
    dpow_main_coins = SEASONS_INFO[season]["servers"]["Main"]["coins"]
    if "Third_Party" in SEASONS_INFO[season]["servers"]:
        dpow_3p_coins = SEASONS_INFO[season]["servers"]["Third_Party"]["coins"]
    else:
        dpow_3p_coins = []

    if len(dpow_main_coins + dpow_3p_coins) > 0:
        thread_list = {}

        if season in NOTARY_PUBKEYS:
            address_data = requests.get(get_notary_addresses_url(season)).json()

            for server in address_data[season]:
                if season in SEASONS_INFO:
                    if server in SEASONS_INFO[season]["servers"]:

                        coins = SEASONS_INFO[season]["servers"][server]["coins"]
                        coins += ["BTC", "KMD", "LTC"]
                        coins.sort()
                        
                        for notary in SEASONS_INFO[season]["notaries"]:
                            thread_list.update({notary:[]})

                            for coin in coins:
                                if coin not in RETIRED_DPOW_COINS:
                                    address = address_data[season][server][notary]["addresses"][coin]
                                    pubkey = address_data[season][server][notary]["pubkey"]
                                    thread_list[notary].append(
                                                            update_notary_balances_thread(
                                                                season, server, notary,
                                                                coin, pubkey, address
                                                            )
                                                        )

                            for thread in thread_list[notary]:
                                thread.start()
                                time.sleep(0.2)
                            time.sleep(1) # 2 sec sleep = 8 min runtime.


def populate_addresses(season, server):
    if season in SEASONS_INFO:
        if server in SEASONS_INFO[season]["servers"]:
            coins = SEASONS_INFO[season]["servers"][server]["coins"]
            coins += ["BTC", "KMD", "LTC"]
            coins.sort()

            if len(coins) > 0:
                i = 0
                pubkeys = get_pubkeys(season, server)

                for notary in pubkeys:
                    pubkey = pubkeys[notary]

                    for coin in coins:
                        row = addresses_row()
                        row.season = season
                        row.server = server
                        row.coin = coin
                        row.notary_id = i
                        row.notary = notary
                        row.pubkey = pubkey
                        row.update()

                    i += 1

@print_runtime
def delete_stale_balances():
    logger.info(f"Removing stale data...")
    sql = f"DELETE FROM balances WHERE update_time < {int(time.time()-24*60*60)};"
    CURSOR.execute(sql)
    CONN.commit()


def update_supply_for_block(coin, blockheight):
    blocktime = RPC[coin].getblock(str(blockheight))["time"]
    logger.info(f"Getting supply for {blockheight} at {blocktime}...")
    data = RPC[coin].coinsupply(str(blockheight))
    total = data["total"]
    if blockheight > 1:
        last_data = RPC[coin].coinsupply(str(blockheight-1))
        last_total = last_data["total"]
        delta = total - last_total
    else:
        delta = total
    row = kmd_supply_row()
    row.block_height = blockheight
    row.block_time = blocktime
    row.total_supply = total
    row.delta = delta
    row.update()
    logger.info(f"Row for kmd block {blockheight} supply {total} added...")
    return

def update_supply(coin="KMD"):
    TIP = int(RPC[coin].getblockcount())
    existing_blocks = lib_query.get_supply_blocks()
    scan_blocks = list(set([*range(1, TIP, 1)]) - set(existing_blocks))
    scan_blocks.sort()
    for block in scan_blocks:
        print(block)
        update_supply_for_block(coin, block)


def import_rewards():
    existing_rewards_txids = lib_query.get_reward_txids()
    logger.info(f"Rewards txids in local DB: {len(existing_rewards_txids)}")
    url = get_rewards_txids_url()
    external_rewards_txids = requests.get(url).json()["results"]
    logger.info(f"Rewards txids in remote DB: {len(external_rewards_txids)}")
    txids_to_import = set(external_rewards_txids) - set(existing_rewards_txids)
    logger.info(f"Rewards txids to import: {len(txids_to_import)}")
    for txid in txids_to_import:
        url = url = get_rewards_txid_url(txid)
        data = requests.get(url).json()["results"]
        check_tx_for_rewards_info("KMD", txid)


def rescan_rewards_blocks(coin="KMD"):
    reward_blocks = lib_query.get_reward_blocks()
    reward_blocks.sort()
    reward_blocks.reverse()
    logger.info(f"Rescanning Blocks in DB: {len(reward_blocks)}")
    scan_blocks_for_rewards(reward_blocks, coin)


def scan_rewards(TIP, coin="KMD", rescan=False, ascending=False):

    file_path = f"{script_path}/scanned_blocks.json"
    lock_path = f"{script_path}/scanned_blocks.json.lock"
    lock = FileLock(lock_path, timeout=10)
    with lock:
        try:
            with open(f"{script_path}/scanned_blocks.json", "r") as j:
                scanned_blocks = json.load(j)
        except Exception as e:
            logger.warning(f"error getting scanned blocks json: {e}")
            scanned_blocks = {}
    if "scanned_blocks" not in scanned_blocks: scanned_blocks.update({"scanned_blocks": []})

    logger.info(f"Previously Scanned Blocks: {len(scanned_blocks['scanned_blocks'])}")
    reward_blocks = lib_query.get_reward_blocks()
    logger.info(f"Blocks in DB: {len(reward_blocks)}")
    scan_blocks = list(set([*range(1, TIP)]) - set(reward_blocks) - set(scanned_blocks['scanned_blocks']))
    logger.info(f"Blocks left to scan: {len(scan_blocks)}")
    scan_blocks.sort()
    if not ascending:
        scan_blocks.reverse()
    chunksize = 1500
    if len(scanned_blocks['scanned_blocks']) == 0:
        chunksize = 50
    if rescan:
        chunk_starts_at = choice(range(len(scan_blocks)))
        scan_blocks = scan_blocks[chunk_starts_at:chunk_starts_at+chunksize]
    else:
        scan_blocks = scan_blocks[:chunksize]
    
    logger.info(f"Scanning these blocks now: {scan_blocks}")
    new_scanned_blocks = scan_blocks_for_rewards(scan_blocks, coin)


    with lock:
        with open(f"{script_path}/scanned_blocks.json", "r") as j:
            scanned_blocks = json.load(j) 
            scanned_blocks["scanned_blocks"].extend(new_scanned_blocks)
            scanned_blocks["scanned_blocks"] = list(set(scanned_blocks["scanned_blocks"]))

        scanned_blocks["scanned_blocks"].sort()

        with open(file_path, "w+") as j:
            json.dump(scanned_blocks, j, indent=4)


def scan_blocks_for_rewards(scan_blocks, coin="KMD"):
    file_path = f"{script_path}/prices_history.json"
    lock_path = f"{script_path}/prices_history.json.lock"
    lock = FileLock(lock_path, timeout=10)

    with lock:
        try:
            with open(f"{script_path}/prices_history.json", "r") as j:
                prices = json.load(j)
        except Exception as e:
            logger.warning(f"error getting prices json: {e}")
            prices = {}

    review_blocks = []
    new_scanned_blocks = []

    for block_height in scan_blocks:
        block = RPC[coin].getblock(str(block_height))
        block_time = block["time"]
        season = lib_validate.get_season(block_time)
        date = str(dt.utcfromtimestamp(block_time)).split(" ")[0]
        date = f"{date}".split("-")
        date.reverse()
        date = "-".join(date)
        logger.info(f"Block Height: {block_height} at {date}")

        if season not in prices:
            prices.update({season: {}})

        if f"{date}" not in prices[season]:
            prices[season].update({f"{date}": {}})

        if 'btc' not in prices[season][f"{date}"]:
            update_prices(season, date, prices)
        elif prices[season][f"{date}"]["btc"] == 0:
            update_prices(season, date, prices)


        for txid in block["tx"]:
            check_tx_for_rewards_info(coin, txid, block, prices)

        if block_height not in review_blocks:
            new_scanned_blocks.append(block_height)

    logger.info("[scan_rewards] Finished!")
    return new_scanned_blocks

def update_prices(season, date, prices):
    api_prices = api.get_kmd_price(date)
    if api_prices:
        prices[season][f"{date}"].update(api_prices)

        file_path = f"{script_path}/prices_history.json"
        lock_path = f"{script_path}/prices_history.json.lock"
        lock = FileLock(lock_path, timeout=10)

        with lock:
            with open(file_path, "w+") as j:
                json.dump(prices, j, indent=4)

    else:
        prices[season][f"{date}"].update({"btc":0,"usd":0})
    return prices


def check_tx_for_rewards_info(coin, txid, block=None, prices=None):
    # logger.info(f"Checking {txid} for rewards...")
    tx_data = RPC[coin].getrawtransaction(txid, 1)
    if not block:
        if "blocktime" in tx_data:
            block_hash = tx_data["blockhash"]
            block_time = tx_data["blocktime"]
            block_height = tx_data["height"]
        else:
            # logger.info(f"txid {txid} is unconfirmed...")
            return
    else:
        block_hash = block["hash"]
        block_time = block["time"]
        block_height = block["height"]
    season = lib_validate.get_season(block_time)
    date = str(dt.utcfromtimestamp(block_time)).split(" ")[0]
    date = f"{date}".split("-")
    date.reverse()
    date = "-".join(date)      
    sum_of_inputs = 0
    sum_of_outputs = 0
    rewards_value = 0

    if not prices:

        file_path = f"{script_path}/prices_history.json"
        lock_path = f"{script_path}/prices_history.json.lock"
        lock = FileLock(lock_path, timeout=10)
        with lock:
            try:
                with open(f"{script_path}/prices_history.json", "r") as j:
                    prices = json.load(j)
            except Exception as e:
                logger.warning(e)
                prices = {}

            if season not in prices:
                prices.update({season: {}})

            if f"{date}" not in prices[season]:
                prices[season].update({f"{date}": {}})

            if 'btc' not in prices[season][f"{date}"]:
                api_prices = api.get_kmd_price(date)
                if api_prices:
                    prices[season][f"{date}"].update(api_prices)

                    with open(file_path, "w+") as j:
                        json.dump(prices, j, indent=4)

                    time.sleep(1)
                else:
                    prices[season][f"{date}"].update({"btc":0,"usd":0})


    output_addresses = []
    address_inputs = {}

    for vin in tx_data["vin"]:
        coinbase = False

        # We can include coinbase tx, but need another coumn to tag them
        if "coinbase" in vin:
            coinbase = True
            # logger.info(f"{txid} is a coinbase tx, skipping...")
            return            

        if "value" in vin:
            sum_of_inputs += float(vin["value"])
            if vin["address"] not in address_inputs:
                address_inputs.update({vin["address"]:0})

            address_inputs[vin["address"]] += float(vin["value"])

    input_addresses = list(address_inputs.keys())
    for vout in tx_data["vout"]:
        sum_of_outputs += float(vout["value"])

        if "scriptPubKey" in vout:
            if "addresses" in vout["scriptPubKey"]:
                output_addresses = vout["scriptPubKey"]["addresses"]

    for address in output_addresses:
        if address in input_addresses:

            # If coinbase, anything over 3 is an unclaimed reward, gained by miner.
            if coinbase:
                rewards_value = sum_of_outputs - 3
            elif len(output_addresses) == 1  and len(input_addresses) == 1 and output_addresses[0] == input_addresses[0]:
                rewards_value = float(vout["value"]) - address_inputs[address]
            else:
                rewards_value = sum_of_outputs - sum_of_inputs
                outputs_in_inputs = list(set(output_addresses).intersection(set(input_addresses)))
                address = outputs_in_inputs[-1]

            if rewards_value > 0:
                row = rewards_tx_row()
                row.txid = txid
                row.block_hash = block["hash"]
                row.block_height = block_height
                row.block_time = block_time
                row.sum_of_inputs = sum_of_inputs
                row.address = address
                row.sum_of_outputs = sum_of_outputs
                row.rewards_value = rewards_value
                row.usd_price = Decimal(prices[season][date]['usd'])
                row.btc_price = Decimal(prices[season][date]['btc'])
                row.update()
                logger.info(f"Row for {txid} rewards added...")
                return
    # logger.info(f"No rewards for {txid}...")



def populate_prices(table, date_field, timestamp=False):
    try:
        with open(f"{script_path}/prices_history.json", "r") as j:
            prices = json.load(j)
    except Exception as e:
        logger.warning(e)
        prices = {}

    for season in prices:
        for day in prices[season]:
            if 'btc' in prices[season][day]:
                btc_price = prices[season][day]["btc"]
                usd_price = prices[season][day]["usd"]
                update_table_prices(table, date_field, day, btc_price, usd_price, timestamp)


if __name__ == "__main__":

    populate_prices('mined', 'block_time', True)
    populate_prices('mined_count_daily', 'mined_date')
    populate_prices('rewards_tx', 'block_time', True)
            
