#!/usr/bin/env python3
import os
import base58
import codecs
import hashlib
import bitcoin
from bitcoin.core import x
from bitcoin.core import CoreMainParams
from bitcoin.wallet import P2PKHBitcoinAddress
import binascii

def sha256(data):
    digest = hashlib.new("sha256")
    digest.update(data)
    return digest.digest()

def doubleSha256(hex_str): 
   hexbin = binascii.unhexlify(hex_str)
   binhash = hashlib.sha256(hexbin).digest()
   hash2 = hashlib.sha256(binhash).digest()
   return hash2

def ripemd160(x):
    d = hashlib.new("ripemd160")
    d.update(x)
    return d.digest()

def get_hash160(pubkey):
    bin_pk = binascii.unhexlify(pubkey)
    sha_pk = sha256(bin_pk)
    ripe_pk = ripemd160(sha_pk)
    return binascii.hexlify(ripe_pk)

def b58(data):
    B58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"

    if data[0] == 0:
        return "1" + b58(data[1:])

    x = sum([v * (256 ** i) for i, v in enumerate(data[::-1])])
    ret = ""
    while x > 0:
        ret = B58[x % 58] + ret
        x = x // 58

    return ret

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

class raw_tx():
    def __init__(self, version='04000080', group_id='85202f89', inputs=list,
                 sequence='feffffff', outputs=list,
                 expiry_height='00000000', locktime='00000000', 
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
        self.sum_inputs = 0
        for vin in self.inputs:
            self.raw_tx_str += lil_endian(vin["tx_hash"])
            self.raw_tx_str += get_hex(vin["tx_pos"], byte_length=8)
            self.sum_inputs += vin["value"]
            if "unlocking_script" in vin:
                unlocking_script = vin["unlocking_script"]
            else:
                unlocking_script = ""
            pubkey = vin["pubkey"]
            print(self.raw_tx_str)
            print(len(unlocking_script))
            print(len(pubkey))
            print(len(unlocking_script+"0121"+pubkey))
            self.len_script = get_hex(len(unlocking_script+"0121"+pubkey)/2, byte_length=2)
            print(self.len_script)

            
            if unlocking_script == "":
                self.raw_tx_str += "00"
            else:
                self.raw_tx_str += self.len_script
                self.raw_tx_str += unlocking_script
                print(self.raw_tx_str)
                self.raw_tx_str += "0121"
                print(lil_endian(pubkey))
                self.raw_tx_str += lil_endian(pubkey)
                print(self.raw_tx_str)


        self.raw_tx_str += self.sequence
        print(self.raw_tx_str)
        self.sum_outputs = 0
        self.len_outputs = get_hex(len(self.outputs), byte_length=2)
        self.raw_tx_str += self.len_outputs
        print(self.raw_tx_str)
        i = 0
        for vout in self.outputs:
            amount = vout["amount"]
            self.sum_outputs += amount
            self.raw_tx_str += lil_endian(get_hex(amount, byte_length=16))
            print(self.raw_tx_str)
            address = vout["address"]
            pubKeyHash = address_to_pubkeyhash(address)
            self.raw_tx_str += get_hex(len(pubKeyHash)/2, byte_length=2)
            print(self.raw_tx_str)
            self.raw_tx_str += pubKeyHash
            print(self.raw_tx_str)
        self.raw_tx_str += self.locktime
        print(self.raw_tx_str)
        self.raw_tx_str += self.expiry_height
        print(self.raw_tx_str)
        self.raw_tx_str += self.valueBalanceSapling
        self.raw_tx_str += self.nSpendsSapling
        self.raw_tx_str += self.vSpendsSapling
        self.raw_tx_str += self.nOutputsSapling
        self.raw_tx_str += self.vOutputsSapling
        print(f"sum_inputs: {self.sum_inputs}")
        print(f"sum_outputs: {self.sum_outputs}")
        print(f"fee: {self.sum_inputs-self.sum_outputs}")
        return self.raw_tx_str

def lil_endian(hex_str):
    return ''.join([hex_str[i:i+2] for i in range(0, len(hex_str), 2)][::-1])

def get_hex(val, byte_length=2, endian='big'):
    print(f"Val: {val}")
    val = hex(int(val))[2:]
    pad_len = byte_length - len(val)
    val = pad_len*"0"+val
    if endian == 'little':
        val = lil_endian(val)
    return val


def address_to_p2pkh_scripthash(address):
    # remove address prefix
    addr_stripped = binascii.hexlify(base58.b58decode_check(address)[1:])
    # Add OP_DUP OP_HASH160 BTYES_PUSHED <ADDRESS> OP_EQUALVERIFY OP_CHECKSIG
    raw_sig_script = b"".join((b"76a914", addr_stripped, b"88ac"))
    script_hash = hashlib.sha256(codecs.decode(raw_sig_script, 'hex')).digest()[::-1].hex()
    return script_hash

def address_to_pubkeyhash(address):
    # decode base58
    decode_58 = bitcoin.base58.decode(address)
    # remove prefix and checksum
    decode_58 = decode_58[1:-4]
    # Add OP codes
    pubKeyHash = "76a914"+binascii.hexlify(decode_58).decode('ascii')+"88ac"
    return pubKeyHash

def pubkey_to_pubkeyhash(address):
    # Get HASH160 of pubkey
    hash160 = get_hash160("0227e5cad3731e381df157de189527aac8eb50d82a13ce2bd81153984ebc749515")
    # Add OP codes
    pubKeyHash = "76a914"+hash160.decode('ascii')+"88ac"
    return pubKeyHash

def pubkey_to_p2pk_scripthash(pubkey):
    scriptpubkey = '21' +pubkey+ 'ac'
    scripthex = codecs.decode(scriptpubkey, 'hex')
    s = hashlib.new('sha256', scripthex).digest()
    sha256_scripthash = codecs.encode(s, 'hex').decode("utf-8")
    script_hash = lil_endian(sha256_scripthash)
    return script_hash

def pubkey_to_p2pkh_scripthash(pubkey):
    publickey = codecs.decode(pubkey, 'hex')
    s = hashlib.new('sha256', publickey).digest()
    r = hashlib.new('ripemd160', s).digest()
    scriptpubkey = "76a914"+codecs.encode(r, 'hex').decode("utf-8")+"88ac"
    h = codecs.decode(scriptpubkey, 'hex')
    s = hashlib.new('sha256', h).digest()
    sha256_scripthash = codecs.encode(s, 'hex').decode("utf-8")
    script_hash = lil_endian(sha256_scripthash)
    return script_hash

test_tx = raw_tx()

test_tx.inputs = [
    {
        "tx_hash": "a84d750867c7f5c3ffbbca87bb27137906c5dbe8af98b108adc9675ce530cec4",
        "tx_pos": 0,
        "height": 2401810,
        "pubkey": "03e81e1333f9f91a8d2afcfe3fcffaba8ba543d5552e4cbe3faf7cf64d2887d4f5",
        "value": 100000000
    }
]
test_tx.outputs = [
    {
        "amount": 99000000,
        "address": "RVB7Vd4JbbjQPV1WE5ZdeWmWo5EjMpXDH6",
        "pubKeyHash": "76a914da3c316ca163b5d3628b1ee0499dfe4330c03c5488ac",
        "pubKeyHash_p2pk": "210227e5cad3731e381df157de189527aac8eb50d82a13ce2bd81153984ebc749515ac"
    }
]
raw_tx = test_tx.construct()
print(raw_tx)
print(address_to_pubkeyhash("RVB7Vd4JbbjQPV1WE5ZdeWmWo5EjMpXDH6"))
print(pubkey_to_pubkeyhash("0227e5cad3731e381df157de189527aac8eb50d82a13ce2bd81153984ebc749515"))
print(address_to_p2pkh_scripthash("RVB7Vd4JbbjQPV1WE5ZdeWmWo5EjMpXDH6"))
print(pubkey_to_p2pkh_scripthash("0227e5cad3731e381df157de189527aac8eb50d82a13ce2bd81153984ebc749515"))
print(pubkey_to_p2pk_scripthash("0227e5cad3731e381df157de189527aac8eb50d82a13ce2bd81153984ebc749515"))