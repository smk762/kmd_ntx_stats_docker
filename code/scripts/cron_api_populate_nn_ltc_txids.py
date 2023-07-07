#!/usr/bin/env python3
import json
import time
import random
import requests
import calendar
from decimal import *
from datetime import datetime as dt
import datetime
import dateutil.parser as dp

import lib_urls as urls
from lib_helper import *
from lib_ntx import *
from lib_update import update_nn_ltc_tx_notary_from_addr
from lib_query import get_existing_nn_ltc_txids, get_existing_notarised_txids
from lib_api import get_ltc_tx_info
from models import ltc_tx_row, notarised_row

from lib_validate import *
from lib_const import *
from known_txids import *



def get_linked_addresses(addr=None, notary=None):
    linked_addresses = {}
    sql = f"SELECT DISTINCT address, notary from nn_ltc_tx"
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

            if notary in KNOWN_NOTARIES:

                if notary not in linked_addresses:
                    if addr not in ALL_SEASON_NOTARY_LTC_ADDRESSES:
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


def detect_ntx(vins, vouts, addresses):
    if LTC_NTX_ADDR in addresses and len(vouts) == 2:
        for vin in vins:
            if vin["output_value"] != 10000:
                return False
            if vin["addresses"][0] not in ALL_SEASON_NOTARY_LTC_ADDRESSES:
                return False

        for vout in vouts:
            if vout["addresses"] is not None:
                if vout["addresses"][0] != LTC_NTX_ADDR:
                    return False
        return True
    else:
        return False

def detect_replenish(vins, vouts):

    vin_notaries = []
    vin_non_notary_addresses = []
    for vin in vins:
        address = vin["addresses"][0]
        if is_notary_ltc_address(address):
            notary = ALL_SEASON_NOTARY_LTC_ADDRESSES[address]
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
            if is_notary_ltc_address(address):
                if sats >= 1000000:
                    notary = ALL_SEASON_NOTARY_LTC_ADDRESSES[address]
                    if notary != "dragonhound_NA":
                        vout_notaries.append(notary)
            elif not is_linked_address(address):
                vout_non_notary_addresses.append(address)

    replenish_vout = False
    if len(vout_notaries) > 0:
        replenish_vout = True

    if replenish_vin and replenish_vout:
        for addr in vin_non_notary_addresses:
            if addr not in ALL_SEASON_NOTARY_LTC_ADDRESSES:
                pass
                #update_nn_ltc_tx_notary_from_addr("dragonhound_NA (linked)", addr)
        for addr in vout_non_notary_addresses:

            if addr not in ALL_SEASON_NOTARY_LTC_ADDRESSES:
                pass
                #update_nn_ltc_tx_notary_from_addr("dragonhound_NA (linked)", addr)
        return True
    return False

def detect_consolidate(vins, vouts):
    vin_notaries = []
    vin_non_notary_addresses = []
    for vin in vins:
        address = vin["addresses"][0]
        if is_notary_ltc_address(address):
            notary = ALL_SEASON_NOTARY_LTC_ADDRESSES[address]
            vin_notaries.append(notary)
        else:
            vin_non_notary_addresses.append(address)

    if len(list(set(vin_notaries))) == 1:
        notary = vin_notaries[0]

        vout_notaries = []
        vout_non_notary_addresses = []
        for vout in vouts:
            address = vout["addresses"][0]
            if is_notary_ltc_address(address):
                notary = ALL_SEASON_NOTARY_LTC_ADDRESSES[address]
                vout_notaries.append(notary)
            else:
                vout_non_notary_addresses.append(address)

        if len(list(set(vout_notaries))) == 1 and is_notary_ltc_address(vouts[0]["addresses"][0]):
            if notary == vout_notaries[0]:
                for addr in vin_non_notary_addresses:
                    if addr not in ALL_SEASON_NOTARY_LTC_ADDRESSES:
                        update_nn_ltc_tx_notary_from_addr(f"{notary} (linked)", addr)
                for addr in vout_non_notary_addresses:
                    if addr not in ALL_SEASON_NOTARY_LTC_ADDRESSES:
                        update_nn_ltc_tx_notary_from_addr(f"{notary} (linked)", addr)
                return True

    return False

def update_notary_linked_vins(vins):
    vin_notaries = []
    vin_non_notary_addresses = []
    for vin in vins:
        address = vin["addresses"][0]
        if is_notary_ltc_address(address):
            notary = ALL_SEASON_NOTARY_LTC_ADDRESSES[address]
            vin_notaries.append(notary)
        else:
            vin_non_notary_addresses.append(address)

    if len(list(set(vin_notaries))) == 1 and len(vin_non_notary_addresses) > 0:
        for addr in vin_non_notary_addresses:
            if addr not in ALL_SEASON_NOTARY_LTC_ADDRESSES:
                update_nn_ltc_tx_notary_from_addr(f"{notary} (linked)", address)


def detect_intra_notary(vins, vouts):
    for vin in vins:
        address = vin["addresses"][0]
        if is_notary_ltc_address(address):
            notary = ALL_SEASON_NOTARY_LTC_ADDRESSES[address]
        else:
            return False

    for vout in vouts:
        address = vout["addresses"][0]
        if is_notary_ltc_address(address):
            notary = ALL_SEASON_NOTARY_LTC_ADDRESSES[address]
        else:
            return False

    return True

# Filters spam message.sv transactions
def detect_spam(txid_data, addresses, vouts):
    if '1See1xxxx1memo1xxxxxxxxxxxxxBuhPF' in addresses:        
        txid_data.input_sats = 0
        txid_data.output_sats = 0
        txid_data.input_index = 0
        txid_data.output_index = 0
        txid_data.category = "SPAM"
        for vout in vouts:
            txid_data.address = addresses[0]
            txid_data.notary = get_name_from_address(txid_data.address)
            if txid_data.notary in KNOWN_NOTARIES:
                txid_data.update()
        return True
    return False

def detect_cipi_faucet(txid_data, addresses, vins):
    if vins[0]["addresses"][0] == CIPI_FAUCET_ADDR and len(addresses) == 2:
        addresses.remove(CIPI_FAUCET_ADDR)
        txid_data.category = "cipi_faucet"
        txid_data.input_sats = -99
        txid_data.output_sats = -99
        txid_data.input_index = -99
        txid_data.output_index = -99
        txid_data.address = addresses[0]
        txid_data.notary = get_name_from_address(txid_data.address)
        txid_data.update()
        return True
    return False

def detect_split(txid_data, addresses):
    if len(addresses) == 1:
        txid_data.category = "Split"
        txid_data.input_sats = -99
        txid_data.output_sats = -99
        txid_data.input_index = -99
        txid_data.output_index = -99
        txid_data.address = addresses[0]
        txid_data.notary = get_name_from_address(txid_data.address)
        txid_data.update()
        return True
    return False

def scan_ltc_transactions(season):
    season_ltc_addresses_resp = requests.get(urls.get_addresses_url(season, server="Main", coin="LTC")).json()["results"]
    season_ltc_addresses = []
    for item in season_ltc_addresses_resp:
        season_ltc_addresses.append(item["address"])
    season_ltc_addresses += [LTC_NTX_ADDR]
    num_addr = len(season_ltc_addresses)

    i = 0
    while len(season_ltc_addresses) > 0:
        if LTC_NTX_ADDR in season_ltc_addresses:
            notary_address = LTC_NTX_ADDR
        elif "LcnrQXJs8kH55iCoqSZ3M3MA5QT4kPu117" in season_ltc_addresses:
            notary_address = "LcnrQXJs8kH55iCoqSZ3M3MA5QT4kPu117"
        else:
            notary_address = random.choice(season_ltc_addresses)
        i += 1

        existing_nn_ltc_txids = get_existing_nn_ltc_txids(notary_address)
        existing_notarised_txids = get_existing_notarised_txids(None, None, "LTC")
        existing_txids = list(set(existing_nn_ltc_txids)&set(existing_notarised_txids))
        txids = get_new_nn_ltc_txids(existing_txids, notary_address)

        num_txids = len(txids)

        j = 0
        for txid in txids:
            j += 1
            # Get tx data from Blockcypher API
            logger.info(f"[scan_ltc_transactions] >>> Processing txid {j}/{num_txids}")
            tx_info = get_ltc_tx_info(txid, True, True)
            if 'error' in tx_info:
                pass
            elif 'fees' in tx_info:
                ltc_row = ltc_tx_row()
                ltc_row.txid = txid
                ltc_row.address = notary_address
                ltc_row.fees = tx_info['fees']

                ltc_row.num_inputs = tx_info['vin_sz']
                ltc_row.num_outputs = tx_info['vout_sz']

                ltc_row.block_hash = tx_info['block_hash']
                ltc_row.block_height = tx_info['block_height']

                block_time_iso8601 = tx_info['confirmed']
                logger.info(block_time_iso8601)
                ltc_row.block_time = calendar.timegm(dt.strptime(block_time_iso8601, "%Y-%m-%dT%H:%M:%SZ").timetuple())
                logger.info(ltc_row.block_time)
                ltc_row.block_datetime = dt.utcfromtimestamp(int(ltc_row.block_time))
                logger.info(ltc_row.block_datetime)

                addresses = tx_info['addresses']


                vouts = tx_info["outputs"]
                vins = tx_info["inputs"]
                # update_notary_linked_vins(vins)

                # Detect Split (single row only)
                if detect_split(ltc_row, addresses):
                    logger.info("[scan_ltc_transactions] SPLIT detected")

                else:                    
                    if detect_ntx(vins, vouts, addresses):
                        ltc_row.category = "NTX"
                    elif detect_replenish(vins, vouts):
                        ltc_row.category = "Replenish"
                    elif detect_consolidate(vins, vouts) or txid in dragonhound_consolidate or txid in strob_consolidate or txid in webworker_2step_consolidate:
                        ltc_row.category = "Consolidate"
                    elif detect_intra_notary(vins, vouts):
                        ltc_row.category = "Intra-Notary"
                    else:
                        ltc_row.category = "Other"

                    notary_list = []
                    notary_addresses = []
                    input_index = 0
                    for vin in vins:
                        ltc_row.output_sats = -1
                        ltc_row.output_index = -1
                        ltc_row.input_sats = vin['output_value']
                        ltc_row.input_index = input_index
                        ltc_row.address = vin["addresses"][0]
                        ltc_row.notary = get_name_from_address(ltc_row.address)
                        ltc_row.update()
                        input_index += 1
                        notary_list.append(ltc_row.notary)
                        notary_addresses.append(ltc_row.address)

                    output_index = 0
                    for vout in vouts:
                        if vout["addresses"] is not None:
                            ltc_row.input_index = -1
                            ltc_row.input_sats = -1
                            ltc_row.address = vout["addresses"][0]
                            ltc_row.notary = get_name_from_address(ltc_row.address)
                            ltc_row.output_sats = vout['value']
                            ltc_row.output_index = output_index
                            ltc_row.update()
                            output_index += 1

                    if ltc_row.category == "NTX":

                        for vout in vouts:
                            if 'data_hex' in vout:
                                opret = vout['data_hex']

                                r = requests.get(get_decode_opret_url(opret))
                                kmd_ntx_info = r.json()['results']
                                ac_ntx_height = kmd_ntx_info['notarised_block']
                                ac_ntx_blockhash = kmd_ntx_info['notarised_blockhash']

                                # Update "notarised" table
                                ntx_row = notarised_row()
                                ntx_row.coin = "LTC"
                                ntx_row.block_height = ltc_row.block_height
                                ntx_row.block_time = int(ltc_row.block_time)
                                ntx_row.block_datetime = ltc_row.block_datetime
                                ntx_row.block_hash = ltc_row.block_hash
                                ntx_row.notaries = notary_list
                                ntx_row.notary_addresses = notary_addresses
                                ntx_row.ac_ntx_blockhash = ac_ntx_blockhash
                                ntx_row.ac_ntx_height = ac_ntx_height
                                ntx_row.txid = ltc_row.txid
                                ntx_row.opret = opret
                                ntx_row.season = ltc_row.season
                                ntx_row.server = "LTC"
                                ntx_row.score_value = 0
                                ntx_row.epoch = "LTC"
                                ntx_row.scored = False
                                ntx_row.update()

                logger.info(f"[scan_ltc_transactions] TXID: {txid} ({ltc_row.category})")
            else:
                logger.warning(f"Fees not in txinfo for {txid}! Likely unconfirmed...")
                logger.warning(tx_info)
        season_ltc_addresses.remove(notary_address)

if __name__ == "__main__":
    
    for season in ["Season_7"]:
            scan_ltc_transactions(season)

    CURSOR.close()
    CONN.close()

