#!/usr/bin/env python3
import requests
import sys
import json
import time
from lib_const import *
from lib_github import *
from lib_urls import get_dpow_active_coins_url, get_kmd_price_url


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
        return True

def get_kmd_price(date):
    url = get_kmd_price_url(date)
    r = requests.get(url)
    try:
        return r.json()["market_data"]["current_price"]
    except:
        print (f"get_kmd_price: {r.text}")

  

def get_ac_block_info():
    ac_block_info = {}
    dpow_coins = requests.get(get_dpow_active_coins_url()).json()["results"]
    for coin in dpow_coins:
        if coin not in RETIRED_DPOW_COINS:
            try:
                url = f'http://{coin.lower()}.explorer.dexstats.info/insight-api-komodo/sync'
                r = requests.get(url)
                ac_block_info.update({coin:{"height":r.json()['blockChainHeight']}})
                url = f'http://{coin.lower()}.explorer.dexstats.info/insight-api-komodo/block-index/'+str(r.json()['blockChainHeight'])
                r = requests.get(url) 
                ac_block_info[coin].update({"hash":r.json()['blockHash']})
            except Exception as e:
                logger.warning(f"{coin} failed in ac_block_info")
                logger.warning(e)
    return ac_block_info


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
        return {"err":str(e)}


def get_btc_tx_info(tx_hash, wait=True, exit_script=False):
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
            return r.json()
        except Exception as e:
            logger.warning(e)
            print("err in get_btc_tx_info")
            return {"err":str(e)}
        if exit_script:
            logger.warning("Exiting script to avoid API rate limits...")
            sys.exit()
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
            return r.json()
        except Exception as e:
            logger.warning(e)
            return {"err":str(e)}
        exit_loop = api_sleep_or_exit(resp)


def get_dexstats_balance(coin, addr):
    try:
        if coin == "MIL":
            url = f'http://{coin.lower()}.kmdexplorer.io/api/addr/{addr}'
        else:
            url = f'http://{coin.lower()}.explorer.dexstats.info/insight-api-komodo/addr/{addr}'
        r = requests.get(url)
        balance = r.json()['balance']
        return balance
    except:
        return -1


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
        return {"err":str(e)}


def get_ltc_tx_info(tx_hash, wait=True, exit_script=False):
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
            return r.json()
        except Exception as e:
            logger.warning(e)
            print("err in get_ltc_tx_info")
            return {"err":str(e)}
        if exit_script:
            logger.warning("Exiting script to avoid API rate limits...")
            sys.exit()
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
            return r.json()
        except Exception as e:
            logger.warning(e)
            return {"err":str(e)}
        exit_loop = api_sleep_or_exit(resp)



# TODO: refactor to use ELECTRUMS const for non-Dexstats urls
# Might need to expand ELECTRUMS to include endpoints format
# http://kmd.explorer.dexstats.info/insight-api-komodo/block-index/8888
# http://explorer.chips.cash/api/getblockcount
# http://chips.komodochainz.info/ext/getbalance/RSAzPFzgTZHNcxLNLdGyVPbjbMA8PRY7Ss
# https://explorer.aryacoin.io/api/getblockcount
# https://chainz.cryptoid.info/emc2/api.dws?q=getbalance&a=RFUN8XezmmZt47pzVmoz7aN5LtFNV9pyuj
# https://chainz.cryptoid.info/emc2/api.dws?q=getblockcount