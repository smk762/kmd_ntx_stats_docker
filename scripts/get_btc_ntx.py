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
from notary_lib import *
from rpclib import def_credentials
import table_lib
from psycopg2.extras import Json

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

#https://api.blockcypher.com/v1/btc/main/addrs/1P3rU1Nk1pmc2BiWC8dEy9bZa1ZbMp5jfg?limit=2
#https://api.blockcypher.com/v1/btc/main/txs/
ntx_addr = '1P3rU1Nk1pmc2BiWC8dEy9bZa1ZbMp5jfg'
def get_address_txids(address, before=None):
    try:
        url = 'https://api.blockcypher.com/v1/btc/main/addrs/'+address
        if before:
            url = url+'?before='+str(before)
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        r = requests.get(url, headers=headers)
        return r.json()
    except Exception as e:
        logger.warning(e)

def get_tx_info(tx_hash):
    try:
        url = 'https://api.blockcypher.com/v1/btc/main/txs/'+tx_hash
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        r = requests.get(url, headers=headers)
        return r.json()
    except Exception as e:
        logger.warning(e)

def get_block_info(block):
    try:
        url = 'https://api.blockcypher.com/v1/btc/main/blocks/'+block
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        r = requests.get(url, headers=headers)
        return r.json()
    except Exception as e:
        logger.warning(e)

conn = connect_db()
cursor = conn.cursor()

existing_txids = []
cursor.execute("SELECT DISTINCT btc_txid FROM notarised_btc;")
txids_results = cursor.fetchall()
for result in txids_results:
    existing_txids.append(result[0])

has_more=True
before_block=None
ntx_txids = []
page = 0
exit_loop = False
while has_more:
    page += 1
    logger.info("Page "+str(page))
    resp = get_address_txids(ntx_addr, before_block)
    if "error" in resp:
        page -= 1
        if resp['error'] == 'API calls limits have been reached. To extend your limits please upgrade your plan on BlockCypher accounts page.':
            logger.info("API limit exceeded, sleeping for 10 min...")
            time.sleep(600)
        else:
            logger.info(resp['error'])
            exit_loop = True
    else:
        if 'txrefs' in resp:
            tx_list = resp['txrefs']
            for tx in tx_list:
                if tx['tx_hash'] not in ntx_txids and tx['tx_hash'] not in existing_txids:
                    ntx_txids.append(tx['tx_hash'])
            logger.info(str(len(ntx_txids))+" txids scanned...")

        if 'hasMore' in resp:
            has_more = resp['hasMore']
            logger.info(has_more)
            if has_more:
                before_block = tx_list[-1]['block_height']
                logger.info("scannning back from block "+str(before_block))
                if before_block < 632500:
                    logger.info("Scanned to start of s4")
                    exit_loop = True
                time.sleep(1)
            else:
                logger.info("No more!")
                exit_loop = True

        else:
            logger.info(resp)
            logger.info("No more tx to scan!")
            exit_loop = True
    if exit_loop or page ==4:
        logger.info("exiting address txid loop!")
        break

logger.info(str(len(ntx_txids))+ " ntxids to process!")
ntx_txids = list(set((ntx_txids)))
logger.info(str(len(ntx_txids))+ " ntxids to process!")

with open("btc_ntx_txids.json", 'w+') as f:
    f.write(json.dumps(ntx_txids))

logger.info(str(len(ntx_txids))+ " ntxids to process!")

i=0
for btc_txid in ntx_txids:
    logger.info("TXID: "+btc_txid)
    exit_loop = False
    while True:
        if exit_loop == True:
            break
        logger.info("Processing ntxid "+str(i)+"/"+str(len(ntx_txids)))
        i += 1
        notaries = []
        tx_info = get_tx_info(btc_txid)
        if 'block_height' in tx_info:
            btc_block_ht = tx_info['block_height']
            btc_block_hash = tx_info['block_hash']
            addresses = tx_info['addresses']
            if ntx_addr in addresses:
                addresses.remove(ntx_addr)
            for address in addresses:    
                if address in known_addresses:
                    notary = known_addresses[address]
                    notaries.append(notary)
                else:
                    notaries.append(address)
            notaries.sort()
            if len(tx_info['outputs']) > 0:
                if 'data_hex' in tx_info['outputs'][-1]:
                    opret = tx_info['outputs'][-1]['data_hex']
                    r = requests.get('http://notary.earth:8762/api/tools/decode_opreturn/?OP_RETURN='+opret)
                    kmd_ntx_info = r.json()

                    if kmd_ntx_info['chain'] == "KMD":
                        kmd_block_hash = kmd_ntx_info['notarised_blockhash']
                        kmd_block_ht = kmd_ntx_info['notarised_block']
                        season = get_season_from_addresses(notaries, addresses, "BTC")
                        row_data = (btc_txid, btc_block_hash, btc_block_ht,
                            addresses, notaries,
                            kmd_block_hash, kmd_block_ht,
                            opret, season)

                        sql = "INSERT INTO notarised_btc (btc_txid, btc_block_hash, btc_block_ht, \
                                                            addresses, notaries, \
                                                            kmd_block_hash, kmd_block_ht, \
                                                            opret, season) \
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"
                        try:
                            cursor.execute(sql, row_data)
                            conn.commit()
                        except Exception as e:
                            if str(e).find('duplicate') == -1:
                                logger.debug(e)
                                logger.debug(row_data)
                            conn.rollback()
                        logger.info("Row inserted")
                        exit_loop = True
                    else:
                        logger.warning("Chain not KMD: "+kmd_ntx_info['chain'])
                        exit_loop = True
                else:
                    logger.warning("No data hex: "+str(tx_info['outputs']))
                    exit_loop = True
        elif "error" in tx_info:
            page -= 1
            if tx_info['error'] == 'API calls limits have been reached. To extend your limits please upgrade your plan on BlockCypher accounts page.':
                logger.info("API limit exceeded, sleeping for 10 min...")
                time.sleep(600)
            else:
                logger.info(tx_info['error'])
                exit_loop = True


cursor.close()

conn.close()
