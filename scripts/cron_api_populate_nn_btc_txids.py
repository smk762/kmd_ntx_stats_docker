#!/usr/bin/env python3
import os
import sys
import json
import time
import logging
import logging.handlers
import psycopg2
import requests
import threading
from decimal import *
from datetime import datetime as dt
import datetime
import dateutil.parser as dp
from dotenv import load_dotenv
from lib_rpc import def_credentials
from lib_electrum import get_ac_block_info
from lib_const import *
from lib_notary import *
from lib_table_update import *
from lib_table_select import *
from lib_api import *

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

load_dotenv()

#txids = ['257391b419292dc24c6c762535b82bdcc9212bf187bb60a1d322dbc3e3709c18'] # KNOWN NTX 
#txids = ['e5f3f5519f48336d3aa6c01dea361a7e703570cea7d4a201610c6df2cc97db5b'] # KNOWN SPLIT 
#txids = ['03402cc2f09e22d90fb9853db14a71ace0f00eb48646387d6ed89ec7bb7254df'] # KNOWN REPLENISH FROM dragonhound_NA
#txids = ['c8dbc9e3af7f5a1d8f910ff03e390a8782a911bc34fc567c27c711e9da191894'] # KNOWN REPLENISH FROM Replenish Addr
#txids = ['03402cc2f09e22d90fb9853db14a71ace0f00eb48646387d6ed89ec7bb7254df', '6a458e37a6b101433cc60e28ccfb8335a29ea3a80e76b69d32f4806f3fb9f040'] # KNOWN REPLENISH FROM Replenish Addr
#txids = ['03402cc2f09e22d90fb9853db14a71ace0f00eb48646387d6ed89ec7bb7254df', '6a458e37a6b101433cc60e28ccfb8335a29ea3a80e76b69d32f4806f3fb9f040', 'c8dbc9e3af7f5a1d8f910ff03e390a8782a911bc34fc567c27c711e9da191894'] # KNOWN REPLENISH FROM Replenish Addr

# set this to True in .env to quickly update tables with most recent data
skip_until_yesterday = (os.getenv("skip_until_yesterday") == 'True')

other_server = os.getenv("other_server")

conn = connect_db()
cursor = conn.cursor()

def get_linked_addresses(addr=None, notary=None):
    linked_addresses = {}
    sql = f"SELECT DISTINCT address, notary from nn_btc_tx"
    conditions = [f"address='{addr}'"]
    if notary:
        conditions = [f"notary = '{notary}' or notary = '{notary} (linked)'"]

    if len(conditions) > 0:
        sql += " where "
        sql += " and ".join(conditions)    
    sql += ";"

    cursor.execute(sql)
    address_rows = cursor.fetchall()

    if len(address_rows) > 0:

        for row in address_rows:
            address = row[0]
            notary = row[1].replace(" (linked)", "")

            if notary in ALL_SEASON_NOTARIES:

                if notary not in linked_addresses:
                    linked_addresses.update({notary:[address]})

                else:
                    linked_addresses[notary].append(address)

    return linked_addresses

def is_linked_address(addr, notary=None):
    linked_addresses = get_linked_addresses(addr, notary)
    if len(linked_addresses) > 0:
        return True
    else:
        return False

def is_notary_address(addr):
    if addr in ALL_SEASON_NOTARY_BTC_ADDRESSES:
        return True
    return False


def detect_replenish(vins, vouts):

    vin_notaries = []
    vin_non_notary_addresses = []
    for vin in vins:
        address = vin["addresses"][0]
        if is_notary_address(address):
            notary = ALL_SEASON_NN_BTC_ADDRESSES_DICT[address]
            vin_notaries.append(notary)
        elif is_linked_address(address, "dragonhound_NA"):
            notary = "dragonhound_NA"
            vin_notaries.append(notary)
        else:
            vin_non_notary_addresses.append(address)
    
    replenish_vin = False
    if len(list(set(vin_notaries))) == 1:
        if vin_notaries[0] == "dragonhound_NA":
            replenish_vin = True

    vout_notaries = []
    vout_non_notary_addresses = []
    for vout in vouts:
        sats = vout["value"]
        address = vout["addresses"][0]
        if is_notary_address(address):
            if sats >= 1000000:
                notary = ALL_SEASON_NN_BTC_ADDRESSES_DICT[address]
                if notary != "dragonhound_NA":
                    vout_notaries.append(notary)
        elif not is_linked_address(address):
            vout_non_notary_addresses.append(address)

    replenish_vout = False
    if len(vout_notaries) > 0:
        replenish_vout = True

    if replenish_vin and replenish_vout:
        for addr in vin_non_notary_addresses:
            update_nn_btc_tx_notary_from_addr(conn, cursor, "dragonhound_NA (linked)", addr)
        for addr in vout_non_notary_addresses:
            update_nn_btc_tx_notary_from_addr(conn, cursor, "dragonhound_NA (linked)", addr)
        return True
    return False

def detect_consolidate(vins, vouts):
    vin_notaries = []
    vin_non_notary_addresses = []
    for vin in vins:
        address = vin["addresses"][0]
        if is_notary_address(address):
            notary = ALL_SEASON_NN_BTC_ADDRESSES_DICT[address]
            vin_notaries.append(notary)
        else:
            vin_non_notary_addresses.append(address)

    if len(list(set(vin_notaries))) == 1:
        notary = vin_notaries[0]

        vout_notaries = []
        vout_non_notary_addresses = []
        for vout in vouts:
            address = vout["addresses"][0]
            if is_notary_address(address):
                notary = ALL_SEASON_NN_BTC_ADDRESSES_DICT[address]
                vout_notaries.append(notary)
            else:
                vout_non_notary_addresses.append(address)

        if len(list(set(vout_notaries))) == 1:
            if notary == vout_notaries[0]:
                for addr in vin_non_notary_addresses:
                    update_nn_btc_tx_notary_from_addr(conn, cursor, f"{notary} (linked)", addr)
                for addr in vout_non_notary_addresses:
                    update_nn_btc_tx_notary_from_addr(conn, cursor, f"{notary} (linked)", addr)
                return True

    return False

season = "Season_4"
i = 0
num_addr = len(NOTARY_BTC_ADDRESSES[season])

for notary_address in NOTARY_BTC_ADDRESSES[season]:
    i += 1

    if notary_address in NN_BTC_ADDRESSES_DICT[season]:
        notary_name = NN_BTC_ADDRESSES_DICT[season][notary_address]
    else:
        notary_name = "non-NN"

    existing_txids = get_existing_nn_btc_txids(cursor, notary_address)
    txids = get_new_nn_btc_txids(existing_txids, notary_address)

    logger.info(f"{len(existing_txids)} EXIST IN DB FOR {notary_address} | {notary_name} {season} ({i}/{num_addr})")
    logger.info(f"{len(txids)} NEW TXIDs TO PROCESS FOR {notary_address} | {notary_name} {season} ({i}/{num_addr})")

    num_txids = len(txids)

    for txid in txids:
        # Get tx data from Blockcypher API
        tx_info = get_btc_tx_info(txid)

        if 'fees' in tx_info:
            txid_data = tx_row()
            txid_data.txid = txid
            txid_data.address = notary_address
            txid_data.fees = tx_info['fees']

            txid_data.num_inputs = tx_info['vin_sz']
            txid_data.num_outputs = tx_info['vout_sz']

            txid_data.block_hash = tx_info['block_hash']
            txid_data.block_height = tx_info['block_height']

            block_time_iso8601 = tx_info['confirmed']
            parsed_time = dp.parse(block_time_iso8601)
            txid_data.block_time = parsed_time.strftime('%s')
            txid_data.block_datetime = dt.utcfromtimestamp(int(txid_data.block_time))

            addresses = tx_info['addresses']
            txid_data.season = get_season_from_btc_addresses(addresses[:], txid_data.block_time)

            vouts = tx_info["outputs"]
            vins = tx_info["inputs"]


            ## CATEGORIES ##
            # SPAM index/outputs = 0
            # NTX
            # SPLIT index/outputs = -99
            # CONSOLIDATE (Add Later)
            #   - vins from notary or linked address, to same notary or linked address. If single non-NN vout, tag as NN-linked.
            #   - Could be confused with REPLENISH, make sure no other notaries involved.
            # REPLENISH (Add Later)
            #   - large sat value (0.01 BTC or higher) to multiple notaries, generally from dragonhound or dragonhound linked address. Single non-NN vout, tag as dragonhound linked.
            #   - very large sat value to dragonhound (0.4 BTC or higher). tag vins as REPLENISH SOURCE.
            # OTHER (FALL BACK)

            # single row for memo.sv spam
            if '1See1xxxx1memo1xxxxxxxxxxxxxBuhPF' in addresses:
                txid_data.input_sats = 0
                txid_data.output_sats = 0
                txid_data.input_index = 0
                txid_data.output_index = 0
                txid_data.category = "SPAM"
                txid_data.update()

            # Detect NTX
            elif BTC_NTX_ADDR in addresses and len(vins) == 13 and len(vouts) == 2:
                txid_data.category = "NTX"
                input_index = 0
                for vin in vins:
                    txid_data.output_sats = -1
                    txid_data.output_index = -1
                    txid_data.input_sats = vin['output_value']
                    txid_data.input_index = input_index
                    txid_data.address = vin["addresses"][0]
                    txid_data.notary = get_notary_from_btc_address(txid_data.address, txid_data.season)
                    txid_data.update()
                    input_index += 1

                output_index = 0
                for vout in vouts:
                    if vout["addresses"] is not None:
                        txid_data.input_index = -1
                        txid_data.input_sats = -1
                        txid_data.output_sats = vout['value']
                        txid_data.output_index = output_index
                        txid_data.address = vout["addresses"][0]
                        txid_data.notary = "BTC_NTX_ADDR"
                        txid_data.update()
                        output_index += 1

            # Detect Split (single row only)
            elif len(addresses) == 1:
                txid_data.category = "Split"
                txid_data.input_sats = -99
                txid_data.output_sats = -99
                txid_data.input_index = -99
                txid_data.output_index = -99
                txid_data.address = addresses[0]
                txid_data.notary = get_notary_from_btc_address(txid_data.address, txid_data.season)
                txid_data.update()

            else:
                if txid in ["9d29730c09f7d1983a413a14bb0b8ffcf0cb652472a428e97c250da03ae47082", "9bc103a16c477d55ba42e4fc97a6256e04813e9b947c895c6cd0e2f028bdfa67"] :
                    txid_data.category = "MadMax personal top up"
                elif txid == "248ef589d50047a43d987f6af05ab8568f5a2070e25c3e1d3b063884948634ee":
                    txid_data.category = "MadMax personal top up repaid"
                elif txid in [
                    "e4b2e4afa20b7cf39e96422bb72a522e0cb9fc49dbd4cfa5386b3733833365aa",
                    "5d93f75414d6c581e8589339fe1915437a01b0e8ee4149a5fea508a080b1815e",
                    "535bac3813dd0e36db503dbeef916f8e1198386a5909b1b7142a5984e91309c5",
                    "f18186cd8a05f2a5148694ccbf95c4230b4b63183d835c9d88fed15b16c1db7d",
                    "8737a7bb20e9f33e2c46a1c5d93b11d2c64f04e1cab4655eeb314e8e93f84ec6"
                    ]:
                    txid_data.category = "previous season funds transfer"
                elif detect_replenish(vins, vouts):
                    txid_data.category = "Replenish"
                    input_index = 0
                    for vin in vins:
                        txid_data.output_sats = -1
                        txid_data.output_index = -1
                        txid_data.input_sats = vin['output_value']
                        txid_data.input_index = input_index
                        txid_data.address = vin["addresses"][0]
                        txid_data.notary = get_notary_from_btc_address(txid_data.address, txid_data.season)
                        txid_data.update()
                        input_index += 1

                    output_index = 0
                    for vout in vouts:
                        if vout["addresses"] is not None:
                            txid_data.input_index = -1
                            txid_data.input_sats = -1
                            txid_data.address = vout["addresses"][0]
                            txid_data.notary = get_notary_from_btc_address(txid_data.address, txid_data.season)
                            txid_data.output_sats = vout['value']
                            txid_data.output_index = output_index
                            txid_data.update()
                            output_index += 1

                elif detect_consolidate(vins, vouts):
                    txid_data.category = "Consolidate"
                    input_index = 0
                    for vin in vins:
                        txid_data.output_sats = -1
                        txid_data.output_index = -1
                        txid_data.input_sats = vin['output_value']
                        txid_data.input_index = input_index
                        txid_data.address = vin["addresses"][0]
                        txid_data.notary = get_notary_from_btc_address(txid_data.address, txid_data.season)
                        txid_data.update()
                        input_index += 1

                    output_index = 0
                    for vout in vouts:
                        if vout["addresses"] is not None:
                            txid_data.input_index = -1
                            txid_data.input_sats = -1
                            txid_data.address = vout["addresses"][0]
                            txid_data.notary = get_notary_from_btc_address(txid_data.address, txid_data.season)
                            txid_data.output_sats = vout['value']
                            txid_data.output_index = output_index
                            txid_data.update()
                            output_index += 1

                else:
                    txid_data.category = "Other"

                    input_index = 0
                    for vin in vins:
                        txid_data.output_sats = -1
                        txid_data.output_index = -1
                        txid_data.input_sats = vin['output_value']
                        txid_data.input_index = input_index
                        txid_data.address = vin["addresses"][0]
                        txid_data.notary = get_notary_from_btc_address(txid_data.address, txid_data.season)
                        txid_data.update()
                        input_index += 1

                    output_index = 0
                    for vout in vouts:
                        if vout["addresses"] is not None:
                            txid_data.input_index = -1
                            txid_data.input_sats = -1
                            txid_data.address = vout["addresses"][0]
                            txid_data.notary = get_notary_from_btc_address(txid_data.address, txid_data.season)
                            txid_data.output_sats = vout['value']
                            txid_data.output_index = output_index
                            txid_data.update()
                            output_index += 1
        else:
            print("Fees not in txinfo! Likely unconfirmed...")

cursor.close()
conn.close()

