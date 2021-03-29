#!/usr/bin/env python3
import logging
import json
import logging.handlers
import os
from psycopg2.extras import execute_values
from lib_const import *

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def update_addresses_tbl(row_data):
    try:
        sql = "INSERT INTO addresses \
              (season, node, notary, notary_id, chain, pubkey, address) \
               VALUES (%s, %s, %s, %s, %s, %s, %s) \
               ON CONFLICT ON CONSTRAINT unique_season_chain_address DO UPDATE SET \
               node='"+str(row_data[1])+"', notary='"+str(row_data[2])+"', \
               pubkey='"+str(row_data[5])+"', address='"+str(row_data[6])+"';"
        CURSOR.execute(sql, row_data)
        CONN.commit()
        return 1
    except Exception as e:
        logger.debug(e)
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        CONN.rollback()
        return 0


def update_rewards_row(row_data):
    try:
        sql = "INSERT INTO rewards \
            (address, notary, utxo_count, eligible_utxo_count, \
            oldest_utxo_block, balance, rewards, update_time) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_reward_address DO UPDATE SET \
            notary='"+str(row_data[1])+"', utxo_count="+str(row_data[2])+", \
            eligible_utxo_count="+str(row_data[3])+", oldest_utxo_block="+str(row_data[4])+", \
            balance="+str(row_data[5])+", rewards="+str(row_data[6])+", \
            update_time="+str(row_data[7])+";"
        CURSOR.execute(sql, row_data)
        CONN.commit()
        return 1
    except Exception as e:
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        CONN.rollback()
        return 0

def update_notarised_btc_tbl(row_data):
    sql = "INSERT INTO notarised_btc (btc_txid, btc_block_hash, btc_block_ht, \
                                      btc_block_time, \
                                      addresses, notaries, kmd_txid, \
                                      kmd_block_hash, kmd_block_ht, \
                                      kmd_block_time, \
                                      opret, season) \
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
    try:
        CURSOR.execute(sql, row_data)
        CONN.commit()
        logger.debug(row_data)
    except Exception as e:
        if str(e).find('duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        CONN.rollback()

def update_ntx_row(row_data):
    sql = f"INSERT INTO notarised (chain, block_height, \
                                block_time, block_datetime, block_hash, \
                                notaries, notary_addresses, ac_ntx_blockhash, ac_ntx_height, \
                                txid, opret, season, server, scored, score_value, btc_validated) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
                ON CONFLICT ON CONSTRAINT unique_txid DO UPDATE SET \
                season='{row_data[11]}', server='{row_data[12]}', scored='{row_data[13]}', \
                notaries=ARRAY{row_data[5]}, notary_addresses=ARRAY{row_data[6]}, score_value={row_data[14]};"
    try:
        CURSOR.execute(sql, row_data)
        logger.info("update_ntx_row executed")
        CONN.commit()
        logger.info("update_ntx_row commited")
    except Exception as e:
        if str(e).find('duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        CONN.rollback()

def update_ntx_records(records):
    try:
        execute_values(CURSOR, "INSERT INTO notarised (chain, block_height, \
                                block_time, block_datetime, block_hash, \
                                notaries, notary_addresses, ac_ntx_blockhash, ac_ntx_height, \
                                txid, opret, season, server, scored, btc_validated) \
                                VALUES %s", records)

        CONN.commit()
    except Exception as e:
        if str(e).find('duplicate') == -1:
            logger.debug(e)
        CONN.rollback()

def update_validation_notarised_tbl(btc_txid, btc_block_hash, btc_block_ht, opret):
    sql = "UPDATE notarised SET \
          chain='BTC', btc_validated='true', \
          txid='"+btc_txid+"', \
          block_hash='"+btc_block_hash+"', \
          block_height="+str(btc_block_ht)+", \
          opret='"+opret+"' \
          WHERE opret LIKE '%' || '"+opret[11:33]+"' || '%';"
    try:
        CURSOR.execute(sql)
        CONN.commit()
        logger.info("btc ntx validated in ntx table")
    except Exception as e:
        if str(e).find('duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        CONN.rollback()


def update_score_notarised_tbl(txid, scored, score_value):
    sql = f"UPDATE notarised SET \
          scored={scored}, score_value={score_value} \
          WHERE txid='{txid}';"
    try:
        CURSOR.execute(sql)
        CONN.commit()
        print(f"{txid} tagged as {scored} ({score_value})")
    except Exception as e:
        logger.debug(e)
        CONN.rollback()

def update_season_notarised_tbl(txid, season, server):
    sql = f"UPDATE notarised SET \
          season='{season}', server='{server}' \
          WHERE txid='{txid}';"
    try:
        CURSOR.execute(sql)
        CONN.commit()
        print(f"{txid} tagged as {season}")
    except Exception as e:
        logger.debug(e)
        CONN.rollback()

def delete_txid_from_notarised_tbl(txid):
    CURSOR.execute(f"DELETE FROM notarised WHERE txid = '{txid}';")
    CONN.commit()

def update_coins_row(row_data):
    try:
        sql = "INSERT INTO coins \
            (chain, coins_info, electrums, electrums_ssl, explorers, dpow, dpow_tenure, dpow_active, mm2_compatible) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_chain_coin DO UPDATE SET \
            coins_info='"+str(row_data[1])+"', \
            electrums='"+str(row_data[2])+"', \
            electrums_ssl='"+str(row_data[3])+"', \
            explorers='"+str(row_data[4])+"', \
            dpow='"+str(row_data[5])+"', \
            dpow_tenure='"+str(row_data[6])+"', \
            dpow_active='"+str(row_data[7])+"', \
            mm2_compatible='"+str(row_data[8])+"';"
        CURSOR.execute(sql, row_data)
        CONN.commit()
        return 1
    except Exception as e:
        logger.debug(e)
        if str(e).find('Duplicate') == -1:
            logger.debug(row_data)
        CONN.rollback()
        return 0
        
def update_mined_row(row_data):
    try:
        sql = "INSERT INTO mined \
            (block_height, block_time, block_datetime, \
             value, address, name, txid, season) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_block DO UPDATE SET \
            block_time='"+str(row_data[1])+"', \
            block_datetime='"+str(row_data[2])+"', \
            value="+str(row_data[3])+", \
            address='"+str(row_data[4])+"', \
            name='"+str(row_data[5])+"', \
            txid='"+str(row_data[6])+"', \
            season='"+str(row_data[7])+"';"
        CURSOR.execute(sql, row_data)
        CONN.commit()
    except Exception as e:
        logger.debug(e)
        if str(e).find('Duplicate') == -1:
            logger.debug(row_data)
        CONN.rollback()

def update_season_mined_count_row(row_data):
    try:
        sql = "INSERT INTO  mined_count_season \
            (notary, season, blocks_mined, sum_value_mined, \
            max_value_mined, last_mined_blocktime, last_mined_block, \
            time_stamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_notary_season_mined DO UPDATE SET \
            blocks_mined="+str(row_data[2])+", sum_value_mined="+str(row_data[3])+", \
            max_value_mined="+str(row_data[4])+", last_mined_blocktime="+str(row_data[5])+", \
            last_mined_block="+str(row_data[6])+", time_stamp='"+str(row_data[7])+"';"
        CURSOR.execute(sql, row_data)
        CONN.commit()
        return 1
    except Exception as e:
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        CONN.rollback()
        return 0

def update_season_notarised_chain_row(row_data):
    sql = "INSERT INTO notarised_chain_season \
         (chain, ntx_count, block_height, kmd_ntx_blockhash,\
          kmd_ntx_txid, kmd_ntx_blocktime, opret, ac_ntx_blockhash, \
          ac_ntx_height, ac_block_height, ntx_lag, season) \
          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
          ON CONFLICT ON CONSTRAINT unique_notarised_chain_season DO UPDATE \
          SET ntx_count="+str(row_data[1])+", block_height="+str(row_data[2])+", \
          kmd_ntx_blockhash='"+str(row_data[3])+"', kmd_ntx_txid='"+str(row_data[4])+"', \
          kmd_ntx_blocktime="+str(row_data[5])+", opret='"+str(row_data[6])+"', \
          ac_ntx_blockhash='"+str(row_data[7])+"', ac_ntx_height="+str(row_data[8])+", \
          ac_block_height='"+str(row_data[9])+"', ntx_lag='"+str(row_data[10])+"';"
         
    CURSOR.execute(sql, row_data)
    CONN.commit()

def update_season_notarised_count_row(row_data): 
    sql = "INSERT INTO notarised_count_season \
        (notary, btc_count, antara_count, \
        third_party_count, other_count, \
        total_ntx_count, chain_ntx_counts, \
        chain_ntx_pct, time_stamp, season) \
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
        ON CONFLICT ON CONSTRAINT unique_notary_season DO UPDATE SET \
        btc_count="+str(row_data[1])+", antara_count="+str(row_data[2])+", \
        third_party_count="+str(row_data[3])+", other_count="+str(row_data[4])+", \
        total_ntx_count="+str(row_data[5])+", chain_ntx_counts='"+str(row_data[6])+"', \
        chain_ntx_pct='"+str(row_data[7])+"', time_stamp="+str(row_data[8])+";"
    CURSOR.execute(sql, row_data)
    CONN.commit()

def update_daily_mined_count_row(row_data):
    try:
        sql = "INSERT INTO mined_count_daily \
            (notary, blocks_mined, sum_value_mined, \
            mined_date, time_stamp) VALUES (%s, %s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_notary_daily_mined \
            DO UPDATE SET \
            blocks_mined="+str(row_data[1])+", \
            sum_value_mined='"+str(row_data[2])+"';"
        CURSOR.execute(sql, row_data)
        CONN.commit()
        return 1
    except Exception as e:
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        CONN.rollback()
        return 0

def update_daily_notarised_chain_row(row_data):
    sql = "INSERT INTO notarised_chain_daily \
         (chain, ntx_count, notarised_date) \
          VALUES (%s, %s, %s) \
          ON CONFLICT ON CONSTRAINT unique_notarised_chain_date DO UPDATE \
          SET ntx_count="+str(row_data[1])+";"
    CURSOR.execute(sql, row_data)
    CONN.commit()

def update_daily_notarised_count_row(row_data): 
    sql = "INSERT INTO notarised_count_daily \
        (notary, btc_count, antara_count, \
        third_party_count, other_count, \
        total_ntx_count, chain_ntx_counts, \
        chain_ntx_pct, time_stamp, season, notarised_date) \
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
        ON CONFLICT ON CONSTRAINT unique_notary_date DO UPDATE SET \
        btc_count="+str(row_data[1])+", antara_count="+str(row_data[2])+", \
        third_party_count="+str(row_data[3])+", other_count="+str(row_data[4])+", \
        total_ntx_count="+str(row_data[5])+", chain_ntx_counts='"+str(row_data[6])+"', \
        chain_ntx_pct='"+str(row_data[7])+"', time_stamp="+str(row_data[8])+",  \
        season='"+str(row_data[9])+"', notarised_date='"+str(row_data[10])+"';"
    CURSOR.execute(sql, row_data)
    CONN.commit()

def update_table(table, update_str, condition):
    try:
        sql = "UPDATE "+table+" \
               SET "+update_str+" WHERE "+condition+";"
        logger.info(sql)
        CURSOR.execute(sql)
        CONN.commit()
        return 1
    except Exception as e:
        logger.debug(e)
        logger.debug(sql)
        CONN.rollback()
        return 0

def update_sync_tbl(row_data):
    try:
        sql = "INSERT INTO chain_sync \
            (chain, block_height, sync_hash, explorer_hash) \
            VALUES (%s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_chain_sync DO UPDATE SET \
            block_height='"+str(row_data[1])+"', \
            sync_hash='"+str(row_data[2])+"', \
            explorer_hash='"+str(row_data[3])+"';"
        CURSOR.execute(sql, row_data)
        CONN.commit()
        return 1
    except Exception as e:
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        CONN.rollback()
        return 0

def update_nn_social_row(row_data):
    try:
        sql = "INSERT INTO  nn_social \
            (notary, twitter, youtube, discord, \
            telegram, github, keybase, \
            website, icon, season) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_notary_season_social DO UPDATE SET \
            twitter='"+str(row_data[1])+"', \
            youtube='"+str(row_data[2])+"', discord='"+str(row_data[3])+"', \
            telegram='"+str(row_data[4])+"', github='"+str(row_data[5])+"', \
            keybase='"+str(row_data[6])+"', website='"+str(row_data[7])+"', \
            icon='"+str(row_data[8])+"', season='"+str(row_data[9])+"';"
        CURSOR.execute(sql, row_data)
        CONN.commit()
        return 1
    except Exception as e:
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        CONN.rollback()
        return 0

def update_coin_social_row(row_data):
    try:
        sql = "INSERT INTO  coin_social \
            (chain, twitter, youtube, discord, \
            telegram, github, explorer, \
            website, icon, season) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_chain_season_social DO UPDATE SET \
            twitter='"+str(row_data[1])+"', \
            youtube='"+str(row_data[2])+"', discord='"+str(row_data[3])+"', \
            telegram='"+str(row_data[4])+"', github='"+str(row_data[5])+"', \
            explorer='"+str(row_data[6])+"', website='"+str(row_data[7])+"', \
            icon='"+str(row_data[8])+"', season='"+str(row_data[9])+"';"
        CURSOR.execute(sql, row_data)
        CONN.commit()
        return 1
    except Exception as e:
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        CONN.rollback()
        return 0

def update_last_ntx_row(row_data):
    try:
        sql = "INSERT INTO  last_notarised \
            (notary, chain, txid, block_height, \
            block_time, season) VALUES (%s, %s, %s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_notary_chain DO UPDATE SET \
            txid='"+str(row_data[2])+"', \
            block_height='"+str(row_data[3])+"', \
            block_time='"+str(row_data[4])+"', \
            season='"+str(row_data[5])+"';"
        CURSOR.execute(sql, row_data)
        CONN.commit()
        logger.info("Added "+str(row_data))
        return 1
    except Exception as e:
        logger.debug(e)
        if str(e).find('Duplicate') == -1:
            logger.debug(row_data)
        CONN.rollback()
        return 0

def update_last_btc_ntx_tbl(row_data):
    try:
        sql = "INSERT INTO  last_btc_notarised \
            (notary, txid, block_height, \
            block_time, season) VALUES (%s, %s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_notary_btc_ntx DO UPDATE SET \
            txid='"+str(row_data[1])+"', \
            block_height='"+str(row_data[2])+"', \
            block_time='"+str(row_data[3])+"', \
            season='"+str(row_data[4])+"';"
        CURSOR.execute(sql, row_data)
        CONN.commit()
        return 1
    except Exception as e:
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        CONN.rollback()
        return 0

def update_btc_address_deltas_tbl(row_data):
    try:
        sql = "INSERT INTO  btc_address_deltas \
            (notary, address, category, txid, block_time, \
             total_in, total_out, fees, vin_addr, vout_addr, season) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        CURSOR.execute(sql, row_data)
        CONN.commit()
        return 1
    except Exception as e:
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        CONN.rollback()
        return 0

def update_funding_row(row_data):
    try:
        sql = "INSERT INTO  funding_transactions \
            (chain, txid, vout, amount, \
            block_hash, block_height, block_time, \
            category, fee, address, notary, season) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_category_vout_txid_funding DO UPDATE SET \
            chain='"+str(row_data[0])+"', \
            amount='"+str(row_data[3])+"', \
            block_hash='"+str(row_data[4])+"', \
            block_height='"+str(row_data[5])+"', \
            block_time='"+str(row_data[6])+"', \
            fee='"+str(row_data[8])+"', \
            address='"+str(row_data[9])+"', \
            notary='"+str(row_data[10])+"', \
            season='"+str(row_data[11])+"';"
        CURSOR.execute(sql, row_data)
        CONN.commit()
        return 1
    except Exception as e:
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        CONN.rollback()
        return 0

def ts_col_to_dt_col(ts_col, dt_col, table):
    sql = "UPDATE "+table+" SET "+dt_col+"=to_timestamp("+ts_col+");"
    CURSOR.execute(sql)
    CONN.commit()

def update_notarised_tenure_row(row_data):
    try:
        sql = "INSERT INTO notarised_tenure (chain, first_ntx_block, \
            last_ntx_block, first_ntx_block_time, last_ntx_block_time, \
            official_start_block_time, official_end_block_time, \
            unscored_ntx_count, scored_ntx_count, season, server) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_chain_season_server_tenure DO UPDATE SET \
            first_ntx_block='"+str(row_data[1])+"', last_ntx_block="+str(row_data[2])+", \
            first_ntx_block_time="+str(row_data[3])+", last_ntx_block_time="+str(row_data[4])+", \
            official_start_block_time="+str(row_data[5])+", official_end_block_time="+str(row_data[6])+", \
            unscored_ntx_count="+str(row_data[7])+", scored_ntx_count="+str(row_data[8])+", \
            server='"+str(row_data[10])+"';"
        CURSOR.execute(sql, row_data)
        CONN.commit()
        return 1
    except Exception as e:
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        CONN.rollback()
        return 0

def delete_nn_btc_tx_transaction(txid):
    CURSOR.execute(f"DELETE FROM nn_btc_tx WHERE txid='{txid}';")
    CONN.commit()

def update_nn_btc_tx_row(row_data):
    sql = "INSERT INTO nn_btc_tx (txid, block_hash, block_height, \
                                block_time, block_datetime, \
                                address, notary, season, category, \
                                input_index, input_sats, \
                                output_index, output_sats, fees, num_inputs, num_outputs) \
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
        ON CONFLICT ON CONSTRAINT unique_btc_nn_txid DO UPDATE SET \
        notary='"+str(row_data[6])+"', category='"+str(row_data[8])+"';"
    try:
        CURSOR.execute(sql, row_data)
        CONN.commit()
    except Exception as e:
        logger.debug(e)
        if str(e).find('duplicate') == -1:
            logger.debug(row_data)
        CONN.rollback()

def insert_nn_btc_tx_row(row_data):
    sql = "INSERT INTO nn_btc_tx (txid, block_hash, block_height, \
                                block_time, block_datetime, \
                                address, notary, season, category, \
                                input_index, input_sats, \
                                output_index, output_sats, fees, num_inputs, num_outputs) \
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
    try:
        CURSOR.execute(sql, row_data)
        CONN.commit()
    except Exception as e:
        logger.debug(e)
        if str(e).find('duplicate') == -1:
            logger.debug(row_data)
        CONN.rollback()

def update_nn_btc_tx_notary_from_addr(notary, addr):
    sql = f"UPDATE nn_btc_tx SET notary='{notary}' WHERE address='{addr}';"
    try:
        CURSOR.execute(sql)
        CONN.commit()
        logger.info(f"{addr} tagged as {notary} in DB")
    except Exception as e:
        logger.debug(e)
        CONN.rollback()

def update_nn_btc_tx_notary_category_from_addr(notary, category, addr):
    sql = f"UPDATE nn_btc_tx SET notary='{notary}', category='{category}' WHERE address='{addr}';"
    try:
        CURSOR.execute(sql)
        CONN.commit()
        logger.info(f"{addr} tagged as {notary} in DB")
    except Exception as e:
        logger.debug(e)
        CONN.rollback()

def update_nn_btc_tx_category_from_txid(category, txid):
    sql = f"UPDATE nn_btc_tx SET category='{category}' WHERE txid='{txid}';"
    try:
        CURSOR.execute(sql)
        CONN.commit()
        logger.info(f"{txid} tagged as {category} in DB")
    except Exception as e:
        logger.debug(e)
        CONN.rollback()

def update_nn_btc_tx_outindex_from_txid(outindex, txid):
    sql = f"UPDATE nn_btc_tx SET output_index='{outindex}' WHERE txid='{txid}';"
    try:
        CURSOR.execute(sql)
        CONN.commit()
        logger.info(f"{txid} tagged as {outindex} in DB")
    except Exception as e:
        logger.debug(e)
        CONN.rollback()

def delete_nn_btc_tx_row(txid, notary):
    sql = "DELETE FROM nn_btc_tx WHERE txid='"+str(txid)+"' and notary='"+str(notary)+"';"
    try:
        CURSOR.execute(sql)
        CONN.commit()
    except Exception as e:
        logger.debug(e)
        CONN.rollback()

#### BALANCES TABLE

def update_balances_row(row_data):
    try:
        sql = "INSERT INTO balances \
            (notary, chain, balance, address, season, node, update_time) \
            VALUES (%s, %s, %s, %s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_chain_address_season_balance DO UPDATE SET \
            balance="+str(row_data[2])+", \
            node='"+str(row_data[5])+"', \
            update_time="+str(row_data[6])+";"
        CURSOR.execute(sql, row_data)
        CONN.commit()
    except Exception as e:
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        CONN.rollback()

def delete_balances_row(chain, address, season):
    try:
        sql = f"DELETE FROM balances WHERE chain='{chain}' and address='{address}' and season={season};"
        CURSOR.execute(sql)
        CONN.commit()
    except Exception as e:
        logger.debug(e)
        CONN.rollback()

#### LTC

def update_nn_ltc_tx_notary_from_addr(notary, addr):
    sql = f"UPDATE nn_ltc_tx SET notary='{notary}' WHERE address='{addr}';"
    try:
        CURSOR.execute(sql)
        CONN.commit()
        logger.info(f"{addr} tagged as {notary} in DB")
    except Exception as e:
        logger.debug(e)
        CONN.rollback()

def update_nn_ltc_tx_row(row_data):
    sql = "INSERT INTO nn_ltc_tx (txid, block_hash, block_height, \
                                block_time, block_datetime, \
                                address, notary, season, category, \
                                input_index, input_sats, \
                                output_index, output_sats, fees, num_inputs, num_outputs) \
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
        ON CONFLICT ON CONSTRAINT unique_ltc_nn_txid DO UPDATE SET \
        notary='"+str(row_data[6])+"', category='"+str(row_data[8])+"';"
    try:
        CURSOR.execute(sql, row_data)
        CONN.commit()
    except Exception as e:
        logger.debug(e)
        if str(e).find('duplicate') == -1:
            logger.debug(row_data)
        CONN.rollback()