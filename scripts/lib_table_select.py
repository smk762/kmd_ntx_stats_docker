#!/usr/bin/env python3
import logging
import logging.handlers
import os
import time
from lib_const import *

logger = logging.getLogger(__name__)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s', datefmt='%d-%b-%y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def get_latest_chain_ntx_info(chain, height):
    sql = "SELECT ac_ntx_blockhash, ac_ntx_height, opret, block_hash, txid \
           FROM notarised WHERE chain = '"+chain+"' AND block_height = "+str(height)+";"
    CURSOR.execute(sql)
    chains_resp = CURSOR.fetchone()
    return chains_resp

def get_validated_ntx_info(opret):
    sql = "SELECT txid, block_time, btc_validated FROM notarised \
          WHERE btc_validated != 'true' AND opret LIKE '%' || '"+opret[11:33]+"' || '%';"
    CURSOR.execute(sql)
    return CURSOR.fetchone()

def get_chain_ntx_season_aggregates(season):
    sql = "SELECT chain, MAX(block_height), MAX(block_time), COALESCE(COUNT(*), 0) \
           FROM notarised WHERE \
           season = '"+str(season)+"' \
           GROUP BY chain;"
    CURSOR.execute(sql)
    return CURSOR.fetchall()

def get_chain_ntx_date_aggregates(day, season):
    sql = "SELECT chain, COALESCE(MAX(block_height), 0), COALESCE(MAX(block_time), 0), COALESCE(COUNT(*), 0) \
           FROM notarised WHERE season='"+season+"' AND \
           DATE_TRUNC('day', block_datetime) = '"+str(day)+"' \
           GROUP BY chain;"
    CURSOR.execute(sql)
    return CURSOR.fetchall()

def get_mined_date_aggregates(day):
    sql = "SELECT name, COALESCE(COUNT(*),0), SUM(value) FROM mined WHERE \
           DATE_TRUNC('day', block_datetime) = '"+str(day)+"' \
           GROUP BY name;"
    CURSOR.execute(sql)
    return CURSOR.fetchall()

def get_ntx_for_season(season):
    sql = "SELECT chain, notaries \
           FROM notarised WHERE \
           season = '"+str(season)+"';"
    CURSOR.execute(sql)
    return CURSOR.fetchall()

def get_ntx_for_day(day, season):
    sql = "SELECT chain, notaries \
           FROM notarised WHERE season='"+season+"' AND \
           DATE_TRUNC('day', block_datetime) = '"+str(day)+"';"
    CURSOR.execute(sql)
    resp = CURSOR.fetchall() 
    return resp

def get_mined_for_season(season):
    sql = "SELECT * \
           FROM mined WHERE \
           season = '"+str(season)+"';"
    CURSOR.execute(sql)
    return CURSOR.fetchall()

def get_mined_for_day(day):
    sql = "SELECT * \
           FROM mined WHERE \
           DATE_TRUNC('day', block_datetime) = '"+str(day)+"';"
    CURSOR.execute(sql)
    return CURSOR.fetchall()


def get_dates_list(table, date_col):
    sql = "SELECT DATE_TRUNC('day', "+date_col+") as day \
           FROM "+table+" \
           GROUP BY day;"
    CURSOR.execute(sql)
    dates = CURSOR.fetchall()
    date_list = []
    for date in dates:
        date_list.append(date[0])
    return date_list

def get_existing_dates_list(table, date_col):
    sql = "SELECT "+date_col+" \
           FROM "+table+";"
    CURSOR.execute(sql)
    dates = CURSOR.fetchall()
    date_list = []
    for date in dates:
        date_list.append(date[0])
    return date_list

def get_records_for_date(table, date_col, date):
    sql = "SELECT * \
           FROM "+table+" WHERE \
           DATE_TRUNC('day',"+date_col+") = '"+str(date)+"';"
    CURSOR.execute(sql)
    return CURSOR.fetchall()

def select_from_table(table, cols, conditions=None):
    sql = "SELECT "+cols+" FROM "+table
    if conditions:
        sql = sql+" WHERE "+conditions
    sql = sql+";"
    CURSOR.execute(sql)
    return CURSOR.fetchall()

def get_min_from_table(table, col):
    sql = "SELECT MIN("+col+") FROM "+table
    CURSOR.execute(sql)
    return CURSOR.fetchone()[0]

def get_max_from_table(table, col):
    sql = "SELECT MAX("+col+") FROM "+table
    CURSOR.execute(sql)
    return CURSOR.fetchone()[0]

def get_count_from_table(table, col):
    sql = "SELECT COALESCE(COUNT("+col+"), 0) FROM "+table
    CURSOR.execute(sql)
    return CURSOR.fetchone()[0]

def get_sum_from_table(table, col):
    sql = "SELECT SUM("+col+") FROM "+table
    CURSOR.execute(sql)
    return CURSOR.fetchone()[0]

def get_table_names():
    sql = "SELECT tablename FROM pg_catalog.pg_tables \
           WHERE schemaname != 'pg_catalog' \
           AND schemaname != 'information_schema';"
    CURSOR.execute(sql)
    tables = CURSOR.fetchall()
    tables_list = []
    for table in tables:
        tables_list.append(table[0])
    return tables_list

def get_season_mined_counts(season, season_notaries):
    sql = "SELECT name, COUNT(*), SUM(value), MAX(value), max(block_time), \
           max(block_height) FROM mined WHERE block_time >= "+str(SEASONS_INFO[season]['start_time'])+" \
           AND block_time <= "+str(SEASONS_INFO[season]['end_time'])+" GROUP BY name;"
    CURSOR.execute(sql)
    return CURSOR.fetchall()

def get_ntx_min_max(season, chain):
    CURSOR.execute("SELECT MAX(block_height), MAX(block_time), \
                    MIN(block_height), MIN(block_time), COUNT(*) \
                    FROM notarised WHERE chain = '"+chain+"' \
                    AND season = '"+season+"';")
    return CURSOR.fetchone()

def get_notarised_chains():
    chains = []
    CURSOR.execute("SELECT DISTINCT chain FROM notarised;")
    chain_results = CURSOR.fetchall()
    for result in chain_results:
        chains.append(result[0])
    return chains

def get_notarised_seasons():
    seasons = []
    CURSOR.execute("SELECT DISTINCT season FROM notarised;")
    season_results = CURSOR.fetchall()
    for result in season_results:
        seasons.append(result[0])
    return seasons

def get_notary_last_ntx(chain=None):
    # Get chain and time of last ntx
    sql = "SELECT notary, chain, block_height from last_notarised"
    if chain:
        sql += f" WHERE chain='{chain}'"
    sql += ";"
    CURSOR.execute(sql)
    last_ntx = CURSOR.fetchall()
    notary_last_ntx = {}
    for item in last_ntx:
        notary = item[0]
        chain = item[1]
        block_height = item[2]
        if notary not in notary_last_ntx:
            notary_last_ntx.update({notary:{}})
        notary_last_ntx[notary].update({chain:block_height})
    return notary_last_ntx


def get_existing_ntxids(address=None, category=None):
    recorded_txids = []
    logger.info("Getting existing TXIDs from database...")
    if address and category:
        CURSOR.execute(f"SELECT txid from notarised WHERE address='{address}' AND category='{category}';")    
    elif category:
        CURSOR.execute(f"SELECT txid from notarised WHERE category='{category}';")    
    elif address:
        CURSOR.execute(f"SELECT txid from notarised WHERE address='{address}';")    
    else:
        CURSOR.execute("SELECT txid from notarised;")
    existing_txids = CURSOR.fetchall()

    for txid in existing_txids:
        recorded_txids.append(txid[0])
    return recorded_txids

def get_existing_nn_btc_txids(address=None, category=None, season=None, notary=None):
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

    CURSOR.execute(sql)
    existing_txids = CURSOR.fetchall()

    for txid in existing_txids:
        recorded_txids.append(txid[0])
    return recorded_txids

def get_non_notary_btc_txids():
    non_notary_txids = []
    logger.info("Getting non-notary TXIDs from database...")
    CURSOR.execute("SELECT DISTINCT txid from nn_btc_tx where notary = 'non-NN';")
    txids = CURSOR.fetchall()

    for txid in txids:
        non_notary_txids.append(txid[0])
    return non_notary_txids

def get_replenish_addresses():
    replenish_addr = []
    logger.info("Getting Replenish Addresses from database...")
    CURSOR.execute("SELECT DISTINCT address from nn_btc_tx WHERE notary = 'Replenish_Address';")
    addresses = CURSOR.fetchall()

    for addr in addresses:
        replenish_addr.append(addr[0])
    return replenish_addr

def get_existing_btc_ntxids():
    existing_txids = []
    CURSOR.execute("SELECT DISTINCT txid FROM notarised WHERE chain = 'BTC';")
    txids_results = CURSOR.fetchall()
    for result in txids_results:
        existing_txids.append(result[0])    
    return existing_txids

def get_existing_notarised_btc():
    existing_txids = []
    CURSOR.execute("SELECT DISTINCT btc_txid FROM notarised_btc;")
    txids_results = CURSOR.fetchall()
    for result in txids_results:
        existing_txids.append(result[0])
    return existing_txids
