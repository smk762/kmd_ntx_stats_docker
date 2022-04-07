#!/usr/bin/env python3
import time
import json
from lib_const import *
from decorators import *
from lib_urls import *
from models import addresses_row, rewards_tx_row
from lib_helper import get_pubkeys
from lib_threads import update_notary_balances_thread


@print_runtime
def get_balances(season):
    dpow_main_coins = SEASONS_INFO[season]["servers"]["Main"]["coins"]
    dpow_3p_coins = SEASONS_INFO[season]["servers"]["Third_Party"]["coins"]

    if len(dpow_main_coins + dpow_3p_coins) > 0:
        thread_list = {}

        for pubkey_season in NOTARY_PUBKEYS:

            if pubkey_season.find(season) != -1:
                address_data = requests.get(get_notary_addresses_url(season)).json()

                if pubkey_season.find("Third_Party") != -1:
                    coins = dpow_3p_coins
                    server = "Third_Party"

                else:
                    coins = dpow_main_coins
                    server = "Main"

                coins += ["BTC", "KMD", "LTC"]
                coins.sort()
                
                for notary in SEASONS_INFO[pubkey_season]["notaries"]:
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
                row.chain = coin
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


def get_rewards_tx_data(block_height, coin="KMD"):
    block = RPC[coin].getblock(str(block_height))
    for txid in block["tx"]:
        tx_data = RPC[coin].getrawtransaction(txid, 1)
        sum_of_inputs = 0
        sum_of_outputs = 0
        input_addresses = []
        output_addresses = []
        input_utxos = []
        output_utxos = []

        for vin in tx_data["vin"]:
            if "value" in vin:
                sum_of_inputs += float(vin["value"])
                input_addresses.append(vin["address"])
                input_utxos.append(f"{vin['txid']}:{vin['vout']}")

            elif "coinbase" in vin:
                input_addresses.append("coinbase")
                break

        for vout in tx_data["vout"]:
            sum_of_outputs += float(vout["value"])

            if "scriptPubKey" in vout:
                if "addresses" in vout["scriptPubKey"]:
                    output_addresses = vout["scriptPubKey"]["addresses"]
            output_utxos.append(f"{txid}:{vout['n']}")

        if sum_of_inputs == 0:
            rewards_value = sum_of_outputs - 3
        else:
            rewards_value = sum_of_outputs - sum_of_inputs

        if rewards_value > 0:
            row = rewards_tx_row()
            row.txid = txid
            row.block_hash = block["hash"]
            row.block_height = block_height
            row.block_time = block["time"]
            row.sum_of_inputs = sum_of_inputs
            row.input_addresses = input_addresses
            row.input_utxos = input_utxos
            row.sum_of_outputs = sum_of_outputs
            row.output_addresses = output_addresses
            row.output_utxos = output_utxos
            row.rewards_value = rewards_value
            row.update()