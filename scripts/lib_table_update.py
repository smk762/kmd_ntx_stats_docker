#!/usr/bin/env python3
import logging
import logging.handlers
from dotenv import load_dotenv
import os
from psycopg2.extras import execute_values
from lib_const import *

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

load_dotenv()
# set this to False in .env when originally populating the table, or rescanning
skip_past_seasons = (os.getenv("skip_past_seasons") == 'True')

# set this to True in .env to quickly update tables with most recent data
skip_until_yesterday = (os.getenv("skip_until_yesterday") == 'True')

def update_addresses_tbl(conn, cursor, row_data):
    try:
        sql = "INSERT INTO addresses \
              (season, node, notary, notary_id, chain, pubkey, address) \
               VALUES (%s, %s, %s, %s, %s, %s, %s) \
               ON CONFLICT ON CONSTRAINT unique_season_chain_address DO UPDATE SET \
               node='"+str(row_data[1])+"', notary='"+str(row_data[2])+"', \
               pubkey='"+str(row_data[5])+"', address='"+str(row_data[6])+"';"
        cursor.execute(sql, row_data)
        conn.commit()
        return 1
    except Exception as e:
        logger.debug(e)
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        conn.rollback()
        return 0

def update_balances_tbl(conn, cursor, row_data):
    try:
        sql = "INSERT INTO balances \
            (notary, chain, balance, address, season, node, update_time) \
            VALUES (%s, %s, %s, %s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_chain_address_season_balance DO UPDATE SET \
            balance="+str(row_data[2])+", \
            node='"+str(row_data[5])+"', \
            update_time="+str(row_data[6])+";"
        cursor.execute(sql, row_data)
        conn.commit()
        return 1
    except Exception as e:
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        conn.rollback()
        return 0

def update_rewards_tbl(conn, cursor, row_data):
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
        cursor.execute(sql, row_data)
        conn.commit()
        return 1
    except Exception as e:
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        conn.rollback()
        return 0

def update_notarised_btc_tbl(conn, cursor, row_data):
    sql = "INSERT INTO notarised_btc (btc_txid, btc_block_hash, btc_block_ht, \
                                      btc_block_time, \
                                      addresses, notaries, kmd_txid, \
                                      kmd_block_hash, kmd_block_ht, \
                                      kmd_block_time, \
                                      opret, season) \
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
    try:
        cursor.execute(sql, row_data)
        conn.commit()
        logger.debug(row_data)
    except Exception as e:
        if str(e).find('duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        conn.rollback()

def update_ntx_row(conn, cursor, row_data):
    sql = "INSERT INTO notarised (chain, block_height, \
                                block_time, block_datetime, block_hash, \
                                notaries, ac_ntx_blockhash, ac_ntx_height, \
                                txid, opret, season, btc_validated) \
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
    try:
        cursor.execute(sql, row_data)
        conn.commit()
    except Exception as e:
        if str(e).find('duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        conn.rollback()

def update_ntx_records(conn, cursor, records):
    try:
        execute_values(cursor, "INSERT INTO notarised (chain, block_height, block_time, block_datetime, block_hash, \
                                notaries, ac_ntx_blockhash, ac_ntx_height, txid, opret, season, btc_validated) VALUES %s", records)

        conn.commit()
    except Exception as e:
        if str(e).find('duplicate') == -1:
            logger.debug(e)
        conn.rollback()

def update_validation_notarised_tbl(conn, cursor, btc_txid, btc_block_hash, btc_block_ht, opret):
    sql = "UPDATE notarised SET \
          chain='BTC', btc_validated='true', \
          txid='"+btc_txid+"', \
          block_hash='"+btc_block_hash+"', \
          block_height="+str(btc_block_ht)+", \
          opret='"+opret+"' \
          WHERE opret LIKE '%' || '"+opret[11:33]+"' || '%';"
    try:
        cursor.execute(sql)
        conn.commit()
        logger.info("btc ntx validated in ntx table")
    except Exception as e:
        if str(e).find('duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        conn.rollback()

def update_coins_tbl(conn, cursor, row_data):
    try:
        sql = "INSERT INTO coins \
            (chain, coins_info, electrums, electrums_ssl, explorers, dpow, dpow_active, mm2_compatible) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_chain_coin DO UPDATE SET \
            coins_info='"+str(row_data[1])+"', \
            electrums='"+str(row_data[2])+"', \
            electrums_ssl='"+str(row_data[3])+"', \
            explorers='"+str(row_data[4])+"', \
            dpow='"+str(row_data[5])+"', \
            dpow_active='"+str(row_data[6])+"', \
            mm2_compatible='"+str(row_data[7])+"';"
        cursor.execute(sql, row_data)
        conn.commit()
        return 1
    except Exception as e:
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        conn.rollback()
        return 0
        
def update_mined_tbl(conn, cursor, row_data):
    try:
        sql = "INSERT INTO mined \
            (block_height, block_time, block_datetime, \
             value, address, name, txid, season) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_block DO UPDATE SET \
            block_time='"+str(row_data[1])+"', \
            block_datetime='"+str(row_data[2])+"', \
            value='"+str(row_data[3])+"', \
            address='"+str(row_data[4])+"', \
            name='"+str(row_data[5])+"', \
            txid='"+str(row_data[6])+"', \
            season='"+str(row_data[7])+"';"
        cursor.execute(sql, row_data)
        logger.info((row_data)+" added to db")
        conn.commit()
        return 1
    except Exception as e:
        logger.debug(e)
        if str(e).find('Duplicate') == -1:
            logger.debug(row_data)
        conn.rollback()
        return 0

def update_season_mined_count_tbl(conn, cursor, row_data):
    try:
        sql = "INSERT INTO  mined_count_season \
            (notary, season, blocks_mined, sum_value_mined, \
            max_value_mined, last_mined_blocktime, last_mined_block, \
            time_stamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_notary_season_mined DO UPDATE SET \
            blocks_mined="+str(row_data[2])+", sum_value_mined="+str(row_data[3])+", \
            max_value_mined="+str(row_data[4])+", last_mined_blocktime="+str(row_data[5])+", \
            last_mined_block="+str(row_data[6])+", time_stamp='"+str(row_data[7])+"';"
        cursor.execute(sql, row_data)
        conn.commit()
        return 1
    except Exception as e:
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        conn.rollback()
        return 0

def update_season_notarised_chain_tbl(conn, cursor, row_data):
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
         
    cursor.execute(sql, row_data)
    conn.commit()

def update_season_notarised_count_tbl(conn, cursor, row_data): 
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
    cursor.execute(sql, row_data)
    conn.commit()

def update_daily_mined_count_tbl(conn, cursor, row_data):
    try:
        sql = "INSERT INTO mined_count_daily \
            (notary, blocks_mined, sum_value_mined, \
            mined_date, time_stamp) VALUES (%s, %s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_notary_daily_mined \
            DO UPDATE SET \
            blocks_mined="+str(row_data[1])+", \
            sum_value_mined='"+str(row_data[2])+"';"
        cursor.execute(sql, row_data)
        conn.commit()
        return 1
    except Exception as e:
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        conn.rollback()
        return 0

def update_daily_notarised_chain_tbl(conn, cursor, row_data):
    sql = "INSERT INTO notarised_chain_daily \
         (chain, ntx_count, notarised_date) \
          VALUES (%s, %s, %s) \
          ON CONFLICT ON CONSTRAINT unique_notarised_chain_date DO UPDATE \
          SET ntx_count="+str(row_data[1])+";"
    cursor.execute(sql, row_data)
    conn.commit()

def update_daily_notarised_count_tbl(conn, cursor, row_data): 
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
    cursor.execute(sql, row_data)
    conn.commit()

def update_table(conn, cursor, table, update_str, condition):
    try:
        sql = "UPDATE "+table+" \
               SET "+update_str+" WHERE "+condition+";"
        logger.info(sql)
        cursor.execute(sql)
        conn.commit()
        return 1
    except Exception as e:
        logger.debug(e)
        logger.debug(sql)
        conn.rollback()
        return 0

def update_sync_tbl(conn, cursor, row_data):
    try:
        sql = "INSERT INTO chain_sync \
            (chain, block_height, sync_hash, explorer_hash) \
            VALUES (%s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_chain_sync DO UPDATE SET \
            block_height='"+str(row_data[1])+"', \
            sync_hash='"+str(row_data[2])+"', \
            explorer_hash='"+str(row_data[3])+"';"
        cursor.execute(sql, row_data)
        conn.commit()
        return 1
    except Exception as e:
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        conn.rollback()
        return 0

def update_nn_social_tbl(conn, cursor, row_data):
    try:
        sql = "INSERT INTO  nn_social \
            (notary, twitter, youtube, discord, \
            telegram, github, keybase, \
            website, icon,season) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_notary_season_social DO UPDATE SET \
            twitter='"+str(row_data[1])+"', \
            youtube='"+str(row_data[2])+"', discord='"+str(row_data[3])+"', \
            telegram='"+str(row_data[4])+"', github='"+str(row_data[5])+"', \
            keybase='"+str(row_data[6])+"', website='"+str(row_data[7])+"', \
            icon='"+str(row_data[8])+"', season='"+str(row_data[9])+"';"
        cursor.execute(sql, row_data)
        conn.commit()
        return 1
    except Exception as e:
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        conn.rollback()
        return 0

def update_coin_social_tbl(conn, cursor, row_data):
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
        cursor.execute(sql, row_data)
        conn.commit()
        return 1
    except Exception as e:
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        conn.rollback()
        return 0

def update_last_ntx_tbl(conn, cursor, row_data):
    try:
        sql = "INSERT INTO  last_notarised \
            (notary, chain, txid, block_height, \
            block_time, season) VALUES (%s, %s, %s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_notary_chain DO UPDATE SET \
            txid='"+str(row_data[2])+"', \
            block_height='"+str(row_data[3])+"', \
            block_time='"+str(row_data[4])+"', \
            season='"+str(row_data[5])+"';"
        cursor.execute(sql, row_data)
        conn.commit()
        logger.info("Added "+str(row_data))
        return 1
    except Exception as e:
        logger.debug(e)
        if str(e).find('Duplicate') == -1:
            logger.debug(row_data)
        conn.rollback()
        return 0

def update_last_btc_ntx_tbl(conn, cursor, row_data):
    try:
        sql = "INSERT INTO  last_btc_notarised \
            (notary, txid, block_height, \
            block_time, season) VALUES (%s, %s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_notary_btc_ntx DO UPDATE SET \
            txid='"+str(row_data[1])+"', \
            block_height='"+str(row_data[2])+"', \
            block_time='"+str(row_data[3])+"', \
            season='"+str(row_data[4])+"';"
        cursor.execute(sql, row_data)
        conn.commit()
        return 1
    except Exception as e:
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        conn.rollback()
        return 0

def update_btc_address_deltas_tbl(conn, cursor, row_data):
    try:
        sql = "INSERT INTO  btc_address_deltas \
            (notary, address, category, txid, block_time, \
             total_in, total_out, fees, vin_addr, vout_addr, season) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
        cursor.execute(sql, row_data)
        conn.commit()
        return 1
    except Exception as e:
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        conn.rollback()
        return 0

def update_funding_tbl(conn, cursor, row_data):
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
        cursor.execute(sql, row_data)
        conn.commit()
        return 1
    except Exception as e:
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        conn.rollback()
        return 0

def ts_col_to_dt_col(conn, cursor, ts_col, dt_col, table):
    sql = "UPDATE "+table+" SET "+dt_col+"=to_timestamp("+ts_col+");"
    cursor.execute(sql)
    conn.commit()

def update_notarised_tenure(conn, cursor, row_data):
    try:
        sql = "INSERT INTO notarised_tenure (chain, first_ntx_block, \
            last_ntx_block, first_ntx_block_time, last_ntx_block_time, ntx_count, season) \
            VALUES (%s, %s, %s, %s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_chain_season_tenure DO UPDATE SET \
            first_ntx_block='"+str(row_data[1])+"', last_ntx_block="+str(row_data[2])+", \
            first_ntx_block_time="+str(row_data[3])+", last_ntx_block_time="+str(row_data[4])+", \
            ntx_count="+str(row_data[5])+";"
        cursor.execute(sql, row_data)
        conn.commit()
        return 1
    except Exception as e:
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        conn.rollback()
        return 0

def update_nn_btc_tx_row(conn, cursor, row_data):
    sql = "INSERT INTO nn_btc_tx (txid, block_hash, block_height, \
                                block_time, block_datetime, \
                                address, notary, season, category, \
                                input_index, input_sats, \
                                output_index, output_sats, fees, num_inputs, num_outputs) \
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
        ON CONFLICT ON CONSTRAINT unique_btc_nn_txid DO UPDATE SET \
        notary='"+str(row_data[6])+"';"
    try:
        cursor.execute(sql, row_data)
        conn.commit()
    except Exception as e:
        logger.debug(e)
        if str(e).find('duplicate') == -1:
            logger.debug(row_data)
        conn.rollback()

def delete_nn_btc_tx_row(conn, cursor, txid, notary):
    sql = "DELETE FROM nn_btc_tx WHERE txid='"+str(txid)+"' and notary='"+str(notary)+"';"
    try:
        cursor.execute(sql)
        conn.commit()
    except Exception as e:
        logger.debug(e)
        conn.rollback()