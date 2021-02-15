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
#txids = ['03402cc2f09e22d90fb9853db14a71ace0f00eb48646387d6ed89ec7bb7254df'] # KNOWN REPLENISH FROM Dragonhouond_NA
#txids = ['c8dbc9e3af7f5a1d8f910ff03e390a8782a911bc34fc567c27c711e9da191894'] # KNOWN REPLENISH FROM Replenish Addr
#txids = ['03402cc2f09e22d90fb9853db14a71ace0f00eb48646387d6ed89ec7bb7254df', '6a458e37a6b101433cc60e28ccfb8335a29ea3a80e76b69d32f4806f3fb9f040'] # KNOWN REPLENISH FROM Replenish Addr
#txids = ['03402cc2f09e22d90fb9853db14a71ace0f00eb48646387d6ed89ec7bb7254df', '6a458e37a6b101433cc60e28ccfb8335a29ea3a80e76b69d32f4806f3fb9f040', 'c8dbc9e3af7f5a1d8f910ff03e390a8782a911bc34fc567c27c711e9da191894'] # KNOWN REPLENISH FROM Replenish Addr

            
# set this to False in .env when originally populating the table, or rescanning
skip_past_seasons = (os.getenv("skip_past_seasons") == 'True')
if skip_past_seasons:
    seasons = [get_season(time.time())]
else:
    seasons = list(SEASONS_INFO.keys())

# set this to True in .env to quickly update tables with most recent data
skip_until_yesterday = (os.getenv("skip_until_yesterday") == 'True')

other_server = os.getenv("other_server")

conn = connect_db()
cursor = conn.cursor()

for season in seasons:
    #NOTARY_BTC_ADDRESSES[season].reverse()
    i = 0
    num_addr = len(NOTARY_BTC_ADDRESSES[season])

    for notary_address in NOTARY_BTC_ADDRESSES[season]:
        i += 1

        # import tx data from other server
        try:
            categorize_import_transactions(notary_address, season)            
        except Exception as e:
            logger.error(f"Error in categorize_import_transactions({notary_address} {season})")
            logger.error(e)

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

                # single row for memo.sv spam
                if '1See1xxxx1memo1xxxxxxxxxxxxxBuhPF' in addresses:
                    txid_data.category = "SPAM"
                    txid_data.update()

                # Detect NTX
                elif BTC_NTX_ADDR in addresses and len(vins) == 13 and len(vouts) == 2:

                    if not validate_ntx_vins(vins):
                        logger.info(f"{txid} looks like an NTX, but has vin addresses not within NN_BTC_ADDRESSES_DICT!")
                        time.sleep(5)

                    elif not validate_ntx_vouts(vouts):
                        logger.info(f"{txid} looks like an NTX, but has vout addresses which is not {BTC_NTX_ADDR}!")
                        time.sleep(5)

                    else:
                        txid_data.category = "NTX"
                        input_index = 0
                        for vin in vins:
                            txid_data.address = vin["addresses"][0]
                            txid_data.notary = get_notary_from_btc_address(txid_data.address, txid_data.season)
                            txid_data.input_sats = vin['output_value']
                            txid_data.input_index = input_index
                            txid_data.update()
                            input_index += 1

                        output_index = 0
                        for vout in vouts:
                            if vout["addresses"] is not None:
                                txid_data.address = vout["addresses"][0]
                                txid_data.notary = "BTC_NTX_ADDR"
                                txid_data.output_sats = vout['value']
                                txid_data.output_index = output_index
                                txid_data.update()
                                output_index += 1

                # Detect Split (single row only)
                elif len(addresses) == 1:
                    txid_data.category = "Split"
                    txid_data.address = addresses[0]
                    txid_data.notary = get_notary_from_btc_address(txid_data.address, txid_data.season)
                    txid_data.input_sats = -99
                    txid_data.output_sats = -99
                    txid_data.input_index = -99
                    txid_data.output_index = -99
                    txid_data.update()

                else:
                    txid_data.category = "Other"
                    input_index = 0
                    for vin in vins:
                        txid_data.address = vin["addresses"][0]
                        txid_data.notary = get_notary_from_btc_address(txid_data.address, txid_data.season)
                        txid_data.input_sats = vin['output_value']
                        txid_data.input_index = input_index

                        txid_data.update()
                        input_index += 1

                    output_index = 0
                    for vout in vouts:
                        if vout["addresses"] is not None:
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

