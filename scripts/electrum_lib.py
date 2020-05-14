#!/usr/bin/env python3
import requests
from coins_lib import third_party_coins, antara_coins, ex_antara_coins, all_antara_coins, all_coins
import socket
import json
import base58
import logging
import logging.handlers
import hashlib
import codecs

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def addr_to_scriptpubkey(addr):
    return "76a914"+base58.b58decode_check(addr).hex()[2:]+"88ac"

def lil_endian(hex_str):
    return ''.join([hex_str[i:i+2] for i in range(0, len(hex_str), 2)][::-1])

def pubkey_to_scriptpubkey(pubkey):
    publickey = codecs.decode(pubkey, 'hex')
    s = hashlib.new('sha256', publickey).digest()
    r = hashlib.new('ripemd160', s).digest()
    return "76a914"+codecs.encode(r, 'hex').decode("utf-8")+"88ac"

def scriptpubkey_to_scripthash(scriptpubkey):
    scripthex = codecs.decode(scriptpubkey, 'hex')
    s = hashlib.new('sha256', scripthex).digest()
    return lil_endian(codecs.encode(s, 'hex').decode("utf-8"))

def addr_to_scripthash(addr):
    scriptpubkey = addr_to_scriptpubkey(addr)
    scripthash = scriptpubkey_to_scripthash(scriptpubkey)
    return scripthash

electrums = {}
r = requests.get('http://notary.earth:8762/info/coins/?dpow_active=1')
coins_info = r.json()
for coin in coins_info['results'][0]:
    if len(coins_info['results'][0][coin]['electrums']) > 0:
        electrum = coins_info['results'][0][coin]['electrums'][0].split(":") 
        electrums.update({
            coin:{
                "url":electrum[0],
                "port":electrum[1]
                }
            })

def get_ac_block_heights():
    ac_block_height = {}
    for chain in antara_coins:
      try:
        url = 'http://'+chain.lower()+'.explorer.dexstats.info/insight-api-komodo/sync'
        r = requests.get(url)
        ac_block_height.update({chain:r.json()['blockChainHeight']})
      except Exception as e:
        logger.info(chain+" failed")
        logger.info(e)
    return ac_block_height

# http://explorer.chips.cash/api/getblockcount
# http://chips.komodochainz.info/ext/getbalance/RSAzPFzgTZHNcxLNLdGyVPbjbMA8PRY7Ss
# https://explorer.aryacoin.io/api/getblockcount
# https://chainz.cryptoid.info/emc2/api.dws?q=getbalance&a=RFUN8XezmmZt47pzVmoz7aN5LtFNV9pyuj
# https://chainz.cryptoid.info/emc2/api.dws?q=getblockcount

def get_from_electrum(url, port, method, params=[]):
    params = [params] if type(params) is not list else params
    socket.setdefaulttimeout(5)
    s = socket.create_connection((url, port))
    s.send(json.dumps({"id": 0, "method": method, "params": params}).encode() + b'\n')
    return json.loads(s.recv(99999)[:-1].decode())

def get_electrum_balance(chain, addr):
    balance = -1
    try:
        if chain in electrums:
            scripthash = addr_to_scripthash(addr)
            url = electrums[chain]["url"]
            port = electrums[chain]["port"]
            resp = get_from_electrum(url, port, 'blockchain.scripthash.get_balance', scripthash)
            balance = resp['result']['confirmed'] / 100000000 # response is in sats.
        elif chain in antara_coins or chain in ["HUSH3"]:
            url = 'http://'+chain.lower()+'.explorer.dexstats.info/insight-api-komodo/addr/'+addr
            r = requests.get(url)
            if 'balance' in r.json():
                balance = r.json()['balance']
            else:
                logger.info(chain+" FAILED | addr: "+addr+" | "+str(r.text))
        elif chain == "KMD":
            scripthash = addr_to_scripthash(addr)
            resp = get_from_electrum('electrum1.cipig.net', 10001, 'blockchain.scripthash.get_balance', scripthash)
            print(chain+": "+str(resp))
            balance = resp['result']['confirmed']
        elif chain == "CHIPS":
            scripthash = addr_to_scripthash(addr)
            resp = get_from_electrum('electrum1.cipig.net', 10053, 'blockchain.scripthash.get_balance', scripthash)
            balance = resp['result']['confirmed']
            print(chain+": "+str(resp))
        elif chain == "EMC2":
            scripthash = addr_to_scripthash(addr)
            resp = get_from_electrum('electrum1.cipig.net', 10062, 'blockchain.scripthash.get_balance', scripthash)
            balance = resp['result']['confirmed']
            print(chain+": "+str(resp))
        elif chain == "GAME":
            scripthash = addr_to_scripthash(addr)
            resp = get_from_electrum('electrum1.cipig.net', 10072, 'blockchain.scripthash.get_balance', scripthash)
            print(chain+": "+str(resp))
            balance = resp['result']['confirmed']
        elif chain == "BTC":
            scripthash = addr_to_scripthash(addr)
            resp = get_from_electrum('electrum1.cipig.net', 10000, 'blockchain.scripthash.get_balance', scripthash)
            balance = resp['result']['confirmed']
            print(chain+": "+str(resp))
        elif chain == "GIN":
            # Gin is dead.
            # addr = addr_to_scripthash_256(addr)
            # resp = get_from_electrum('electrum2.gincoin.io', 6001, 'blockchain.scripthash.get_balance', addr)
            # balance = resp['result']['confirmed']
            return -1
        elif chain == "AYA":
            url = 'https://explorer.aryacoin.io/ext/getaddress/'+addr
            r = requests.get(url)
            if 'balance' in r.json():
                balance = r.json()['balance']
            else:
                logger.info(chain+" failed")
                logger.info("addr: "+addr)
                logger.info(r.json())
            

    except Exception as e:
        if chain not in ex_antara_coins:
            logger.info(chain+" failed")
            logger.info("addr: "+addr)
            logger.info(e)
    return balance