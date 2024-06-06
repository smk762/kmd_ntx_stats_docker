#!/usr/bin/env python3
import os
import json
from psycopg2.extras import execute_values
from lib_const import *
from lib_filter import get_notarised_conditions_filter


def update_ntx_row(row_data, table='notarised', unique='unique_txid'):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    sql = f"INSERT INTO {table} (coin, block_height, \
                                block_time, block_datetime, block_hash, \
                                notaries, notary_addresses, ac_ntx_blockhash, ac_ntx_height, \
                                txid, opret, season, server, scored, score_value, epoch) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
                ON CONFLICT ON CONSTRAINT {unique} DO UPDATE SET \
                season='{row_data[11]}', server='{row_data[12]}', scored='{row_data[13]}', \
                notaries=ARRAY{row_data[5]}, notary_addresses=ARRAY{row_data[6]}, \
                score_value={row_data[14]}, epoch='{row_data[15]}';"
    try:
        CURSOR.execute(sql, row_data)
        CONN.commit()
    except Exception as e:
        if str(e).find('duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        CONN.rollback()




def update_server_notarised_tbl(old_server, server):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    sql = f"UPDATE notarised SET \
          server='{server}' \
          WHERE server='{old_server}';"
    try:
        CURSOR.execute(sql)
        CONN.commit()
        print(f"{old_server} reclassed as {server}")
    except Exception as e:
        logger.debug(e)
        CONN.rollback()

def update_coin_server_season_notarised_tbl(server, season, coin):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    sql = f"UPDATE notarised SET \
          server='{server}' \
          WHERE season='{season}'\
          AND coin='{coin}';"
    try:
        CURSOR.execute(sql)
        CONN.commit()
    except Exception as e:
        logger.debug(e)
        CONN.rollback()

def update_unofficial_coin_notarised_tbl(season, coin):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    sql = f"UPDATE notarised SET \
          season='Unofficial', server='Unofficial', epoch='Unofficial' \
          WHERE season='{season}'\
          AND coin='{coin}';"
    try:
        CURSOR.execute(sql)
        CONN.commit()
        print(f"Unofficial coin {coin} updated for {season}")
    except Exception as e:
        logger.debug(e)
        CONN.rollback()

def update_coin_score_notarised_tbl(coin, score_value, scored, min_time=None, max_time=None, season=None, server=None, epoch=None):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    sql = f"UPDATE notarised SET scored={scored}, score_value={score_value}"
    conditions = []
    if coin:
        conditions.append(f"coin = '{coin}'")
    if min_time:
        conditions.append(f"block_time >= {min_time}")
    if max_time:
        conditions.append(f"block_time <= {max_time}")
    if season:
        conditions.append(f"season = '{season}'")
    if server:
        conditions.append(f"server = '{server}'")
    if epoch:
        conditions.append(f"epoch = '{epoch}'")
    if len(conditions) > 0:
        sql += " WHERE "
        sql += " AND ".join(conditions)    
    sql += ";"

    try:
        CURSOR.execute(sql)
        CONN.commit()
        logger.info(f"UPDATED [notarised]: Set score_value to {score_value} WHERE {conditions}")
    except Exception as e:
        logger.debug(e)
        CONN.rollback()

def update_txid_score_notarised_tbl(txid, scored, score_value):
    CONN = connect_db()
    CURSOR = CONN.cursor()
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

def update_season_server_addresses_notarised_tbl(txid, season, server, addresses=None):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    if addresses:
        sql = f"UPDATE notarised SET \
              notary_addresses=ARRAY{addresses},  \
              season='{season}', server='{server}' \
              WHERE txid='{txid}';"
    else:
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
    CONN = connect_db()
    CURSOR = CONN.cursor()
    CURSOR.execute(f"DELETE FROM notarised WHERE txid = '{txid}';")
    CONN.commit()


def delete_from_notarised_tbl_where(
        season=None, server=None, epoch=None, coin=None,
        include_coins=None, exclude_coins=None
    ):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    sql = f"DELETE FROM notarised"
    sql = get_notarised_conditions_filter(
        sql, season=season, server=server, epoch=epoch,
        coin=coin, include_coins=include_coins,
        exclude_coins=exclude_coins
    )
    CURSOR.execute(sql)
    CONN.commit()


def update_coin_ntx_season_row(row_data): 
    CONN = connect_db()
    CURSOR = CONN.cursor()
    sql = f"INSERT INTO coin_ntx_season \
            (season, coin, coin_data, timestamp) \
            VALUES (%s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_coin_season DO UPDATE SET \
            coin_data='{row_data[2]}',\
            timestamp={row_data[3]};"
    CURSOR.execute(sql, row_data)
    CONN.commit()


def update_notary_ntx_season_row(row_data): 
    CONN = connect_db()
    CURSOR = CONN.cursor()
    sql = f"INSERT INTO notary_ntx_season \
            (season, notary, notary_data, timestamp) \
            VALUES (%s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_notary_season DO UPDATE SET \
            notary_data='{row_data[2]}',\
            timestamp={row_data[3]};"
    CURSOR.execute(sql, row_data)
    CONN.commit()


def update_server_ntx_season_row(row_data): 
    CONN = connect_db()
    CURSOR = CONN.cursor()
    sql = f"INSERT INTO server_ntx_season \
            (season, server, server_data, timestamp) \
            VALUES (%s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_server_season DO UPDATE SET \
            server_data='{row_data[2]}',\
            timestamp={row_data[3]};"
    CURSOR.execute(sql, row_data)
    CONN.commit()


def update_daily_notarised_coin_row(row_data):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    sql = f"INSERT INTO notarised_coin_daily \
          (season, server, coin, ntx_count, notarised_date) \
          VALUES (%s, %s, %s, %s, %s) \
          ON CONFLICT ON CONSTRAINT unique_notarised_coin_daily DO UPDATE \
          SET ntx_count={row_data[3]};"
    CURSOR.execute(sql, row_data)
    CONN.commit()


def update_daily_notarised_count_row(row_data): 
    CONN = connect_db()
    CURSOR = CONN.cursor()
    sql = "INSERT INTO notarised_count_daily \
        (notary, master_server_count, main_server_count, \
        third_party_server_count, other_server_count, \
        total_ntx_count, coin_ntx_counts, \
        coin_ntx_pct, timestamp, season, notarised_date) \
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
        ON CONFLICT ON CONSTRAINT unique_notary_date DO UPDATE SET \
        master_server_count="+str(row_data[1])+", main_server_count="+str(row_data[2])+", \
        third_party_server_count="+str(row_data[3])+", other_server_count="+str(row_data[4])+", \
        total_ntx_count="+str(row_data[5])+", coin_ntx_counts='"+str(row_data[6])+"', \
        coin_ntx_pct='"+str(row_data[7])+"', timestamp="+str(row_data[8])+",  \
        season='"+str(row_data[9])+"', notarised_date='"+str(row_data[10])+"';"
    CURSOR.execute(sql, row_data)
    CONN.commit()


def update_coin_last_ntx_row(row_data):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    try:
        sql = F"INSERT INTO coin_last_ntx \
                    (season, server, coin,\
                     notaries, opret, kmd_ntx_blockhash,\
                     kmd_ntx_blockheight, kmd_ntx_blocktime,\
                     kmd_ntx_txid, ac_ntx_blockhash,\
                     ac_ntx_height) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
                ON CONFLICT ON CONSTRAINT unique_coin_last_ntx_season DO UPDATE SET \
                    server='{row_data[1]}', \
                    notaries=ARRAY{row_data[3]}::text[], \
                    opret='{row_data[4]}', \
                    kmd_ntx_blockhash='{row_data[5]}', \
                    kmd_ntx_blockheight={row_data[6]}, \
                    kmd_ntx_blocktime={row_data[7]}, \
                    kmd_ntx_txid='{row_data[8]}', \
                    ac_ntx_blockhash='{row_data[9]}', \
                    ac_ntx_height={row_data[10]};"
        CURSOR.execute(sql, row_data)
        CONN.commit()
    except Exception as e:
        logger.debug(e)
        if str(e).find('Duplicate') == -1:
            logger.debug(row_data)
        CONN.rollback()


def update_notary_last_ntx_row(row_data):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    try:
        sql = F"INSERT INTO notary_last_ntx \
                    (season, server, coin, notary,\
                     notaries, opret, kmd_ntx_blockhash,\
                     kmd_ntx_blockheight, kmd_ntx_blocktime,\
                     kmd_ntx_txid, ac_ntx_blockhash,\
                     ac_ntx_height) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
                ON CONFLICT ON CONSTRAINT unique_notary_last_ntx_notary_season_coin DO UPDATE SET \
                    server='{row_data[1]}', \
                    notaries=ARRAY{row_data[4]}::text[], \
                    opret='{row_data[5]}', \
                    kmd_ntx_blockhash='{row_data[6]}', \
                    kmd_ntx_blockheight={row_data[7]}, \
                    kmd_ntx_blocktime={row_data[8]}, \
                    kmd_ntx_txid='{row_data[9]}', \
                    ac_ntx_blockhash='{row_data[10]}', \
                    ac_ntx_height={row_data[11]};"
        CURSOR.execute(sql, row_data)
        CONN.commit()
        
        return 1
    except Exception as e:
        logger.debug(e)
        if str(e).find('Duplicate') == -1:
            logger.debug(row_data)
        CONN.rollback()
        return 0


def update_notarised_tenure_row(row_data):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    try:
        sql = "INSERT INTO notarised_tenure (coin, first_ntx_block, \
            last_ntx_block, first_ntx_block_time, last_ntx_block_time, \
            official_start_block_time, official_end_block_time, \
            unscored_ntx_count, scored_ntx_count, season, server) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_coin_season_server_tenure DO UPDATE SET \
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


def update_notarised_epoch(actual_epoch, season=None, server=None, coin=None, txid=None):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    sql = f"UPDATE notarised SET epoch='{actual_epoch}'"
    conditions = []
    if season:
        conditions.append(f"season = '{season}'")
    if server:
        conditions.append(f"server = '{server}'")
    if coin:
        conditions.append(f"coin = '{coin}'")
    if txid:
        conditions.append(f"txid = '{txid}'") 
    if len(conditions) > 0:
        sql += " WHERE "
        sql += " AND ".join(conditions)    
    sql += ";"

    try:
        CURSOR.execute(sql)
        CONN.commit()
    except Exception as e:
        logger.debug(e)
        CONN.rollback()


def update_notarised_epoch_scores(coin=None, season=None, server=None, epoch=None, epoch_start=None, epoch_end=None, score_per_ntx=None, scored=None):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    sql = f"UPDATE notarised SET epoch='{epoch}', score_value={score_per_ntx}, scored={scored}"
    conditions = []
    if coin:
        conditions.append(f"coin = '{coin}'")
    if season:
        conditions.append(f"season = '{season}'")
    if server:
        conditions.append(f"server = '{server}'")
    if epoch_start:
        conditions.append(f"block_time >= {epoch_start}")
    if epoch_end:
        conditions.append(f"block_time <= {epoch_end}")
    if len(conditions) > 0:
        sql += " WHERE "
        sql += " AND ".join(conditions)    
    sql += ";"

    try:
        CURSOR.execute(sql)
        CONN.commit()
    except Exception as e:
        logger.debug(e)
        CONN.rollback()



