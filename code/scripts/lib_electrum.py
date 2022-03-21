#!/usr/bin/env python3
import json
import socket
from lib_const import ELECTRUMS
from lib_crypto import *


def get_from_electrum(url, port, method, params=[]):
    params = [params] if not isinstance(params, list) else params
    socket.setdefaulttimeout(5)
    s = socket.create_connection((url, port))
    s.send(json.dumps({"id": 0, "method": method, "params": params}).encode() + b'\n')
    return json.loads(s.recv(99999)[:-1].decode())


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


def get_listunspent(chain, pubkey):
    try:
        if chain in ELECTRUMS:
            url = ELECTRUMS[chain]["url"]
            port = ELECTRUMS[chain]["port"]
            logger.info(f"{chain} {url}:{port}")
            p2pk_scripthash = get_p2pk_scripthash_from_pubkey(pubkey)
            p2pk_resp = get_from_electrum(url, port, 'blockchain.scripthash.listunspent', p2pk_scripthash)
            p2pkh_scripthash = get_p2pkh_scripthash_from_pubkey(pubkey)
            p2pkh_resp = get_from_electrum(url, port, 'blockchain.scripthash.listunspent', p2pkh_scripthash)
            num_unspent = 0
            for item in p2pk_resp['result']:
                if item['value'] == 10000:
                    num_unspent +=1
            return num_unspent
            #unspent = get_full_electrum_balance(pubkey, url, port)
        else:
            logger.info(f"{chain} not in electrums")
    except Exception as e:
        logger.error(e)
