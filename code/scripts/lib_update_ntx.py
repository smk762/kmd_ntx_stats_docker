#!/usr/bin/env python3
import os
import json
from psycopg2.extras import execute_values
from lib_const import *



def update_ntx_row(row_data):
    sql = f"INSERT INTO notarised (chain, block_height, \
                                block_time, block_datetime, block_hash, \
                                notaries, notary_addresses, ac_ntx_blockhash, ac_ntx_height, \
                                txid, opret, season, server, scored, score_value, epoch) \
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
                ON CONFLICT ON CONSTRAINT unique_txid DO UPDATE SET \
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


def update_ntx_row_epoch_scores(row_data):
    sql = f"UPDATE notarised SET \
            scored='{scored}', score_value={score_value} \
            WHERE season='{season}' AND server='{server}' \
            AND epoch='{epoch}';"
    try:
        CURSOR.execute(sql, row_data)
        CONN.commit()
    except Exception as e:
        if str(e).find('duplicate') == -1:
            logger.debug(e)
            logger.debug(row_data)
        CONN.rollback()



def update_server_notarised_tbl(old_server, server):
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
    sql = f"UPDATE notarised SET \
          server='{server}' \
          WHERE season='{season}'\
          AND chain='{coin}';"
    try:
        CURSOR.execute(sql)
        CONN.commit()
        print(f"{old_server} reclassed as {server}")
    except Exception as e:
        logger.debug(e)
        CONN.rollback()

def update_unofficial_coin_notarised_tbl(season, coin):
    sql = f"UPDATE notarised SET \
          season='Unofficial', server='Unofficial', epoch='Unofficial' \
          WHERE season='{season}'\
          AND chain='{coin}';"
    try:
        CURSOR.execute(sql)
        CONN.commit()
        print(f"Unofficial coin {coin} updated for {season}")
    except Exception as e:
        logger.debug(e)
        CONN.rollback()

def update_coin_score_notarised_tbl(coin, score_value, scored, min_time=None, max_time=None, season=None, server=None, epoch=None):
    sql = f"UPDATE notarised SET scored={scored}, score_value={score_value}"
    conditions = []
    if coin:
        conditions.append(f"chain = '{coin}'")
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
    if addresses:
        sql = f"UPDATE notarised SET \
              notary_addresses=ARRAY{addresses},  \
              season='{season}', server='{server}' \
              WHERE txid='{txid}';"
    else:
        sql = f"UPDATE notarised SET \
              season='{season}', server='{server}' \
              WHERE txid='{txid}';"

    print(sql)
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


def delete_from_notarised_tbl_where(
        season=None, server=None, epoch=None, chain=None,
        include_coins=None, exclude_coins=None
    ):
    sql = f"DELETE FROM notarised"
    sql = get_notarised_conditions_filter(
        sql, season=season, server=server, epoch=epoch,
        chain=chain, include_coins=include_coins,
        exclude_coins=exclude_coins
    )
    CURSOR.execute()
    CONN.commit()



def update_season_notarised_coin_row(row_data):
    sql = "INSERT INTO notarised_chain_season \
         (chain, ntx_count, block_height, kmd_ntx_blockhash,\
          kmd_ntx_txid, kmd_ntx_blocktime, opret, ac_ntx_blockhash, \
          ac_ntx_height, ac_block_height, ntx_lag, season, server) \
          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
          ON CONFLICT ON CONSTRAINT unique_notarised_chain_season_server DO UPDATE \
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
        total_ntx_count, chain_ntx_counts, season_score, \
        chain_ntx_pct, time_stamp, season) \
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
        ON CONFLICT ON CONSTRAINT unique_notary_season DO UPDATE SET \
        btc_count="+str(row_data[1])+", antara_count="+str(row_data[2])+", \
        third_party_count="+str(row_data[3])+", other_count="+str(row_data[4])+", \
        total_ntx_count="+str(row_data[5])+", chain_ntx_counts='"+str(row_data[6])+"', \
        season_score='"+str(row_data[7])+"', chain_ntx_pct='"+str(row_data[8])+"', \
        time_stamp="+str(row_data[9])+";"
    CURSOR.execute(sql, row_data)
    CONN.commit()


def update_daily_notarised_coin_row(row_data):
    sql = f"INSERT INTO notarised_chain_daily \
          (season, server, chain, ntx_count, notarised_date) \
          VALUES (%s, %s, %s, %s, %s) \
          ON CONFLICT ON CONSTRAINT unique_notarised_chain_daily DO UPDATE \
          SET ntx_count={row_data[3]};"
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


def update_last_ntx_row(row_data):
    try:
        sql = "INSERT INTO last_notarised \
            (notary, chain, txid, block_height, \
            block_time, season, server) VALUES (%s, %s, %s, %s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_notary_season_server_chain DO UPDATE SET \
            txid='"+str(row_data[2])+"', \
            block_height='"+str(row_data[3])+"', \
            block_time='"+str(row_data[4])+"', \
            season='"+str(row_data[5])+"', \
            server='"+str(row_data[6])+"';"
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


def update_notarised_epoch(actual_epoch, season=None, server=None, coin=None, txid=None):
    sql = f"UPDATE notarised SET epoch='{actual_epoch}'"
    conditions = []
    if season:
        conditions.append(f"season = '{season}'")
    if server:
        conditions.append(f"server = '{server}'")
    if coin:
        conditions.append(f"chain = '{coin}'")
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


def update_notarised_epoch_scores(coin, season, server, epoch, epoch_start, epoch_end, score_per_ntx, scored):
    sql = f"UPDATE notarised SET epoch='{epoch}', score_value={score_per_ntx}, scored={scored}"
    conditions = []
    if coin:
        conditions.append(f"chain = '{coin}'")
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



