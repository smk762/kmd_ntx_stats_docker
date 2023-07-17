#!/usr/bin/env python3
import codecs
import hashlib
import binascii
import bitcoin
from bitcoin.core import x
from bitcoin.core import CoreMainParams
from bitcoin.wallet import P2PKHBitcoinAddress
import hashlib
import binascii
from base58 import b58decode_check
from kmd_ntx_api.const import OP_DUP, OP_HASH160, OP_EQUALVERIFY, OP_CHECKSIG
from kmd_ntx_api.const import EXCLUDE_DECODE_OPRET_COINS, noMoM, SMARTCHAINS
from kmd_ntx_api.info import get_all_coins
from kmd_ntx_api.cache_data import b58_params_cache
from kmd_ntx_api.helper import has_error
from kmd_ntx_api.logger import logger


OP_CODES = {
    "OP_RETURN": "6a",
    "OP_PUSHDATA1": "4c",
    "OP_PUSHDATA2": "4d",
    "OP_CHECKSIG": "ac", 
    "OP_FALSE": "00",
    "OP_IF": "63",
    "OP_NOTIF": "64",
    "OP_ELSE": "67",
    "OP_ENDIF": "68",
    "OP_VERIFY": "69",
    "OP_DUP": "76"
}


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


class MIL_CoinParams(CoreMainParams):
    MESSAGE_START = b'\x24\xe9\x27\x64'
    DEFAULT_PORT = 7770
    BASE58_PREFIXES = {'PUBKEY_ADDR': 50,
                       'SCRIPT_ADDR': 196,
                       'SECRET_KEY': 239}


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


class GLEEC_OLD_CoinParams(CoreMainParams):
    MESSAGE_START = b'\x24\xe9\x27\x64'
    DEFAULT_PORT = 7770
    BASE58_PREFIXES = {'PUBKEY_ADDR': 35,
                       'SCRIPT_ADDR': 38,
                       'SECRET_KEY': 65}


COIN_PARAMS = {
    "KMD": KMD_CoinParams,
    "MCL": KMD_CoinParams,
    "MIL": MIL_CoinParams,
    "CHIPS": KMD_CoinParams,
    "VRSC": KMD_CoinParams,
    "PGT": KMD_CoinParams,
    "BTC": BTC_CoinParams,
    "RFOX": KMD_CoinParams,
    "STBL": KMD_CoinParams,
    "TKL": KMD_CoinParams,
    "TOKEL": KMD_CoinParams,
    "VOTE2021": KMD_CoinParams,
    "VOTE2022": KMD_CoinParams,
    "WLC21": KMD_CoinParams,
    "LTC": LTC_CoinParams,
    "AYA": AYA_CoinParams,
    "EMC2": EMC2_CoinParams,
    "GAME": GAME_CoinParams,
    "GLEEC-OLD": GLEEC_OLD_CoinParams,
    "GLEEC": KMD_CoinParams
}

for _coin in SMARTCHAINS:
    COIN_PARAMS.update({_coin: KMD_CoinParams})


def sha256(data):
    d = hashlib.new("sha256")
    d.update(data)
    return d.digest()


def ripemd160(x):
    d = hashlib.new("ripemd160")
    d.update(x)
    return d.digest()


def doubleSha256(hex_str):
    hexbin = binascii.unhexlify(hex_str)
    binhash = hashlib.sha256(hexbin).digest()
    hash2 = hashlib.sha256(binhash).digest()
    return hash2


def get_hex(val, byte_length=2, endian='big'):
    val = hex(int(val))[2:]
    pad_len = byte_length - len(val)
    val = pad_len*"0"+val
    if endian == 'little':
        val = lil_endian(val)
    return val


def get_hash160(pubkey):
    bin_pk = binascii.unhexlify(pubkey)
    sha_pk = sha256(bin_pk)
    ripe_pk = ripemd160(sha_pk)
    return binascii.hexlify(ripe_pk)


def address_to_p2pkh(address):
    decode_58 = bitcoin.base58.decode(address)
    decode_58 = decode_58[1:-4]
    pubKeyHash = "76a914"+binascii.hexlify(decode_58).decode('ascii')+"88ac"
    return pubKeyHash


def pubkey_to_p2pkh(pubkey):
    hash160 = get_hash160(pubkey)
    p2pkh = "76a914"+hash160.decode('ascii')+"88ac"
    return p2pkh


def pubkey_to_p2pk(pubkey):
    hash160 = get_hash160(pubkey)
    p2pk = "21"+pubkey+"ac"
    return p2pk


def calc_addr_from_pubkey(coin, pubkey):
    bitcoin.params = COIN_PARAMS[coin]
    try:
        return str(P2PKHBitcoinAddress.from_pubkey(x(pubkey)))
    except Exception as e:
        logger.error(f"[calc_addr_from_pubkey] Exception: {e}")
        return {"error": str(e)}


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
            "pubkey": pubkey,
            "pubtype": pubtype,
            "p2shtype": p2shtype,
            "wiftype": wiftype,
            "address": address
        }

    except Exception as e:
        logger.error(f"[calc_addr_tool] Exception: {e}")
        return {"error": str(e)}


# OP_RETURN functions
def lil_endian(hex_str):
    return ''.join([hex_str[i:i+2] for i in range(0, len(hex_str), 2)][::-1])


def validate_pubkey(pubkey):
    resp = calc_addr_from_pubkey("KMD", pubkey)
    return not has_error(resp)


def get_ticker(x):
    coin = ''
    while len(coin) < 1:
        for i in range(len(x)):
            if chr(x[i]).encode() == b'\x00':
                j = i+1
                while j < len(x)-1:
                    coin += chr(x[j])
                    j += 1
                    if chr(x[j]).encode() == b'\x00':
                        break
                break
    if chr(x[-4])+chr(x[-3])+chr(x[-2]) == "KMD":
        coin = "KMD"
    return coin


def decode_opret(op_return):
    op_return = op_return.replace("OP_RETURN ", "")
    if op_return.startswith("6a"):
        datalen_byte = op_return[2:4]
        datalen = int(datalen_byte, 16)
        if len(op_return) == datalen * 2 + 4:
            op_return = op_return[4:]

    ac_ntx_blockhash = lil_endian(op_return[:64])

    try:
        ac_ntx_height = int(lil_endian(op_return[64:72]), 16)

    except Exception as e:
        logger.error(f"[decode_opret] Exception: {e}")
        err = {"error": f"{op_return} is invalid and can not be decoded. {e}"}
        return err

    x = binascii.unhexlify(op_return[70:])
    coin = get_ticker(x)

    coins_list = get_all_coins() 
    for x in coins_list:
        if len(x) > 2 and x not in EXCLUDE_DECODE_OPRET_COINS:
            if coin.endswith(x):
                coin = x

    if coin == "KMD":
        btc_txid = lil_endian(op_return[72:136])

    elif coin not in noMoM:
        # not sure about this bit, need another source to validate the data
        try:
            start = 72+len(coin)*2+4
            end = 72+len(coin)*2+4+64
            MoM_hash = lil_endian(op_return[start:end])
            MoM_depth = int(lil_endian(op_return[end:]), 16)
        except Exception as e:
            logger.error(f"[decode_opret] Exception: {e}")
    resp = {
            "op_return": op_return,
            "coin": coin,
            "notarised_block": ac_ntx_height,
            "notarised_blockhash": ac_ntx_blockhash
        }
    return resp


def convert_addresses(address):
    resp = {
        "results": [],
        "errors": []
    }

    base58_coins = b58_params_cache()

    for coin in base58_coins:
        decoded_bytes = bitcoin.base58.decode(address)
        addr_format = decoded_bytes[0]    # PUBKEY_ADDR
        addr = decoded_bytes[1:-4]        # RIPEMD-160 hash
        checksum = decoded_bytes[-4:]
        calculated_checksum = bitcoin.core.Hash(decoded_bytes[:-4])[:4]

        if checksum != calculated_checksum:
            resp["errors"].append(
                f"Checksum {coin} mismatch: expected {checksum},"
                f" got {calculated_checksum}")

        new_format = base58_coins[coin]['pubtype']
        if new_format < 16:
            new_addr_format = f"0{hex(new_format)[2:]}"
        else:
            new_addr_format = hex(new_format)[2:]

        new_ripemedhash = new_addr_format.encode(
            'ascii') + binascii.hexlify(addr)
        # first 4 bytes, sha256 new_ripemedhash twice
        checksum = doubleSha256(new_ripemedhash)[:4]
        ripemedhash_full = new_ripemedhash + binascii.hexlify(checksum)
        new_address = bitcoin.base58.encode(
            binascii.unhexlify(ripemedhash_full))
        resp["results"].append({f"{coin}": new_address})

    return resp


def get_p2pkh_scripthash_from_address(address):
    # remove address prefix
    addr_stripped = binascii.hexlify(b58decode_check(address)[1:])
    # Add OP_DUP OP_HASH160 BTYES_PUSHED <ADDRESS> OP_EQUALVERIFY OP_CHECKSIG
    raw_sig_script = b"".join((b"76a914", addr_stripped, b"88ac"))
    script_hash = hashlib.sha256(
        codecs.decode(raw_sig_script, 'hex')
    ).digest()[::-1].hex()
    return script_hash


def get_p2pk_scripthash_from_pubkey(pubkey):
    scriptpubkey = f"21{pubkey}ac"
    scripthex = codecs.decode(scriptpubkey, 'hex')
    s = hashlib.new('sha256', scripthex).digest()
    sha256_scripthash = codecs.encode(s, 'hex').decode("utf-8")
    script_hash = lil_endian(sha256_scripthash)
    return script_hash


def get_p2pkh_scripthash_from_pubkey(pubkey):
    publickey = codecs.decode(pubkey, 'hex')
    s = hashlib.new('sha256', publickey).digest()
    r = hashlib.new('ripemd160', s).digest()
    scriptpubkey = OP_DUP \
                 + OP_HASH160 \
                 + '14' \
                 + codecs.encode(r, 'hex').decode("utf-8") \
                 + OP_EQUALVERIFY \
                 + OP_CHECKSIG 
    scriptpubkey = "76a914"+codecs.encode(r, 'hex').decode("utf-8")+"88ac"
    h = codecs.decode(scriptpubkey, 'hex')
    s = hashlib.new('sha256', h).digest()
    sha256_scripthash = codecs.encode(s, 'hex').decode("utf-8")
    script_hash = lil_endian(sha256_scripthash)
    return script_hash
