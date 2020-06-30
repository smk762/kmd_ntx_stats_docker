#!/usr/bin/env python3
import os
import time
import json
import logging
import binascii
import datetime
from datetime import datetime as dt
import psycopg2
from decimal import *
import bitcoin
from bitcoin.core import x
from bitcoin.core import CoreMainParams
from bitcoin.wallet import P2PKHBitcoinAddress
from datetime import datetime as dt
from dotenv import load_dotenv
from rpclib import def_credentials
import logging
import logging.handlers
from base_58 import *
from lib_const import *
from lib_api import *
from lib_table_update import *
from lib_table_select import *

load_dotenv()

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def connect_db():
    conn = psycopg2.connect(
        host='localhost',
        user=os.getenv("DB_USER"),
        password=os.getenv("PASSWORD"),
        port = "7654",
        database='postgres'
    )
    return conn

def get_season_notaries(season):
    notaries = []
    for season_num in notary_pubkeys:
        if season == season_num[0:8]:
            for notary in notary_pubkeys[season_num]:
                if notary not in notaries:
                    notaries.append(notary)
    return notaries

def get_season(time_stamp):
    # detect & convert js timestamps
    if round((time_stamp/1000)/time.time()) == 1:
        time_stamp = time_stamp/1000
    for season in seasons_info:
        if time_stamp >= seasons_info[season]['start_time'] and time_stamp <= seasons_info[season]['end_time']:
            return season
    return "season_undefined"

def get_season_from_block(block):
    if not isinstance(block, int):
        block = int(block)
    for season in seasons_info:
        if block >= seasons_info[season]['start_block'] and block <= seasons_info[season]['end_block']:
            return season
    return "season_undefined"

def get_seasons_from_address(addr, chain="KMD"):
    addr_seasons = []
    for season in notary_addresses:
        for notary in notary_addresses[season]:
            season_addr = notary_addresses[season][notary][chain]
            if addr == season_addr:
                addr_seasons.append(season)
    return addr_seasons

def get_season_from_addresses(notaries, address_list, tx_chain="KMD"):
    seasons = list(notary_addresses.keys())[::-1]
    notary_seasons = []
    last_season_num = None

    for season in seasons:
        # ignore .5 and third_party suffixes
        season_num = season[0:8]

        if last_season_num != season_num:
            notary_seasons = []

        season_notaries = list(notary_addresses[season].keys())
        for notary in season_notaries:
            addr = notary_addresses[season][notary][tx_chain]
            if addr in address_list:
                notary_seasons.append(season_num)

        if len(notary_seasons) == 13:
            break
        last_season_num = season_num

    if len(notary_seasons) == 13 and len(set(notary_seasons)) == 1:
        return notary_seasons[0]
    else:
        return "season_undefined"

def get_known_addr(coin, season):
    # k:v dict for matching address to owner
    # TODO: add pool addresses
    addresses = {}
    bitcoin.params = coin_params[coin]
    for notary in notary_pubkeys[season]:
        addr = str(P2PKHBitcoinAddress.from_pubkey(x(notary_pubkeys[season][notary])))
        addresses.update({addr:notary})

    return addresses

def get_notary_from_address(address):
    if address in known_addresses:
        return known_addresses[address]
    return "unknown"

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
                address_list = []
                for item in raw_tx['vin']:
                    if "address" in item:
                        address_list.append(item['address'])
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
                        season = get_season_from_addresses(notary_list, address_list, "KMD")
                        row_data = (chain, this_block_height, block_time, block_datetime,
                                    block_hash, notary_list, ac_ntx_blockhash, ac_ntx_height,
                                    txid, opret, season, "N/A")
                        return row_data
                else:
                    # no opretrun in tx, and shouldnt polute the DB.
                    return None
                
            else:
                # These are related to easy mining, and shouldnt polute the DB.
                return None
        else:
            # These are outgoing, and should not polute the DB.
            return None

def get_btc_ntxids(stop_block):
    has_more=True
    before_block=None
    ntx_txids = []
    page = 0
    exit_loop = False
    existing_txids = get_existing_ntxids(cursor)
    while has_more:
        page += 1
        logger.info("Page "+str(page))
        resp = get_btc_address_txids(btc_ntx_addr, before_block)
        if "error" in resp:
            page -= 1
            exit_loop = api_sleep_or_exit(resp)
        else:
            if 'txrefs' in resp:
                tx_list = resp['txrefs']
                for tx in tx_list:
                    if tx['tx_hash'] not in ntx_txids and tx['tx_hash'] not in existing_txids:
                        ntx_txids.append(tx['tx_hash'])
                logger.info(str(len(ntx_txids))+" txids scanned...")

            if 'hasMore' in resp:
                has_more = resp['hasMore']
                logger.info(has_more)
                if has_more:
                    before_block = tx_list[-1]['block_height']
                    logger.info("scannning back from block "+str(before_block))
                    if before_block < stop_block:
                        logger.info("Scanned to start of s4")
                        exit_loop = True
                    time.sleep(1)
                else:
                    logger.info("No more!")
                    exit_loop = True

            else:
                logger.info(resp)
                logger.info("No more tx to scan!")
                exit_loop = True
                
        if exit_loop or page > int(os.getenv("btc_validate_pages")):
            logger.info("exiting address txid loop!")
            break
    ntx_txids = list(set((ntx_txids)))
    return ntx_txids

def get_notaries_from_addresses(addresses):
    notaries = []
    if btc_ntx_addr in addresses:
        addresses.remove(btc_ntx_addr)
    for address in addresses:
        if address in known_addresses:
            notary = known_addresses[address]
            notaries.append(notary)
        else:
            notaries.append(address)
    notaries.sort()
    return notaries

# MINED OPS

def get_miner(block):
    logger.info("Getting mining data for block "+str(block))
    rpc = {}
    rpc["KMD"] = def_credentials("KMD")
    blockinfo = rpc["KMD"].getblock(str(block), 2)
    blocktime = blockinfo['time']
    block_datetime = dt.utcfromtimestamp(blockinfo['time'])
    for tx in blockinfo['tx']:
        if len(tx['vin']) > 0:
            if 'coinbase' in tx['vin'][0]:
                if 'addresses' in tx['vout'][0]['scriptPubKey']:
                    address = tx['vout'][0]['scriptPubKey']['addresses'][0]
                    if address in known_addresses:
                        name = known_addresses[address]
                    else:
                        name = address
                else:
                    address = "N/A"
                    name = "non-standard"
                for season_num in seasons_info:
                    if blocktime < seasons_info[season_num]['end_time']:
                        season = season_num
                        break

                value = tx['vout'][0]['value']
                row_data = (block, blocktime, block_datetime, Decimal(value), address, name, tx['txid'], season)
                return row_data

def get_daily_mined_counts(conn, cursor, day):
    results = get_mined_date_aggregates(cursor, day)
    time_stamp = int(time.time())
    for item in results:
        row_data = (item[0], int(item[1]), float(item[2]), str(day), int(time_stamp))
        if item[0] in notary_info:
            logger.info("Adding "+str(row_data)+" to daily_mined_counts table")
        result = update_daily_mined_count_tbl(conn, cursor, row_data)
    return result

# MISC TABLE OPS

def delete_from_table(conn, cursor, table, condition=None):
    sql = "TRUNCATE "+table
    if condition:
        sql = sql+" WHERE "+condition
    sql = sql+";"
    cursor.execute()
    conn.commit()

def ts_col_to_season_col(conn, cursor, ts_col, season_col, table):
    for season in seasons_info:
        sql = "UPDATE "+table+" \
               SET "+season_col+"='"+season+"' \
               WHERE "+ts_col+" > "+str(seasons_info[season]['start_time'])+" \
               AND "+ts_col+" < "+str(seasons_info[season]['end_time'])+";"
        cursor.execute(sql)
        conn.commit()

now = int(time.time())

rpc = {}
rpc["KMD"] = def_credentials("KMD")
ntx_addr = 'RXL3YXG2ceaB6C5hfJcN4fvmLH2C34knhA'
noMoM = ['CHIPS', 'GAME', 'HUSH3', 'EMC2', 'GIN', 'AYA']

if now > seasons_info['Season_3']['end_time']:
    pubkey_file = 's4_nn_pubkeys.json'
else:
    pubkey_file = 's3_nn_pubkeys.json'

pubkey_file = os.path.join(os.path.dirname(__file__), pubkey_file)

with open(pubkey_file) as f:
    season_pubkeys = json.load(f)

conn = connect_db()
cursor = conn.cursor()
dpow_coins = get_dpow_coins(conn, cursor)

third_party_coins = []
antara_coins = []

for item in dpow_coins:
    if item[6]['server'] == 'dpow-mainnet':
        if item[1] not in ['KMD', 'BTC']:
            antara_coins.append(item[1])
    elif item[6]['server'] == 'dpow-3p':
        third_party_coins.append(item[1])
                   
all_coins = antara_coins + third_party_coins + ['BTC', 'KMD']
all_antara_coins = antara_coins +[] # add retired smartchains here

for coin in antara_coins:
    coin_params.update({coin:KMD_CoinParams})

for coin in third_party_coins:
    coin_params.update({coin:coin_params[coin]})

known_addresses = {}
for coin in all_coins:
    for season in notary_pubkeys:
        known_addresses.update(get_known_addr(coin, season))

known_addresses.update({"RKrMB4guHxm52Tx9LG8kK3T5UhhjVuRand":"funding bot"})

# lists all season, name, address and id info for each notary
notary_info = {}

# detailed address info categories by season. showing notary name, id and pubkey
address_info = {}

# shows addresses for all coins for each notary node, by season.
notary_addresses = {}

for season in notary_pubkeys:
    notary_addresses.update({season:{}})
    notary_id = 0
    notaries = list(notary_pubkeys[season].keys())
    notaries.sort()
    for notary in notaries:
        if notary not in notary_addresses:
            notary_addresses[season].update({notary:{}})
        for coin in coin_params:
            bitcoin.params = coin_params[coin]
            pubkey = notary_pubkeys[season][notary]
            address = str(P2PKHBitcoinAddress.from_pubkey(x(pubkey)))
            notary_addresses[season][notary].update({coin:address})

bitcoin.params = coin_params["KMD"]
for season in notary_pubkeys:
    notary_id = 0    
    address_info.update({season:{}})
    notaries = list(notary_pubkeys[season].keys())
    notaries.sort()
    for notary in notaries:
        if notary not in notary_info:
            notary_info.update({
                notary:{
                    "Notary_ids":[],
                    "Seasons":[],
                    "Addresses":[],
                    "Pubkeys":[]
                }})
        addr = str(P2PKHBitcoinAddress.from_pubkey(x(notary_pubkeys[season][notary])))
        address_info[season].update({
            addr:{
                "Notary":notary,
                "Notary_id":notary_id,
                "Pubkey":notary_pubkeys[season][notary]
            }})
        notary_info[notary]['Notary_ids'].append(notary_id)
        notary_info[notary]['Seasons'].append(season)
        notary_info[notary]['Addresses'].append(addr)
        notary_info[notary]['Pubkeys'].append(notary_pubkeys[season][notary])
        notary_id += 1

for season in notary_pubkeys:
    notaries = list(notary_pubkeys[season].keys())
    notaries.sort()
    for notary in notaries:
        if season.find("Season_3") != -1:
            seasons_info["Season_3"]['notaries'].append(notary)
        elif season.find("Season_4") != -1:
            seasons_info["Season_4"]['notaries'].append(notary)
        else:
            seasons_info[season]['notaries'].append(notary)

def update_ntx_tenure(chains, seasons):
    for chain in chains:
        for season in seasons:
            ntx_results = get_ntx_min_max(cursor, season, chain)
            logger.info(chain+" "+season+": "+str(ntx_results))
            max_blk = ntx_results[0]
            max_blk_time = ntx_results[1]
            min_blk = ntx_results[2]
            min_blk_time = ntx_results[3]
            ntx_count = ntx_results[4]
            if max_blk is not None:
                row_data = (chain, min_blk, max_blk, min_blk_time, max_blk_time, ntx_count, season)
                update_notarised_tenure(conn, cursor, row_data)
                logger.info(chain+" "+season+" notarised tenure updated!")

def get_unrecorded_txids(cursor, tip, season):
    recorded_txids = []
    start_block = seasons_info[season]["start_block"]
    end_block = seasons_info[season]["end_block"]

    if end_block <= tip:
        tip = end_block

    if skip_until_yesterday:
        start_block = tip - 24*60

    all_txids = []
    chunk_size = 100000

    while tip - start_block > chunk_size:
        logger.info("Getting notarization TXIDs from block chain data for blocks " \
               +str(start_block+1)+" to "+str(start_block+chunk_size)+"...")
        all_txids += get_ntx_txids(ntx_addr, start_block+1, start_block+chunk_size)
        start_block += chunk_size
    all_txids += get_ntx_txids(ntx_addr, start_block+1, tip)
    recorded_txids = get_existing_ntxids(cursor)
    unrecorded_txids = set(all_txids) - set(recorded_txids)
    return unrecorded_txids