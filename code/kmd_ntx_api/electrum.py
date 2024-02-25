#!/usr/bin/env python3
import json
import random
import ssl
import socket
from kmd_ntx_api.helper import get_or_none
from kmd_ntx_api.based_58 import get_p2pk_scripthash_from_pubkey, \
    get_p2pkh_scripthash_from_pubkey, get_p2pkh_scripthash_from_address
from kmd_ntx_api.query import get_coins_data
# https://electrumx.readthedocs.io/en/latest/

socket.setdefaulttimeout(5)

def get_electrums(request) -> dict:
    coin = get_or_none(request, "coin")
    data = get_coins_data(coin)
    data = data.order_by('coin').values('coin', 'electrums')
    resp = {}
    for item in data:
        electrums = item['electrums']
        if len(electrums) > 0:
            resp.update({item['coin']: electrums})
    return resp


def get_electrums_ssl(request):
    coin = get_or_none(request, "coin")
    data = get_coins_data(coin)
    data = data.order_by('coin').values('coin', 'electrums_ssl')
    resp = {}
    for item in data:
        electrums_ssl = item['electrums_ssl']
        if len(electrums_ssl) > 0:
            resp.update({item['coin']: electrums_ssl})
    return resp

def get_electrums_wss(request):
    coin = get_or_none(request, "coin")
    data = get_coins_data(coin)
    data = data.order_by('coin').values('coin', 'electrums_wss')
    resp = {}
    for item in data:
        electrums_wss = item['electrums_wss']
        if len(electrums_wss) > 0:
            resp.update({item['coin']: electrums_wss})
    return resp


def get_coin_electrums(coin):
    data = get_coins_data(coin)
    if data.count() == 1:
        return data[0].values('electrums')[0]['electrums']


def get_coin_electrums_ssl(coin):
    data = get_coins_data(coin)
    if data.count() == 1:
        return data.values('electrums_ssl')[0]['electrums_ssl']


def get_coin_electrums_wss(coin):
    data = get_coins_data(coin)
    if data.count() == 1:
        return data.values('electrums_wss')[0]['electrums_wss']


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
    coin_electrums = get_coin_electrums_ssl(coin)
    if len(coin_electrums) == 0:
        ssl = False
        coin_electrums = get_coin_electrums(coin)

    if len(coin_electrums) != 0:
        electrum_ = random.choice(coin_electrums).split(":")
        url = electrum_[0]
        port = electrum_[1]

    return url, port, ssl
