#!/usr/bin/env python3
import lib_helper
from lib_const import *
from lib_query_ntx import *
from lib_filter import *
from decorators import print_runtime


def get_mined_date_aggregates(day):
    sql = "SELECT name, COUNT(*), SUM(value) FROM mined WHERE \
           DATE_TRUNC('day', block_datetime) = '"+str(day)+"' \
           GROUP BY name;"
    CURSOR.execute(sql)
    return helper.get_results_or_none(CURSOR)


def get_mined_year_aggregates(year):
    sql = "SELECT COUNT(*), SUM(value) FROM mined WHERE \
           DATE_PART('year', block_datetime) = '"+str(year)+"';"
    CURSOR.execute(sql)
    return helper.get_results_or_none(CURSOR)


def get_rewards_year_aggregates(year):
    sql = "SELECT COUNT(*), SUM(rewards_value) FROM rewards_tx WHERE \
           DATE_PART('year', block_datetime) = '"+str(year)+"';"
    CURSOR.execute(sql)
    return helper.get_results_or_none(CURSOR)


def get_mined_since_genesis():
    sql = "SELECT COUNT(*), SUM(value) FROM mined;"
    CURSOR.execute(sql)
    return helper.get_results_or_none(CURSOR)


def get_rewards_since_genesis():
    sql = "SELECT COUNT(*), SUM(rewards_value) FROM rewards_tx;"
    CURSOR.execute(sql)
    return helper.get_results_or_none(CURSOR)


def get_epochs(season=None, server=None, epoch=None):
    sql = "SELECT season, server, epoch, epoch_start, epoch_end, \
                    start_event, end_event, epoch_coins,  score_per_ntx \
                    FROM scoring_epochs"
    conditions = []
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

    resp = []
    try:
        CURSOR.execute(sql)
        results = CURSOR.fetchall()
        for item in results:
            resp.append({
                "season":item[0],
                "server":item[1],
                "epoch":item[2],
                "epoch_start":item[3],
                "epoch_end":item[4],
                "start_event":item[5],
                "end_event":item[6],
                "epoch_coins":item[7],
                'score_per_ntx':float(item[8])
            })
        if len(resp) == 1:
            return resp[0]
        return resp
        
    except Exception as e:
        logger.error(f"Error in get_epochs: {e}")
        return []


def select_from_table(table, cols, conditions=None):
    sql = "SELECT "+cols+" FROM "+table
    if conditions:
        sql = sql+" WHERE "+conditions
    sql = sql+";"
    CURSOR.execute(sql)
    return helper.get_results_or_none(CURSOR)


def get_season_mined_counts(season):
    end_time = SEASONS_INFO[season]['end_time']
    if lib_helper.is_postseason():
        if 'post_season_end_time' in SEASONS_INFO[season]:
            end_time = SEASONS_INFO[season]['post_season_end_time']

    sql = "SELECT name, address, COUNT(*), SUM(value), MAX(value), max(block_time), \
           max(block_height) FROM mined WHERE block_time >= "+str(SEASONS_INFO[season]['start_time'])+" \
           AND block_time <= "+str(end_time)+" GROUP BY name, address;"

    CURSOR.execute(sql)
    results = CURSOR.fetchall()
    if len(results) > 0:
        return results
    else:
        return ()


def get_max_value_mined_txid(max_value, season=None):
    sql = f"SELECT txid FROM mined WHERE value = {max_value}"
    if season:
        sql += f" AND season = '{season}'"
    sql += ";"
    CURSOR.execute(sql)
    results = CURSOR.fetchone()
    try:
        if results:
            if len(results) > 0:
                return results[0]
    except Exception as e:
        #print(sql)
        print(e)

    return ''


def get_all_coins():
    coins = []
    CURSOR.execute("SELECT DISTINCT coin FROM coins;")
    try:
        results = CURSOR.fetchall()
        for result in results:
            coins.append(result[0])
        coins.sort()
        coins.reverse()
        
    except Exception as e:
        logger.warning(f"No [get_all_coins] results? {e}")

    return coins


def get_supply_blocks():
    blocks = []
    CURSOR.execute("SELECT DISTINCT block_height FROM kmd_supply;")
    try:
        results = CURSOR.fetchall()
        for result in results:
            blocks.append(result[0])
        blocks.sort()
        blocks.reverse()
        
    except Exception as e:
        logger.warning(f"No [get_supply_blocks] results? {e}")

    return blocks


@print_runtime
def get_notary_last_ntx():
    sql = f"SELECT notary, coin, kmd_ntx_blockheight from notary_last_ntx;"
    CURSOR.execute(sql)
    last_ntx = CURSOR.fetchall()
    notary_last_ntx = {}
    for item in last_ntx:
        if item[0] not in notary_last_ntx:
            notary_last_ntx.update({item[0]: {}})
        notary_last_ntx[item[0]].update({
                item[1]: item[2]
        })
    return notary_last_ntx


@print_runtime
def get_coin_last_ntx():
    sql = f"SELECT coin, kmd_ntx_blockheight from coin_last_ntx;"
    CURSOR.execute(sql)
    last_ntx = CURSOR.fetchall()
    coin_last_ntx = {}
    for item in last_ntx:
        coin = item[0]
        block_height = item[1]
        coin_last_ntx.update({coin: block_height})
    return coin_last_ntx


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


def get_existing_nn_ltc_txids(address=None, category=None, season=None, notary=None):
    recorded_txids = []
    sql = f"SELECT DISTINCT txid from nn_ltc_tx"
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



def get_reward_blocks():
    resp = []
    CURSOR.execute("SELECT DISTINCT block_height FROM rewards_tx;")
    try:
        results = CURSOR.fetchall()
        for result in results:
            resp.append(result[0])
        resp.sort()
        resp.reverse()
        
    except Exception as e:
        logger.warning(f"No [get_reward_blocks] results? {e}")

    return resp


def get_reward_txids():
    resp = []
    CURSOR.execute("SELECT DISTINCT txid FROM rewards_tx;")
    try:
        results = CURSOR.fetchall()
        for result in results:
            resp.append(result[0])
        resp.sort()
        resp.reverse()
        
    except Exception as e:
        logger.warning(f"No [get_reward_txids] results? {e}")

    return resp


def get_reward_input_addresses():
    resp = []
    CURSOR.execute("SELECT DISTINCT address FROM rewards_tx;")
    try:
        results = CURSOR.fetchall()
        for result in results:
            resp += result[0]
        resp = list(set(resp))
        resp.sort()
        
    except Exception as e:
        logger.warning(f"No [get_reward_input_addresses] results? {e}")

    return resp
