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
import logging
import logging.handlers
from base_58 import *
from lib_const import *
from lib_api import *
from lib_table_update import *
from lib_table_select import *
from models import *

logger = logging.getLogger(__name__)

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
        if season.find("Testnet") == -1:
            if time_stamp >= SEASONS_INFO[season]['start_time'] and time_stamp <= SEASONS_INFO[season]['end_time']:
                return season
        else:
            return season
    return None

def get_season_from_block(block):
    if not isinstance(block, int):
        block = int(block)
    for season in SEASONS_INFO:
        if season.find("Testnet") == -1:
            if block >= SEASONS_INFO[season]['start_block'] and block <= SEASONS_INFO[season]['end_block']:
                return season
    return None

def get_seasons_from_address(addr, chain="KMD"):
    addr_seasons = []
    for season in NOTARY_ADDRESSES_DICT:
        for notary in NOTARY_ADDRESSES_DICT[season]:
            season_addr = NOTARY_ADDRESSES_DICT[season][notary][chain]
            if addr == season_addr:
                addr_seasons.append(season)
    return addr_seasons

def get_season_from_addresses(address_list, time_stamp, tx_chain="KMD"):
    if BTC_NTX_ADDR in address_list:
        address_list.remove(BTC_NTX_ADDR)

    print(address_list)

    seasons = list(SEASONS_INFO.keys())[::-1]
    notary_seasons = []
    last_season = None

    for season in seasons:

        if last_season != season:
            notary_seasons = []

        season_notaries = list(NOTARY_ADDRESSES_DICT[season].keys())

        for notary in season_notaries:
            addr = NOTARY_ADDRESSES_DICT[season][notary][tx_chain]

            if addr in address_list:
                notary_seasons.append(season)

        if len(notary_seasons) == 13 or "Season_5_Testnet" in notary_seasons and len(set(notary_seasons)) == 1:
            break
        last_season_num = season

    if "Season_5_Testnet" in notary_seasons and len(set(notary_seasons)) == 1:
        return "Season_5_Testnet"

    elif len(notary_seasons) == 13 and len(set(notary_seasons)) == 1:
        return notary_seasons[0]

    else:
        return get_season(time_stamp)

def get_season_from_btc_addresses(address_list, time_stamp):
    if BTC_NTX_ADDR in address_list:
        address_list.remove(BTC_NTX_ADDR)

    seasons = list(SEASONS_INFO.keys())[::-1]
    for season in seasons:
        notaries_in_season = []
        for address in address_list:
            if address in NN_BTC_ADDRESSES_DICT[season]:
                notaries_in_season.append(NN_BTC_ADDRESSES_DICT[season][address])
                if len(notaries_in_season) == 13:
                    return season

    return get_season(time_stamp)


def get_notary_from_address(address):
    if address in KNOWN_ADDRESSES:
        return KNOWN_ADDRESSES[address]
    return "unknown"

def lil_endian(hex_str):
    return ''.join([hex_str[i:i+2] for i in range(0, len(hex_str), 2)][::-1])

def get_ntx_txids(NTX_ADDR, start, end):
    return RPC["KMD"].getaddresstxids({"addresses": [NTX_ADDR], "start":start, "end":end})
  
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
    raw_tx = RPC["KMD"].getrawtransaction(txid,1)
    block_hash = raw_tx['blockhash']
    dest_addrs = raw_tx["vout"][0]['scriptPubKey']['addresses']
    block_time = raw_tx['blocktime']
    block_datetime = dt.utcfromtimestamp(raw_tx['blocktime'])
    this_block_height = raw_tx['height']
    if len(dest_addrs) > 0:
        if NTX_ADDR in dest_addrs:
            if len(raw_tx['vin']) > 1:
                notary_list = []
                address_list = []
                for item in raw_tx['vin']:
                    if "address" in item:
                        address_list.append(item['address'])
                        if item['address'] in KNOWN_ADDRESSES:
                            notary = KNOWN_ADDRESSES[item['address']]
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

def get_btc_ntxids(stop_block, exit=None):
    has_more=True
    before_block=None
    ntx_txids = []
    page = 1
    exit_loop = False
    existing_txids = get_existing_btc_ntxids()
    while has_more:
        logger.info(f"Getting TXIDs from API Page {page}...")
        resp = get_btc_address_txids(BTC_NTX_ADDR, before_block)
        # To avoid API limits when running on cron, we dont want to go back too many pages. Set this to 99 when back filling, otherwise 2 pages should be enough.
        if page > API_PAGE_BREAK:
            break
        if "error" in resp:
            exit_loop = api_sleep_or_exit(resp, exit)
        else:
            page += 1
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
                
        if exit_loop or page >= API_PAGE_BREAK:
            logger.info("exiting address txid loop!")
            break
    ntx_txids = list(set((ntx_txids)))
    return ntx_txids



def get_new_nn_btc_txids(existing_txids, notary_address):
    before_block=None
    page = 1
    exit_loop = False
    api_txids = []
    new_txids = []
    while True:
        # To avoid API limits when running on cron, we dont want to go back too many pages. Set this to 99 when back filling, otherwise 2 pages should be enough.
        if page > API_PAGE_BREAK:
            break
        logger.info(f"Getting TXIDs from API Page {page}...")
        resp = get_btc_address_txids(notary_address, before_block)
        if "error" in resp:
            logger.info(f"Error in resp: {resp}")
            exit_loop = api_sleep_or_exit(resp, exit=None)
        else:
            page += 1
            if 'txrefs' in resp:
                tx_list = resp['txrefs']
                before_block = tx_list[-1]['block_height']

                for tx in tx_list:
                    api_txids.append(tx['tx_hash'])
                    if tx['tx_hash'] not in new_txids and tx['tx_hash'] not in existing_txids:
                        new_txids.append(tx['tx_hash'])
                        logger.info(f"appended tx {tx}")

                # exit loop if earlier than s4
                if before_block < 634774:
                    logger.info("No more for s4!")
                    exit_loop = True
            else:
                # exit loop if no more tx for address at api
                logger.info("No more for address!")
                exit_loop = True

        if exit_loop:
            logger.info("exiting address txid loop!")
            break

    num_api_txids = list(set((api_txids)))
    logger.info(f"{len(num_api_txids)} DISTINCT TXIDs counted from API")

    return new_txids


def get_notaries_from_addresses(addresses):
    notaries = []
    if BTC_NTX_ADDR in addresses:
        addresses.remove(BTC_NTX_ADDR)
    for address in addresses:
        if address in KNOWN_ADDRESSES:
            notary = KNOWN_ADDRESSES[address]
            notaries.append(notary)
        else:
            notaries.append(address)
    notaries.sort()
    return notaries

# MINED OPS

def update_miner(block):
    logger.info("Getting mining data for block "+str(block))
    blockinfo = RPC["KMD"].getblock(str(block), 2)
    for tx in blockinfo['tx']:
        if len(tx['vin']) > 0:
            if 'coinbase' in tx['vin'][0]:
                if 'addresses' in tx['vout'][0]['scriptPubKey']:
                    address = tx['vout'][0]['scriptPubKey']['addresses'][0]
                    if address in KNOWN_ADDRESSES:
                        name = KNOWN_ADDRESSES[address]
                    else:
                        name = address
                else:
                    address = "N/A"
                    name = "non-standard"

                row = mined_row()
                row.block_height = block
                row.block_time = blockinfo['time']
                row.block_datetime = dt.utcfromtimestamp(blockinfo['time'])
                row.address = address
                row.name = name
                row.txid = tx['txid']
                row.season = get_season_from_block(block)
                row.value = Decimal(tx['vout'][0]['value'])
                row.update()

def get_daily_mined_counts(day):
    result = 0
    results = get_mined_date_aggregates(day)
    time_stamp = int(time.time())
    for item in results:
        row = daily_mined_count_row()
        row.notary = item[0]
        if row.notary in ALL_SEASON_NOTARIES:
            row.blocks_mined = int(item[1])
            row.sum_value_mined = float(item[2])
            row.mined_date = str(day)
            row.update()
    return result

# MISC TABLE OPS

def delete_from_table(table, condition=None):
    sql = "DELETE FROM "+table
    if condition:
        sql = sql+" WHERE "+condition
    sql = sql+";"
    CURSOR.execute()
    CONN.commit()

def ts_col_to_season_col(ts_col, season_col, table):
    for season in SEASONS_INFO:
        sql = "UPDATE "+table+" \
               SET "+season_col+"='"+season+"' \
               WHERE "+ts_col+" > "+str(SEASONS_INFO[season]['start_time'])+" \
               AND "+ts_col+" < "+str(SEASONS_INFO[season]['end_time'])+";"
        CURSOR.execute(sql)
        CONN.commit()

now = int(time.time())


def update_ntx_tenure(chains, seasons):
    for chain in chains:
        for season in seasons:
            logger.info(f"Getting tenure for {season} {chain}")      
            ntx_results = get_ntx_min_max(season, chain)
            logger.info(chain+" "+season+": "+str(ntx_results))
            max_blk = ntx_results[0]
            max_blk_time = ntx_results[1]
            min_blk = ntx_results[2]
            min_blk_time = ntx_results[3]
            ntx_count = ntx_results[4]
            if max_blk is not None:
                row = ntx_tenure_row()
                row.chain = chain
                row.first_ntx_block = min_blk
                row.last_ntx_block = max_blk
                row.first_ntx_block_time = min_blk_time
                row.last_ntx_block_time = max_blk_time
                row.ntx_count = ntx_count
                row.season = season
                row.update()


def get_unrecorded_KMD_txids(tip, season):
    recorded_txids = []
    start_block = SEASONS_INFO[season]["start_block"]
    end_block = SEASONS_INFO[season]["end_block"]

    if end_block <= tip:
        tip = end_block

    if SKIP_UNTIL_YESTERDAY:
        start_block = tip - 24*60*2

    all_txids = []
    chunk_size = 100000

    while tip - start_block > chunk_size:
        logger.info("Getting notarization TXIDs from block chain data for blocks " \
               +str(start_block+1)+" to "+str(start_block+chunk_size)+"...")
        all_txids += get_ntx_txids(NTX_ADDR, start_block+1, start_block+chunk_size)
        start_block += chunk_size
    all_txids += get_ntx_txids(NTX_ADDR, start_block+1, tip)
    recorded_txids = get_existing_ntxids()
    unrecorded_txids = set(all_txids) - set(recorded_txids)
    return unrecorded_txids


def get_nn_btc_tx_parts(txid):
    r = requests.get(f"{OTHER_SERVER}/api/info/nn_btc_txid?txid={txid}")
    tx_parts_list = r.json()["results"][0]
    
    tx_vins = []
    tx_vouts = []
    for part in tx_parts_list:
        if part["input_index"] != -1:
            tx_vins.append(part)
        if part["output_index"] != -1:
            tx_vouts.append(part)
    return tx_vins, tx_vouts

def get_nn_btc_tx_parts_local(txid):
    r = requests.get(f"{THIS_SERVER}/api/info/nn_btc_txid?txid={txid}")
    tx_parts_list = r.json()["results"][0]
    
    tx_vins = []
    tx_vouts = []
    for part in tx_parts_list:
        if part["input_index"] != -1:
            tx_vins.append(part)
        if part["output_index"] != -1:
            tx_vouts.append(part)
    return tx_vins, tx_vouts

def get_new_notary_txids(notary_address, season=None): 
    if season:
        existing_txids = get_existing_nn_btc_txids(None, None, season, NN_BTC_ADDRESSES_DICT[season][notary_address])
        url = f"{OTHER_SERVER}/api/info/nn_btc_txid_list?notary={NN_BTC_ADDRESSES_DICT[season][notary_address]}&season={season}"
        logger.info(f"{len(existing_txids)} existing txids in local DB detected for {NN_BTC_ADDRESSES_DICT[season][notary_address]} {notary_address} {season}")
    else:
        existing_txids = get_existing_nn_btc_txids(None, None, None, ALL_SEASON_NN_BTC_ADDRESSES_DICT[notary_address])
        url = f"{OTHER_SERVER}/api/info/nn_btc_txid_list?notary={ALL_SEASON_NN_BTC_ADDRESSES_DICT[notary_address]}"
        logger.info(f"{len(existing_txids)} existing txids in local DB detected for {ALL_SEASON_NN_BTC_ADDRESSES_DICT[notary_address]} {notary_address}")
    
    logger.info(url)
    r = requests.get(url)
    resp = r.json()
    txids = resp['results'][0]

    new_txids = []
    for txid in txids:
        if txid not in existing_txids:
            new_txids.append(txid)
    new_txids = list(set(new_txids))

    if season:
        logger.info(f"{len(new_txids)} extra txids detected for {NN_BTC_ADDRESSES_DICT[season][notary_address]} {notary_address} {season}")
    else:
        logger.info(f"{len(new_txids)} extra txids detected for {ALL_SEASON_NN_BTC_ADDRESSES_DICT[notary_address]} {notary_address}")
    return new_txids


def categorize_import_transactions(notary_address, season):

    logger.info(f">>> Categorising {notary_address} for {season}")
    new_txids = get_new_notary_txids(notary_address)
    logger.info(f"Processing ETA: {0.02*len(new_txids)} sec")
    i = 1
    j = 1
    for txid in new_txids:
        txid_data = tx_row()
        txid_data.txid = txid

        # import NTX if existing on other server
        url = f"{OTHER_SERVER}/api/info/nn_btc_txid?txid={txid}"
        r = requests.get(url)
        time.sleep(0.02)
        try:
            resp = r.json()
            if resp['count'] > 0:

                # Detect NTX season
                tx_addresses = []
                for item in resp['results'][0]:
                    txid_data.block_hash = item["block_hash"]
                    txid_data.block_height = item["block_height"]
                    txid_data.block_time = item["block_time"]
                    txid_data.block_datetime = item["block_datetime"]
                    txid_data.num_inputs = item["num_inputs"]
                    txid_data.num_outputs = item["num_outputs"]
                    txid_data.fees = item["fees"]

                    if item["address"] != BTC_NTX_ADDR:
                        tx_addresses.append(item["address"])
                tx_addresses = list(set(tx_addresses))

                txid_data.season = get_season_from_btc_addresses(tx_addresses, resp['results'][0][0]["block_time"])

                tx_vins, tx_vouts = get_nn_btc_tx_parts(txid)
                txid_data.category = get_category_from_vins_vouts(tx_vins, tx_vouts, txid_data.season)

                for vin in tx_vins:
                    txid_data.address = vin["address"]
                    txid_data.notary = get_notary_from_btc_address(vin["address"], txid_data.season, vin["notary"])
                    txid_data.address = vin["address"]
                    txid_data.input_index = vin["input_index"]
                    txid_data.input_sats = vin["input_sats"]
                    txid_data.output_index = vin["output_index"]
                    txid_data.output_sats = vin["output_sats"]
                    txid_data.update()

                for vout in tx_vouts:
                    txid_data.address = vout["address"]
                    txid_data.notary = get_notary_from_btc_address(vout["address"], txid_data.season, vout["notary"])                    
                    txid_data.address = vout["address"]
                    txid_data.input_index = vout["input_index"]
                    txid_data.input_sats = vout["input_sats"]
                    txid_data.output_index = vout["output_index"]
                    txid_data.output_sats = vout["output_sats"]
                    txid_data.update()

        except Exception as e:
            logger.error(e)
            logger.error(r.text)
            
        
        j += 1
    i += 1

def get_notary_from_btc_address(address, season=None, notary=None):
    if address == BTC_NTX_ADDR:
        return "BTC_NTX_ADDR"

    if address in NN_BTC_ADDRESSES_DICT[season]:
        return NN_BTC_ADDRESSES_DICT[season][address]

    seasons = list(SEASONS_INFO.keys())[::-1]

    for s in seasons:
        if address in NN_BTC_ADDRESSES_DICT[s]:
            return NN_BTC_ADDRESSES_DICT[s][address]
    if notary:
        return notary
    else:
        return "non-NN"

def validate_ntx_vins(vins):
    for vin in vins:
        notary = get_notary_from_btc_address(vin["addresses"][0])

        if notary == "non-NN" or vin["output_value"] != 10000:
            return False

    return True

def validate_ntx_vouts(vouts):
    for vout in vouts:

        if vout["addresses"] is not None:

            if vout["addresses"][0] == BTC_NTX_ADDR and vout["value"] == 98800:
                return True

    return False

def get_category_from_vins_vouts(tx_vins, tx_vouts, season):
    # TODO: Align this with api populate script
    notary_vins = []
    notary_vouts = []
    non_notary_vins = []
    non_notary_vouts = []
    replenish_vins = False
    replenish_vouts = False
    to_dragonhound = False
    ntx_vin = True
    ntx_vout = False

    for vin in tx_vins:
        txid = vin["txid"]
        import_category = vin["category"]
        notary = get_notary_from_btc_address(vin["address"], season, vin["notary"])
        if notary in ALL_SEASON_NOTARIES:
            notary_vins.append(notary)
        else:
            non_notary_vins.append(notary)

        if notary in ["dragonhound_NA", "Replenish_Address"]:
            replenish_vins = True

        if vin["input_sats"] != 10000:
            ntx_vin = False

    for vout in tx_vouts:
        txid = vout["txid"]
        import_category = vout["category"]
        notary = get_notary_from_btc_address(vout["address"], season, vout["notary"])
        if notary in ALL_SEASON_NOTARIES:
            notary_vouts.append(notary)
        else:
            non_notary_vouts.append(notary)

        if vout["address"] == "SPAM":
            # TODO: SPAM sometimes being mis-tagged as Replenish
            return "SPAM"

        elif vout['address'] == BTC_NTX_ADDR:
            ntx_vout = True

        elif notary == "dragonhound_NA":
            sats = vout["output_sats"]
            to_dragonhound = True

        elif notary in ALL_SEASON_NOTARIES:
            replenish_vouts = True

    notary_vins = list(set(notary_vins))
    notary_vouts = list(set(notary_vouts))
    non_notary_vins = list(set(non_notary_vins))
    non_notary_vouts = list(set(non_notary_vouts))
    
    '''
    if txid == "0b415ea1ec9852393903370fb4c3bf38b437a024f681f8b734de29579a06cf2f":
        print(f"ntx_vout {ntx_vout}")
        print(f"ntx_vin {ntx_vin}")
        print(f"len(notary_vins) {len(notary_vins)}")
        print(f"import_category {import_category}")
        input("continue?")
    '''

    # overrides (skip if -1 vin/vout)
    try:
        if txid == ["9d29730c09f7d1983a413a14bb0b8ffcf0cb652472a428e97c250da03ae47082", "9bc103a16c477d55ba42e4fc97a6256e04813e9b947c895c6cd0e2f028bdfa67"] :
            return "MadMax personal top up"
        elif txid == "248ef589d50047a43d987f6af05ab8568f5a2070e25c3e1d3b063884948634ee":
            return "MadMax personal top up repaid"
        elif txid in [
            "e4b2e4afa20b7cf39e96422bb72a522e0cb9fc49dbd4cfa5386b3733833365aa",
            "5d93f75414d6c581e8589339fe1915437a01b0e8ee4149a5fea508a080b1815e",
            "535bac3813dd0e36db503dbeef916f8e1198386a5909b1b7142a5984e91309c5",
            "f18186cd8a05f2a5148694ccbf95c4230b4b63183d835c9d88fed15b16c1db7d"
            ]:
            return "previous season funds transfer"
    except:
        pass

    if ntx_vout and ntx_vin:
        if len(notary_vins) == 13:
            return "NTX"
        elif import_category == "NTX":
            return "Low Vin NTX"
        else:
            return "Damaged NTX"

    if ntx_vin and import_category == "NTX":
        if len(notary_vins) == 13:
            return "No Vout NTX"
        else:
            return "Low Vin, No Vout NTX"


    if len(notary_vins) == len(notary_vouts) and len(notary_vins) == 1 and notary_vins[0] == notary_vouts[0]:
        # 76aeb20c7af38141720ef672cbb295015e24ca129b62ac02830c35b357d02238 not a split!
        if len(non_notary_vins) == 0 and len(non_notary_vouts) == 0:
            return "Split"
        else:
            # TODO: add NN-related addresses
            return "Consolidate"
        

    if replenish_vins and replenish_vouts:
        return "Top Up"

    if to_dragonhound and sats >= 10000000:
        return "Incoming Replenish"

    return "Other"

