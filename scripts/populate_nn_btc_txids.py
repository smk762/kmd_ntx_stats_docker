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

conn = connect_db()
cursor = conn.cursor()

addresses_dict = {}
try:
    addresses = requests.get("http://notary.earth:8762/api/source/addresses/?chain=BTC&season=Season_4").json()
    for item in addresses['results']:
        print(item)
        addresses_dict.update({item["address"]:item["notary"]})
    addresses_dict.update({BTC_NTX_ADDR:"BTC_NTX_ADDR"})
except Exception as e:
    logger.error(e)
    logger.info("Addresses API might be down!")

notary_btc_addresses = addresses_dict.keys()
i = 1
num_addr = len(notary_btc_addresses)
print(num_addr)

for notary_address in notary_btc_addresses:
    print(notary_address)
    if notary_address in addresses_dict:
        notary_name = addresses_dict[notary_address]
    else:
        notary_name = "non-NN"
    try:
        existing_txids = get_existing_nn_btc_txids(cursor)
        txids = get_new_nn_btc_txids(existing_txids, notary_address)
    except Exception as e:
        print(e)
        txids = []
    logger.info(str(len(txids))+" to process for "+notary_address+" | "+notary_name+" ("+str(i)+"/"+str(num_addr)+")")
    j = 1
    for txid in txids:
        if notary_address in addresses_dict:
            notary_name = addresses_dict[notary_address]
        else:
            notary_name = "non-NN"
        logger.info("Processing "+str(j)+"/"+str(len(txids))+" for "+notary_address+" | "+notary_name+" ("+str(i)+"/"+str(num_addr)+")")
        # Check if available on other server
        r = requests.get("http://stats.kmd.io/api/info/nn_btc_txid?txid={txid}")
        resp = r.json()
        if resp['count'] > 0:
            for item in resp['results'][0]:
                row_data = (
                    item["txid"],
                    item["block_hash"],
                    item["block_height"],
                    item["block_time"],
                    item["block_datetime"],
                    item["address"],
                    item["notary"],
                    item["season"],
                    item["category"],
                    item["input_index"],
                    item["input_sats"],
                    item["output_index"],
                    item["output_sats"],
                    item["fees"],
                    item["num_inputs"],
                    item["num_outputs"]
                )
                logger.info(f"Adding {item['txid']} from other server")
                update_nn_btc_tx_row(conn, cursor, row_data)
        else:
            tx_info = get_btc_tx_info(txid)
            if 'fees' in tx_info:
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

                # single row for memo.sv spam
                if '1See1xxxx1memo1xxxxxxxxxxxxxBuhPF' in tx_info['addresses']:
                    row_data = (txid, block_hash, block_height, block_time,
                                block_datetime, 'SPAM', 'non-NN', season, 'SPAM',
                                0, 0, 0, 0, fees, num_inputs, num_outputs)
                    logger.info("Adding "+txid+" SPAM")
                    update_nn_btc_tx_row(conn, cursor, row_data)
                else:
                    vouts = tx_info["outputs"]
                    vins = tx_info["inputs"]

                    # single row for splits
                    if len(tx_info['addresses']) == 1:
                        category = "Split or Consolidate"
                        address = tx_info['addresses'][0]
                        if address in addresses_dict:
                            notary_name = addresses_dict[address]
                        else:
                            notary_name = "non-NN"
                        input_sats = 0
                        output_sats = 0
                        output_index = None
                        output_sats = None
                        input_index = None
                        input_sats = None
                        row_data = (txid, block_hash, block_height, block_time,
                                    block_datetime, address, notary_name, season, category,
                                    input_index, input_sats, output_index,
                                    output_sats, fees, num_inputs, num_outputs)
                        logger.info("Adding "+txid+" "+str(notary_name)+" "+str(address)+" "+str(len(vouts)-1)+" vouts"+" ("+category.upper()+")")
                        update_nn_btc_tx_row(conn, cursor, row_data)
                    else:
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
                            row_data = (txid, block_hash, block_height, block_time,
                                        block_datetime, address, notary_name, season, category,
                                        input_index, input_sats, output_index,
                                        output_sats, fees, num_inputs, num_outputs)
                            logger.info("Adding "+txid+" vin "+str(input_index)+" "+str(notary_name)+" "+str(address)+" ("+category.upper()+")")
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
                                row_data = (txid, block_hash, block_height, block_time,
                                            block_datetime, address, notary_name, season, category,
                                            input_index, input_sats, output_index,
                                            output_sats, fees, num_inputs, num_outputs)
                                logger.info("Adding "+txid+" vout "+str(output_index)+" "+str(notary_name)+" "+str(address)+" ("+category.upper()+")")
                                update_nn_btc_tx_row(conn, cursor, row_data)
                                output_index += 1
            else:
                print("Fees not in txinfo!")
                #print(tx_info)
        j += 1
    i += 1

cursor.close()
conn.close()

