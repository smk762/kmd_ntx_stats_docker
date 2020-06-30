import requests
import json
import time
import logging
import logging.handlers
from lib_const import *

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def get_btc_address_txids(address, before=None):
    exit_loop = False
    resp = {}
    while True:
        if exit_loop == True:
            return resp
        logger.info("getting BTC TXIDs for "+str(address))
        try:
            url = 'https://api.blockcypher.com/v1/btc/main/addrs/'+address
            if before:
                url = url+'?before='+str(before)
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            r = requests.get(url, headers=headers)
            resp = r.json()
        except Exception as e:
            logger.warning(e)
        exit_loop = api_sleep_or_exit(resp)

def get_btc_tx_info(tx_hash):
    exit_loop = False
    resp = {}
    while True:
        if exit_loop == True:
            return resp
        logger.info("getting info for BTC TX "+str(tx_hash))
        try:
            url = 'https://api.blockcypher.com/v1/btc/main/txs/'+tx_hash
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            r = requests.get(url, headers=headers)
            resp = r.json()
        except Exception as e:
            logger.warning(e)
        exit_loop = api_sleep_or_exit(resp)

def get_btc_block_info(block):
    exit_loop = False
    resp = {}
    while True:
        if exit_loop == True:
            return resp
        logger.info("getting info for BTC block "+str(block))
        try:
            url = 'https://api.blockcypher.com/v1/btc/main/blocks/'+str(block)
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            r = requests.get(url, headers=headers)
            resp = r.json()
        except Exception as e:
            logger.warning(e)
        exit_loop = api_sleep_or_exit(resp)

def api_sleep_or_exit(resp):
    if 'error' in resp:
        if resp['error'] == 'API calls limits have been reached. To extend your limits please upgrade your plan on BlockCypher accounts page.':
            logger.warning("API limit exceeded, sleeping for 10 min...")
            time.sleep(600)
            return False
        else:
            logger.warning(resp['error'])
            return True
    else:
        return True