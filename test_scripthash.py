from base58 import b58decode_check
from binascii import hexlify
import hashlib
from hashlib import sha256
import codecs
import socket
import time
import json

OP_DUP = b'76'
OP_HASH160 = b'a9'
BYTES_TO_PUSH = b'14'
OP_EQUALVERIFY = b'88'
OP_CHECKSIG = b'ac'
DATA_TO_PUSH = lambda address: hexlify(b58decode_check(address)[1:])
sig_script_raw = lambda address: b''.join((OP_DUP, OP_HASH160, BYTES_TO_PUSH, DATA_TO_PUSH(address), OP_EQUALVERIFY, OP_CHECKSIG))
script_hash = lambda address: sha256(codecs.decode(sig_script_raw(address), 'hex_codec')).digest()[::-1].hex()

def get_scripthash_from_address(address):
	# remove address prefix
	addr_stripped = hexlify(b58decode_check(address)[1:])
	# Add OP_DUP OP_HASH160 BTYES_PUSHED <ADDRESS> OP_EQUALVERIFY OP_CHECKSIG
	raw_sig_script = b"".join((b"76a914", addr_stripped, b"88ac"))
	script_hash = sha256(codecs.decode(raw_sig_script, 'hex')).digest()[::-1].hex()
	return script_hash

def get_from_electrum(url, port, method, params=[]):
    params = [params] if type(params) is not list else params
    socket.setdefaulttimeout(20)
    s = socket.create_connection((url, port))
    s.send(json.dumps({"id": 0, "method": method, "params": params}).encode() + b'\n')
    time.sleep(0.1)
    return json.loads(s.recv(999999)[:-1].decode())



'''
a.send("server.version")
a.send("server.banner")
a.send('blockchain.scripthash.get_balance', script_hash('mksHkTDsauAP1L79rLZUQA3u36J3ntLtJx'))
a.send('blockchain.scripthash.get_mempool', script_hash('mksHkTDsauAP1L79rLZUQA3u36J3ntLtJx'))
a.send('blockchain.scripthash.subscribe', script_hash('mksHkTDsauAP1L79rLZUQA3u36J3ntLtJx'))
'''

def lil_endian(hex_str):
    return ''.join([hex_str[i:i+2] for i in range(0, len(hex_str), 2)][::-1])

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

print(get_scripthash_from_address('LiL6rJxoVKjaPWHCJXnhYjRpvyqigkENDh'))
print(get_p2pkh_scripthash_from_pubkey("0227e5cad3731e381df157de189527aac8eb50d82a13ce2bd81153984ebc749515"))
print(get_p2pk_scripthash_from_pubkey("0227e5cad3731e381df157de189527aac8eb50d82a13ce2bd81153984ebc749515"))
p2pk_resp1 = get_from_electrum('electrum2.cipig.net', 10063, 'blockchain.scripthash.get_balance', get_scripthash_from_address('LiL6rJxoVKjaPWHCJXnhYjRpvyqigkENDh'))
p2pk_resp2 = get_from_electrum('electrum2.cipig.net', 10001, 'blockchain.scripthash.get_balance', get_p2pkh_scripthash_from_pubkey('0227e5cad3731e381df157de189527aac8eb50d82a13ce2bd81153984ebc749515'))
p2pk_resp3 = get_from_electrum('electrum2.cipig.net', 10001, 'blockchain.scripthash.get_balance', get_p2pk_scripthash_from_pubkey('0227e5cad3731e381df157de189527aac8eb50d82a13ce2bd81153984ebc749515'))
print(p2pk_resp1)
print(p2pk_resp2)
print(p2pk_resp3)