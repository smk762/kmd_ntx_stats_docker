#!/usr/bin/env python3
import requests
import socket
import json
import time
import hashlib
import codecs
import base58
import logging
import bitcoin
from bitcoin.core import x
from bitcoin.core import CoreMainParams
from bitcoin.wallet import P2PKHBitcoinAddress
from notary_lib import notary_addresses, known_addresses, season_pubkeys, notary_pubkeys
from coins_lib import third_party_coins, antara_coins, ex_antara_coins, all_antara_coins, all_coins

logger = logging.getLogger()

class BTC_CoinParams(CoreMainParams):
    MESSAGE_START = b'\x24\xe9\x27\x64'
    DEFAULT_PORT = 7770
    BASE58_PREFIXES = {'PUBKEY_ADDR': 0,
                       'SCRIPT_ADDR': 5,
                       'SECRET_KEY': 128}

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

def get_addr_from_pubkey(pubkey):
    return str(P2PKHBitcoinAddress.from_pubkey(x(pubkey)))

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

electrums = {}
r = requests.get('http://notary.earth:8762/api/info/coins/?dpow_active=1')
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
        if chain == "GIN":
            logger.warning("Getting "+chain+" {"+node+"}"+" {"+notary+"}")
        if chain in electrums:
            try:
                url = electrums[chain]["url"]
                port = electrums[chain]["port"]
                balance = get_full_electrum_balance(pubkey, url, port)
            except Exception as e:
                logger.warning(">>>>> "+chain+" via ["+url+":"+str(port)+"] FAILED | addr: "+addr+" | "+str(e))
                try:
                    balance = get_dexstats_balance(chain, addr)
                    logger.warning(">>>>> "+chain+" via [DEXSTATS] OK | addr: "+addr+" | balance: "+str(balance))
                except Exception as e:
                    logger.warning(">>>>> "+chain+" via [DEXSTATS] FAILED | addr: "+addr+" | "+str(e))

        elif chain in antara_coins or chain in ["HUSH3"]:
            try:
                balance = get_dexstats_balance(chain, addr)
            except Exception as e:
                logger.warning(">>>>> "+chain+" via [DEXSTATS] FAILED | addr: "+addr+" | "+str(e))

        elif chain == "GIN":
            # Gin is dead.
            # addr = addr_to_scripthash_256(addr)
            # resp = get_from_electrum('electrum2.gincoin.io', 6001, 'blockchain.scripthash.get_balance', addr)
            # balance = resp['result']['confirmed']
            pass
        elif chain == "AYA":
            url = 'https://explorer.aryacoin.io/ext/getaddress/'+addr
            r = requests.get(url)
            if 'balance' in r.json():
                balance = r.json()['balance']
            else:
                logger.warning(">>>>> "+chain+" via explorer.aryacoin.io FAILED | addr: "+addr+" | "+str(r.text))

    except Exception as e:
        logger.warning(">>>>> "+chain+" FAILED | addr: "+addr+" | "+str(e))
    return balance
