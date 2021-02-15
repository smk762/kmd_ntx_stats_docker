#!/usr/bin/env python3
import time
import logging
import logging.handlers
from datetime import datetime as dt
import datetime
import requests
import psycopg2
from decimal import *
from psycopg2.extras import execute_values
from lib_notary import *
from lib_rpc import def_credentials

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def calc_address_txid_rows(address_txs):
    season = get_season(int(time.time()))
    if 'txs' in address_txs:
        num_tx = address_txs['n_tx']
        total_sent = address_txs['total_sent']
        total_received = address_txs['total_received']
        final_balance = address_txs['final_balance']

        for tx in address_txs['txs']:
            txid = tx['hash']

            if 'block_height' in tx:
                block_height = tx['block_height']
                block_time = tx['time']
                tx_season = get_season(block_time)
                if tx_season == season:
                    vin_sz = tx['vin_sz']
                    result = tx['result']

                    vin_addr = []
                    total_in = 0

                    for vin in tx['inputs']:
                        if 'addr' in vin['prev_out']:
                            total_in += vin['prev_out']['value']
                            vin_addr.append({vin['prev_out']['addr']:vin['prev_out']['value']})

                    vout_addr = []
                    total_out = 0

                    for vout in tx['out']:
                        if 'addr' in vout:
                            total_out += vout['value']
                            vout_addr.append({vout['addr']:vout['value']})
                            
                    fees = total_in - total_out

                    if vin_sz == 13 and result == -10000:
                        category = "notarisation"
                    elif vin_addr[0].keys() == vout_addr[0].keys():
                        category = "self send"
                    elif result > 0:
                        category = "top up"
                    else:
                        category = "unrecognised"

                    notary = get_notary_from_address(notary_address)
                    season = get_season(int(block_time))

                    row_data = (notary, notary_address, category, txid, block_time,
                                total_in, total_out, fees, json.dumps(vin_addr), json.dumps(vout_addr),
                                season)
                    
                    print("inserting "+txid)
                    update_btc_address_deltas_tbl(conn, cursor, row_data)
                else:
                    print("skipping non current season tx "+txid)
            else:
                print("skipping unconfirmed tx "+txid)

conn = connect_db()
cursor = conn.cursor()

existing_txids = []
season = get_season(int(time.time()))
rate_limit_sec = 10

notary_btc_addresses = []
cursor.execute("SELECT address FROM addresses WHERE chain = 'BTC' AND season = '"+season+"' AND node = 'main';")
address_results = cursor.fetchall()
for result in address_results:
    notary_btc_addresses.append(result[0])

for notary_address in notary_btc_addresses:
    offset = 0
    try:
        r = requests.get('https://blockchain.info/address/'+notary_address+'?format=json&offset='+str(offset))
        print('https://blockchain.info/address/'+notary_address+'?format=json&offset='+str(offset))
        address_txs = r.json()
    except Exception as e:
        print(e)
        address_txs = []
    if len(address_txs) > 0:
        while len(address_txs['txs']) == 50:
            calc_address_txid_rows(address_txs)
            offset += 50
            try:
                print("sleeping for "+str(rate_limit_sec)+" sec")
                time.sleep(rate_limit_sec)
                url = 'https://blockchain.info/address/'+notary_address+'?format=json&offset='+str(offset)
                r = requests.get(url)
                address_txs = r.json()
            except:
                address_txs = []
            if 'txs' not in address_txs:
                print(address_txs) 
                break

        calc_address_txid_rows(address_txs)

cursor.close()
conn.close()
