#!/usr/bin/env python3
import time
from dotenv import load_dotenv
import psycopg2
import logging
import logging.handlers
from address_lib import seasons_info, notary_info

logger = logging.getLogger(__name__)

load_dotenv()

def connect_db():
    conn = psycopg2.connect(
        host='localhost',
        user='postgres',
        password='postgres',
        port = "7654",
        database='postgres'
    )
    return conn

def get_max_col_val_in_table(col, table):
    sql = "SELECT MAX("+col+") FROM "+table+";"
    cursor.execute(sql)
    max_val = cursor.fetchone()
    logger.info("Max "+col+" value is "+str(max_val))
    return max_val

def select_from_table(cursor, table, cols, conditions=None):
    sql = "SELECT "+cols+" FROM "+table
    if conditions:
        sql = sql+" WHERE "+conditions
    sql = sql+";"
    cursor.execute(sql)
    return cursor.fetchall()

def get_min_from_table(cursor, table, col):
    sql = "SELECT MIN("+col+") FROM "+table
    cursor.execute(sql)
    return cursor.fetchone()

def get_max_from_table(cursor, table, col):
    sql = "SELECT MAX("+col+") FROM "+table
    cursor.execute(sql)
    return cursor.fetchone()

def get_count_from_table(cursor, table, col):
    sql = "SELECT COUNT("+col+") FROM "+table
    cursor.execute(sql)
    return cursor.fetchone()

def get_sum_from_table(cursor, table, col):
    sql = "SELECT SUM("+col+") FROM "+table
    cursor.execute(sql)
    return cursor.fetchone()

def delete_from_table(conn, cursor, table, condition=None):
    sql = "TRUNCATE "+table
    if condition:
        sql = sql+" WHERE "+condition
    sql = sql+";"
    cursor.execute()
    conn.commit()

def get_latest_chain_ntx_aggregates(cursor):
    sql = "SELECT chain, MAX(block_ht), MAX(block_time), COUNT(*) FROM notarised WHERE block_time >= "+str(seasons_info["Season_3"]["start_time"])+" GROUP BY chain;"
    cursor.execute(sql)
    return cursor.fetchall()

def get_latest_chain_ntx_info(cursor, chain, height):
    sql = "SELECT prev_block_hash, prev_block_ht, opret, block_hash, txid FROM notarised WHERE chain = '"+chain+"' AND block_ht = "+str(height)+";"
    cursor.execute(sql)
    chains_resp = cursor.fetchone()
    return chains_resp

def add_row_to_notarised_chain_tbl(conn, cursor, row_data):
    sql = "INSERT INTO notarised_chain \
         (chain, ntx_count, kmd_ntx_height, kmd_ntx_blockhash,\
          kmd_ntx_txid, lastnotarization, opret, ac_ntx_block_hash, \
          ac_ntx_height, ac_block_height, ntx_lag) \
          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
          ON CONFLICT (chain) DO UPDATE SET ntx_count="+str(row_data[1])+", kmd_ntx_height="+str(row_data[2])+", \
          kmd_ntx_blockhash='"+str(row_data[3])+"', kmd_ntx_txid='"+str(row_data[4])+"', \
          lastnotarization="+str(row_data[5])+", opret='"+str(row_data[6])+"', \
          ac_ntx_block_hash='"+str(row_data[7])+"', ac_ntx_height="+str(row_data[8])+", \
          ac_block_height='"+str(row_data[9])+"', ntx_lag='"+str(row_data[10])+"';"
         
    cursor.execute(sql, row_data)
    conn.commit()

def add_row_to_addresses_tbl(conn, cursor, row_data):
    try:
        sql = "INSERT INTO addresses \
              (season, notary_name, notary_id, coin, pubkey, address) \
               VALUES (%s, %s, %s, %s, %s, %s)"
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


def add_row_to_notarised_count_tbl(conn, cursor, row_data):
    sql = "INSERT INTO notarised_count \
        (notary, btc_count, antara_count, \
        third_party_count, other_count, \
        total_ntx_count, json_count, \
        time_stamp, season) \
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) \
        ON CONFLICT ON CONSTRAINT unique_notary_season DO UPDATE SET \
        btc_count="+str(row_data[1])+", antara_count="+str(row_data[2])+", \
        third_party_count="+str(row_data[3])+", other_count="+str(row_data[4])+", \
        total_ntx_count="+str(row_data[5])+", json_count='"+str(row_data[6])+"', \
        time_stamp="+str(row_data[7])+";"
    cursor.execute(sql, row_data)
    conn.commit()

def add_row_to_mined_count_tbl(conn, cursor, row_data):
    try:
        sql = "INSERT INTO mined_count \
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

def get_mined_counts(conn, cursor, season):
    sql = "SELECT name, COUNT(*), SUM(value), MAX(value), max(block_time), \
           max(block) FROM mined WHERE block_time >= "+str(seasons_info[season]['start_time'])+" \
           AND block_time <= "+str(seasons_info[season]['end_time'])+" GROUP BY name;"
    cursor.execute(sql)
    results = cursor.fetchall()
    time_stamp = int(time.time())
    for item in results:
        row_data = (item[0], season, int(item[1]), float(item[2]), float(item[3]),
                    int(item[4]), int(item[5]), int(time_stamp))
        if item[0] in notary_info:
            print("Adding "+str(row_data)+" to get_mined_counts table")
        result = add_row_to_mined_count_tbl(conn, cursor, row_data)
    return result

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

def update_balances_tbl(conn, cursor, row_data):
    try:
        sql = "INSERT INTO balances \
            (notary, chain, balance, address, update_time) \
            VALUES (%s, %s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_notary_chain_addr_balance DO UPDATE SET \
            balance="+str(row_data[2])+", \
            update_time="+str(row_data[4])+";"
        cursor.execute(sql, row_data)
        conn.commit()
        return 1
    except Exception as e:
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        conn.rollback()
        return 0