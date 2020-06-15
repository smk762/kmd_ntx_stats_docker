import datetime
import logging
import binascii
from datetime import datetime as dt
from rpclib import def_credentials
from notary_lib import notary_info, seasons_info, known_addresses
from coins_lib import third_party_coins, antara_coins, ex_antara_coins, all_antara_coins, all_coins
logger = logging.getLogger(__name__)

rpc = {}
rpc["KMD"] = def_credentials("KMD")
ntx_addr = 'RXL3YXG2ceaB6C5hfJcN4fvmLH2C34knhA'
noMoM = ['CHIPS', 'GAME', 'HUSH3', 'EMC2', 'GIN', 'AYA']

def lil_endian(hex_str):
    return ''.join([hex_str[i:i+2] for i in range(0, len(hex_str), 2)][::-1])

def get_ntx_txids(ntx_addr, start, end):
    return rpc["KMD"].getaddresstxids({"addresses": [ntx_addr], "start":start, "end":end})
    
def get_ticker(scriptPubKeyBinary):
    chain = ''
    while len(chain) < 1:
        for i in range(len(scriptPubKeyBinary)):
            if chr(scriptPubKeyBinary[i]).encode() == b'\x00':
                j = i+1
                while j < len(scriptPubKeyBinary)-1:
                    chain += chr(scriptPubKeyBinary[j])
                    j += 1
                    if chr(scriptPubKeyBinary[j]).encode() == b'\x00':
                        break
                break
    if chr(scriptPubKeyBinary[-4])+chr(scriptPubKeyBinary[-3])+chr(scriptPubKeyBinary[-2]) =="KMD":
        chain = "KMD"
    return str(chain)


def get_ntx_data(txid):
    raw_tx = rpc["KMD"].getrawtransaction(txid,1)
    block_hash = raw_tx['blockhash']
    dest_addrs = raw_tx["vout"][0]['scriptPubKey']['addresses']
    block_time = raw_tx['blocktime']
    block_datetime = dt.utcfromtimestamp(raw_tx['blocktime'])
    this_block_height = raw_tx['height']
    if len(dest_addrs) > 0:
        if ntx_addr in dest_addrs:
            if len(raw_tx['vin']) == 13:
                notary_list = []
                for item in raw_tx['vin']:
                    if "address" in item:
                        if item['address'] in known_addresses:
                            notary = known_addresses[item['address']]
                            notary_list.append(notary)
                        else:
                            notary_list.append(item['address'])
                notary_list.sort()
                opret = raw_tx['vout'][1]['scriptPubKey']['asm']
                logger.info(opret)
                if opret.find("OP_RETURN") != -1:
                    scriptPubKey_asm = opret.replace("OP_RETURN ","")
                    ac_ntx_blockhash = lil_endian(scriptPubKey_asm[:64])
                    try:
                        ac_ntx_height = int(lil_endian(scriptPubKey_asm[64:72]),16) 
                    except:
                        logger.info(scriptPubKey_asm)
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
                    # some decodes have a null char error, this gets rid of that so populate script doesnt error out 
                    if chain.find('\x00') != -1:
                        chain = chain.replace('\x00','')
                    # (some s1 op_returns seem to be decoding differently/wrong. This ignores them)
                    if chain.upper() == chain:
                        if chain not in ['KMD', 'BTC']:
                            for season_num in seasons_info:
                                if block_time < seasons_info[season_num]['end_time'] and block_time >= seasons_info[season_num]['start_time']:
                                    season = season_num
                        else:
                            for season_num in seasons_info:
                                if this_block_height < seasons_info[season_num]['end_block'] and this_block_height >= seasons_info[season_num]['start_block']:
                                    season = season_num
                        row_data = (chain, this_block_height, block_time, block_datetime,
                                    block_hash, notary_list, ac_ntx_blockhash, ac_ntx_height,
                                    txid, opret, season)
                        return row_data
                else:
                    # no opretrun in tx, and shouldnt polute the DB.
                    row_data = ("not_opret", this_block_height, block_time, block_datetime,
                                block_hash, notary_list, "unknown", 0, txid, "unknown", "N/A")
                    return None
                
            else:
                # These are related to easy mining, and shouldnt polute the DB.
                row_data = ("low_vin", this_block_height, block_time, block_datetime,
                            block_hash, [], "unknown", 0, txid, "unknown", "N/A")
                return None
        else:
            # These are outgoing, and should not polute the DB.
            row_data = ("not_dest", this_block_height, block_time, block_datetime,
                        block_hash, [], "unknown", 0, txid, "unknown", "N/A")
            return None

def get_ntx_data_v2(txid):
    raw_tx = rpc["KMD"].getrawtransaction(txid,1)
    block_time = raw_tx['blocktime']
    block_datetime = dt.utcfromtimestamp(block_time)
    for season_num in seasons_info:
        if block_time < seasons_info[season_num]['end_time']:
            season = season_num
            break
    block_hash = raw_tx['blockhash']
    dest_addrs = raw_tx["vout"][0]['scriptPubKey']['addresses']
    this_block_height = raw_tx['height']
    notary_list = []
    for item in raw_tx['vin']:
        if "address" in item:
            if item['address'] in known_addresses:
                notary = known_addresses[item['address']]
                notary_list.append(notary)
            else:
                notary_list.append(item['address'])
    notary_list.sort()
    opret = raw_tx['vout'][1]['scriptPubKey']['asm']
    logger.info(opret)
    if opret.find("OP_RETURN") != -1:
        scriptPubKey_asm = opret.replace("OP_RETURN ","")
        ac_ntx_blockhash = lil_endian(scriptPubKey_asm[:64])
        try:
            ac_ntx_height = int(lil_endian(scriptPubKey_asm[64:72]),16) 
        except:
            logger.info(scriptPubKey_asm)
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
        # some decodes have a null char error, this gets rid of that so populate script doesnt error out 
        if chain.find('\x00') != -1:
            chain = chain.replace('\x00','')
        # (some s1 op_returns seem to be decoding differently/wrong. This ignores them)
        if chain.upper() == chain:
            row_data = (chain, this_block_height, block_time, block_datetime,
                        block_hash, notary_list, ac_ntx_blockhash, ac_ntx_height,
                        txid, opret, season)
            return row_data
