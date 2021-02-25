#!/usr/bin/env python3
import requests
import socket
import json
import time
import hashlib
import codecs
import logging
from base_58 import *
from lib_const import *

logger = logging.getLogger()

def lil_endian(hex_str):
    return ''.join([hex_str[i:i+2] for i in range(0, len(hex_str), 2)][::-1])

def get_p2pk_scripthash_from_pubkey(pubkey):
    scriptpubkey = '21' +pubkey+ 'ac'
    scripthex = codecs.decode(scriptpubkey, 'hex')
    s = hashlib.new('sha256', scripthex).digest()
    sha256_scripthash = codecs.encode(s, 'hex').decode("utf-8")
    script_hash = lil_endian(sha256_scripthash)
    return script_hash

def get_p2pkh_scripthash_from_pubkey(pubkey):
    publickey = codecs.decode(pubkey, 'hex')
    s = hashlib.new('sha256', publickey).digest()
    r = hashlib.new('ripemd160', s).digest()
    scriptpubkey = "76a914"+codecs.encode(r, 'hex').decode("utf-8")+"88ac"
    h = codecs.decode(scriptpubkey, 'hex')
    s = hashlib.new('sha256', h).digest()
    sha256_scripthash = codecs.encode(s, 'hex').decode("utf-8")
    script_hash = lil_endian(sha256_scripthash)
    return script_hash

def get_full_electrum_balance(pubkey, url, port):
    p2pk_scripthash = get_p2pk_scripthash_from_pubkey(pubkey)
    p2pkh_scripthash = get_p2pkh_scripthash_from_pubkey(pubkey)
    p2pk_resp = get_from_electrum(url, port, 'blockchain.scripthash.get_balance', p2pk_scripthash)
    p2pkh_resp = get_from_electrum(url, port, 'blockchain.scripthash.get_balance', p2pkh_scripthash)
    p2pk_confirmed_balance = p2pk_resp['result']['confirmed']
    p2pkh_confirmed_balance = p2pkh_resp['result']['confirmed']
    p2pk_unconfirmed_balance = p2pk_resp['result']['unconfirmed']
    p2pkh_unconfirmed_balance = p2pkh_resp['result']['unconfirmed']
    total_confirmed = p2pk_confirmed_balance + p2pkh_confirmed_balance
    total_unconfirmed = p2pk_unconfirmed_balance + p2pkh_unconfirmed_balance
    total = total_confirmed + total_unconfirmed
    return total/100000000
    # NINJA returns "1", TODO: check electrum version etc.

def get_ac_block_info():
    ac_block_info = {}
    for chain in ANTARA_COINS:
      try:
        url = 'http://'+chain.lower()+'.explorer.dexstats.info/insight-api-komodo/sync'
        r = requests.get(url)
        ac_block_info.update({chain:{"height":r.json()['blockChainHeight']}})
        url = 'http://'+chain.lower()+'.explorer.dexstats.info/insight-api-komodo/block-index/'+str(r.json()['blockChainHeight'])
        r = requests.get(url) 
        ac_block_info[chain].update({"hash":r.json()['blockHash']})
      except Exception as e:
        logger.warning(chain+" failed in ac_block_info")
        logger.warning(e)
    return ac_block_info

# http://kmd.explorer.dexstats.info/insight-api-komodo/block-index/8888
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

def get_dexstats_balance(chain, addr):
    url = 'http://'+chain.lower()+'.explorer.dexstats.info/insight-api-komodo/addr/'+addr
    r = requests.get(url)
    balance = r.json()['balance']
    return balance

def get_balance(chain, pubkey, addr, notary, node):
    balance = -1
    check_bal = False
    try:
        if chain in ELECTRUMS:
            try:
                url = ELECTRUMS[chain]["url"]
                port = ELECTRUMS[chain]["port"]
                balance = get_full_electrum_balance(pubkey, url, port)
            except Exception as e:
                logger.warning(">>>>> "+chain+" via ["+url+":"+str(port)+"] FAILED | addr: "+addr+" | "+str(e))
                try:
                    balance = get_dexstats_balance(chain, addr)
                    logger.warning(">>>>> "+chain+" via [DEXSTATS] OK | addr: "+addr+" | balance: "+str(balance))
                except Exception as e:
                    logger.warning(">>>>> "+chain+" via [DEXSTATS] FAILED | addr: "+addr+" | "+str(e))

        elif chain in ANTARA_COINS:
            try:
                balance = get_dexstats_balance(chain, addr)
            except Exception as e:
                logger.warning(">>>>> "+chain+" via [DEXSTATS] FAILED | addr: "+addr+" | "+str(e))

        elif chain == "AYA":
            url = 'https://explorer.aryacoin.io/ext/getaddress/'+addr
            r = requests.get(url)
            if 'balance' in r.json():
                balance = r.json()['balance']
            else:
                logger.warning(">>>>> "+chain+" via explorer.aryacoin.io FAILED | addr: "+addr+" | "+str(r.text))

    except Exception as e:
        logger.warning(">>>>> "+chain+" FAILED ALL METHODS | addr: "+addr+" | "+str(e))
    return balance
