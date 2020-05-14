#!/usr/bin/env python3
import requests
from coins_lib import third_party_coins, antara_coins, ex_antara_coins, all_antara_coins, all_coins
import socket
import json
import base58
import logging
import logging.handlers

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

'''
 rpc validateaddress > scriptpubkey
 256_hash the scriptpubkey
 endian reverse -> electrum

addr = 'RT2auNGywenHJW3iiEAQxfJfFwqzMvVCxy'
scriptpubkey = '76a914c2af13fb5dc17581e42914887ef5c25317c7088388ac'
'''
import hashlib
import codecs


addr = 'RRfUCLxfT5NMpxsC9GHVbdfVy5WJnJFQLV'
scriptpubkey = '76a914b3b89e3c87e3fed305f6656cfdd6e1c12ce6dbab88ac'
pub = '0224a9d951d3a06d8e941cc7362b788bb1237bb0d56cc313e797eb027f37c2d375'

def addr_to_script_pub(addr):
    return "76a914"+base58.b58decode_check(addr).hex()[2:]+"88ac"

def lil_endian(hex_str):
    return ''.join([hex_str[i:i+2] for i in range(0, len(hex_str), 2)][::-1])

def pubkey_to_scripthash(pubkey):
    publickey = codecs.decode(pubkey, 'hex')
    s = hashlib.new('sha256', publickey).digest()
    r = hashlib.new('ripemd160', s).digest()
    # return codecs.encode(r, 'hex').decode("utf-8")
    return "76a914"+codecs.encode(r, 'hex').decode("utf-8")+"88ac"

def scripthash_to_p2sh(scripthash):
    scripthex = codecs.decode(scripthash, 'hex')
    s = hashlib.new('sha256', scripthex).digest()
    return codecs.encode(s, 'hex').decode("utf-8")

print(scriptpubkey)
print(addr_to_script_pub(addr))
sh = pubkey_to_scripthash(pub)
print(sh)
p2sh = scripthash_to_p2sh(sh)
print(p2sh)
script_hash = lil_endian(p2sh)
print(script_hash)
print("---------------------------------------------------")




def addr_to_p2pkh():
    pass

def get_scripthash(script_pub):
    print("script_pub: "+script_pub)
    scriptpub_256 = hashlib.sha256(scriptpubkey.encode('utf-8')).hexdigest()
    print("sha256 hash: "+scriptpub_256)
    scripthash = lil_endian(scriptpub_256)
    print("scripthash: "+scripthash)
    return scripthash


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



r = requests.get('http://notary.earth:8762/info/coins/?dpow_active=1')
coins_info = r.json()
for coin in coins_info['results'][0]:
    if len(coins_info['results'][0][coin]['electrums']) > 0:
        electrum = coins_info['results'][0][coin]['electrums'][0].split(":")
        print(coin+": "+str(electrum))
        url = electrum[0]
        port = electrum[1]

        resp = get_from_electrum(url, port, 'blockchain.scripthash.get_balance', script_hash)
        print(coin+": "+str(resp))
    else:
        print("No electrums for "+coin)
