#!/usr/bin/env python3
import requests
from coins_lib import third_party_coins, antara_coins, ex_antara_coins, all_antara_coins, all_coins
import socket
import json
import base58
from hashlib import sha256

def get_scripthash_256(addr):
    scriptpub = base58.b58decode_check(addr).hex()[2:]
    lilendian_scriptpub = lil_endian(scriptpub)
    scriptpub_256 = sha256(lilendian_scriptpub.encode('utf-8')).hexdigest()
    return scriptpub_256

def lil_endian(hex_str):
    return ''.join([hex_str[i:i+2] for i in range(0, len(hex_str), 2)][::-1])

def get_ac_block_heights():
    ac_block_height = {}
    for chain in antara_coins:
      try:
        url = 'http://'+chain.lower()+'.explorer.dexstats.info/insight-api-komodo/sync'
        r = requests.get(url)
        ac_block_height.update({chain:r.json()['blockChainHeight']})
      except Exception as e:
        print(chain+" failed")
        print(e)
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
    balance = 0
    try:
        if chain in antara_coins or chain in ["HUSH3", "KMD"]:
            url = 'http://'+chain.lower()+'.explorer.dexstats.info/insight-api-komodo/addr/'+addr
            r = requests.get(url)
            balance = r.json()['balance']
        elif chain == "CHIPS":
            addr = get_scripthash_256(addr)
            resp = get_from_electrum('electrum3.cipig.net', 10053, 'blockchain.scripthash.get_balance', addr)
            balance = resp['result']['confirmed']
        elif chain == "EMC2":
            addr = get_scripthash_256(addr)
            resp = get_from_electrum('electrum3.cipig.net', 10062, 'blockchain.scripthash.get_balance', addr)
            balance = resp['result']['confirmed']
        elif chain == "GAME":
            addr = get_scripthash_256(addr)
            resp = get_from_electrum('electrum2.cipig.net', 10072, 'blockchain.scripthash.get_balance', addr)
            balance = resp['result']['confirmed']
        elif chain == "GIN":
            # Gin is dead.
            # addr = get_scripthash_256(addr)
            # resp = get_from_electrum('electrum2.gincoin.io', 6001, 'blockchain.scripthash.get_balance', addr)
            # balance = resp['result']['confirmed']
            return 0
        elif chain == "AYA":
            url = 'https://explorer.aryacoin.io/ext/getaddress/'+addr
            r = requests.get(url)
            if 'balance' in r.json():
                balance = r.json()['balance']
            else:
                print(r.json())
            

    except Exception as e:
        if chain not in ex_antara_coins:
            print(chain+" failed")
            print(e)
    return balance