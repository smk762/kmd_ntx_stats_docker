import requests
import json
import time
from lib_const import *


def get_btc_address_txids(address, before=None):
    logger.info(f"getting BTC TXIDs for {address} before block {before}")
    try:
        url = 'https://api.blockcypher.com/v1/btc/main/addrs/'+address+'?limit=2000'
        print(url)
        if before:
            url = url+'&before='+str(before)
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        r = requests.get(url, headers=headers)
        return r.json()
    except Exception as e:
        logger.warning(e)
        return {"error":str(e)}

def get_btc_tx_info(tx_hash, wait=True):
    exit_loop = False
    resp = {}
    i = 0
    while True:
        i += 1
        if exit_loop == True or i == 6:
            return resp
        logger.info("getting BLOCKCYPHER API info for BTC TX "+str(tx_hash))
        try:
            url = 'https://api.blockcypher.com/v1/btc/main/txs/'+tx_hash+'?limit=800'
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            r = requests.get(url, headers=headers)
            resp = r.json()
        except Exception as e:
            logger.warning(e)
            print("err in get_btc_tx_info")
        if wait:
            exit_loop = api_sleep_or_exit(resp)
        else:
            return resp

def get_btc_block_info(block):
    exit_loop = False
    resp = {}
    i = 0
    while True:
        i += 1
        if exit_loop == True or i == 10:
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

## LTC

def get_ltc_address_txids(address, before=None):
    logger.info(f"getting LTC TXIDs for {address} before block {before}")
    try:
        url = 'https://api.blockcypher.com/v1/ltc/main/addrs/'+address+'?limit=2000'
        if before:
            url = url+'&before='+str(before)
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        r = requests.get(url, headers=headers)
        return r.json()
    except Exception as e:
        logger.warning(e)
        return {"error":str(e)}

def get_ltc_tx_info(tx_hash, wait=True):
    exit_loop = False
    resp = {}
    i = 0
    while True:
        i += 1
        if exit_loop == True or i == 6:
            return resp
        logger.info("getting BLOCKCYPHER API info for LTC TX "+str(tx_hash))
        try:
            url = 'https://api.blockcypher.com/v1/ltc/main/txs/'+tx_hash+'?limit=800'
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            r = requests.get(url, headers=headers)
            resp = r.json()
        except Exception as e:
            logger.warning(e)
            print("err in get_ltc_tx_info")
        if wait:
            exit_loop = api_sleep_or_exit(resp)
        else:
            return resp

def get_ltc_block_info(block):
    exit_loop = False
    resp = {}
    i = 0
    while True:
        i += 1
        if exit_loop == True or i == 10:
            return resp
        logger.info("getting info for LTC block "+str(block))
        try:
            url = 'https://api.blockcypher.com/v1/ltc/main/blocks/'+str(block)
            headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
            r = requests.get(url, headers=headers)
            resp = r.json()
        except Exception as e:
            logger.warning(e)
        exit_loop = api_sleep_or_exit(resp)

def api_sleep_or_exit(resp, exit=None):
    if 'error' in resp:
        if exit:
            return True
        elif resp['error'] == 'API calls limits have been reached. To extend your limits please upgrade your plan on BlockCypher accounts page.':
            logger.warning("API limit exceeded, sleeping for 10 min...")
            time.sleep(600)
            return False
        elif resp['error'] == 'Limits reached.':
            logger.warning("API limit exceeded, sleeping for 10 min...")
            time.sleep(600)
            return False            
        else:
            logger.warning(resp['error'])
            return True
    else:
        #print(resp)
        return True