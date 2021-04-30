#!/usr/bin/env python3
import json
import time
import random
import requests
from decimal import *
from datetime import datetime as dt
import datetime
import dateutil.parser as dp
from lib_helper import *
from lib_notary import *
from lib_table_update import update_nn_btc_tx_notary_from_addr
from lib_table_select import get_existing_nn_btc_txids, get_existing_notarised_txids, get_notarised_seasons
from lib_api import get_btc_tx_info

from models import tx_row, notarised_row, get_chain_epoch_score_at, get_chain_epoch_at
from lib_const import *
from known_txids import *


def get_linked_addresses(addr=None, notary=None):
    linked_addresses = {}
    sql = f"SELECT DISTINCT address, notary from nn_btc_tx"
    conditions = [f"address='{addr}'"]
    if notary:
        conditions = [f"notary = '{notary}' or notary = '{notary} (linked)'"]

    if len(conditions) > 0:
        sql += " where "
        sql += " and ".join(conditions)    
    sql += ";"

    CURSOR.execute(sql)
    address_rows = CURSOR.fetchall()

    if len(address_rows) > 0:

        for row in address_rows:
            address = row[0]
            notary = row[1].replace(" (linked)", "")

            if notary in ALL_SEASON_NOTARIES:

                if notary not in linked_addresses:
                    if addr not in ALL_SEASON_NOTARY_BTC_ADDRESSES:
                        linked_addresses.update({notary:[address]})

                else:
                    linked_addresses[notary].append(address)

    return linked_addresses

def is_linked_address(addr, notary=None):
    linked_addresses = get_linked_addresses(addr, notary)
    if len(linked_addresses) > 0:
        return True
    else:
        return False

def is_notary_address(addr):
    if addr in ALL_SEASON_NOTARY_BTC_ADDRESSES:
        return True
    return False

def detect_ntx(vins, vouts, addresses):
    if BTC_NTX_ADDR in addresses and len(vins) == 13 and len(vouts) == 2:
        for vin in vins:
            if vin["output_value"] != 10000:
                logger.debug('vin["output_value"] != 10000')
                return False
            if vin["addresses"][0] not in ALL_SEASON_NOTARY_BTC_ADDRESSES:
                logger.debug('vin["addresses"][0] not in ALL_SEASON_NOTARY_BTC_ADDRESSES')
                return False

        for vout in vouts:
            if vout["addresses"] is not None:
                if vout["addresses"][0] != BTC_NTX_ADDR:
                    logger.debug('vout["addresses"] != BTC_NTX_ADDR')
                    return False
                if vout["value"] != 98800:
                    logger.debug('vout["value"] != 98800')
                    return False

        return True
    else:
        return False

def detect_replenish(vins, vouts):

    vin_notaries = []
    vin_non_notary_addresses = []
    for vin in vins:
        address = vin["addresses"][0]
        if is_notary_address(address):
            notary = ALL_SEASON_NN_BTC_ADDRESSES_DICT[address]
            vin_notaries.append(notary)
        elif is_linked_address(address, "dragonhound_NA"):
            notary = "dragonhound_NA"
            vin_notaries.append(notary)
        else:
            vin_non_notary_addresses.append(address)
    
    replenish_vin = False
    if len(list(set(vin_notaries))) == 1:
        if vin_notaries[0] == "dragonhound_NA":
            replenish_vin = True

    vout_notaries = []
    vout_non_notary_addresses = []
    for vout in vouts:
        if vout["addresses"]:
            sats = vout["value"]
            address = vout["addresses"][0]
            if is_notary_address(address):
                if sats >= 1000000:
                    notary = ALL_SEASON_NN_BTC_ADDRESSES_DICT[address]
                    if notary != "dragonhound_NA":
                        vout_notaries.append(notary)
            elif not is_linked_address(address):
                vout_non_notary_addresses.append(address)

    replenish_vout = False
    if len(vout_notaries) > 0:
        replenish_vout = True

    if replenish_vin and replenish_vout:
        '''
        for addr in vin_non_notary_addresses:

            if addr not in ALL_SEASON_NOTARY_BTC_ADDRESSES:
                update_nn_btc_tx_notary_from_addr("dragonhound_NA (linked)", addr)
        for addr in vout_non_notary_addresses:
            if addr not in ALL_SEASON_NOTARY_BTC_ADDRESSES:
                update_nn_btc_tx_notary_from_addr("dragonhound_NA (linked)", addr)
        '''
        return True
    return False

def detect_consolidate(vins, vouts):
    vin_notaries = []
    vin_non_notary_addresses = []
    for vin in vins:
        address = vin["addresses"][0]
        if is_notary_address(address):
            notary = ALL_SEASON_NN_BTC_ADDRESSES_DICT[address]
            vin_notaries.append(notary)
        else:
            vin_non_notary_addresses.append(address)

    if len(list(set(vin_notaries))) == 1:
        notary = vin_notaries[0]

        vout_notaries = []
        vout_non_notary_addresses = []
        for vout in vouts:
            address = vout["addresses"][0]
            if is_notary_address(address):
                notary = ALL_SEASON_NN_BTC_ADDRESSES_DICT[address]
                vout_notaries.append(notary)
            else:
                vout_non_notary_addresses.append(address)

        if len(list(set(vout_notaries))) == 1 and is_notary_address(vouts[0]["addresses"][0]):
            if notary == vout_notaries[0]:
                '''
                for addr in vin_non_notary_addresses:
                    if addr not in ALL_SEASON_NOTARY_BTC_ADDRESSES:
                        update_nn_btc_tx_notary_from_addr(f"{notary} (linked)", addr)
                for addr in vout_non_notary_addresses:
                    if addr not in ALL_SEASON_NOTARY_BTC_ADDRESSES:
                        update_nn_btc_tx_notary_from_addr(f"{notary} (linked)", addr)
                '''
                return True

    return False

def update_notary_linked_vins(vins):
    vin_notaries = []
    vin_non_notary_addresses = []
    for vin in vins:
        address = vin["addresses"][0]
        if is_notary_address(address):
            notary = ALL_SEASON_NN_BTC_ADDRESSES_DICT[address]
            vin_notaries.append(notary)
        else:
            vin_non_notary_addresses.append(address)

    if len(list(set(vin_notaries))) == 1 and len(vin_non_notary_addresses) > 0:
        for addr in vin_non_notary_addresses:
            if addr not in ALL_SEASON_NOTARY_BTC_ADDRESSES:
                update_nn_btc_tx_notary_from_addr(f"{notary} (linked)", address)


def detect_intra_notary(vins, vouts):
    for vin in vins:
        address = vin["addresses"][0]
        if is_notary_address(address):
            notary = ALL_SEASON_NN_BTC_ADDRESSES_DICT[address]
        else:
            return False

    for vout in vouts:
        address = vout["addresses"][0]
        if is_notary_address(address):
            notary = ALL_SEASON_NN_BTC_ADDRESSES_DICT[address]
        else:
            return False

    return True

def detect_spam(btc_row, addresses, vouts):
    if '1See1xxxx1memo1xxxxxxxxxxxxxBuhPF' in addresses:        
        btc_row.input_sats = 0
        btc_row.output_sats = 0
        btc_row.input_index = 0
        btc_row.output_index = 0
        btc_row.category = "SPAM"
        for vout in vouts:
            btc_row.address = addresses[0]
            btc_row.notary = get_notary_from_btc_address(btc_row.address, btc_row.season)
            if btc_row.notary != "non-NN":
                btc_row.update()
        return True
    return False

def detect_cipi_faucet(btc_row, addresses, vins):
    if vins[0]["addresses"][0] == CIPI_FAUCET_ADDR and len(addresses) == 2:
        addresses.remove(CIPI_FAUCET_ADDR)
        btc_row.category = "cipi_faucet"
        btc_row.input_sats = -99
        btc_row.output_sats = -99
        btc_row.input_index = -99
        btc_row.output_index = -99
        btc_row.address = addresses[0]
        btc_row.notary = get_notary_from_btc_address(btc_row.address, btc_row.season)
        btc_row.update()
        return True
    return False

def detect_split(btc_row, addresses):
    if len(addresses) == 1:
        btc_row.category = "Split"
        btc_row.input_sats = -99
        btc_row.output_sats = -99
        btc_row.input_index = -99
        btc_row.output_index = -99
        btc_row.address = addresses[0]
        btc_row.notary = get_notary_from_btc_address(btc_row.address, btc_row.season)
        btc_row.update()
        return True
    return False



def scan_btc_transactions(season):
    season_btc_addresses = NOTARY_BTC_ADDRESSES[season][:]+[BTC_NTX_ADDR]
    num_addr = len(season_btc_addresses)
    notary_last_ntx = get_notary_last_ntx("BTC")

    i = 0


    while len(season_btc_addresses) > 0:
        if BTC_NTX_ADDR in season_btc_addresses:
            notary_address = BTC_NTX_ADDR
        else:
            notary_address = random.choice(season_btc_addresses)
        i += 1

        if notary_address in NN_BTC_ADDRESSES_DICT[season]:
            notary_name = NN_BTC_ADDRESSES_DICT[season][notary_address]
        else:
            notary_name = "non-NN"

        existing_nn_btc_txids = get_existing_nn_btc_txids(notary_address)
        existing_notarised_txids = get_existing_notarised_txids("BTC")
        existing_txids = list(set(existing_nn_btc_txids)&set(existing_notarised_txids))
        txids = get_new_nn_btc_txids(existing_txids, notary_address)

        logger.info(f"[scan_btc_transactions] {len(existing_txids)} EXIST IN DB FOR {notary_address} | {notary_name} {season} ({i}/{num_addr})")
        logger.info(f"[scan_btc_transactions] {len(txids)} NEW TXIDs TO PROCESS FOR {notary_address} | {notary_name} {season} ({i}/{num_addr})")

        num_txids = len(txids)

        j = 0
        for txid in txids:
            j += 1
            # Get tx data from Blockcypher API
            logger.info(f"[scan_btc_transactions] >>> Processing txid {j}/{num_txids}")
            tx_info = get_btc_tx_info(txid, True, True)
            if 'error' in tx_info:
                pass
            elif 'fees' in tx_info:
                btc_row = tx_row()
                btc_row.txid = txid
                btc_row.address = notary_address
                btc_row.fees = tx_info['fees']

                btc_row.num_inputs = tx_info['vin_sz']
                btc_row.num_outputs = tx_info['vout_sz']

                btc_row.block_hash = tx_info['block_hash']
                btc_row.block_height = tx_info['block_height']

                block_time_iso8601 = tx_info['confirmed']
                parsed_time = dp.parse(block_time_iso8601)
                btc_row.block_time = parsed_time.strftime('%s')
                btc_row.block_datetime = dt.utcfromtimestamp(int(btc_row.block_time))

                addresses = tx_info['addresses']
                btc_row.season, btc_row.server = get_season_from_addresses(addresses[:], btc_row.block_time, "BTC", "BTC")

                vouts = tx_info["outputs"]
                vins = tx_info["inputs"]
                # update_notary_linked_vins(vins)

                # single row for memo.sv spam
                if detect_spam(btc_row, addresses, vouts):
                    logger.info("[scan_btc_transactions] SPAM detected")

                elif detect_cipi_faucet(btc_row, addresses, vins):
                    logger.info("[scan_btc_transactions] CIPI_FAUCET detected")

                # Detect Split (single row only)
                elif detect_split(btc_row, addresses):
                    logger.info("[scan_btc_transactions] SPLIT detected")

                else:
                    if txid in MadMax_personal_top_up:
                        btc_row.category = "MadMax personal top up"
                    elif txid in BTC_NTX_ADDR_consolidate:
                        btc_row.category = "BTC_NTX_ADDR consolidate"
                    elif txid in previous_season_funds_transfer:
                        btc_row.category = "previous season funds transfer"
                    elif txid in team_incoming:
                        btc_row.category = "team_incoming"
                    elif txid in REPORTED:
                        btc_row.category = "REPORTED"
                    #elif txid in pungo_other:
                    #    btc_row.category = "Other"
                        
                    elif detect_ntx(vins, vouts, addresses):
                        btc_row.category = "NTX"
                    elif detect_replenish(vins, vouts):
                        btc_row.category = "Replenish"
                    elif detect_consolidate(vins, vouts) or txid in dragonhound_consolidate or txid in strob_consolidate or txid in webworker_2step_consolidate:
                        btc_row.category = "Consolidate"
                    elif detect_intra_notary(vins, vouts):
                        btc_row.category = "Intra-Notary"
                    else:
                        btc_row.category = "Other"

                    notary_list = []
                    notary_addresses = []
                    input_index = 0
                    for vin in vins:
                        btc_row.output_sats = -1
                        btc_row.output_index = -1
                        btc_row.input_sats = vin['output_value']
                        btc_row.input_index = input_index
                        btc_row.address = vin["addresses"][0]
                        btc_row.notary = get_notary_from_btc_address(btc_row.address, btc_row.season)
                        btc_row.update()
                        input_index += 1
                        notary_list.append(btc_row.notary)
                        notary_addresses.append(btc_row.address)

                    output_index = 0
                    for vout in vouts:
                        if vout["addresses"] is not None:
                            btc_row.input_index = -1
                            btc_row.input_sats = -1
                            btc_row.address = vout["addresses"][0]
                            btc_row.notary = get_notary_from_btc_address(btc_row.address, btc_row.season)
                            btc_row.output_sats = vout['value']
                            btc_row.output_index = output_index
                            btc_row.update()
                            output_index += 1

                    if btc_row.category == "NTX":

                        for vout in vouts:
                            if 'data_hex' in vout:
                                opret = vout['data_hex']

                                opret_url = f'{THIS_SERVER}/api/tools/decode_opreturn/?OP_RETURN={opret}'
                                r = requests.get(opret_url)
                                kmd_ntx_info = r.json()

                                ac_ntx_height = kmd_ntx_info['notarised_block']
                                ac_ntx_blockhash = kmd_ntx_info['notarised_blockhash']

                                # Update "notarised" table
                                ntx_row = notarised_row()
                                ntx_row.chain = 'BTC'
                                ntx_row.block_height = btc_row.block_height
                                ntx_row.block_time = int(btc_row.block_time)
                                ntx_row.block_datetime = btc_row.block_datetime
                                ntx_row.block_hash = btc_row.block_hash
                                ntx_row.notaries = notary_list
                                ntx_row.notary_addresses = notary_addresses
                                ntx_row.ac_ntx_blockhash = ac_ntx_blockhash
                                ntx_row.ac_ntx_height = ac_ntx_height
                                ntx_row.txid = btc_row.txid
                                ntx_row.opret = opret
                                ntx_row.season = btc_row.season
                                ntx_row.server = btc_row.server
                                ntx_row.score_value = get_chain_epoch_score_at(ntx_row.season, ntx_row.server, ntx_row.chain, int(ntx_row.block_time))
                                ntx_row.epoch = get_chain_epoch_at(ntx_row.season, ntx_row.server, ntx_row.chain, int(ntx_row.block_time))
                                if ntx_row.score_value > 0:
                                    ntx_row.scored = True
                                else:
                                    ntx_row.scored = False
                                ntx_row.btc_validated = "true"
                                ntx_row.update()

                logger.info(f"[scan_btc_transactions] TXID: {txid} ({btc_row.category})")
            else:
                logger.warning(f"[scan_btc_transactions] Fees not in txinfo for {txid}! Likely unconfirmed...")
        season_btc_addresses.remove(notary_address)

if __name__ == "__main__":
    
    seasons = get_notarised_seasons()

    for season in seasons:
        if season not in ["Season_1", "Season_2", "Season_3", "Unofficial", "Season_5_Testnet"]: 
            scan_btc_transactions(season)


