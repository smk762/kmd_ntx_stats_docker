#!/usr/bin/env python3
from lib_const import *
from lib_filter import *
from lib_db import connect_db
import lib_helper as helper
from decorators import print_runtime


def select_from_notarised_tbl_where(
        season=None, server=None, epoch=None, coin=None,
        include_coins=None, exclude_coins=None,
        lowest_blocktime=None, highest_blocktime=None,
        lowest_blockheight=None, highest_blockheight=None,
        lowest_ac_blockheight=None, highest_ac_blockheight=None,
        not_season=None, not_server=None, not_epoch=None, order_by=None
    ):
    sql = f"SELECT * FROM notarised"
    sql = get_notarised_conditions_filter(
        sql, season=season, server=server, epoch=epoch, coin=coin,
        include_coins=include_coins, exclude_coins=exclude_coins,
        lowest_blocktime=lowest_blocktime, highest_blocktime=highest_blocktime,
        lowest_blockheight=lowest_blockheight, highest_blockheight=highest_blockheight,
        lowest_ac_blockheight=lowest_ac_blockheight, highest_ac_blockheight=highest_ac_blockheight,
        not_season=not_season, not_server=not_server, not_epoch=not_epoch, order_by=order_by
    )
    CONN = connect_db()
    CURSOR = CONN.cursor()
    CURSOR.execute(sql)
    return helper.get_results_or_none(CURSOR)

@print_runtime
def get_notarised_servers(season=None):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    sql = "SELECT DISTINCT server FROM notarised"
    sql = get_notarised_conditions_filter(sql, season=season)
    CURSOR.execute(sql)
    results = CURSOR.fetchall()
    servers = sorted_list_set([i[0] for i in results])
    servers.sort()
    return servers


@print_runtime
def get_notarised_epochs(season=None, server=None):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    sql = "SELECT DISTINCT epoch FROM notarised"
    sql = get_notarised_conditions_filter(sql, season=season, server=server)
    CURSOR.execute(sql)
    results = CURSOR.fetchall()
    epochs = sorted_list_set([i[0] for i in results])
    epochs.sort()
    return epochs


@print_runtime
def get_notarised_server_epochs(season, server=None):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    sql = "SELECT DISTINCT server, epoch FROM notarised"
    sql = get_notarised_conditions_filter(
        sql, season=season, server=server
    )
    CURSOR.execute(sql)
    results = CURSOR.fetchall()
    resp = {}
    for item in results:
        if item[0] not in resp:
            resp.update({item[0]: []})
        resp[item[0]].append(item[1])
    return resp


@print_runtime
def get_notarised_server_epoch_coins(season, server=None, epoch=None):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    sql = "SELECT DISTINCT server, epoch, coin FROM notarised"
    sql = get_notarised_conditions_filter(
        sql, season=season, server=server, epoch=epoch
    )
    CURSOR.execute(sql)
    results = CURSOR.fetchall()
    resp = {}
    for item in results:
        server = item[0]
        epoch = item[1]
        coin = item[2]
        if server not in resp:
            resp.update({server: {}})
        if epoch not in resp[server]:
            resp[server].update({epoch: []})
        resp[server][epoch].append(coin)
    for server in resp:
        for epoch in resp[server]:
            resp[server][epoch].sort()
    return resp


@print_runtime
def get_notarised_coins(season=None, server=None, epoch=None):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    sql = "SELECT DISTINCT coin FROM notarised"
    sql = get_notarised_conditions_filter(sql, season=season, server=server, epoch=epoch)
    CURSOR.execute(sql)
    results = CURSOR.fetchall()
    coins = sorted_list_set([i[0] for i in results])
    coins.sort()
    return coins


def get_notarised_data_for_season(season):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    sql = f"SELECT coin, block_height, block_time, block_datetime, \
            block_hash, notaries, notary_addresses, ac_ntx_blockhash, \
            ac_ntx_height, txid, opret, season,\
            server, epoch, score_value, scored \
            FROM notarised"
    where = []
    if season:
        where.append(f"season = '{season}'")

    if len(where) > 0:
        sql += " WHERE "
        sql += " AND ".join(where)
    sql += " ORDER BY block_time asc;"

    CURSOR.execute(sql)
    return CURSOR.fetchall()


def get_official_ntx_results(
        season, group_by, server=None,
        epoch=None, coin=None, notary=None
    ):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    group_by = ", ".join(group_by)
    sql = f"SELECT {group_by}, \
            COALESCE(COUNT(*), 0), \
            COALESCE(SUM(score_value), 0) \
            FROM notarised"
    sql = get_notarised_conditions_filter(sql, 
        season=season, group_by=group_by, server=server,
        epoch=epoch, coin=coin, notary=notary
    )
    CURSOR.execute(sql)
    results = CURSOR.fetchall()
    return results


def get_notarised_server_epoch_scores(season, server=None, epoch=None):
    sql = "SELECT DISTINCT server, epoch, score_value FROM notarised"
    sql = get_notarised_conditions_filter(
        sql, season=season, server=server, epoch=epoch
    )
    CONN = connect_db()
    CURSOR = CONN.cursor()
    CURSOR.execute(sql)
    results = CURSOR.fetchall()
    resp = {}
    for item in results:
        server = item[0]
        epoch = item[1]
        score = item[2]
        if server not in resp:
            resp.update({server: {}})
        if epoch not in resp[server]:
            resp[server].update({epoch: []})
        resp[server][epoch].append(score)
    return resp


def get_notarised_coin_epoch_scores(
        season=None, server=None, epoch=None,
        lowest_blocktime=None, highest_blocktime=None
    ):

    CONN = connect_db()
    CURSOR = CONN.cursor()
    sql = "SELECT DISTINCT score_value FROM notarised"
    sql = get_notarised_conditions_filter(
        sql, season=season, server=server,
        epoch=epoch, lowest_blocktime=lowest_blocktime,
        highest_blocktime=highest_blocktime
    )
    CURSOR.execute(sql)
    results = CURSOR.fetchall()
    scores = sorted_list_set([i[0] for i in results])   
    return scores


@print_runtime
def get_notarised_last_data_by_coin():
    sql = f"SELECT coin, MAX(block_height), \
                MAX(block_time), COALESCE(COUNT(*), 0) \
                FROM notarised WHERE \
                server != 'Unofficial' GROUP BY coin;"
    CONN = connect_db()
    CURSOR = CONN.cursor()
    CURSOR.execute(sql)
    last_ntx = CURSOR.fetchall()
    coin_last_ntx = {}
    for item in last_ntx:
        coin_last_ntx.update({
            item[0]: {
                "block_height": item[1],
                "block_time": item[2],
                "ntx_count": item[3]
            }
        })
    return coin_last_ntx


def get_notarised_coin_date_aggregates(season, day):
    sql = f"SELECT coin, COALESCE(MAX(block_height), 0), \
                          COALESCE(MAX(block_time), 0), \
                          COALESCE(COUNT(*), 0) \
           FROM notarised \
           WHERE season = '{season}' AND epoch != 'Unofficial' \
           AND DATE_TRUNC('day', block_datetime) = '{day}' \
           GROUP BY coin;"
    CONN = connect_db()
    CURSOR = CONN.cursor()
    CURSOR.execute(sql)
    try:
        results = CURSOR.fetchall()
        return results
    except Exception as e:
        print(e)
        print(sql)
        logger.warning(f"No get_notarised_coin_date_aggregates results for {day} {season}")
        return ()


def get_notarised_for_day(season, day):
    sql = f"SELECT coin, notaries \
           FROM notarised WHERE season='{season}' \
           AND epoch != 'Unofficial' \
           AND DATE_TRUNC('day', block_datetime) = '{day}';"
    CONN = connect_db()
    CURSOR = CONN.cursor()
    CURSOR.execute(sql)
    return helper.get_results_or_none(CURSOR)


def get_ntx_min_max(season, server=None, epoch=None, coin=None):
    sql = "SELECT MIN(block_height), MIN(block_time), \
                  MAX(block_height), MAX(block_time), COUNT(*) \
           FROM notarised"
    sql = get_notarised_conditions_filter(
        sql, season=season, server=server, epoch=epoch, coin=coin
    )
    CONN = connect_db()
    CURSOR = CONN.cursor()

    CURSOR.execute(sql)
    return CURSOR.fetchone()


def get_notary_coin_last_nota(season, notary):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    sql = "SELECT coin, MAX(block_height), COUNT(*) \
           FROM notarised  WHERE season = '"+str(season)+"' \
           AND server != 'Unofficial' \
           AND notaries && "+"'{\""+notary+"\"}' GROUP BY coin;"; 
    
    notary_last_ntx = {}
    try:
        CURSOR.execute(sql)
        last_ntx = CURSOR.fetchall()
        for item in last_ntx:
            notary_last_ntx.update({
                item[0]: {
                    "block_height": item[1],
                    "ntx_count": item[2]
                }
            })
    except:
        logger.info("#############")
        logger.info(sql)
        logger.info(f"No results for {notary}")
        logger.info("#############")
    return notary_last_ntx


def get_ntx_scored(season, server, coin, lowest_blocktime, highest_blocktime):
    CONN = connect_db()
    CURSOR = CONN.cursor()
    scored_list = []
    unscored_list = []

    sql = f"SELECT DISTINCT txid \
                    FROM notarised WHERE coin = '{coin}' \
                    AND season = '{season}' \
                    AND server = '{server}';"
    CURSOR.execute(sql)
    in_season_server_resp = CURSOR.fetchall()

    sql = f"SELECT DISTINCT txid \
                    FROM notarised WHERE coin = '{coin}' \
                    AND season = '{season}' \
                    AND server = '{server}' \
                    AND block_time >= {lowest_blocktime} \
                    AND block_time <= {highest_blocktime} \
                    ;"
    CURSOR.execute(sql)
    scored_resp = CURSOR.fetchall()

    sql = f"SELECT DISTINCT txid \
                    FROM notarised WHERE coin = '{coin}' \
                    AND season = '{season}' \
                    AND server = '{server}' \
                    AND (block_time < {lowest_blocktime} \
                    OR block_time > {highest_blocktime}) \
                    ;"
    CURSOR.execute(sql)
    unscored_resp = CURSOR.fetchall()

    sql = f"SELECT DISTINCT txid \
                    FROM notarised WHERE coin = '{coin}' \
                    AND season = '{season}' \
                    AND server = 'Unofficial';"
    CURSOR.execute(sql)
    unofficial_resp = CURSOR.fetchall()

    print(f"------------------------------------")
    print(f"Coin: {coin}")
    print(f"Season: {season}")
    print(f"Server: {server}")
    print(f"lowest_blocktime: {lowest_blocktime}")
    print(f"highest_blocktime: {highest_blocktime}")
    print(f"in_season_server_resp: {len(in_season_server_resp)}")
    print(f"scored_resp: {len(scored_resp)}")
    print(f"unscored_resp: {len(unscored_resp)}")
    print(f"unofficial_resp: {len(unofficial_resp)}")
    print(f"------------------------------------")

    for item in scored_resp:
        scored_list.append(scored_resp[0])

    for item in unscored_resp:
        unscored_list.append(unscored_resp[0])

    return scored_list, unscored_list


def get_existing_notarised_txids(season=None, server=None, coin=None):
    CONN = connect_db()
    CURSOR = CONN.cursor()

    logger.info("Getting existing TXIDs from [notarised]...")
    sql = f"SELECT DISTINCT txid from notarised"

    conditions = []
    if season:
        conditions.append(f"season = '{season}'")
    if server:
        conditions.append(f"server = '{server}'")
    if coin:
        conditions.append(f"coin = '{coin}'")
    if len(conditions) > 0:
        sql += " WHERE "
        sql += " AND ".join(conditions)    
    sql += ";"

    CURSOR.execute(sql)
    existing_txids = CURSOR.fetchall()

    recorded_txids = []
    for txid in existing_txids:
        recorded_txids.append(txid[0])
    return recorded_txids


def validate_notarised_epoch_timespan(season, server, epoch):
    min_max = get_ntx_min_max(season, server, epoch)
    min_time = min_max[1]
    max_time = min_max[3]

