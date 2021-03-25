import bitcoin
from bitcoin.core import x
from bitcoin.core import CoreMainParams
from bitcoin.wallet import P2PKHBitcoinAddress

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

class GLEEC_CoinParams(CoreMainParams):
    MESSAGE_START = b'\x24\xe9\x27\x64'
    DEFAULT_PORT = 7770
    BASE58_PREFIXES = {'PUBKEY_ADDR': 35,
                       'SCRIPT_ADDR': 38,
                       'SECRET_KEY': 65}


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
    "GLEEC": GLEEC_CoinParams
}

def get_addr_from_pubkey(coin, pubkey):
    bitcoin.params = COIN_PARAMS[coin]
    try:
      return str(P2PKHBitcoinAddress.from_pubkey(x(pubkey)))
    except Exception as e:
      return str(e)

def get_addr_tool(pubkey, pub_addr, script_addr, secret_key):
    class CoinParams(CoreMainParams):
        MESSAGE_START = b'\x24\xe9\x27\x64'
        DEFAULT_PORT = 7770
        BASE58_PREFIXES = {'PUBKEY_ADDR': int(pub_addr),
                           'SCRIPT_ADDR': int(script_addr),
                           'SECRET_KEY': int(secret_key)}
    bitcoin.params = CoinParams

    try:
        address = str(P2PKHBitcoinAddress.from_pubkey(x(pubkey)))
        return {
            "pubkey":pubkey,
            "pub_addr_param":pub_addr,
            "script_addr_param":script_addr,
            "secret_key_param":secret_key,
            "address":address
        }

    except Exception as e:
        return {"error":str(e)}