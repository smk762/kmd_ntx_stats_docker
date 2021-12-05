#!/usr/bin/env python3
import json
import time
import codecs
import random
import socket
import requests
from kmd_ntx_api.lib_const import *
from kmd_ntx_api.lib_base58 import *
import kmd_ntx_api.lib_dexstats as dexstats


def get_utxo_count(chain, pubkey, server):
    try:
        endpoint = f"{THIS_SERVER}/api/info/electrums"
        electrums_info = requests.get(f"{endpoint}").json()["results"]

        block_tip = dexstats.get_blocktip(chain)

        if chain in ["PIRATE", "NINJA", "MESH", "AXO"]:
            address = calc_addr_from_pubkey("KMD", pubkey)
            resp = dexstats.get_utxos(chain, address)
            utxos = []
            utxo_count = 0
            dpow_utxo_count = 0
            for item in resp:

                if item['satoshis'] == 10000:
                    dpow_utxo_count += 1
                    item.update({"dpow_utxo": True})
                else:
                    item.update({"dpow_utxo": False})

                utxo_count += 1
                utxos.append(item)

            return {
                "block_tip": block_tip,
                "utxo_count": utxo_count,
                "dpow_utxo_count": dpow_utxo_count,
                "utxos": utxos,
            }
        else:
            if chain == "GLEEC" and server == "Third_Party":
                chain = "GLEEC-OLD"
            if chain in electrums_info:
                electrum = random.choice(electrums_info[chain]).split(": ")
                url = electrum[0]
                port = electrum[1]
                logger.info(f"{chain} {url}:{port} {pubkey}")
                p2pk_scripthash = get_p2pk_scripthash_from_pubkey(pubkey)
                p2pk_resp = get_from_electrum(
                    url, port, 'blockchain.scripthash.listunspent',
                    p2pk_scripthash)
                p2pkh_scripthash = get_p2pkh_scripthash_from_pubkey(pubkey)
                p2pkh_resp = get_from_electrum(
                    url, port, 'blockchain.scripthash.listunspent',
                    p2pkh_scripthash)
                headers_resp = get_from_electrum(
                    url, port, 'blockchain.headers.subscribe')

                block_tip = headers_resp['result']['height']
                resp = p2pk_resp['result'] + p2pkh_resp['result']
                utxos = []
                utxo_count = 0
                dpow_utxo_count = 0
                for item in resp:
                    if item["value"] > 0:
                        utxos.append(item)

                if chain in ["AYA", "EMC2", "SFUSD"]:
                    utxo_size = 100000
                else:
                    utxo_size = 10000

                for item in utxos:
                    utxo_count += 1
                    if item['value'] == utxo_size:
                        dpow_utxo_count += 1
                        item.update({"dpow_utxo": True})
                    else:
                        item.update({"dpow_utxo": False})

                return {
                    "block_tip": block_tip,
                    "utxo_count": utxo_count,
                    "dpow_utxo_count": dpow_utxo_count,
                    "utxos": utxos,
                }

            else:
                return {"error": f"{chain} not in electrums"}
                logger.info(f"{chain} not in electrums")
    except Exception as e:
        return {
            "error": f"{e}",
            "resp": []
        }
        logger.error(e)

def get_balance(coin, address):
    sh = get_scripthash_from_address(address)

def get_scripthash_from_address(address):
    # remove address prefix
    addr_stripped = binascii.hexlify(b58decode_check(address)[1:])
    # Add OP_DUP OP_HASH160 BTYES_PUSHED <ADDRESS> OP_EQUALVERIFY OP_CHECKSIG
    raw_sig_script = b"".join((b"76a914", addr_stripped, b"88ac"))
    script_hash = hashlib.sha256(codecs.decode(
        raw_sig_script, 'hex')).digest()[::-1].hex()
    return script_hash


def get_from_electrum(url, port, method, params=[]):
    params = [params] if type(params) is not list else params
    socket.setdefaulttimeout(20)

    s = socket.create_connection((url, port))
    s.send(json.dumps({"id": 0, "method": 'server.version',
                       "params": ['ElectrumX 1.16.0', '1.4']}).encode() + b'\n')
    #print(json.loads(s.recv(999999)[:-1].decode()))
    time.sleep(0.1)
    s.send(json.dumps({"id": 0, "method": method,
                       "params": params}).encode() + b'\n')
    time.sleep(0.1)

    return json.loads(s.recv(999999)[:-1].decode())


def get_p2pk_scripthash_from_pubkey(pubkey):
    scriptpubkey = '21' + pubkey + 'ac'
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


def get_full_electrum_balance(url, port, address=None, pubkey=None):
    if pubkey:
        p2pk_scripthash = get_p2pk_scripthash_from_pubkey(pubkey)
        p2pkh_scripthash = get_p2pkh_scripthash_from_pubkey(pubkey)
        p2pkh_resp = get_from_electrum(
            url, port, 'blockchain.scripthash.get_balance', p2pkh_scripthash)
        p2pkh_confirmed_balance = p2pkh_resp['result']['confirmed']
        p2pkh_unconfirmed_balance = p2pkh_resp['result']['unconfirmed']
    elif address:
        p2pk_scripthash = get_scripthash_from_address(address)
        p2pkh_confirmed_balance = 0
        p2pkh_unconfirmed_balance = 0
    else:
        return -1
    p2pk_resp = get_from_electrum(
        url, port, 'blockchain.scripthash.get_balance', p2pk_scripthash)
    #print(p2pk_resp)
    p2pk_confirmed_balance = p2pk_resp['result']['confirmed']
    p2pk_unconfirmed_balance = p2pk_resp['result']['unconfirmed']

    total_confirmed = p2pk_confirmed_balance + p2pkh_confirmed_balance
    total_unconfirmed = p2pk_unconfirmed_balance + p2pkh_unconfirmed_balance

    total = total_confirmed + total_unconfirmed
    return total/100000000
    # NINJA returns "1", TODO: check electrum version etc.
