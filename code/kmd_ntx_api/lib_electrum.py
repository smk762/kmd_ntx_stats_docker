#!/usr/bin/env python3
import json
import time
import codecs
import random
import ssl
import socket
import hashlib
import binascii
from base58 import b58decode_check
import requests
from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_base58 as b58
import kmd_ntx_api.lib_info as info
import kmd_ntx_api.lib_dexstats as dexstats

# https://electrumx.readthedocs.io/en/latest/

socket.setdefaulttimeout(5)

def get_from_electrum(url, port, method, params=[]):
    params = [params] if not isinstance(params, list) else params
    with socket.create_connection((url, port)) as sock:
        sock.send(json.dumps({"id": 0, "method": method, "params": params}).encode() + b'\n')
        return json.loads(sock.recv(99999)[:-1].decode())


def get_from_electrum_ssl(url, port, method, params=[]):
    params = [params] if not isinstance(params, list) else params
    context = ssl.create_default_context()
    with socket.create_connection((url, port)) as sock:
        with context.wrap_socket(sock, server_hostname=url) as ssock:
            ssock.send(json.dumps({"id": 0, "method": method, "params": params}).encode() + b'\n')
            return json.loads(ssock.recv(99999)[:-1].decode())


def get_p2pkh_scripthash_from_address(address):
    # remove address prefix
    addr_stripped = binascii.hexlify(b58decode_check(address)[1:])
    # Add OP_DUP OP_HASH160 BTYES_PUSHED <ADDRESS> OP_EQUALVERIFY OP_CHECKSIG
    raw_sig_script = b"".join((b"76a914", addr_stripped, b"88ac"))
    script_hash = hashlib.sha256(codecs.decode(
        raw_sig_script, 'hex')).digest()[::-1].hex()
    return script_hash


def get_p2pk_scripthash_from_pubkey(pubkey):
    scriptpubkey = '21' + pubkey + 'ac'
    scripthex = codecs.decode(scriptpubkey, 'hex')
    s = hashlib.new('sha256', scripthex).digest()
    sha256_scripthash = codecs.encode(s, 'hex').decode("utf-8")
    script_hash = b58.lil_endian(sha256_scripthash)
    return script_hash


def get_p2pkh_scripthash_from_pubkey(pubkey):
    publickey = codecs.decode(pubkey, 'hex')
    s = hashlib.new('sha256', publickey).digest()
    r = hashlib.new('ripemd160', s).digest()
    scriptpubkey = "76a914"+codecs.encode(r, 'hex').decode("utf-8")+"88ac"
    h = codecs.decode(scriptpubkey, 'hex')
    s = hashlib.new('sha256', h).digest()
    sha256_scripthash = codecs.encode(s, 'hex').decode("utf-8")
    script_hash = b58.lil_endian(sha256_scripthash)
    return script_hash


def get_full_electrum_balance(url, port, address=None, pubkey=None):
    p2pkh_confirmed_balance = 0
    p2pkh_unconfirmed_balance = 0
    p2pk_confirmed_balance = 0
    p2pk_unconfirmed_balance = 0
    if pubkey:
        p2pk_scripthash = get_p2pk_scripthash_from_pubkey(pubkey)
        p2pkh_scripthash = get_p2pkh_scripthash_from_pubkey(pubkey)
        p2pkh_resp = get_from_electrum(
            url, port, 'blockchain.scripthash.get_balance', p2pkh_scripthash)
        if 'result' in p2pkh_resp:
            if 'confirmed' in p2pkh_resp['result']:
                p2pkh_confirmed_balance = p2pkh_resp['result']['confirmed']
                p2pkh_unconfirmed_balance = p2pkh_resp['result']['unconfirmed']
    elif address:
        p2pk_scripthash = get_p2pkh_scripthash_from_address(address)
    else:
        return -1
    p2pk_resp = get_from_electrum(
        url, port, 'blockchain.scripthash.get_balance', p2pk_scripthash)
    if 'result' in p2pk_resp:
        if not isinstance(p2pk_resp['result'], int):
            p2pk_confirmed_balance = p2pk_resp['result']['confirmed']
            p2pk_unconfirmed_balance = p2pk_resp['result']['unconfirmed']

    total_confirmed = p2pk_confirmed_balance + p2pkh_confirmed_balance
    total_unconfirmed = p2pk_unconfirmed_balance + p2pkh_unconfirmed_balance

    total = total_confirmed + total_unconfirmed
    return total/100000000
    # NINJA returns "1", TODO: check electrum version etc.


def broadcast_raw_tx(url, port, raw_tx, ssl):
    if ssl:
        return get_from_electrum_ssl(url, port, 'blockchain.transaction.broadcast', raw_tx)
    return get_from_electrum(url, port, 'blockchain.transaction.broadcast', raw_tx)

def get_coin_electrum(coin):
    url = None
    port = None
    ssl = True
    coin_electrums = info.get_coin_electrums_ssl(coin)
    if len(coin_electrums) == 0:
        ssl = False
        coin_electrums = info.get_coin_electrums(coin)

    if len(coin_electrums) != 0:
        electrum_ = random.choice(coin_electrums).split(":")
        url = electrum_[0]
        port = electrum_[1]

    return url, port, ssl