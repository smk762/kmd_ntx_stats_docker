import bitcoin
from bitcoin.core import x
from bitcoin.core import CoreMainParams
from bitcoin.wallet import P2PKHBitcoinAddress

# check /src/chainparams.cpp for params

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

def get_addr_from_pubkey(coin, pubkey):
    bitcoin.params = COIN_PARAMS[coin]
    return str(P2PKHBitcoinAddress.from_pubkey(x(pubkey)))

SMARTCHAIN_BASE_58 = {
                "pubtype": 60,
                "p2shtype": 85,
                "wiftype": 188,
                "txfee": 1000
            }