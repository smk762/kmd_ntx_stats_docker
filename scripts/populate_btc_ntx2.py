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
from rpclib import def_credentials
from electrum_lib import get_ac_block_info
from lib_const import *
from notary_lib import *
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

# set this to False in .env when originally populating the table, or rescanning
skip_past_seasons = (os.getenv("skip_past_seasons") == 'True')

# set this to True in .env to quickly update tables with most recent data
skip_until_yesterday = (os.getenv("skip_until_yesterday") == 'True')

'''
This script scans the blockchain for notarisation txids that are not already recorded in the database.
After updaing the "notarised" table, aggregations are performed to get counts for notaries and chains within each season.
It is intended to be run as a cronjob every 15-30 min
Script runtime is around 5-10 mins, except for initial population which is up to 1 day per season
'''

def update_btc_notarisations(conn, cursor):
    # Get existing data to avoid unneccesary updates 
    existing_txids = get_existing_btc_ntxids(cursor)
    notary_last_ntx = get_notary_last_ntx(cursor)

    stop_block = 634000
    # Loop API queries to get BTC ntx
    ntx_txids = get_btc_ntxids(cursor, stop_block)

    with open("btc_ntx_txids.json", 'w+') as f:
        f.write(json.dumps(ntx_txids))

    addresses_dict = {}
    try:
        addresses = requests.get("http://notary.earth:8762/api/source/addresses/?chain=BTC&season=Season_4").json()
        for item in addresses['results']:
            addresses_dict.update({item["address"]:item["notary"]})
        addresses_dict.update({BTC_NTX_ADDR:"BTC_NTX_ADDR"})
    except Exception as e:
        logger.error(e)
    logger.info("Addresses API might be down!")

    i=0
    for btc_txid in ntx_txids:
        logger.info("TXID: "+btc_txid)
        exit_loop = False

        while True:
            if exit_loop == True:
                break
            logger.info("Processing ntxid "+str(i)+"/"+str(len(ntx_txids)))
            i += 1
            tx_info = get_btc_tx_info(btc_txid)

            if "error" in tx_info:
                exit_loop = api_sleep_or_exit(tx_info)

            elif 'block_height' in tx_info:
                block_height = tx_info['block_height']
                block_hash = tx_info['block_hash']
                addresses = tx_info['addresses']
                if '1See1xxxx1memo1xxxxxxxxxxxxxBuhPF' in addresses:
                    logger.warning("SPAM TX")
                    exit_loop = True

                else:
                    notaries = get_notaries_from_addresses(addresses)
                    season = get_season_from_addresses(notaries, addresses, "BTC")

                    btc_block_info = get_btc_block_info(block_height)
                    if 'time' in btc_block_info:
                        block_time_iso8601 = btc_block_info['time']
                        parsed_time = dp.parse(block_time_iso8601)
                        block_time = parsed_time.strftime('%s')
                        block_datetime = dt.utcfromtimestamp(int(block_time))
                        logger.info("Block datetime "+str(block_datetime))

                        for notary in notaries:
                            result = 0
                            last_ntx_row_data = (notary, "BTC", btc_txid, block_height,
                                                 block_time, season)
                            if notary in notary_last_ntx:
                                if "BTC" not in notary_last_ntx[notary]:
                                    notary_last_ntx[notary].update({"BTC":0})

                                if int(block_height) > int(notary_last_ntx[notary]["BTC"]):
                                    result = update_last_ntx_tbl(conn, cursor, last_ntx_row_data)
                            else:
                                result = update_last_ntx_tbl(conn, cursor, last_ntx_row_data)
                            if result == 1:
                                logger.info("last_ntx_tbl updated!")
                            else:
                                logger.warning("last_ntx_tbl not updated!")

                        if len(tx_info['outputs']) > 0:
                            if 'data_hex' in tx_info['outputs'][-1]:
                                opret = tx_info['outputs'][-1]['data_hex']
                                r = requests.get('http://notary.earth:8762/api/tools/decode_opreturn/?OP_RETURN='+opret)
                                kmd_ntx_info = r.json()
                                ac_ntx_height = kmd_ntx_info['notarised_block']
                                ac_ntx_blockhash = kmd_ntx_info['notarised_blockhash']

                                row_data = ('BTC', block_height, block_time, block_datetime,
                                            block_hash, notaries, ac_ntx_blockhash, ac_ntx_height,
                                            btc_txid, opret, season, "true")

                                update_ntx_records(conn, cursor, [row_data])
                                logger.info("Row inserted")

                                fees = tx_info['fees']
                                num_outputs = tx_info['vout_sz']
                                num_inputs = tx_info['vin_sz']
                                block_hash = tx_info['block_hash']
                                block_height = tx_info['block_height']
                                block_time_iso8601 = tx_info['confirmed']
                                parsed_time = dp.parse(block_time_iso8601)
                                block_time = parsed_time.strftime('%s')
                                season = get_season(int(block_time))
                                block_datetime = dt.utcfromtimestamp(int(block_time))
                                vouts = tx_info["outputs"]
                                vins = tx_info["inputs"]

                                input_index = 0
                                for vin in vins:
                                    if BTC_NTX_ADDR in tx_info['addresses']:
                                        category = "NTX"
                                    else:
                                        category = "Sent"
                                    address = vin["addresses"][0]
                                    if address in addresses_dict:
                                        notary_name = addresses_dict[address]
                                    else:
                                        notary_name = "non-NN"
                                    input_sats = vin['output_value']
                                    output_index = None
                                    output_sats = None
                                    row_data = (btc_txid, block_hash, block_height, block_time,
                                                block_datetime, address, notary_name, season, category,
                                                input_index, input_sats, output_index,
                                                output_sats, fees, num_inputs, num_outputs)
                                    logger.info("Adding "+btc_txid+" vin "+str(input_index)+" "+str(notary_name)+" "+str(address)+" ("+category.upper()+")")
                                    update_nn_btc_tx_row(conn, cursor, row_data)
                                    input_index += 1

                                output_index = 0
                                for vout in vouts:
                                    if BTC_NTX_ADDR in tx_info['addresses']:
                                        category = "NTX"
                                    else:
                                        category = "Received"
                                    if vout["addresses"] is not None:
                                        address = vout["addresses"][0]
                                        if address in addresses_dict:
                                            notary_name = addresses_dict[address]
                                        else:
                                            notary_name = "non-NN"
                                        input_index = None
                                        input_sats = None
                                        output_sats = vout['value']
                                        row_data = (btc_txid, block_hash, block_height, block_time,
                                                    block_datetime, address, notary_name, season, category,
                                                    input_index, input_sats, output_index,
                                                    output_sats, fees, num_inputs, num_outputs)
                                        logger.info("Adding "+btc_txid+" vout "+str(output_index)+" "+str(notary_name)+" "+str(address)+" ("+category.upper()+")")
                                        update_nn_btc_tx_row(conn, cursor, row_data)
                                        output_index += 1

                                exit_loop = True
                            else:
                                logger.warning("No data hex: "+str(tx_info['outputs']))
                                exit_loop = True
                    else:
                        logger.info(btc_block_info)


season = get_season(time.time())

conn = connect_db()
cursor = conn.cursor()

update_btc_notarisations(conn, cursor)

cursor.close()
conn.close()
