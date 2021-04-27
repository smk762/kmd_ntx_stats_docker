#!/usr/bin/env python3
import os
import time
import json
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
from base_58 import *
from lib_const import *
from lib_api import *
from lib_helper import *
from lib_table_update import *
from lib_table_select import *
from models import daily_mined_count_row, mined_row, ntx_tenure_row


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

def get_notarised_data(txid):
    coins_list = get_all_coins()

    try:
        raw_tx = RPC["KMD"].getrawtransaction(txid,1)
        block_hash = raw_tx['blockhash']
        dest_addrs = raw_tx["vout"][0]['scriptPubKey']['addresses']
        if 'blocktime' in raw_tx:
            if len(dest_addrs) > 0:
                if NTX_ADDR in dest_addrs:
                    block_time = raw_tx['blocktime']

                    block_datetime = dt.utcfromtimestamp(raw_tx['blocktime'])
                    this_block_height = raw_tx['height']
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

                        if opret.find("OP_RETURN") != -1:
                            scriptPubKey_asm = opret.replace("OP_RETURN ","")
                            ac_ntx_blockhash = lil_endian(scriptPubKey_asm[:64])
                            try:
                                ac_ntx_height = int(lil_endian(scriptPubKey_asm[64:72]),16) 
                            except Exception as e:
                                logger.error(f"error {e} scriptPubKey_asm: {scriptPubKey_asm}")
                                sys.exit()
                            scriptPubKeyBinary = binascii.unhexlify(scriptPubKey_asm[70:])
                            chain = get_ticker(scriptPubKeyBinary)
                            if len(chain) > 10:
                                logger.warning(f"chain = {chain} for {txid}")

                            # TODO: This could potentially misidentify - be vigilant.
                            for x in coins_list:
                                if len(x) > 2 and x not in EXCLUDE_DECODE_OPRET_COINS:
                                    if chain.endswith(x):
                                        chain = x

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
                                season, server = get_season_from_addresses(address_list, block_time, "KMD", chain, txid, notary_list)
                                if season in DPOW_EXCLUDED_CHAINS: 
                                    if chain in DPOW_EXCLUDED_CHAINS[season]:
                                        season = "Unofficial"
                                        server = "Unofficial"
                                row_data = (chain, this_block_height, block_time, block_datetime,
                                            block_hash, notary_list, address_list, ac_ntx_blockhash, ac_ntx_height,
                                            txid, opret, season, server, "N/A")
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
        else:
            return None
    except Exception as e:
        logger.error(f"Error in [get_notarised_data]: {e}")
        logger.error(f"[get_notarised_data] txid: {txid}")
        return None




def get_new_nn_btc_txids(existing_txids, notary_address, page_break=None, stop_block=None):
    before_block=None
    stop_block = 634774
    page = 1
    exit_loop = False
    api_txids = []
    new_txids = []
    
    if not page_break:
        page_break = API_PAGE_BREAK
    
    if not stop_block:
        stop_block = 634774

    while True:
        # To avoid API limits when running on cron, we dont want to go back too many pages. Set this to 99 when back filling, otherwise 2 pages should be enough.
        if page > page_break:
            break
        logger.info(f"Getting TXIDs from API Page {page}...")
        resp = get_btc_address_txids(notary_address, before_block)
        if "error" in resp:
            logger.info(f"Error in resp: {resp}")
            exit_loop = api_sleep_or_exit(resp, exit=True)
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
                if before_block < stop_block:
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

# MINED OPS


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



def get_dpow_scoring_window(season, chain, server):

    official_start = None
    official_end = None

    if season in SEASONS_INFO:

        official_start = SEASONS_INFO[season]["start_time"]
        official_end = SEASONS_INFO[season]["end_time"]

    if season in PARTIAL_SEASON_DPOW_CHAINS:
        for partial_season_server in PARTIAL_SEASON_DPOW_CHAINS[season]["Servers"]:

            if chain in PARTIAL_SEASON_DPOW_CHAINS[season]["Servers"][partial_season_server]:

                # Overcomes Duel Wielding GLEEC issue.
                if partial_season_server == server:

                    if "start_time" in PARTIAL_SEASON_DPOW_CHAINS[season]["Servers"][partial_season_server][chain]:
                        official_start = PARTIAL_SEASON_DPOW_CHAINS[season]["Servers"][partial_season_server][chain]["start_time"]

                    if "end_time" in PARTIAL_SEASON_DPOW_CHAINS[season]["Servers"][partial_season_server][chain]:
                        official_end = PARTIAL_SEASON_DPOW_CHAINS[season]["Servers"][partial_season_server][chain]["end_time"]

    scored_list, unscored_list = get_ntx_scored(season, chain, official_start, official_end, server)

    return official_start, official_end, scored_list, unscored_list



def get_unrecorded_KMD_txids(tip, season, start_block=None, end_block=None):
    recorded_txids = []
    if not start_block:
        start_block = SEASONS_INFO[season]["start_block"]
    if not end_block:
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
    recorded_txids = get_existing_notarised_txids()
    logger.info(f"Scanned txids: {len(all_txids)}")
    logger.info(f"Recorded txids: {len(recorded_txids)}")
    unrecorded_txids = list(set(all_txids) - set(recorded_txids))
    logger.info(f"Unrecorded txids: {len(unrecorded_txids)}")
    return unrecorded_txids


def get_new_notary_txids(notary_address, chain, season):

    existing_txids = []
    if chain == "BTC":
        existing_txids = get_existing_nn_btc_txids(None, None, season, NN_BTC_ADDRESSES_DICT[season][notary_address])
        url = f"{OTHER_SERVER}/api/info/btc_txid_list?notary={NN_BTC_ADDRESSES_DICT[season][notary_address]}&season={season}"
        logger.info(f"{len(existing_txids)} existing txids in local DB detected for {NN_BTC_ADDRESSES_DICT[season][notary_address]} {notary_address} {season}")
           
    elif chain == "LTC":
        existing_txids = get_existing_nn_ltc_txids(None, None, season, NN_LTC_ADDRESSES_DICT[season][notary_address])
        url = f"{OTHER_SERVER}/api/info/ltc_txid_list?notary={NN_LTC_ADDRESSES_DICT[season][notary_address]}&season={season}"
        logger.info(f"{len(existing_txids)} existing txids in local DB detected for {NN_LTC_ADDRESSES_DICT[season][notary_address]} {notary_address} {season}")
     
    logger.info(url)
    r = requests.get(url)
    resp = r.json()
    txids = resp['results']

    new_txids = []
    for txid in txids:
        if txid not in existing_txids:
            new_txids.append(txid)
    new_txids = list(set(new_txids))

    if chain == "BTC":
        logger.info(f"{len(new_txids)} extra txids detected for {NN_BTC_ADDRESSES_DICT[season][notary_address]} {notary_address} {season}")
    
    if chain == "LTC":
        logger.info(f"{len(new_txids)} extra txids detected for {NN_LTC_ADDRESSES_DICT[season][notary_address]} {notary_address} {season}")

    return new_txids



def validate_ntx_vins(vins):
    for vin in vins:
        notary = get_notary_from_btc_address(vin["addresses"][0])

        if notary == "non-NN" or vin["output_value"] != 10000:
            return False

    return True

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

### LTC
### TODO: standardise this for all chains.

def get_new_nn_ltc_txids(existing_txids, notary_address):
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
        resp = get_ltc_address_txids(notary_address, before_block)
        if "error" in resp:
            logger.info(f"Error in resp: {resp}")
            exit_loop = api_sleep_or_exit(resp, exit=True)
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


def get_category_from_ltc_vins_vouts(tx_vins, tx_vouts, season):
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
        notary = get_notary_from_ltc_address(vin["address"], season, vin["notary"])
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
        notary = get_notary_from_ltc_address(vout["address"], season, vout["notary"])
        if notary in ALL_SEASON_NOTARIES:
            notary_vouts.append(notary)
        else:
            non_notary_vouts.append(notary)

        if vout["address"] == "SPAM":
            # TODO: SPAM sometimes being mis-tagged as Replenish
            return "SPAM"

        elif vout['address'] == LTC_NTX_ADDR:
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

def validate_ltc_ntx_vins(vins):
    for vin in vins:
        notary = get_notary_from_ltc_address(vin["addresses"][0])

        if notary == "non-NN" or vin["output_value"] != 10000:
            return False

    return True
