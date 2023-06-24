#!/usr/bin/env python3
import hashlib
import codecs
import bitcoin
import binascii
import requests
from bitcoin.core import x
from bitcoin.core import CoreMainParams
from bitcoin.wallet import P2PKHBitcoinAddress
import alerts
import lib_urls  


# For more params, check a project's /src/chainparams.cpp file
class KMD_CoinParams(CoreMainParams):
    MESSAGE_START = b'\x24\xe9\x27\x64'
    DEFAULT_PORT = 7770
    BASE58_PREFIXES = {'PUBKEY_ADDR': 60,
                       'SCRIPT_ADDR': 85,
                       'SECRET_KEY': 188}

class PBC_CoinParams(CoreMainParams):
    MESSAGE_START = b'\x24\xe9\x27\x64'
    DEFAULT_PORT = 7770
    BASE58_PREFIXES = {'PUBKEY_ADDR': 60,
                       'SCRIPT_ADDR': 85,
                       'SECRET_KEY': 188}

class SFUSD_CoinParams(CoreMainParams):
    MESSAGE_START = b'\x24\xe9\x27\x64'
    DEFAULT_PORT = 7770
    BASE58_PREFIXES = {'PUBKEY_ADDR': 63,
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

class MIL_CoinParams(CoreMainParams):
    MESSAGE_START = b'\x24\xe9\x27\x64'
    DEFAULT_PORT = 7770
    BASE58_PREFIXES = {'PUBKEY_ADDR': 50,
                       'SCRIPT_ADDR': 196,
                       'SECRET_KEY': 239}
                       
class GLEEC_3P_CoinParams(CoreMainParams):
    MESSAGE_START = b'\x24\xe9\x27\x64'
    DEFAULT_PORT = 7770
    BASE58_PREFIXES = {'PUBKEY_ADDR': 35,
                       'SCRIPT_ADDR': 38,
                       'SECRET_KEY': 65}


COIN_PARAMS = {
    "KMD": KMD_CoinParams,
    "MIL": MIL_CoinParams,
    "VOTE2021": KMD_CoinParams,
    "VOTE2022": KMD_CoinParams,
    "VOTE2023": KMD_CoinParams,
    "KIP0001": KMD_CoinParams,
    "WLC21": KMD_CoinParams,
    "MCL": KMD_CoinParams,
    "RFOX": KMD_CoinParams,
    "STBL": KMD_CoinParams,
    "PGT": KMD_CoinParams,
    "GLEEC": KMD_CoinParams,
    "GLEEC-OLD": GLEEC_3P_CoinParams,
    "PBC": PBC_CoinParams,
    "SFUSD": SFUSD_CoinParams,
    "CHIPS": KMD_CoinParams,
    "TKL": KMD_CoinParams,
    "TOKEL": KMD_CoinParams,
    "VRSC": KMD_CoinParams,
    "BTC": BTC_CoinParams,
    "LTC": LTC_CoinParams,
    "AYA": AYA_CoinParams,
    "EMC2": EMC2_CoinParams,
    "GAME": GAME_CoinParams
}

COINS_INFO = requests.get(lib_urls.get_coins_info_url()).json()['results']

# Defines BASE_58 coin parameters
for coin in COINS_INFO:
    if "pubtype" in COINS_INFO[coin]["coins_info"] and "wiftype" in COINS_INFO[coin]["coins_info"] and "p2shtype" in COINS_INFO[coin]["coins_info"]:
        if COINS_INFO[coin]["coins_info"]["pubtype"] == 60:
            if COINS_INFO[coin]["coins_info"]["wiftype"] == 188:
                if COINS_INFO[coin]["coins_info"]["p2shtype"] == 85:
                    COIN_PARAMS.update({coin: COIN_PARAMS["KMD"]})

    elif "dpow" in COINS_INFO[coin]:
        if "server" in COINS_INFO[coin]["dpow"]:
            if COINS_INFO[coin]["dpow"]["server"] == "Third_Party":
                if coin in COIN_PARAMS:
                    COIN_PARAMS.update({coin: COIN_PARAMS[coin]})
                else:
                    print(alerts.send_telegram(f"{__name__}: {coin} doesnt have params defined!"))


SMARTCHAIN_BASE_58 = {
                "pubtype": 60,
                "p2shtype": 85,
                "wiftype": 188,
                "txfee": 1000
            }


def get_addr_from_pubkey(coin, pubkey):
    if coin in COIN_PARAMS:
        bitcoin.params = COIN_PARAMS[coin]
        return str(P2PKHBitcoinAddress.from_pubkey(x(pubkey)))
    return None


def get_opret_ticker(scriptPubKey_asm):
    
    scriptPubKeyBinary = binascii.unhexlify(scriptPubKey_asm[70:])
    coin = ''
    while len(coin) < 1:
        for i in range(len(scriptPubKeyBinary)):
            if chr(scriptPubKeyBinary[i]).encode() == b'\x00':
                j = i+1
                while j < len(scriptPubKeyBinary)-1:
                    coin += chr(scriptPubKeyBinary[j])
                    j += 1
                    if chr(scriptPubKeyBinary[j]).encode() == b'\x00':
                        break
                break
    if chr(scriptPubKeyBinary[-4])+chr(scriptPubKeyBinary[-3])+chr(scriptPubKeyBinary[-2]) == "KMD":
        coin = "KMD"

    # some decodes have a null char error, this gets rid of that so populate script doesnt error out 
    if coin.find('\x00') != -1:
        coin = coin.replace('\x00','')

    return str(coin)
    

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


def lil_endian(hex_str):
    return ''.join([hex_str[i:i+2] for i in range(0, len(hex_str), 2)][::-1])
