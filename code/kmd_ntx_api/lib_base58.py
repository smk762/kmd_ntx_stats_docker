#!/usr/bin/env python3
import hashlib
import binascii
import bitcoin
from bitcoin.core import x
from bitcoin.core import CoreMainParams
from bitcoin.wallet import P2PKHBitcoinAddress
from base58 import b58decode_check
from .lib_const import *

class KMD_CoinParams(CoreMainParams):
    MESSAGE_START = b'\x24\xe9\x27\x64'
    DEFAULT_PORT = 7770
    BASE58_PREFIXES = {'PUBKEY_ADDR': 60,
                       'SCRIPT_ADDR': 85,
                       'SECRET_KEY': 188}


class BTC_CoinParams(CoreMainParams):
    MESSAGE_START = b'\x24\xe9\x27\x64'
    DEFAULT_PORT = 7770
    BASE58_PREFIXES = {'PUBKEY_ADDR': 0,
                       'SCRIPT_ADDR': 5,
                       'SECRET_KEY': 128}


class LTC_CoinParams(CoreMainParams):
    MESSAGE_START = b'\x24\xe9\x27\x64'
    DEFAULT_PORT = 7770
    BASE58_PREFIXES = {'PUBKEY_ADDR': 48,
                       'SCRIPT_ADDR': 5,
                       'SECRET_KEY': 176}


class AYA_CoinParams(CoreMainParams):
    MESSAGE_START = b'\x24\xe9\x27\x64'
    DEFAULT_PORT = 7770
    BASE58_PREFIXES = {'PUBKEY_ADDR': 23,
                       'SCRIPT_ADDR': 5,
                       'SECRET_KEY': 176}


class EMC2_CoinParams(CoreMainParams):
    MESSAGE_START = b'\x24\xe9\x27\x64'
    DEFAULT_PORT = 7770
    BASE58_PREFIXES = {'PUBKEY_ADDR': 33,
                       'SCRIPT_ADDR': 5,
                       'SECRET_KEY': 176}


class GAME_CoinParams(CoreMainParams):
    MESSAGE_START = b'\x24\xe9\x27\x64'
    DEFAULT_PORT = 7770
    BASE58_PREFIXES = {'PUBKEY_ADDR': 38,
                       'SCRIPT_ADDR': 5,
                       'SECRET_KEY': 166}

'''
class GLEEC_CoinParams(CoreMainParams):
    MESSAGE_START = b'\x24\xe9\x27\x64'
    DEFAULT_PORT = 7770
    BASE58_PREFIXES = {'PUBKEY_ADDR': 35,
                       'SCRIPT_ADDR': 38,
                       'SECRET_KEY': 65}
'''

COIN_PARAMS = {
    "KMD": KMD_CoinParams,
    "MCL": KMD_CoinParams,
    "SFUSD": KMD_CoinParams,
    "CHIPS": KMD_CoinParams,
    "VRSC": KMD_CoinParams,
    "BTC": BTC_CoinParams,
    "LTC": LTC_CoinParams,
    "AYA": AYA_CoinParams,
    "EMC2": EMC2_CoinParams,
    "GAME": GAME_CoinParams,
    #"GLEEC": GLEEC_CoinParams,
    "GLEEC": KMD_CoinParams
}


def calc_addr_from_pubkey(coin, pubkey):
    bitcoin.params = COIN_PARAMS[coin]
    try:
        return str(P2PKHBitcoinAddress.from_pubkey(x(pubkey)))
    except Exception as e:
        logger.error(f"[calc_addr_from_pubkey] Exception: {e}")
        return {"error":str(e)}


def calc_addr_tool(pubkey, pubtype, p2shtype, wiftype):
    class CoinParams(CoreMainParams):
        MESSAGE_START = b'\x24\xe9\x27\x64'
        DEFAULT_PORT = 7770
        BASE58_PREFIXES = {'PUBKEY_ADDR': int(pubtype),
                           'SCRIPT_ADDR': int(p2shtype),
                           'SECRET_KEY': int(wiftype)}
    bitcoin.params = CoinParams

    try:
        address = str(P2PKHBitcoinAddress.from_pubkey(x(pubkey)))
        return {
            "pubkey":pubkey,
            "pubtype":pubtype,
            "p2shtype":p2shtype,
            "wiftype":wiftype,
            "address":address
        }

    except Exception as e:
        logger.error(f"[calc_addr_tool] Exception: {e}")
        return {"error":str(e)}


# OP_RETURN functions
def lil_endian(hex_str):
    return ''.join([hex_str[i:i+2] for i in range(0, len(hex_str), 2)][::-1])

def validate_pubkey(pubkey):
    resp = calc_addr_from_pubkey("KMD", pubkey)
    if "error" in resp:
        return False
    return True
    
def get_ticker(x):
    chain = ''
    while len(chain) < 1:
        for i in range(len(x)):
            if chr(x[i]).encode() == b'\x00':
                j = i+1
                while j < len(x)-1:
                    chain += chr(x[j])
                    j += 1
                    if chr(x[j]).encode() == b'\x00':
                        break
                break
    if chr(x[-4])+chr(x[-3])+chr(x[-2]) == "KMD":
        chain = "KMD"
    return chain


def decode_opret(op_return, coins_list):  
    
    ac_ntx_blockhash = lil_endian(op_return[:64])

    try:
        ac_ntx_height = int(lil_endian(op_return[64:72]),16) 

    except Exception as e:
        logger.error(f"[decode_opret] Exception: {e}")
        err = {"error":f"{op_return} is invalid and can not be decoded. {e}"}
        logger.error(err)
        return err

    x = binascii.unhexlify(op_return[70:])
    chain = get_ticker(x)

    for x in coins_list:
        if len(x) > 2 and x not in EXCLUDE_DECODE_OPRET_COINS:
            if chain.endswith(x):
                chain = x

    if chain == "KMD":
        btc_txid = lil_endian(op_return[72:136])
        
    elif chain not in noMoM:
        # not sure about this bit, need another source to validate the data
        try:
            start = 72+len(chain)*2+4
            end = 72+len(chain)*2+4+64
            MoM_hash = lil_endian(op_return[start:end])
            MoM_depth = int(lil_endian(op_return[end:]),16)
        except Exception as e:
            logger.error(f"[decode_opret] Exception: {e}")
    resp = { "chain":chain, "notarised_block":ac_ntx_height, "notarised_blockhash":ac_ntx_blockhash }
    return resp


def convert_addresses(address):
    resp = {
        "results":[],
        "errors":[]
    }

    try:
        base58_coins = requests.get(f"{THIS_SERVER}/api/info/base_58/").json()["results"]
    except:
        return {"Error": f"cant get base58_coins from {THIS_SERVER}/api/info/base_58/"}

    for coin in base58_coins:
        decoded_bytes = bitcoin.base58.decode(address)
        addr_format = decoded_bytes[0]    # PUBKEY_ADDR
        addr = decoded_bytes[1:-4]        # RIPEMD-160 hash
        checksum = decoded_bytes[-4:]
        calculated_checksum = bitcoin.core.Hash(decoded_bytes[:-4])[:4]

        if checksum != calculated_checksum:
            resp["errors"].append(f"Checksum {coin} mismatch: expected {checksum}, got {calculated_checksum}")

        new_format = base58_coins[coin]['pubtype']
        if new_format < 16:
            new_addr_format = f"0{hex(new_format)[2:]}"
        else:
            new_addr_format = hex(new_format)[2:]
        
        new_ripemedhash = new_addr_format.encode('ascii') + binascii.hexlify(addr)
        binhash = hashlib.sha256(new_ripemedhash).digest()
        hash2 = hashlib.sha256(binhash).digest()
        checksum = doubleSha256(new_ripemedhash)[:4] # first 4 bytes, sha256 new_ripemedhash twice 
        new_ripemedhash_full = new_ripemedhash + binascii.hexlify(checksum)
        new_address = bitcoin.base58.encode(binascii.unhexlify(new_ripemedhash_full))
        print(f"{coin} address: {new_address}")
        resp["results"].append({f"{coin}":new_address})

    return resp

def doubleSha256(hex_str): 
   hexbin = binascii.unhexlify(hex_str)
   binhash = hashlib.sha256(hexbin).digest()
   hash2 = hashlib.sha256(binhash).digest()
   return hash2