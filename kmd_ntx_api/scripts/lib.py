#!/usr/bin/env python3
import os
import sys
import json
import binascii
import time
import logging
import logging.handlers

def lil_endian(hex_str):
    return ''.join([hex_str[i:i+2] for i in range(0, len(hex_str), 2)][::-1])

def decode_opret(scriptPubKey_asm):   
    prev_block_hash = lil_endian(scriptPubKey_asm[:64])
    try:
        prev_block_ht = int(lil_endian(scriptPubKey_asm[64:72]),16) 
    except:
        print(scriptPubKey_asm)
        sys.exit()
    scriptPubKeyBinary = binascii.unhexlify(scriptPubKey_asm[70:])
    chain = get_ticker(scriptPubKeyBinary)
    if chain.endswith("KMD"):
        chain = "KMD"
    if chain == "KMD":
        btc_txid = lil_endian(scriptPubKey_asm[72:136])
    elif chain not in noMoM:
        # not sure about this bit, need another source to validate the data
        try:
            start = 72+len(chain)*2+4
            end = 72+len(chain)*2+4+64
            MoM_hash = lil_endian(scriptPubKey_asm[start:end])
            MoM_depth = int(lil_endian(scriptPubKey_asm[end:]),16)
        except Exception as e:
            logger.debug(e)
    return opret_obj(chain=chain, prevblock=prev_block_ht, prevhash=prev_block_hash)
