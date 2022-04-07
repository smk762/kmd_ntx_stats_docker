#!/usr/bin/env python3
from lib_const import *
from lib_filter import *
from lib_db import CONN, CURSOR
from decorators import print_runtime


def select_from_notarised_tbl_where(
        season=None, server=None, epoch=None, chain=None,
        include_coins=None, exclude_coins=None,
        lowest_blocktime=None, highest_blocktime=None,
        not_season=None, not_server=None, not_epoch=None
    ):
    sql = f"SELECT * FROM notarised"
    sql = get_notarised_conditions_filter(
        sql, season=season, server=server, epoch=epoch, chain=chain,
        include_coins=include_coins, exclude_coins=exclude_coins,
        lowest_blocktime=lowest_blocktime, highest_blocktime=highest_blocktime,
        not_season=not_season, not_server=not_server, not_epoch=not_epoch
    )
    CURSOR.execute(sql)
    try:
        results = CURSOR.fetchall()
        return results
    except:
        return ()


@print_runtime
def get_notarised_servers(season=None):
    sql = "SELECT DISTINCT server FROM notarised"
    sql = get_notarised_conditions_filter(sql, season=season)
    CURSOR.execute(sql)
    results = CURSOR.fetchall()
    servers = sorted_list_set([i[0] for i in results])
    servers.sort()
    return servers


@print_runtime
def get_notarised_epochs(season=None, server=None):
    sql = "SELECT DISTINCT epoch FROM notarised"
    sql = get_notarised_conditions_filter(sql, season=season, server=server)
    CURSOR.execute(sql)
    results = CURSOR.fetchall()
    epochs = sorted_list_set([i[0] for i in results])
    epochs.sort()
    return epochs


@print_runtime
def get_notarised_server_epochs(season, server=None):
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
    sql = "SELECT DISTINCT server, epoch, chain FROM notarised"
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
    sql = "SELECT DISTINCT chain FROM notarised"
    sql = get_notarised_conditions_filter(sql, season=season, server=server, epoch=epoch)
    CURSOR.execute(sql)
    results = CURSOR.fetchall()
    coins = sorted_list_set([i[0] for i in results])
    coins.sort()
    return coins


@print_runtime
def get_official_ntx_results(
        season, group_by, server=None,
        epoch=None, coin=None, notary=None
    ):
    group_by = ", ".join(group_by)
    sql = f"SELECT {group_by}, \
            COALESCE(COUNT(*), 0), \
            COALESCE(SUM(score_value), 0) \
            FROM notarised "
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

    sql = "SELECT DISTINCT score_value FROM notarised"
    sql = get_notarised_conditions_filter(
        season=season, server=server, epoch=epoch,
        lowest_blocktime=lowest_blocktime,
        highest_blocktime=highest_blocktime
    )
    CURSOR.execute(sql)
    results = CURSOR.fetchall()
    scores = sorted_list_set([i[0] for i in results])   
    return scores


def get_coin_ntx_season_aggregates(season):
    sql = f"SELECT chain, MAX(block_height), \
                          MAX(block_time), \
                          COALESCE(COUNT(*), 0) \
           FROM notarised \
           WHERE season = '{season}' \
           AND epoch != 'Unofficial' \
           GROUP BY chain;"
    CURSOR.execute(sql)
    try:
        results = CURSOR.fetchall()
        return results
    except:
        return ()


def get_notarised_coin_date_aggregates(season, day):
    sql = f"SELECT chain, COALESCE(MAX(block_height), 0), \
                          COALESCE(MAX(block_time), 0), \
                          COALESCE(COUNT(*), 0) \
           FROM notarised \
           WHERE season = '{season}' \
           AND epoch != 'Unofficial' \
           AND DATE_TRUNC('day', block_datetime) = '{day}' \
           GROUP BY chain;"
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
    sql = f"SELECT chain, notaries \
           FROM notarised \
           WHERE season='{season}' \
           AND epoch != 'Unofficial' \
           AND DATE_TRUNC('day', block_datetime) = '{day}';"
    CURSOR.execute(sql)
    try:
        results = CURSOR.fetchall()
        return results
    except:
        return ()


def get_ntx_min_max(season, server=None, epoch=None, coin=None):
    sql = "SELECT MIN(block_height), MIN(block_time), \
                  MAX(block_height), MAX(block_time), \
                  COUNT(*) \
           FROM notarised"
    sql = get_notarised_conditions_filter(
        sql, season=season, server=server, epoch=epoch, chain=coin
    )

    CURSOR.execute(sql)
    return CURSOR.fetchone()


def get_ntx_scored(season, server, coin, lowest_blocktime, highest_blocktime):
    scored_list = []
    unscored_list = []

    sql = f"SELECT DISTINCT txid \
                    FROM notarised WHERE chain = '{coin}' \
                    AND season = '{season}' \
                    AND server = '{server}' \
                    AND block_time >= {lowest_blocktime} \
                    AND block_time <= {highest_blocktime} \
                    ;"
    CURSOR.execute(sql)
    scored_resp = CURSOR.fetchall()

    sql = f"SELECT DISTINCT txid \
                    FROM notarised WHERE chain = '{coin}' \
                    AND season = '{season}' \
                    AND server = '{server}' \
                    AND (block_time < {lowest_blocktime} \
                    OR block_time > {highest_blocktime}) \
                    ;"
    CURSOR.execute(sql)
    unscored_resp = CURSOR.fetchall()

    for item in scored_resp:
        scored_list.append(scored_resp[0])

    for item in unscored_resp:
        unscored_list.append(unscored_resp[0])

    return scored_list, unscored_list


def get_existing_notarised_txids(coin=None, season=None, server=None):

    logger.info("Getting existing TXIDs from [notarised]...")
    sql = f"SELECT DISTINCT txid from notarised"

    conditions = []
    if coin:
        conditions.append(f"chain = '{coin}'")
    if season:
        conditions.append(f"season = '{season}'")
    if server:
        conditions.append(f"server = '{server}'")
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

