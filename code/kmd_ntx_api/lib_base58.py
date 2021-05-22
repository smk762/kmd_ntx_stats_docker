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

def sha256(data):
    digest = hashlib.new("sha256")
    digest.update(data)
    return digest.digest()

def ripemd160(x):
    d = hashlib.new("ripemd160")
    d.update(x)
    return d.digest()

def doubleSha256(hex_str): 
   hexbin = binascii.unhexlify(hex_str)
   binhash = hashlib.sha256(hexbin).digest()
   hash2 = hashlib.sha256(binhash).digest()
   return hash2

def get_hex(val, byte_length=2):
    val = hex(new_format)[2:]
    pad_len = byte_length - len(val)
    val = pad_len*"0"+val
    return val        

def get_hash160(pubkey):
    bin_pk = binascii.unhexlify(pubkey)
    sha_pk = sha256(bin_pk)
    ripe_pk = ripemd160(sha_pk)
    return binascii.hexlify(ripe_pk)

def address_to_p2pkh(address):
    # decode base58
    decode_58 = bitcoin.base58.decode(address)
    # remove prefix and checksum
    decode_58 = decode_58[1:-4]
    # Add OP codes
    pubKeyHash = "76a914"+binascii.hexlify(decode_58).decode('ascii')+"88ac"
    return pubKeyHash

def pubkey_to_p2pkh(pubkey):
    # Get HASH160 of pubkey
    hash160 = get_hash160(pubkey)
    # Add OP codes
    p2pkh = "76a914"+hash160.decode('ascii')+"88ac"
    return p2pkh

def pubkey_to_p2pk(pubkey):
    # Get HASH160 of pubkey
    hash160 = get_hash160(pubkey)
    # Add OP codes
    p2pk = "21"+pubkey+"ac"
    return p2pk

class raw_tx():
    def __init__(self, version='04000080', group_id='85202f89', inputs=list,
                 sequence='feffffff', outputs=list,
                 expiry_height=0, locktime='', 
                 valueBalanceSapling="0000000000000000", nSpendsSapling="0",
                 vSpendsSapling="00", nOutputsSapling="0", vOutputsSapling="00"):
        self.version = version
        self.group_id = group_id
        self.inputs = inputs
        self.sequence = sequence
        self.outputs = outputs
        self.expiry_height = expiry_height
        self.locktime = locktime
        self.valueBalanceSapling = valueBalanceSapling
        self.nSpendsSapling = nSpendsSapling
        self.vSpendsSapling = vSpendsSapling
        self.nOutputsSapling = nOutputsSapling
        self.vOutputsSapling = vOutputsSapling

    def construct(self):
        self.raw_tx_str = self.version+self.group_id
        self.len_inputs = get_hex(len(self.inputs), byte_length=2)
        self.raw_tx_str += self.len_inputs
        self.vin_value = 0
        for vin in inputs:
            self.raw_tx_str += self.vin["txid"]
            self.raw_tx_str += self.vin["tx_pos"]
            self.vin_value += self.vin["value"]
            if "unlocking_script" in self.vin:
                unlocking_script = self.vin["unlocking_script"]
            else:
                unlocking_script = "00"
            pubkey = self.vin["pubkey"]
            self.len_script = len(self.unlocking_script+"0121"+pubkey)

            self.raw_tx_str += self.len_script
            self.raw_tx_str += "0121"
            self.raw_tx_str += self.pubkey            

        self.len_outputs = get_hex(len(self.outputs), byte_length=2)
        self.raw_tx_str += self.len_outputs
        for vout in outputs:
            amount = vout["amount"]
            self.raw_tx_str += amount
            self.raw_tx_str += get_hex(len(vout["scriptPubkey"]), byte_length=8)
            self.raw_tx_str += vout["scriptPubkey"]
        self.raw_tx_str += self.locktime
        self.raw_tx_str += self.expiry_height
        self.raw_tx_str += self.valueBalanceSapling
        self.raw_tx_str += self.nSpendsSapling
        self.raw_tx_str += self.vSpendsSapling
        self.raw_tx_str += self.nOutputsSapling
        self.raw_tx_str += self.vOutputsSapling
        return self.raw_tx_str


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
        checksum = doubleSha256(new_ripemedhash)[:4] # first 4 bytes, sha256 new_ripemedhash twice 
        new_ripemedhash_full = new_ripemedhash + binascii.hexlify(checksum)
        new_address = bitcoin.base58.encode(binascii.unhexlify(new_ripemedhash_full))
        print(f"{coin} address: {new_address}")
        resp["results"].append({f"{coin}":new_address})

    return resp
