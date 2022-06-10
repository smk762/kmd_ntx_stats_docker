#!/usr/bin/env python3
import hashlib
import binascii
import bitcoin
from bitcoin.core import x
from bitcoin.core import CoreMainParams
from bitcoin.wallet import P2PKHBitcoinAddress
from base58 import b58decode_check
from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_dexstats as dexstats
import kmd_ntx_api.lib_info as info
import kmd_ntx_api.lib_helper as helper


class raw_tx():
    def __init__(self, version='04000080', group_id='85202f89',
                 inputs=list, sequence='feffffff', outputs=list,
                 expiry_ht='00000000', locktime=int(time.time()-5*60),
                 valueBalanceSapling="0000000000000000",
                 nSpendsSapling="0", vSpendsSapling="00",
                 nOutputsSapling="0", vOutputsSapling="00"):
        self.version = version
        self.group_id = group_id
        self.inputs = inputs
        self.sequence = sequence
        self.outputs = outputs
        # TODO: by default, 200 blocks past current tip
        self.expiry_ht = expiry_ht
        self.locktime = locktime  # time.now()
        self.valueBalanceSapling = valueBalanceSapling
        self.nSpendsSapling = nSpendsSapling
        self.vSpendsSapling = vSpendsSapling
        self.nOutputsSapling = nOutputsSapling
        self.vOutputsSapling = vOutputsSapling

    def construct(self):
        self.locktime = lil_endian(get_hex(self.locktime, byte_length=8))
        self.raw_tx_str = self.version+self.group_id
        self.len_inputs = get_hex(len(self.inputs), byte_length=2)
        self.raw_tx_str += self.len_inputs
        self.expiry_ht = lil_endian(
            get_hex(int(self.expiry_ht), byte_length=8))
        self.sum_inputs = 0
        for vin in self.inputs:
            self.raw_tx_str += lil_endian(vin["tx_hash"])
            self.raw_tx_str += lil_endian(
                get_hex(vin["tx_pos"], byte_length=8))
            self.sum_inputs += vin["value"]*100000000
            if "unlocking_script" in vin:
                unlocking_script = vin["unlocking_script"]
            else:
                unlocking_script = ""
            pubkey = vin["scriptPubKey"]
            self.len_script = get_hex(
                len(unlocking_script+"0121"+pubkey)/2, byte_length=2)

            if unlocking_script == "":
                self.raw_tx_str += "00"
            else:
                self.raw_tx_str += self.len_script
                self.raw_tx_str += unlocking_script
                self.raw_tx_str += "0121"
                self.raw_tx_str += lil_endian(pubkey)

            self.raw_tx_str += self.sequence
        self.sum_outputs = 0
        self.len_outputs = get_hex(len(self.outputs), byte_length=2)
        self.raw_tx_str += self.len_outputs
        i = 0
        for vout in self.outputs:
            amount = float(vout["amount"])*100000000
            self.sum_outputs += amount
            self.raw_tx_str += lil_endian(get_hex(amount, byte_length=16))
            address = vout["address"]
            pubKeyHash = address_to_p2pkh(address)
            self.raw_tx_str += get_hex(len(pubKeyHash)/2, byte_length=2)
            self.raw_tx_str += pubKeyHash
        self.raw_tx_str += self.locktime
        self.raw_tx_str += self.expiry_ht
        self.raw_tx_str += self.valueBalanceSapling
        self.raw_tx_str += self.nSpendsSapling
        self.raw_tx_str += self.vSpendsSapling
        self.raw_tx_str += self.nOutputsSapling
        self.raw_tx_str += self.vOutputsSapling
        return self.raw_tx_str


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

for _coin in dexstats.DEXSTATS_COINS:
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
    return not helper.has_error(resp)


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

    coins_list = info.get_all_coins() 
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

    try:
        endpoint = f"{THIS_SERVER}/api/info/base_58/"
        base58_coins = requests.get(endpoint).json()["results"]
    except Exception as e:
        return {"Error": f"cant get base58_coins from {endpoint} - {e}"}

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


