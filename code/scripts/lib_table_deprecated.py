

### UNUSED 


# Unused, prefer SEASONS_INFO.keys()
@print_runtime
def get_notarised_seasons(coin=None):
    sql = "SELECT DISTINCT season FROM notarised"
    sql = get_notarised_conditions_filter(sql, chain=coin)
    CURSOR.execute(sql)
    results = CURSOR.fetchall()
    seasons = sorted_list_set([i[0] for i in results])
    seasons.sort()
    return seasons


def get_latest_coin_ntx_info(coin, height):
    sql = f"SELECT ac_ntx_blockhash, ac_ntx_height, opret, block_hash, txid \
           FROM notarised WHERE chain = '{coin}' AND block_height = {height};"
    CURSOR.execute(sql)
    coins_resp = CURSOR.fetchone()
    return coins_resp


def get_latest_season_coin_ntx(season):
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


def get_tenure_coins(season=None, server=None):
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
    for row in results:
        resp.append(row[0])
    resp.sort()
    return resp


def season_server_coin_has_ntx(season, coin, server):
    CURSOR.execute("SELECT COUNT(txid) \
                    FROM notarised WHERE chain = '"+coin+"' \
                    AND season = '"+season+"' \
                    AND server = '"+server+"';")
    if CURSOR.fetchone() == 0:
        return False
    return True


def get_season_ntx_sum_count(season, server, epoch, coin):
    end_time = SEASONS_INFO[season]['end_time']
    if lib_helper.is_postseason():
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

### UNUSED 

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


def get_table_list():
    sql = "SELECT * FROM pg_catalog.pg_tables \
            WHERE schemaname != 'information_schema' \
            AND schemaname != 'pg_catalog';"

    CURSOR.execute(sql)
    print(CURSOR.fetchall())


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


def get_min_from_table(table, col):
    sql = "SELECT MIN("+col+") FROM "+table
    CURSOR.execute(sql)
    return CURSOR.fetchone()[0]


def get_max_from_table(table, col):
    sql = "SELECT MAX("+col+") FROM "+table
    CURSOR.execute(sql)
    return CURSOR.fetchone()[0]


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

