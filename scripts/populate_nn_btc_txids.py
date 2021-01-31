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

other_server = os.getenv("other_server")

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

notary_btc_addresses = list(addresses_dict.keys())
i = 1
num_addr = len(notary_btc_addresses)
print(num_addr)

#notary_btc_addresses.reverse()

for notary_address in notary_btc_addresses:
    print(notary_address)
    if notary_address in addresses_dict:
        notary_name = addresses_dict[notary_address]
    else:
        notary_name = "non-NN"
    try:
        existing_txids = get_existing_nn_btc_txids(cursor, notary_address)
        logger.info(str(len(existing_txids))+" EXIST IN DB FOR "+notary_address+" | "+notary_name+" ("+str(i)+"/"+str(num_addr)+")")
        txids = get_new_nn_btc_txids(existing_txids, notary_address)
        logger.info(str(len(txids))+" new TXIDs to process for "+notary_address+" | "+notary_name+" ("+str(i)+"/"+str(num_addr)+")")
    except Exception as e:
        print(e)
        txids = []
    j = 1
    for txid in txids:
        # Try to get data from other server
        print(f"{other_server}/api/info/nn_btc_txid?txid={txid}")
        r = requests.get(f"{other_server}/api/info/nn_btc_txid?txid={txid}")
        resp = r.json()
        if resp['count'] > 0:
            tx_addresses = []
            season = None
            for item in resp['results'][0]:
                if item["address"] != '1P3rU1Nk1pmc2BiWC8dEy9bZa1ZbMp5jfg':
                    tx_addresses.append(item["address"])
            tx_addresses = list(set(tx_addresses))
            season = get_season_from_addresses(tx_addresses, resp['results'][0][0]["block_time"], "BTC")
            logger.info(f"Detected {season} from addresses")
            for item in resp['results'][0]:
                if item["output_index"] is None:
                    output_index = -1
                else:
                    output_index = item["output_index"]

                if item["input_index"] is None or item["input_index"] == 1000:
                    input_index = -1
                else:
                    input_index = item["input_index"]

                if item["input_sats"] is None:
                    input_sats = -1
                else:
                    input_sats = item["input_sats"]

                if item["output_sats"] is None or item["output_index"] == 1000:
                    output_sats = -1
                else:
                    output_sats = item["output_sats"]

                if item["num_inputs"] is None:
                    num_inputs = 0
                else:
                    num_inputs = item["num_inputs"]

                if item["num_outputs"] is None:
                    num_outputs = 0
                else:
                    num_outputs = item["num_outputs"]

                if item["address"] in addresses_dict:
                    notary = addresses_dict[item["address"]]
                else:
                    notary = item["notary"]

                row_data = (
                    item["txid"],
                    item["block_hash"],
                    item["block_height"],
                    item["block_time"],
                    item["block_datetime"],
                    item["address"],
                    notary,
                    season,
                    item["category"],
                    input_index,
                    input_sats,
                    output_index,
                    output_sats,
                    item["fees"],
                    num_inputs,
                    num_outputs
                )
                logger.info(f"Adding {item['txid']} {item['category']} from other server for {notary}")
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
                block_datetime = dt.utcfromtimestamp(int(block_time))

                addresses = tx_info['addresses']
                season = get_season_from_addresses(addresses, block_time, "BTC")

                # single row for memo.sv spam
                if '1See1xxxx1memo1xxxxxxxxxxxxxBuhPF' in addresses:
                    row_data = (txid, block_hash, block_height, block_time,
                                block_datetime, 'SPAM', 'non-NN', season, 'SPAM',
                                0, 0, 0, 0, fees, num_inputs, num_outputs)
                    logger.info("Adding "+txid+" SPAM")
                    update_nn_btc_tx_row(conn, cursor, row_data)
                else:
                    vouts = tx_info["outputs"]
                    vins = tx_info["inputs"]

                    # single row for splits
                    if len(addresses) == 1:
                        category = "Split or Consolidate"
                        address = addresses[0]
                        if address in addresses_dict:
                            notary_name = addresses_dict[address]
                        else:
                            notary_name = "non-NN"
                        input_sats = 0
                        output_sats = 0
                        output_index = -1
                        output_sats = -1
                        input_index = -1
                        input_sats = -1
                        row_data = (txid, block_hash, block_height, block_time,
                                    block_datetime, address, notary_name, season, category,
                                    input_index, input_sats, output_index,
                                    output_sats, fees, num_inputs, num_outputs)
                        logger.info("Adding "+txid+" "+str(notary_name)+" "+str(address)+" "+str(len(vouts)-1)+" vouts"+" ("+category.upper()+")")
                        update_nn_btc_tx_row(conn, cursor, row_data)
                    else:
                        input_index = 0
                        for vin in vins:
                            if BTC_NTX_ADDR in addresses:
                                category = "NTX"
                            else:
                                category = "Sent"
                            address = vin["addresses"][0]
                            if address in addresses_dict:
                                notary_name = addresses_dict[address]
                            else:
                                notary_name = "non-NN"
                            input_sats = vin['output_value']
                            output_index = -1
                            output_sats = -1
                            row_data = (txid, block_hash, block_height, block_time,
                                        block_datetime, address, notary_name, season, category,
                                        input_index, input_sats, output_index,
                                        output_sats, fees, num_inputs, num_outputs)
                            logger.info("Adding "+txid+" vin "+str(input_index)+" "+str(notary_name)+" "+str(address)+" ("+category.upper()+")")
                            update_nn_btc_tx_row(conn, cursor, row_data)
                            input_index += 1

                        output_index = 0
                        for vout in vouts:
                            if BTC_NTX_ADDR in addresses:
                                category = "NTX"
                            else:
                                category = "Received"
                            if vout["addresses"] is not None:
                                address = vout["addresses"][0]
                                if address in addresses_dict:
                                    notary_name = addresses_dict[address]
                                else:
                                    notary_name = "non-NN"
                                input_index = -1
                                input_sats = -1
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

