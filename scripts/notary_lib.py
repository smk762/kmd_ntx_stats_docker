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
import dateutil.parser as dp
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
    for season_num in NOTARY_PUBKEYS:
        if season == season_num[0:8]:
            for notary in NOTARY_PUBKEYS[season_num]:
                if notary not in notaries:
                    notaries.append(notary)
    return notaries

def get_season(time_stamp):
    # detect & convert js timestamps
    time_stamp = int(time_stamp)
    if round((time_stamp/1000)/time.time()) == 1:
        time_stamp = time_stamp/1000
    for season in SEASONS_INFO:
        if time_stamp >= SEASONS_INFO[season]['start_time'] and time_stamp <= SEASONS_INFO[season]['end_time']:
            return season
    return None

def get_season_from_block(block):
    if not isinstance(block, int):
        block = int(block)
    for season in SEASONS_INFO:
        if block >= SEASONS_INFO[season]['start_block'] and block <= SEASONS_INFO[season]['end_block']:
            return season
    return None

def get_seasons_from_address(addr, chain="KMD"):
    addr_seasons = []
    for season in notary_addresses:
        for notary in notary_addresses[season]:
            season_addr = notary_addresses[season][notary][chain]
            if addr == season_addr:
                addr_seasons.append(season)
    return addr_seasons

def get_season_from_addresses(address_list, time_stamp, tx_chain="KMD"):
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
        return get_season(time_stamp)

def get_known_addr(coin, season):
    # k:v dict for matching address to owner
    # TODO: add pool addresses
    addresses = {}
    bitcoin.params = coin_params[coin]
    for notary in NOTARY_PUBKEYS[season]:
        addr = str(P2PKHBitcoinAddress.from_pubkey(x(NOTARY_PUBKEYS[season][notary])))
        addresses.update({addr:notary})

    return addresses

def get_notary_from_address(address):
    if address in known_addresses:
        return known_addresses[address]
    return "unknown"

def lil_endian(hex_str):
    return ''.join([hex_str[i:i+2] for i in range(0, len(hex_str), 2)][::-1])

def get_ntx_txids(NTX_ADDR, start, end):
    return rpc["KMD"].getaddresstxids({"addresses": [NTX_ADDR], "start":start, "end":end})
  
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
        if NTX_ADDR in dest_addrs:
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
                        season = get_season_from_addresses(address_list, block_time, "KMD")
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

def get_btc_ntxids(cursor, stop_block, exit=None):
    has_more=True
    before_block=None
    ntx_txids = []
    page = 0
    exit_loop = False
    existing_txids = get_existing_btc_ntxids(cursor)
    while has_more:
        page += 1
        logger.info("Page "+str(page))
        resp = get_btc_address_txids(BTC_NTX_ADDR, before_block)
        if "error" in resp:
            page -= 1
            exit_loop = api_sleep_or_exit(resp, exit)
        else:
            if 'txrefs' in resp:
                tx_list = resp['txrefs']
                for tx in tx_list:
                    if tx['tx_hash'] not in ntx_txids and tx['tx_hash'] not in existing_txids:
                        ntx_txids.append(tx['tx_hash'])
                logger.info(str(len(ntx_txids))+" txids scanned...")

            if 'hasMore' in resp:
                has_more = resp['hasMore']
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
                logger.info("No more tx to scan!")
                exit_loop = True
                
        if exit_loop or page >= int(os.getenv("btc_validate_pages")):
            logger.info("exiting address txid loop!")
            break
    ntx_txids = list(set((ntx_txids)))
    return ntx_txids

def update_BTC_notarisations(conn, cursor, stop_block=634000):
    # Get existing data to avoid unneccesary updates 
    existing_txids = get_existing_btc_ntxids(cursor)
    notary_last_ntx = get_notary_last_ntx(cursor)

    # Loop API queries to get BTC ntx
    ntx_txids = get_btc_ntxids(cursor, stop_block, False)

    with open("btc_ntx_txids.json", 'w+') as f:
        f.write(json.dumps(ntx_txids))

    addresses_dict = {}
    try:
        addresses = requests.get("http://notary.earth:8762/api/source/addresses/?chain=BTC&season=Season_4").json()
        for item in addresses['results']:
            addresses_dict.update({item["address"]:item["notary"]})
        addresses_dict.update({BTC_NTX_ADDR:"BTC_NTX_ADDR"})
    except Exception as e:
        logger.error(e)
        logger.info("Addresses API might be down!")

    i=0
    for btc_txid in ntx_txids:
        logger.info("TXID: "+btc_txid)

        logger.info("Processing ntxid "+str(i)+"/"+str(len(ntx_txids)))
        i += 1
        tx_info = get_btc_tx_info(btc_txid, False)

        if "error" in tx_info:
            exit_loop = True

        elif 'block_height' in tx_info:

            block_height = tx_info['block_height']
            block_hash = tx_info['block_hash']
            block_time_iso8601 = tx_info['confirmed']
            parsed_time = dp.parse(block_time_iso8601)
            block_time = parsed_time.strftime('%s')
            block_datetime = dt.utcfromtimestamp(int(block_time))
            logger.info("Block datetime "+str(block_datetime))

            addresses = tx_info['addresses'][:]
            fees = tx_info['fees']
            num_outputs = tx_info['vout_sz']
            num_inputs = tx_info['vin_sz']
            vouts = tx_info["outputs"]
            vins = tx_info["inputs"]
            if '1See1xxxx1memo1xxxxxxxxxxxxxBuhPF' not in addresses:
                notaries = get_notaries_from_addresses(addresses)
                print(notaries)
                season = get_season_from_addresses(addresses, block_time, "BTC")
                for notary in notaries:
                    result = 0
                    last_ntx_row_data = (notary, "BTC", btc_txid, block_height,
                                         block_time, season)
                    if notary in notary_last_ntx:
                        if "BTC" not in notary_last_ntx[notary]:
                            notary_last_ntx[notary].update({"BTC":0})

                        if int(block_height) > int(notary_last_ntx[notary]["BTC"]):
                            result = update_last_ntx_tbl(conn, cursor, last_ntx_row_data)
                    else:
                        result = update_last_ntx_tbl(conn, cursor, last_ntx_row_data)
                    if result == 1:
                        logger.info("last_ntx_tbl updated!")
                    else:
                        logger.warning("last_ntx_tbl not updated!")

                if len(tx_info['outputs']) > 0:
                    if 'data_hex' in tx_info['outputs'][-1]:
                        opret = tx_info['outputs'][-1]['data_hex']

                        r = requests.get('http://notary.earth:8762/api/tools/decode_opreturn/?OP_RETURN='+opret)
                        kmd_ntx_info = r.json()

                        ac_ntx_height = kmd_ntx_info['notarised_block']
                        ac_ntx_blockhash = kmd_ntx_info['notarised_blockhash']

                        # Update "notarised" table
                        row_data = ('BTC', block_height, block_time, block_datetime,
                                    block_hash, notaries, ac_ntx_blockhash, ac_ntx_height,
                                    btc_txid, opret, season, "true")
                        update_ntx_records(conn, cursor, [row_data])
                        logger.info("Row inserted")

                        input_index = 0

                        category = "NTX"
                        for vin in vins:
                            address = vin["addresses"][0]

                            if address in addresses_dict:
                                notary_name = addresses_dict[address]
                            else:
                                notary_name = "non-NN"

                            input_sats = vin['output_value']
                            output_index = None
                            output_sats = None

                            row_data = (btc_txid, block_hash, block_height, block_time,
                                        block_datetime, address, notary_name, season, category,
                                        input_index, input_sats, output_index,
                                        output_sats, fees, num_inputs, num_outputs)
                            logger.info("Adding "+btc_txid+" vin "+str(input_index)+" "+str(notary_name)+" "+str(address)+" ("+category.upper()+")")
                            update_nn_btc_tx_row(conn, cursor, row_data)

                            input_index += 1

                        output_index = 0
                        for vout in vouts:
                            if vout["addresses"] is not None:
                                address = vout["addresses"][0]

                                if address in addresses_dict:
                                    notary_name = addresses_dict[address]
                                else:
                                    notary_name = "non-NN"

                                input_index = None
                                input_sats = None
                                output_sats = vout['value']
                                row_data = (btc_txid, block_hash, block_height, block_time,
                                            block_datetime, address, notary_name, season, category,
                                            input_index, input_sats, output_index,
                                            output_sats, fees, num_inputs, num_outputs)

                                logger.info("Adding "+btc_txid+" vout "+str(output_index)+" "+str(notary_name)+" "+str(address)+" ("+category.upper()+")")
                                update_nn_btc_tx_row(conn, cursor, row_data)
                                output_index += 1
            else:
                print("SPAM")


def get_new_nn_btc_txids(existing_txids, notary_address):
    before_block=None
    page = 0
    exit_loop = False
    api_txids = []
    new_txids = []
    while True:
        page += 1
        logger.info("Page "+str(page))
        resp = get_btc_address_txids(notary_address, before_block)
        if "error" in resp:
            page -= 1
            exit_loop = True
            logger.info(f"Error in resp: {resp}")
            api_sleep_or_exit(resp, exit=None)
        else:
            if 'txrefs' in resp:
                tx_list = resp['txrefs']
                before_block = tx_list[-1]['block_height']

                for tx in tx_list:
                    api_txids.append(tx['tx_hash'])
                    if tx['tx_hash'] not in new_txids and tx['tx_hash'] not in existing_txids:
                        new_txids.append(tx['tx_hash'])
                        print(f"appended tx {tx}")

                # exit loop if earlier than s4
                if before_block < 634774:
                    logger.info("No more for s4!")
                    exit_loop = True

                logger.info("scannning back from block "+str(before_block))
            else:
                # exit loop if no more tx for address at api
                logger.info("No more for address!")
                exit_loop = True

        if exit_loop:
            logger.info("exiting address txid loop!")
            break

    logger.info(f"{len(api_txids)} TXIDs counted from API")
    num_api_txids = list(set((api_txids)))
    logger.info(f"{len(num_api_txids)} DISTINCT TXIDs counted from API")

    logger.info(f"{len(new_txids)} NEW TXIDs counted from API")
    new_txids = list(set((new_txids)))
    logger.info(f"{len(new_txids)} DISTINCT NEW TXIDs counted from API")
    return new_txids


def get_notaries_from_addresses(addresses):
    notaries = []
    if BTC_NTX_ADDR in addresses:
        addresses.remove(BTC_NTX_ADDR)
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
                for season_num in SEASONS_INFO:
                    if blocktime < SEASONS_INFO[season_num]['end_time']:
                        season = season_num
                        break

                value = tx['vout'][0]['value']
                row_data = (block, blocktime, block_datetime, Decimal(value), address, name, tx['txid'], season)
                return row_data

def get_daily_mined_counts(conn, cursor, day):
    result = 0
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
    for season in SEASONS_INFO:
        sql = "UPDATE "+table+" \
               SET "+season_col+"='"+season+"' \
               WHERE "+ts_col+" > "+str(SEASONS_INFO[season]['start_time'])+" \
               AND "+ts_col+" < "+str(SEASONS_INFO[season]['end_time'])+";"
        cursor.execute(sql)
        conn.commit()

now = int(time.time())

rpc = {}
rpc["KMD"] = def_credentials("KMD")
NTX_ADDR = 'RXL3YXG2ceaB6C5hfJcN4fvmLH2C34knhA'
noMoM = ['CHIPS', 'GAME', 'HUSH3', 'EMC2', 'GIN', 'AYA', 'GLEEC']

if now > SEASONS_INFO['Season_3']['end_time']:
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
    for season in NOTARY_PUBKEYS:
        known_addresses.update(get_known_addr(coin, season))

known_addresses.update({"RKrMB4guHxm52Tx9LG8kK3T5UhhjVuRand":"funding bot"})

# lists all season, name, address and id info for each notary
notary_info = {}

# detailed address info categories by season. showing notary name, id and pubkey
address_info = {}

# shows addresses for all coins for each notary node, by season.
notary_addresses = {}

for season in NOTARY_PUBKEYS:
    notary_addresses.update({season:{}})
    notary_id = 0
    notaries = list(NOTARY_PUBKEYS[season].keys())
    notaries.sort()
    for notary in notaries:
        if notary not in notary_addresses:
            notary_addresses[season].update({notary:{}})
        for coin in coin_params:
            bitcoin.params = coin_params[coin]
            pubkey = NOTARY_PUBKEYS[season][notary]
            address = str(P2PKHBitcoinAddress.from_pubkey(x(pubkey)))
            notary_addresses[season][notary].update({coin:address})

bitcoin.params = coin_params["KMD"]
for season in NOTARY_PUBKEYS:
    notary_id = 0    
    address_info.update({season:{}})
    notaries = list(NOTARY_PUBKEYS[season].keys())
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
        addr = str(P2PKHBitcoinAddress.from_pubkey(x(NOTARY_PUBKEYS[season][notary])))
        address_info[season].update({
            addr:{
                "Notary":notary,
                "Notary_id":notary_id,
                "Pubkey":NOTARY_PUBKEYS[season][notary]
            }})
        notary_info[notary]['Notary_ids'].append(notary_id)
        notary_info[notary]['Seasons'].append(season)
        notary_info[notary]['Addresses'].append(addr)
        notary_info[notary]['Pubkeys'].append(NOTARY_PUBKEYS[season][notary])
        notary_id += 1

for season in NOTARY_PUBKEYS:
    notaries = list(NOTARY_PUBKEYS[season].keys())
    notaries.sort()
    for notary in notaries:
        if season.find("Season_3") != -1:
            SEASONS_INFO["Season_3"]['notaries'].append(notary)
        elif season.find("Season_4") != -1:
            SEASONS_INFO["Season_4"]['notaries'].append(notary)
        else:
            SEASONS_INFO[season]['notaries'].append(notary)

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

def get_unrecorded_KMD_txids(cursor, tip, season):
    recorded_txids = []
    start_block = SEASONS_INFO[season]["start_block"]
    end_block = SEASONS_INFO[season]["end_block"]

    if end_block <= tip:
        tip = end_block

    if skip_until_yesterday:
        start_block = tip - 24*60*2

    all_txids = []
    chunk_size = 100000

    while tip - start_block > chunk_size:
        logger.info("Getting notarization TXIDs from block chain data for blocks " \
               +str(start_block+1)+" to "+str(start_block+chunk_size)+"...")
        all_txids += get_ntx_txids(NTX_ADDR, start_block+1, start_block+chunk_size)
        start_block += chunk_size
    all_txids += get_ntx_txids(NTX_ADDR, start_block+1, tip)
    recorded_txids = get_existing_ntxids(cursor)
    unrecorded_txids = set(all_txids) - set(recorded_txids)
    return unrecorded_txids