#!/usr/bin/env python3
import requests
from coins_lib import third_party_coins, antara_coins, ex_antara_coins, all_antara_coins, all_coins
import socket
import json
import time
import hashlib
import codecs
import base58
import logging
import logging.handlers

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

addr = 'RRfUCLxfT5NMpxsC9GHVbdfVy5WJnJFQLV'
scriptpubkey = '76a914b3b89e3c87e3fed305f6656cfdd6e1c12ce6dbab88ac'
pubkey = '0224a9d951d3a06d8e941cc7362b788bb1237bb0d56cc313e797eb027f37c2d375'

def get_from_electrum(url, port, method, params=[]):
    try:
        params = [params] if type(params) is not list else params
        socket.setdefaulttimeout(5)
        s = socket.create_connection((url, port))
        s.send(json.dumps({"id": 0, "method": method, "params": params}).encode() + b'\n')
        return json.loads(s.recv(99999)[:-1].decode())
    except Exception as e:
        print("==============================")
        print(str(url)+""+str(port)+" failed!")
        print(e)
        print("==============================")


def lil_endian(hex_str):
    return ''.join([hex_str[i:i+2] for i in range(0, len(hex_str), 2)][::-1])

def get_scripthash_from_pubkey(pubkey):
    scriptpubkey = '21' +pubkey+ 'ac'
    scripthex = codecs.decode(scriptpubkey, 'hex')
    s = hashlib.new('sha256', scripthex).digest()
    sha256_scripthash = codecs.encode(s, 'hex').decode("utf-8")
    script_hash = lil_endian(sha256_scripthash)
    return script_hash

def get_other_scripthash_from_pubkey(pubkey):
    publickey = codecs.decode(pubkey, 'hex')
    s = hashlib.new('sha256', publickey).digest()
    r = hashlib.new('ripemd160', s).digest()
    scriptpubkey = "76a914"+codecs.encode(r, 'hex').decode("utf-8")+"88ac"
    h = codecs.decode(scriptpubkey, 'hex')
    s = hashlib.new('sha256', h).digest()
    sha256_scripthash = codecs.encode(s, 'hex').decode("utf-8")
    script_hash = lil_endian(sha256_scripthash)
    return script_hash

scripthash = get_scripthash_from_pubkey(pubkey)
other_scripthash = get_other_scripthash_from_pubkey(pubkey)

print("script_hash: "+scripthash)
print("other_scripthash: "+other_scripthash)
print("---------------------------------------------------")

r = requests.get('http://notary.earth:8762/api/info/coins/?dpow_active=1')
coins_info = r.json()
for coin in coins_info['results'][0]:
    if len(coins_info['results'][0][coin]['electrums']) > 0:
        electrum = coins_info['results'][0][coin]['electrums'][0].split(":")
        print(coin+": "+str(electrum))
        url = electrum[0]
        port = electrum[1]

        resp = get_from_electrum(url, port, 'blockchain.scripthash.get_balance', scripthash)
        print(coin+": "+str(resp))
        resp = get_from_electrum(url, port, 'blockchain.scripthash.get_balance', other_scripthash)
        print(coin+": "+str(resp))
    else:
        print("No electrums for "+coin)

def get_ac_block_info():
    ac_block_info = {}
    for chain in antara_coins:
      try:
        url = 'http://'+chain.lower()+'.explorer.dexstats.info/insight-api-komodo/sync'
        r = requests.get(url)
        ac_block_info.update({chain:{"height":r.json()['blockChainHeight']}})
        url = 'http://'+chain.lower()+'.explorer.dexstats.info/insight-api-komodo/block-index/'+str(r.json()['blockChainHeight'])
        r = requests.get(url) 
        ac_block_info[chain].update({"hash":r.json()['blockHash']})
      except Exception as e:
        logger.info(chain+" failed")
        logger.info(e)
    return ac_block_info

sync_node_data = requests.get('http://138.201.207.24/show_sync_node_data').json()
for chain in sync_node_data:
    try:
        sync_hash = sync_node_data[chain]['last_longesthash']
        block = sync_node_data[chain]['last_longestchain']
    except:
        print(sync_node_data[chain])
    try:
        url = 'http://'+chain.lower()+'.explorer.dexstats.info/insight-api-komodo/block-index/'+str(block)
        r = requests.get(url) 
        exp_hash = r.json()['blockHash']
        if exp_hash == sync_hash:
            print(chain+" block "+str(block)+" hash matching ["+sync_hash+"]")
        else:
            print(chain+" MISMATCH ON BLOCK "+str(block)+"!")
            print("["+sync_hash+"] vs ["+exp_hash+"]")
        time.sleep(1)
    except:
        print("NO EXPLORER FOR "+chain)


# http://kmd.explorer.dexstats.info/insight-api-komodo/block-index/8888
