#!/usr/bin/env python3
import logging
import logging.handlers
import os
import time
from dotenv import load_dotenv
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

def get_latest_chain_ntx_info(cursor, chain, height):
    sql = "SELECT ac_ntx_blockhash, ac_ntx_height, opret, block_hash, txid \
           FROM notarised WHERE chain = '"+chain+"' AND block_height = "+str(height)+";"
    cursor.execute(sql)
    chains_resp = cursor.fetchone()
    return chains_resp

def get_validated_ntx_info(cursor, opret):
    sql = "SELECT txid, block_time, btc_validated FROM notarised \
          WHERE btc_validated != 'true' AND opret LIKE '%' || '"+opret[11:33]+"' || '%';"
    cursor.execute(sql)
    return cursor.fetchone()

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

def get_dpow_coins(conn, cursor):
    sql = "SELECT * \
           FROM coins WHERE \
           dpow_active = 1;"
    cursor.execute(sql)
    return cursor.fetchall()

def get_season_mined_counts(cursor, season, season_notaries):
    sql = "SELECT name, COUNT(*), SUM(value), MAX(value), max(block_time), \
           max(block_height) FROM mined WHERE block_time >= "+str(SEASONS_INFO[season]['start_time'])+" \
           AND block_time <= "+str(SEASONS_INFO[season]['end_time'])+" GROUP BY name;"
    cursor.execute(sql)
    return cursor.fetchall()

def get_ntx_min_max(cursor, season, chain):
    cursor.execute("SELECT MAX(block_height), MAX(block_time), \
                    MIN(block_height), MIN(block_time), COUNT(*) \
                    FROM notarised WHERE chain = '"+chain+"' \
                    AND season = '"+season+"';")
    return cursor.fetchone()

def get_notarised_chains(cursor):
    chains = []
    cursor.execute("SELECT DISTINCT chain FROM notarised;")
    chain_results = cursor.fetchall()
    for result in chain_results:
        chains.append(result[0])
    return chains

def get_notarised_seasons(cursor):
    seasons = []
    cursor.execute("SELECT DISTINCT season FROM notarised;")
    season_results = cursor.fetchall()
    for result in season_results:
        seasons.append(result[0])
    return seasons

def get_notary_last_ntx(cursor):
    # Get chain and time of last ntx
    cursor.execute("SELECT notary, chain, block_height from last_notarised;")
    last_ntx = cursor.fetchall()
    notary_last_ntx = {}
    for item in last_ntx:
        notary = item[0]
        chain = item[1]
        block_height = item[2]
        if notary not in notary_last_ntx:
            notary_last_ntx.update({notary:{}})
        notary_last_ntx[notary].update({chain:block_height})
    return notary_last_ntx

def get_existing_ntxids(cursor, address=None, category=None):
    recorded_txids = []
    logger.info("Getting existing TXIDs from database...")
    if address and category:
        cursor.execute(f"SELECT txid from notarised WHERE address='{address}' AND category='{category}';")    
    elif category:
        cursor.execute(f"SELECT txid from notarised WHERE category='{category}';")    
    elif address:
        cursor.execute(f"SELECT txid from notarised WHERE address='{address}';")    
    else:
        cursor.execute("SELECT txid from notarised;")
    existing_txids = cursor.fetchall()

    for txid in existing_txids:
        recorded_txids.append(txid[0])
    return recorded_txids

def get_existing_nn_btc_txids(cursor, address=None, category=None, season=None, notary=None):
    recorded_txids = []
    sql = f"SELECT DISTINCT txid from nn_btc_tx"
    conditions = []
    if category:
        conditions.append(f"category = '{category}'")
    if season:
        conditions.append(f"season = '{season}'")
    if address:
        conditions.append(f"address = '{address}'")
    if notary:
        conditions.append(f"notary = '{notary}'")

    if len(conditions) > 0:
        sql += " where "
        sql += " and ".join(conditions)    
    sql += ";"

    cursor.execute(sql)
    existing_txids = cursor.fetchall()

    for txid in existing_txids:
        recorded_txids.append(txid[0])
    return recorded_txids

def get_non_notary_btc_txids(cursor):
    non_notary_txids = []
    logger.info("Getting non-notary TXIDs from database...")
    cursor.execute("SELECT DISTINCT txid from nn_btc_tx where notary = 'non-NN';")
    txids = cursor.fetchall()

    for txid in txids:
        non_notary_txids.append(txid[0])
    return non_notary_txids

def get_replenish_addresses(cursor):
    replenish_addr = []
    logger.info("Getting Replenish Addresses from database...")
    cursor.execute("SELECT DISTINCT address from nn_btc_tx WHERE notary = 'Replenish_Address';")
    addresses = cursor.fetchall()

    for addr in addresses:
        replenish_addr.append(addr[0])
    return replenish_addr

def get_existing_btc_ntxids(cursor):
    existing_txids = []
    cursor.execute("SELECT DISTINCT txid FROM notarised WHERE chain = 'BTC';")
    txids_results = cursor.fetchall()
    for result in txids_results:
        existing_txids.append(result[0])    
    return existing_txids

def get_existing_notarised_btc(cursor):
    existing_txids = []
    cursor.execute("SELECT DISTINCT btc_txid FROM notarised_btc;")
    txids_results = cursor.fetchall()
    for result in txids_results:
        existing_txids.append(result[0])
    return existing_txids
