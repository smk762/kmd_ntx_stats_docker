#!/usr/bin/env python3.12

import json
import time
import random
import requests
import calendar
from decimal import Decimal
import datetime
from datetime import datetime as dt
import dateutil.parser as dp

import lib_urls as urls
from lib_helper import *
from lib_ntx import *
from lib_update import update_nn_ltc_tx_notary_from_addr
from lib_query import get_existing_nn_txids, get_existing_notarised_txids
from lib_api import get_ltc_tx_info
from models import ltc_tx_row, NotarisedRow

from lib_validate import *
from lib_const import *
from known_txids import *

def get_linked_addresses(addr=None, notary=None):
    conditions = [f"address='{addr}'"] if addr else []
    if notary:
        conditions.append(f"notary = '{notary}' OR notary = '{notary} (linked)'")

    sql = f"SELECT DISTINCT address, notary FROM nn_ltc_tx"
    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    CURSOR.execute(sql)
    address_rows = CURSOR.fetchall()

    linked_addresses = {}
    for address, notary in address_rows:
        notary = notary.replace(" (linked)", "")
        if notary in KNOWN_NOTARIES:
            linked_addresses.setdefault(notary, []).append(address)

    return linked_addresses

def is_linked_address(addr, notary=None):
    return bool(get_linked_addresses(addr, notary))

def detect_ntx(vins, vouts, addresses):
    if LTC_NTX_ADDR in addresses and len(vouts) == 2:
        return all(
            vin["output_value"] == 10000 and vin["addresses"][0] in ALL_SEASON_NOTARY_LTC_ADDRESSES
            for vin in vins
        ) and all(vout["addresses"] and vout["addresses"][0] == LTC_NTX_ADDR for vout in vouts)
    return False

def detect_replenish(vins, vouts):
    vin_notaries = []
    vin_non_notary_addresses = []
    
    for vin in vins:
        address = vin["addresses"][0]
        if is_notary_ltc_address(address):
            vin_notaries.append(ALL_SEASON_NOTARY_LTC_ADDRESSES[address])
        elif is_linked_address(address, "dragonhound_NA"):
            vin_notaries.append("dragonhound_NA")
        else:
            vin_non_notary_addresses.append(address)

    replenish_vin = len(set(vin_notaries)) == 1 and vin_notaries[0] == "dragonhound_NA"

    vout_notaries = []
    vout_non_notary_addresses = []
    
    for vout in vouts:
        if vout["addresses"]:
            address = vout["addresses"][0]
            if is_notary_ltc_address(address) and vout["value"] >= 1000000:
                vout_notaries.append(ALL_SEASON_NOTARY_LTC_ADDRESSES[address])
            elif not is_linked_address(address):
                vout_non_notary_addresses.append(address)

    replenish_vout = bool(vout_notaries)

    if replenish_vin and replenish_vout:
        for addr in vin_non_notary_addresses + vout_non_notary_addresses:
            if addr not in ALL_SEASON_NOTARY_LTC_ADDRESSES:
                update_nn_ltc_tx_notary_from_addr("dragonhound_NA (linked)", addr)
        return True
    return False

def detect_consolidate(vins, vouts):
    vin_notaries = []
    vin_non_notary_addresses = []

    for vin in vins:
        address = vin["addresses"][0]
        if is_notary_ltc_address(address):
            vin_notaries.append(ALL_SEASON_NOTARY_LTC_ADDRESSES[address])
        else:
            vin_non_notary_addresses.append(address)

    if len(set(vin_notaries)) == 1:
        notary = vin_notaries[0]
        vout_notaries = []
        vout_non_notary_addresses = []

        for vout in vouts:
            address = vout["addresses"][0]
            if is_notary_ltc_address(address):
                vout_notaries.append(ALL_SEASON_NOTARY_LTC_ADDRESSES[address])
            else:
                vout_non_notary_addresses.append(address)

        if len(set(vout_notaries)) == 1 and is_notary_ltc_address(vouts[0]["addresses"][0]) and notary == vout_notaries[0]:
            for addr in vin_non_notary_addresses + vout_non_notary_addresses:
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
            vin_notaries.append(ALL_SEASON_NOTARY_LTC_ADDRESSES[address])
        else:
            vin_non_notary_addresses.append(address)

    if len(set(vin_notaries)) == 1 and vin_non_notary_addresses:
        notary = vin_notaries[0]
        for addr in vin_non_notary_addresses:
            if addr not in ALL_SEASON_NOTARY_LTC_ADDRESSES:
                update_nn_ltc_tx_notary_from_addr(f"{notary} (linked)", addr)

def detect_intra_notary(vins, vouts):
    return all(
        is_notary_ltc_address(vin["addresses"][0]) for vin in vins
    ) and all(
        is_notary_ltc_address(vout["addresses"][0]) for vout in vouts
    )

# Filters spam messages
def detect_spam(txid_data, addresses, vouts):
    if '1See1xxxx1memo1xxxxxxxxxxxxxBuhPF' in addresses:
        txid_data.update(
            input_sats=0,
            output_sats=0,
            input_index=0,
            output_index=0,
            category="SPAM",
            address=addresses[0],
            notary=get_name_from_address(addresses[0])
        )
        return True
    return False

def detect_cipi_faucet(txid_data, addresses, vins):
    if vins[0]["addresses"][0] == CIPI_FAUCET_ADDR and len(addresses) == 2:
        addresses.remove(CIPI_FAUCET_ADDR)
        txid_data.update(
            category="cipi_faucet",
            input_sats=-99,
            output_sats=-99,
            input_index=-99,
            output_index=-99,
            address=addresses[0],
            notary=get_name_from_address(addresses[0])
        )
        return True
    return False

def detect_split(txid_data, addresses):
    if len(addresses) == 1:
        txid_data.update(
            category="Split",
            input_sats=-99,
            output_sats=-99,
            input_index=-99,
            output_index=-99,
            address=addresses[0],
            notary=get_name_from_address(addresses[0])
        )
        return True
    return False

def scan_ltc_transactions(season):
    url = urls.get_addresses_url(season, server="Main", coin="LTC")
    season_ltc_addresses_resp = requests.get(url).json()["results"]
    season_ltc_addresses = [item["address"] for item in season_ltc_addresses_resp] + [LTC_NTX_ADDR]

    while season_ltc_addresses:
        notary_address = LTC_NTX_ADDR if LTC_NTX_ADDR in season_ltc_addresses else random.choice(season_ltc_addresses)

        existing_nn_ltc_txids = get_existing_nn_txids(coin="LTC", address=notary_address, season=season)
        existing_notarised_txids = get_existing_notarised_txids(None, None, "LTC")
        existing_txids = set(existing_nn_ltc_txids) & set(existing_notarised_txids)
        txids = get_new_nn_ltc_txids(existing_txids, notary_address)

        for j, txid in enumerate(txids, start=1):
            logger.info(f"[scan_ltc_transactions] >>> Processing txid {j}/{len(txids)}")
            tx_info = get_ltc_tx_info(txid, True, True)

            if 'error' in tx_info:
                continue

            if 'fees' in tx_info:
                ltc_row = ltc_tx_row(
                    txid=txid,
                    address=notary_address,
                    fees=tx_info['fees'],
                    num_inputs=tx_info['vin_sz'],
                    num_outputs=tx_info['vout_sz'],
                    block_hash=tx_info['block_hash'],
                    block_height=tx_info['block_height']
                )

                block_time_iso8601 = tx_info['confirmed']
                ltc_row.block_time = calendar.timegm(dt.strptime(block_time_iso8601, "%Y-%m-%dT%H:%M:%SZ").timetuple())
                ltc_row.block_datetime = dt.fromtimestamp(ltc_row.block_time, datetime.UTC)

                addresses = tx_info['addresses']
                vouts = tx_info["outputs"]
                vins = tx_info["inputs"]

                # Detect categories
                if detect_split(ltc_row, addresses):
                    logger.info("[scan_ltc_transactions] SPLIT detected")
                else:
                    if detect_spam(ltc_row, addresses, vouts):
                        logger.info("[scan_ltc_transactions] SPAM detected")
                        continue
                    if detect_cipi_faucet(ltc_row, addresses, vins):
                        logger.info("[scan_ltc_transactions] CIPI FAUCET detected")
                        continue

                    if detect_ntx(vins, vouts, addresses):
                        logger.info("[scan_ltc_transactions] NTX detected")
                    elif detect_replenish(vins, vouts):
                        logger.info("[scan_ltc_transactions] REPLENISH detected")
                    elif detect_consolidate(vins, vouts):
                        logger.info("[scan_ltc_transactions] CONSOLIDATE detected")
                    elif detect_intra_notary(vins, vouts):
                        logger.info("[scan_ltc_transactions] INTRA-NOTARY detected")

                # Handle linked addresses
                update_notary_linked_vins(vins)

        season_ltc_addresses.remove(notary_address)


if __name__ == "__main__":
    seasons = helper.get_active_seasons()
    for season in seasons:
        scan_ltc_transactions(season)
    CURSOR.close()
    CONN.close()

