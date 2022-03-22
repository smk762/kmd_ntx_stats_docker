#!/usr/bin/env python3
from lib_const import *
from lib_helper import is_postseason
from decorators import print_runtime

def get_latest_chain_ntx_info(chain, height):
    sql = f"SELECT ac_ntx_blockhash, ac_ntx_height, opret, block_hash, txid \
           FROM notarised WHERE chain = '{chain}' AND block_height = {height};"
    CURSOR.execute(sql)
    chains_resp = CURSOR.fetchone()
    return chains_resp


def get_latest_season_chain_ntx(season):
    sql = f"SELECT chain, \
            MAX(block_height), \
            MAX(block_time), \
            COUNT(*) \
            FROM notarised \
            WHERE season = '{season}' \
            GROUP BY chain;"
    CURSOR.execute(sql)
    try:
        results = CURSOR.fetchall()
        return results
    except:
        return ()


def get_official_ntx_results(season, group_by, server=None, epoch=None, chain=None, notary=None):
    group_by = ", ".join(group_by)
    sql = f"SELECT {group_by}, \
            COALESCE(COUNT(*), 0), \
            COALESCE(SUM(score_value), 0) \
            FROM notarised "

    conditions = []
    if season:
        conditions.append(f"season = '{season}'")
    if server:
        conditions.append(f"server = '{server}'")
    if epoch:
        conditions.append(f"epoch = '{epoch}'")
    if chain:
        conditions.append(f"chain = '{chain}'")
    if notary:
        conditions.append(f"'{notary}' = ANY (notaries)")
    if len(conditions) > 0:
        sql += " WHERE "
        sql += " AND ".join(conditions)    

    sql += f" GROUP BY {group_by};"
    CURSOR.execute(sql)
    try:
        results = CURSOR.fetchall()
        return results
    except:
        return ()


def get_chain_ntx_season_aggregates(season):
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


def get_notarised_chain_date_aggregates(season, day):
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
        logger.warning(f"No get_notarised_chain_date_aggregates results for {day} {season}")
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


def get_mined_date_aggregates(day):
    sql = "SELECT name, COUNT(*), SUM(value) FROM mined WHERE \
           DATE_TRUNC('day', block_datetime) = '"+str(day)+"' \
           GROUP BY name;"
    CURSOR.execute(sql)
    try:
        results = CURSOR.fetchall()
        return results
    except:
        return ()

    CURSOR.execute(sql)
    try:
        results = CURSOR.fetchall()
        return results
    except:
        return ()


def get_epochs(season=None, server=None):
    sql = "SELECT season, server, epoch, epoch_start, epoch_end, \
                    start_event, end_event,  epoch_chains,  score_per_ntx \
                    FROM scoring_epochs"
    conditions = []
    if season:
        conditions.append(f"season = '{season}'")
    if server:
        conditions.append(f"server = '{server}'")
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
                "epoch_chains":item[7],
                'score_per_ntx':item[8]
            })

        return resp
        
    except Exception as e:
        logger.error(f"Error in get_epochs: {e}")
        return []


def get_epochs_list(season=None, server=None):
    sql = "SELECT epoch FROM scoring_epochs"
    conditions = []
    if season:
        conditions.append(f"season = '{season}'")
    if server:
        conditions.append(f"server = '{server}'")
    if len(conditions) > 0:
        sql += " WHERE "
        sql += " AND ".join(conditions)    
    sql += ";"

    resp = []
    try:
        CURSOR.execute(sql)
        results = CURSOR.fetchall()
        for item in results:
            resp.append(item[0])
        return resp
        
    except Exception as e:
        logger.error(f"Error in get_epochs_list: {e}")
        return []


def get_ntx_for_season(season):
    sql = "SELECT chain, notaries \
           FROM notarised WHERE \
           season = '"+str(season)+"';"
    CURSOR.execute(sql)
    try:
        results = CURSOR.fetchall()
        return results
    except:
        return ()


def get_mined_for_season(season):
    sql = "SELECT * \
           FROM mined WHERE \
           season = '"+str(season)+"';"
    CURSOR.execute(sql)
    try:
        results = CURSOR.fetchall()
        return results
    except:
        return ()

def get_mined_for_day(day):
    sql = "SELECT * \
           FROM mined WHERE \
           DATE_TRUNC('day', block_datetime) = '"+str(day)+"';"
    CURSOR.execute(sql)
    try:
        results = CURSOR.fetchall()
        return results
    except:
        return ()


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
    results = CURSOR.fetchall()
    if len(results) > 0:
        return results
    else:
        return ()


def get_tenure_chains(season=None, server=None):
    sql = "SELECT DISTINCT chain from notarised_tenure"
    conditions = []
    if season:
        conditions.append(f"season = '{season}'")
    if server:
        conditions.append(f"server = '{server}'")
    if len(conditions) > 0:
        sql += " WHERE "
        sql += " AND ".join(conditions)    
    sql += ";"
    CURSOR.execute(sql)
    results = CURSOR.fetchall()
    resp = []
    for chain in results:
        resp.append(chain[0])
    resp.sort()
    return resp


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


def get_season_mined_counts(season):
    end_time = SEASONS_INFO[season]['end_time']
    if is_postseason():
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
        sql += f"AND season = '{season}'"
    sql += ";"
    CURSOR.execute(sql)
    results = CURSOR.fetchone()
    if len(results) > 0:
        return results[0]
    else:
        return ''


def season_server_chain_has_ntx(season, chain, server):
    CURSOR.execute("SELECT COUNT(txid) \
                    FROM notarised WHERE chain = '"+chain+"' \
                    AND season = '"+season+"' \
                    AND server = '"+server+"';")
    if CURSOR.fetchone() == 0:
        return False
    return True


def get_ntx_min_max(season, chain, server):
    CURSOR.execute("SELECT MAX(block_height), MAX(block_time), \
                    MIN(block_height), MIN(block_time), COUNT(*) \
                    FROM notarised WHERE chain = '"+chain+"' \
                    AND season = '"+season+"' \
                    AND server = '"+server+"';")
    return CURSOR.fetchone()


def get_ntx_scored(season, chain, lowest_block_time, highest_block_time, server):
    scored_list = []
    unscored_list = []

    sql = f"SELECT DISTINCT txid \
                    FROM notarised WHERE chain = '{chain}' \
                    AND season = '{season}' \
                    AND server = '{server}' \
                    AND block_time >= {lowest_block_time} \
                    AND block_time <= {highest_block_time} \
                    ;"
                    
    CURSOR.execute(sql)
    scored_resp = CURSOR.fetchall()

    sql = f"SELECT DISTINCT txid \
                    FROM notarised WHERE chain = '{chain}' \
                    AND season = '{season}' \
                    AND server = '{server}' \
                    AND (block_time < {lowest_block_time} \
                    OR block_time > {highest_block_time}) \
                    ;"

    CURSOR.execute(sql)
    unscored_resp = CURSOR.fetchall()

    for item in scored_resp:
        scored_list.append(scored_resp[0])

    for item in unscored_resp:
        unscored_list.append(unscored_resp[0])

    return scored_list, unscored_list


@print_runtime
def get_notarised_chains(season=None, server=None, epoch=None):

    sql = "SELECT DISTINCT chain FROM notarised"
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

    CURSOR.execute(sql)

    chains = []
    try:
        chain_results = CURSOR.fetchall()
        for result in chain_results:
            chains.append(result[0])
        chains.sort()
        
    except Exception as e:
        logger.warning(f"No [get_notarised_chains] results for {season} {server} {epoch} | {sql}? {e}")

    return chains


@print_runtime
def get_notarised_epochs(season=None, server=None):

    sql = "SELECT DISTINCT epoch FROM notarised"
    conditions = []
    if season:
        conditions.append(f"season = '{season}'")
    if server:
        conditions.append(f"server = '{server}'")

    if len(conditions) > 0:
        sql += " WHERE "
        sql += " AND ".join(conditions)    
    sql += ";"

    CURSOR.execute(sql)

    epochs = []

    try:
        epoch_results = CURSOR.fetchall()
        for result in epoch_results:
            epochs.append(result[0])
        epochs.sort()
        
    except Exception as e:
        logger.warning(f"No [get_notarised_epochs] results for {season} {server}| {sql}? {e}")

    return epochs


@print_runtime
def get_notarised_seasons(chain=None):

    sql = "SELECT DISTINCT season FROM notarised"

    conditions = []

    if chain:
        conditions.append(f"chain = '{chain}'")
    else:
        resp = list(SEASONS_INFO.keys())
        resp.reverse()
        return resp

    if len(conditions) > 0:
        sql += " WHERE "
        sql += " AND ".join(conditions)    
    sql += ";"

    CURSOR.execute(sql)

    seasons = []

    try:
        season_results = CURSOR.fetchall()
        for result in season_results:
            seasons.append(result[0])
        seasons.sort()
        seasons.reverse()
        
    except Exception as e:
        logger.warning(f"No [get_notarised_seasons] results for {chain}| {sql}? {e}")

    return seasons


@print_runtime
def get_notarised_servers(season=None):

    sql = "SELECT DISTINCT server FROM notarised"
    conditions = []
    if season:
        conditions.append(f"season = '{season}'")

    if len(conditions) > 0:
        sql += " WHERE "
        sql += " AND ".join(conditions)    
    sql += ";"

    CURSOR.execute(sql)

    servers = []

    try:
        servers_results = CURSOR.fetchall()
        for result in servers_results:
            servers.append(result[0])
        servers.sort()
        
    except Exception as e:
        logger.warning(f"No [get_notarised_servers] results for {season} | {sql}? {e}")

    return servers


def get_all_coins():
    coins = []
    CURSOR.execute("SELECT DISTINCT chain FROM coins;")
    try:
        results = CURSOR.fetchall()
        for result in results:
            coins.append(result[0])
        coins.sort()
        coins.reverse()
        
    except Exception as e:
        logger.warning(f"No [get_all_coins] results? {e}")

    return coins


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


def get_season_last_ntx(season):
    # Get chain and time of last ntx
    sql = "SELECT notary, chain, block_height from last_notarised"
    if season:
        sql += f" WHERE season='{season}'"
    sql += ";"
    CURSOR.execute(sql)
    last_ntx = CURSOR.fetchall()
    season_last_ntx = {}
    for item in last_ntx:
        notary = item[0]
        chain = item[1]
        block_height = item[2]
        if notary not in season_last_ntx:
            season_last_ntx.update({notary:{}})
        season_last_ntx[notary].update({chain:block_height})
    return season_last_ntx


def get_existing_notarised_txids(chain=None, season=None, server=None):

    logger.info("Getting existing TXIDs from [notarised]...")
    sql = f"SELECT DISTINCT txid from notarised"

    conditions = []
    if chain:
        conditions.append(f"chain = '{chain}'")
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


def get_distinct_col_vals_from_table(table, column, conditions=None):
    logger.info(f"Getting DISTINCT [{column}] values from [{table}] {conditions}...")
    sql = f"SELECT DISTINCT {column} from {table}"
    if conditions:
        sql += f" {conditions}"
    sql += ";"

    CURSOR.execute(sql)
    results = CURSOR.fetchall()

    distinct_values = []
    for item in results:
        distinct_values.append(item[0])
    distinct_values.sort()
    return distinct_values


def get_season_ntx_sum_count(season, server, epoch, chain):
    end_time = SEASONS_INFO[season]['end_time']
    if is_postseason():
        if 'post_season_end_time' in SEASONS_INFO[season]:
            end_time = SEASONS_INFO[season]['post_season_end_time']

    sql = "SELECT server, epoch, chain, COUNT(*), SUM(score_value) \
            FROM notarised WHERE block_time >= "+str(SEASONS_INFO[season]['start_time'])+" \
           AND block_time <= "+str(end_time)+" \
           AND season = '"+str(season)+"' \
           GROUP BY server, epoch, chain;"

    CURSOR.execute(sql)
    results = CURSOR.fetchall()
    if len(results) > 0:
        return results
    else:
        return ()


def get_table_list():
    sql = "SELECT * FROM pg_catalog.pg_tables \
            WHERE schemaname != 'information_schema' \
            AND schemaname != 'pg_catalog';"

    CURSOR.execute(sql)
    print(CURSOR.fetchall())
