#!/usr/bin/env python3
import os
import time
from datetime import datetime as dt
import datetime
from dotenv import load_dotenv
import psycopg2
from decimal import *
from rpclib import def_credentials
import logging
import logging.handlers
from notary_lib import seasons_info, notary_info, known_addresses

logger = logging.getLogger()

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

# TABLE UPDATES


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
            (block_height, block_time, block_datetime, value, address, name, txid, season) \
            VALUES (%s, %s, %s, %s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_block DO UPDATE SET \
            block_time='"+str(row_data[1])+"', \
            block_datetime='"+str(row_data[2])+"', \
            value='"+str(row_data[3])+"', \
            address='"+str(row_data[4])+"', \
            name='"+str(row_data[5])+"', \
            txid='"+str(row_data[6])+"', \
            season='"+str(row_data[7])+"';"
        cursor.execute(sql, row_data)
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
    conf = "btc_count="+str(row_data[1])+", antara_count="+str(row_data[2])+", \
        third_party_count="+str(row_data[3])+", other_count="+str(row_data[4])+", \
        total_ntx_count="+str(row_data[5])+", chain_ntx_counts='"+str(row_data[6])+"', \
        chain_ntx_pct='"+str(row_data[7])+"', time_stamp="+str(row_data[8])+";"
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

# NOTARISATION OPS

def get_latest_chain_ntx_info(cursor, chain, height):
    sql = "SELECT ac_ntx_blockhash, ac_ntx_height, opret, block_hash, txid \
           FROM notarised WHERE chain = '"+chain+"' AND block_height = "+str(height)+";"
    cursor.execute(sql)
    chains_resp = cursor.fetchone()
    return chains_resp

# MINED OPS

def get_miner(block):
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
                for season_num in seasons_info:
                    if blocktime < seasons_info[season_num]['end_time']:
                        season = season_num
                        break

                value = tx['vout'][0]['value']
                row_data = (block, blocktime, block_datetime, Decimal(value), address, name, tx['txid'], season)
                return row_data

def get_season_mined_counts(conn, cursor, season):
    sql = "SELECT name, COUNT(*), SUM(value), MAX(value), max(block_time), \
           max(block_height) FROM mined WHERE block_time >= "+str(seasons_info[season]['start_time'])+" \
           AND block_time <= "+str(seasons_info[season]['end_time'])+" GROUP BY name;"
    cursor.execute(sql)
    results = cursor.fetchall()
    time_stamp = int(time.time())
    for item in results:
        row_data = (item[0], season, int(item[1]), float(item[2]), float(item[3]),
                    int(item[4]), int(item[5]), int(time_stamp))
        if item[0] in notary_info:
            logger.info("Adding "+str(row_data)+" to season_mined_counts table")
        result = update_season_mined_count_tbl(conn, cursor, row_data)
    return result

def get_daily_mined_counts(conn, cursor, day):
    results = get_mined_date_aggregates(cursor, day)
    time_stamp = int(time.time())
    for item in results:
        row_data = (item[0], int(item[1]), float(item[2]), str(day), int(time_stamp))
        if item[0] in notary_info:
            logger.info("Adding "+str(row_data)+" to daily_mined_counts table")
        result = update_daily_mined_count_tbl(conn, cursor, row_data)
    return result

# AGGREGATES

def get_chain_ntx_season_aggregates(cursor, season):
    sql = "SELECT chain, MAX(block_height), MAX(block_time), COALESCE(COUNT(*), 0) \
           FROM notarised WHERE \
           season = '"+str(season)+"' \
           GROUP BY chain;"
    cursor.execute(sql)
    return cursor.fetchall()

def get_chain_ntx_date_aggregates(cursor, day):
    sql = "SELECT chain, COALESCE(MAX(block_height), 0), COALESCE(MAX(block_time), 0), COALESCE(COUNT(*), 0) \
           FROM notarised WHERE \
           DATE_TRUNC('day', block_datetime) = '"+str(day)+"' \
           GROUP BY chain;"
    cursor.execute(sql)
    return cursor.fetchall()

def get_mined_date_aggregates(cursor, day):
    sql = "SELECT name, COALESCE(COUNT(*),0), SUM(value) FROM mined WHERE \
           DATE_TRUNC('day', block_datetime) = '"+str(day)+"' \
           GROUP BY name;"
    cursor.execute(sql)
    return cursor.fetchall()

# SEASON / DAY FILTERED

def get_ntx_for_season(cursor, season):
    sql = "SELECT chain, notaries \
           FROM notarised WHERE \
           season = '"+str(season)+"';"
    cursor.execute(sql)
    return cursor.fetchall()

def get_ntx_for_day(cursor, day):
    sql = "SELECT chain, notaries \
           FROM notarised WHERE \
           DATE_TRUNC('day', block_datetime) = '"+str(day)+"';"
    cursor.execute(sql)
    resp = cursor.fetchall() 
    return resp

def get_mined_for_season(cursor, season):
    sql = "SELECT * \
           FROM mined WHERE \
           season = '"+str(season)+"';"
    cursor.execute(sql)
    return cursor.fetchall()

def get_mined_for_day(cursor, day):
    sql = "SELECT * \
           FROM mined WHERE \
           DATE_TRUNC('day', block_datetime) = '"+str(day)+"';"
    cursor.execute(sql)
    return cursor.fetchall()


# QUICK QUERIES

def get_dates_list(cursor, table, date_col):
    sql = "SELECT DATE_TRUNC('day', "+date_col+") as day \
           FROM "+table+" \
           GROUP BY day;"
    cursor.execute(sql)
    dates = cursor.fetchall()
    date_list = []
    for date in dates:
        date_list.append(date[0])
    return date_list

def get_existing_dates_list(cursor, table, date_col):
    sql = "SELECT "+date_col+" \
           FROM "+table+";"
    cursor.execute(sql)
    dates = cursor.fetchall()
    date_list = []
    for date in dates:
        date_list.append(date[0])
    return date_list

def get_records_for_date(cursor, table, date_col, date):
    sql = "SELECT * \
           FROM "+table+" WHERE \
           DATE_TRUNC('day',"+date_col+") = '"+str(date)+"';"
    cursor.execute(sql)
    return cursor.fetchall()

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
    return cursor.fetchone()[0]

def get_max_from_table(cursor, table, col):
    sql = "SELECT MAX("+col+") FROM "+table
    cursor.execute(sql)
    return cursor.fetchone()[0]

def get_count_from_table(cursor, table, col):
    sql = "SELECT COALESCE(COUNT("+col+"), 0) FROM "+table
    cursor.execute(sql)
    return cursor.fetchone()[0]

def get_sum_from_table(cursor, table, col):
    sql = "SELECT SUM("+col+") FROM "+table
    cursor.execute(sql)
    return cursor.fetchone()[0]


# MISC TABLE OPS

def get_table_names(cursor):
    sql = "SELECT tablename FROM pg_catalog.pg_tables \
           WHERE schemaname != 'pg_catalog' \
           AND schemaname != 'information_schema';"
    cursor.execute(sql)
    tables = cursor.fetchall()
    tables_list = []
    for table in tables:
        tables_list.append(table[0])
    return tables_list

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

def delete_from_table(conn, cursor, table, condition=None):
    sql = "TRUNCATE "+table
    if condition:
        sql = sql+" WHERE "+condition
    sql = sql+";"
    cursor.execute()
    conn.commit()

def ts_col_to_dt_col(conn, cursor, ts_col, dt_col, table):
    sql = "UPDATE "+table+" SET "+dt_col+"=to_timestamp("+ts_col+");"
    cursor.execute(sql)
    conn.commit()

def ts_col_to_season_col(conn, cursor, ts_col, season_col, table):
    for season in seasons_info:
        sql = "UPDATE "+table+" \
               SET "+season_col+"='"+season+"' \
               WHERE "+ts_col+" > "+str(seasons_info[season]['start_time'])+" \
               AND "+ts_col+" < "+str(seasons_info[season]['end_time'])+";"
        cursor.execute(sql)
        conn.commit()

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
        return 1
    except Exception as e:
        if str(e).find('Duplicate') == -1:
            logger.debug(e)
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