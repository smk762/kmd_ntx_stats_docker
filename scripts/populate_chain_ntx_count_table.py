#!/usr/bin/env python3
from address_lib import seasons_info
from coins_lib import third_party_coins, antara_coins, ex_antara_coins, all_antara_coins, all_coins
import table_lib
from electrum_lib import get_ac_block_heights
import logging
import logging.handlers

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def calc_chain_notarised_counts():
    conn = table_lib.connect_db()
    cursor = conn.cursor()
    chains_aggr_resp = table_lib.get_latest_chain_ntx_aggregates(cursor)

    ac_block_heights = get_ac_block_heights()

    chain_json = {}
    for item in chains_aggr_resp:
        chain = item[0]
        kmd_ntx_height = item[1]
        kmd_ntx_time = item[2]
        ntx_count = item[3]

        chains_resp = table_lib.get_latest_chain_ntx_info(cursor, chain, kmd_ntx_height)
        chain_json.update({
            chain:{
                "ntx_count": ntx_count,
                "kmd_ntx_height": kmd_ntx_height,
                "lastnotarization": kmd_ntx_time,
                "kmd_ntx_blockhash": chains_resp[3],
                "kmd_ntx_txid": chains_resp[4],
                "opret": chains_resp[2],
                "ac_ntx_block_hash": chains_resp[0],
                "ac_ntx_height": chains_resp[1]
            }
        })
        if chain in ac_block_heights:
            chain_json[chain].update({
                "ac_block_height": ac_block_heights[chain],
                "ntx_lag": ac_block_heights[chain] - chains_resp[1]
            })
        else:
            chain_json[chain].update({
                "ac_block_height": "no data",
                "ntx_lag": "no data"
            })
        row_data = ( chain, ntx_count, kmd_ntx_height, chain_json[chain]['kmd_ntx_blockhash'], chain_json[chain]['kmd_ntx_txid'],
                     chain_json[chain]['lastnotarization'], chain_json[chain]['opret'], chain_json[chain]['ac_ntx_block_hash'],
                     chain_json[chain]['ac_ntx_height'], chain_json[chain]['ac_block_height'],
                     chain_json[chain]['ntx_lag'])
        logger.info("Adding counts for "+chain+" to notarised_chain table")
        table_lib.add_row_to_notarised_chain_tbl(conn, cursor, row_data)
    cursor.close()
    conn.close()

calc_chain_notarised_counts()
