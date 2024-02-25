#!/usr/bin/env python3
import json
import ssl
import socket
from lib_helper import get_electrum_url_port
from lib_const import ELECTRUMS, ELECTRUMS_SSL, ELECTRUMS_WSS, logger
from lib_crypto import *

socket.setdefaulttimeout(5)

def get_from_electrum(url, port, method, params=[]):
    params = [params] if not isinstance(params, list) else params
    with socket.create_connection((url, port)) as sock:
        sock.send(json.dumps({"id": 0, "method": method, "params": params}).encode() + b'\n')
        return json.loads(sock.recv(99999)[:-1].decode())


def get_from_electrum_ssl(url, port, method, params=[]):
    params = [params] if not isinstance(params, list) else params
    context = ssl.create_default_context()
    try:
        with socket.create_connection((url, port)) as sock:
            with context.wrap_socket(sock, server_hostname=url) as ssock:
                ssock.send(json.dumps({"id": 0, "method": method, "params": params}).encode() + b'\n')
                return json.loads(ssock.recv(99999)[:-1].decode())
    except Exception as e:
        return e


def get_full_electrum_balance(pubkey, coin):
    if coin in ELECTRUMS_SSL:
        for electrum in ELECTRUMS_SSL[coin]:
            try:
                url, port = get_electrum_url_port(electrum)
                p2pk_scripthash = get_p2pk_scripthash_from_pubkey(pubkey)
                p2pkh_scripthash = get_p2pkh_scripthash_from_pubkey(pubkey)
                p2pk_resp = get_from_electrum_ssl(url, port, 'blockchain.scripthash.get_balance', p2pk_scripthash)
                p2pkh_resp = get_from_electrum_ssl(url, port, 'blockchain.scripthash.get_balance', p2pkh_scripthash)
                p2pk_confirmed_balance = p2pk_resp['result']['confirmed']
                p2pkh_confirmed_balance = p2pkh_resp['result']['confirmed']
                p2pk_unconfirmed_balance = p2pk_resp['result']['unconfirmed']
                p2pkh_unconfirmed_balance = p2pkh_resp['result']['unconfirmed']
                total_confirmed = p2pk_confirmed_balance + p2pkh_confirmed_balance
                total_unconfirmed = p2pk_unconfirmed_balance + p2pkh_unconfirmed_balance
                total = total_confirmed + total_unconfirmed
                return total/100000000
            except Exception as e:
                print(f"Error in [get_full_electrum_balance] with ELECTRUMS_SSL for {coin}: {e}")

    if coin in ELECTRUMS:
        for electrum in ELECTRUMS[coin]:
            try:
                url, port = get_electrum_url_port(electrum)
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
            except Exception as e:
                print(f"Error in [get_full_electrum_balance] with ELECTRUMS for {coin}: {e}")
    return -1


def get_notary_utxo_count(coin, pubkey):
    if coin in ELECTRUMS_SSL:
        for electrum in ELECTRUMS_SSL[coin]:
            url, port = get_electrum_url_port(electrum)
            p2pk_scripthash = get_p2pk_scripthash_from_pubkey(pubkey)
            p2pk_resp = get_from_electrum_ssl(url, port, 'blockchain.scripthash.listunspent', p2pk_scripthash)
            if not isinstance(p2pk_resp['result'], int):
                num_unspent = 0
                for item in p2pk_resp['result']:
                    if item['value'] == 10000:
                        num_unspent +=1
                return num_unspent
            else:
                print(f"ELECTRUM returning 'int' response for {coin}")


    elif coin in ELECTRUMS:
        for electrum in ELECTRUMS[coin]:
            url, port = get_electrum_url_port(electrum)
            p2pk_scripthash = get_p2pk_scripthash_from_pubkey(pubkey)
            p2pk_resp = get_from_electrum(url, port, 'blockchain.scripthash.listunspent', p2pk_scripthash)
            if not isinstance(p2pk_resp['result'], int):
                num_unspent = 0
                for item in p2pk_resp['result']:
                    if item['value'] == 10000:
                        num_unspent +=1
                return num_unspent
            else:
                print(f"ELECTRUM returning 'int' response for {coin}")
    else:
        logger.info(f"{coin} not in electrums or electrums_ssl")


def get_version(coin):
    if coin in ELECTRUMS_SSL:
        for electrum in ELECTRUMS_SSL[coin]:
            split = electrum.split(":")
            url = split[0]
            port = split[1]
            return get_from_electrum_ssl(url, port, "server.version")

    if coin in ELECTRUMS:
        for electrum in ELECTRUMS[coin]:
            split = electrum.split(":")
            url = split[0]
            port = split[1]
            return get_from_electrum(url, port, "server.version")