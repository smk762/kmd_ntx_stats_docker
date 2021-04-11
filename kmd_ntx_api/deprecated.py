# Deprecated by get_dpow_coins_list() so season removed coins are included.
def get_active_dpow_coins():
    dpow_chains = coins.objects.filter(dpow_active=1).values('chain', 'dpow')
    chains_list = []
    for item in dpow_chains:
        if item['chain'] not in chains_list:
            chains_list.append(item['chain'])
    chains_list.sort()
    return chains_list

def btc_ntx_all(request):
    season = get_season()
    btc_ntx = get_notarised_data(season, "BTC").values()

    context = {
        "sidebar_links":get_sidebar_links(season),
        "eco_data_link":get_eco_data_link(),
        "explorers":get_explorers(),
        "btc_ntx":btc_ntx,
        "season":season.replace("_"," ")
    }

    return render(request, 'btc_ntx_all.html', context)
    
# TODO: Unassigned - is this a duplicate?
def get_btc_split_stats(address):
    resp = {}
    filter_kwargs = {}
    data = get_nn_btc_tx_data(None, None, "Split or Consolidate", address)
    sum_fees = data.annotate(Sum("fees"))
    avg_split_size = 0
    for item in data:        
        address = item['address']

        if address not in resp:
            resp.update({address:[]})
        resp[address].append(item)

    return wrap_api(resp)

def get_low_balance_tooltip(low_balances, ignore_chains):
    low_balances_dict = low_balances[0]
    low_balance_count = low_balances[1]
    sufficient_balance_count = low_balances[2]
    low_balances_pct = round(sufficient_balance_count/(low_balance_count+sufficient_balance_count)*100,2)
    low_balances_tooltip = "<h4 class='kmd_teal'>"+str(sufficient_balance_count)+"/"+str(low_balance_count+sufficient_balance_count)+" ("+str(low_balances_pct)+"%)</h4>\n"
    low_balances_tooltip += "<h6 class='kmd_ui_light1'>where balances < 0.03 </h6>\n"
    low_balances_tooltip += "<h6 class='kmd_ui_light1'>"+str(ignore_chains)+" ignored (no electrum) </h6>\n"
    # open container
    low_balances_tooltip += "<div class='container m-auto' style='width:100%;'>\n"
    i = 1
    notaries = list(low_balances_dict.keys())
    notaries.sort()
    notaries = region_sort(notaries)
    for notary in notaries:
        if i == 1:
            # open row
            low_balances_tooltip += "<div class='row m-auto py-1' style='width:100%;'>\n"
        # open col
        low_balances_tooltip += "<div class='col'><b class='kmd_teal'>"+notary.upper()+"</b><br />"
        if len(low_balances_dict[notary]) > 3:
            low_balances_tooltip += "<b class='kmd_secondary_red'>>3 CHAINS<br /> LOW BALANCE!!!<br /></b>"
        else:
            for chain in low_balances_dict[notary]:
                bal = low_balances_dict[notary][chain]
                low_balances_tooltip += "<b>"+chain+": </b>"+bal+"<br />"
        low_balances_tooltip += "</div>\n"
        # close col
        if i == 5 or notary == notaries[-1]:
            i = 0
            # close row
            low_balances_tooltip += "</div>\n"
        i += 1
    # close container
    low_balances_tooltip += "</div>"
    return low_balances_tooltip
    
# No longer used
def get_nn_health():
    # widget using this has been deprecated, but leaving code here for reference
    # to use in potential replacement functions.
    if 1 == 0:
        coins_data = coins.objects.filter(dpow_active=1).values('chain')
        chains_list = []
        for item in coins_data:
            # ignore BTC, OP RETURN lists ntx to BTC as "KMD"
            if item['chain'] not in chains_list and item['chain'] != 'BTC':
                chains_list.append(item['chain'])

        sync_matches = []
        sync_mismatches = []
        sync_no_exp = []
        sync_no_sync = []
        sync = chain_sync.objects.all().values()
        for item in sync:
            if item['sync_hash'] == item['explorer_hash']:
                sync_matches.append(item['chain'])
            else:
                if item['explorer_hash'] != 'no exp data' and item['sync_hash'] != 'no sync data':
                    sync_mismatches.append(item['chain'])
                if item['sync_hash'] == 'no sync data':
                    sync_no_sync.append(item['chain'])
                if item['explorer_hash'] == 'no exp data':
                    sync_no_exp.append(item['chain'])    
        sync_count = len(sync_matches)
        no_sync_count = len(sync_mismatches)
        sync_pct = round(sync_count/(len(sync))*100,2)

        sync_tooltip = "<h4 class='kmd_teal'>"+str(sync_count)+"/"+str(len(sync))+" ("+str(sync_pct)+"%) recent sync hashes matching</h4>\n"
        if len(sync_mismatches) > 0:
            sync_tooltip += "<h5 class='kmd_secondary_red'>"+str(sync_mismatches)+" have mismatched hashes </h5>\n"
        if len(sync_no_sync) > 0:
            sync_tooltip += "<h5 class='kmd_secondary_red'>"+str(sync_no_sync)+" are not syncing </h5>\n"
        if len(sync_no_exp) > 0:
            sync_tooltip += "<h5 class='kmd_secondary_red'>"+str(sync_no_exp)+" have no explorer </h5>\n"

        season = get_season()
        notary_list = get_notary_list(season)

        timenow = int(time.time())
        day_ago = timenow-60*60*24

        filter_kwargs = {
            'block_time__gte':day_ago,
            'block_time__lte':timenow
        }

        ntx_data = notarised.objects.filter(**filter_kwargs)
        ntx_chain_24hr = ntx_data.values('chain') \
                         .annotate(max_ntx_time=Max('block_time'))

        ntx_chains = []
        for item in ntx_chain_24hr:
            ntx_chains.append(item['chain'])
        ntx_chains = list(set(ntx_chains))

        ntx_node_24hr = ntx_data.values('notaries')
        ntx_nodes = []
        for item in ntx_node_24hr:
            ntx_nodes += item['notaries']
        ntx_nodes = list(set(ntx_nodes))

        mining_data = mined.objects.filter(**filter_kwargs) \
                     .values('name') \
                     .annotate(num_mined=Count('name'))
        mining_nodes = []
        for item in mining_data:
            if item['name'] in notary_list:
                mining_nodes.append(item['name'])

        season = get_season()
        filter_kwargs = {'season':season}
        balances_dict = get_balances_dict(filter_kwargs) 

        # some chains do not have a working electrum, so balances ignored
        ignore_chains = ['K64', 'PGT', 'GIN']
        low_balances = get_low_balances(notary_list, balances_dict, ignore_chains)
        low_balances_dict = low_balances[0]
        low_balance_count = low_balances[1]
        sufficient_balance_count = low_balances[2]
        low_balances_tooltip = get_low_balance_tooltip(low_balances, ignore_chains)
        low_balances_pct = round(sufficient_balance_count/(low_balance_count+sufficient_balance_count)*100,2)

        non_mining_nodes = list(set(notary_list)- set(mining_nodes))
        non_ntx_nodes = list(set(notary_list).symmetric_difference(set(ntx_nodes)))
        non_ntx_chains = list(set(chains_list).symmetric_difference(set(ntx_chains)))
        mining_nodes_pct = round(len(mining_nodes)/len(notary_list)*100,2)
        ntx_nodes_pct = round(len(ntx_nodes)/len(notary_list)*100,2)
        ntx_chains_pct = round(len(ntx_chains)/len(chains_list)*100,2)


        mining_tooltip = "<h4 class='kmd_teal'>"+str(len(mining_nodes))+"/"+str(len(non_mining_nodes)+len(mining_nodes))+" ("+str(mining_nodes_pct)+"%) mined 1+ block in last 24hrs</h4>\n"
        mining_tooltip += "<h5 class='kmd_secondary_red'>"+str(non_mining_nodes)+" are not mining! </h5>\n"

        ntx_nodes_tooltip = "<h4 class='kmd_teal'>"+str(len(ntx_nodes))+"/"+str(len(non_ntx_nodes)+len(ntx_nodes))+" ("+str(ntx_nodes_pct)+"%) notarised 1+ times in last 24hrs</h4>\n"
        ntx_nodes_tooltip += "<h5 class='kmd_secondary_red'>"+str(non_ntx_nodes)+" are not notarising! </h5>\n"

        ntx_chains_tooltip = "<h4 class='kmd_teal'>"+str(len(ntx_chains))+"/"+str(len(non_ntx_chains)+len(ntx_chains))+" ("+str(ntx_chains_pct)+"%) notarised 1+ times in last 24hrs</h4>\n"
        ntx_chains_tooltip += "<h5 class='kmd_secondary_red'>"+str(non_ntx_chains)+" are not notarising! </h5>\n"

        regions_info = get_regions_info(notary_list)
        sync_no_exp = []
        sync_no_sync = []
        nn_health = {
            "sync_pct":sync_pct,
            "regions_info":regions_info,
            "sync_tooltip":sync_tooltip,
            "low_balances_dict":low_balances_dict,
            "low_balances_tooltip":low_balances_tooltip,
            "low_balance_count":low_balance_count,
            "sufficient_balance_count":sufficient_balance_count,
            "balance_pct":low_balances_pct,
            "non_mining_nodes":non_mining_nodes,
            "mining_nodes":mining_nodes,
            "mining_tooltip":mining_tooltip,
            "non_mining_nodes":non_mining_nodes,
            "mining_nodes_pct":mining_nodes_pct,
            "ntx_nodes":ntx_nodes,
            "non_ntx_nodes":non_ntx_nodes,
            "ntx_nodes_pct":ntx_nodes_pct,
            "ntx_chains_tooltip":ntx_chains_tooltip,
            "chains_list":chains_list,
            "ntx_chains":ntx_chains,
            "non_ntx_chains":non_ntx_chains,
            "ntx_chains_pct":ntx_chains_pct,
            "ntx_nodes_tooltip":ntx_nodes_tooltip
        }
        return nn_health
    else:
        return {}


def get_balances_dict(filter_kwargs):
    balances_dict = {}
    balances_data = balances.objects.filter(**filter_kwargs).order_by('notary', 'chain').values('notary', 'chain', 'balance')
    for item in balances_data:
        if item['notary'] not in balances_dict:
            balances_dict.update({item['notary']:{}})
        if item['chain'] not in balances_dict[item['notary']]:
            balances_dict[item['notary']].update({item['chain']:item['balance']})
        else:
            bal = balances_dict[item['notary']][item['chain']] + item['balance']
            balances_dict[item['notary']].update({item['chain']:bal})
    return balances_dict  

# Response too large
def get_mined_data(request):
    resp = {}
    data = mined.objects.all()
    data = apply_filters_api(request, MinedSerializer, data)
    if len(data) == len(mined.objects.all()):
        yesterday = int(time.time() -60*60*24)
        data = mined.objects.filter(block_time__gte=yesterday) \
            .order_by('season','name', 'block_height') \
            .values()
    for item in data:
        name = item['name']
        address = item['address']
        #ignore unknown addresses
        if name != address:
            season = item['season']
            block_height = item['block_height']
            if season not in resp:
                resp.update({season:{}})
            if name not in resp[season]:
                resp[season].update({name:{}})
            resp[season][name].update({
                block_height:{
                    "block_time":item['block_time'],
                    "block_datetime":item['block_datetime'],
                    "value":item['value'],
                    "address":address,
                    "txid":item['txid']
                }
            })

    return wrap_api(resp)

# Response too large
class mined_filter(viewsets.ViewSet):
    """
    API endpoint showing notary node mined blocks. 
    Use filters or be patient, this is a big dataset.
    """
    serializer_class = MinedSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        api_resp = get_mined_data(request)
        return Response(api_resp)
#!/usr/bin/env python3
import os
import time
from datetime import datetime
from dotenv import load_dotenv
import psycopg2
from decimal import *
import logging
import logging.handlers
from .lib_const import *

logger = logging.getLogger("mylogger")

load_dotenv()

def connect_db():
    conn = psycopg2.connect(
        host='localhost',
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
        port = "7654",
        database='postgres'
    )
    return conn

# TABLE UPDATES

def update_addresses_tbl(conn, cursor, row_data):
    try:
        sql = "INSERT INTO addresses \
              (season, owner_name, notary_id, chain, pubkey, address) \
               VALUES (%s, %s, %s, %s, %s, %s) \
               ON CONFLICT ON CONSTRAINT unique_season_chain_address DO UPDATE SET \
               owner_name='"+str(row_data[1])+"', pubkey='"+str(row_data[4])+"', \
               address='"+str(row_data[5])+"';"
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
            (notary, chain, balance, address, season, update_time) \
            VALUES (%s, %s, %s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_notary_chain_season_balance DO UPDATE SET \
            balance="+str(row_data[2])+", \
            update_time="+str(row_data[5])+";"
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
            (notary, address, season, blocks_mined, sum_value_mined, \
            max_value_mined, last_mined_blocktime, last_mined_block, \
            time_stamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_notary_season_mined DO UPDATE SET \
            address="+str(row_data[1])+", blocks_mined="+str(row_data[2])+", sum_value_mined="+str(row_data[3])+", \
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
          kmd_ntx_txid, lastnotarization, opret, ac_ntx_block_hash, \
          ac_ntx_height, ac_block_height, ntx_lag, season) \
          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
          ON CONFLICT ON CONSTRAINT unique_notarised_chain_season DO UPDATE \
          SET ntx_count="+str(row_data[1])+", block_height="+str(row_data[2])+", \
          kmd_ntx_blockhash='"+str(row_data[3])+"', kmd_ntx_txid='"+str(row_data[4])+"', \
          lastnotarization="+str(row_data[5])+", opret='"+str(row_data[6])+"', \
          ac_ntx_block_hash='"+str(row_data[7])+"', ac_ntx_height="+str(row_data[8])+", \
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
            ON CONFLICT ON CONSTRAINT unique_notary_daily_mined DO UPDATE SET \
            blocks_mined="+str(row_data[1])+", sum_value_mined="+str(row_data[2])+", \
            time_stamp='"+str(row_data[7])+"';"
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
    for season in SEASONS_INFO:
        sql = "UPDATE "+table+" \
               SET "+season_col+"='"+season+"' \
               WHERE "+ts_col+" > "+str(SEASONS_INFO[season]['start_time'])+" \
               AND "+ts_col+" < "+str(SEASONS_INFO[season]['end_time'])+";"
        cursor.execute(sql)
        conn.commit()
        
# NOTARISATION OPS

def get_latest_chain_ntx_info(cursor, chain, height):
    sql = "SELECT prev_block_hash, prev_block_height, opret, block_hash, txid \
           FROM notarised WHERE chain = '"+chain+"' AND block_height = "+str(height)+";"
    cursor.execute(sql)
    chains_resp = cursor.fetchone()
    return chains_resp

# MINED OPS



# AGGREGATES

def get_chain_ntx_season_aggregates(cursor, season):
    sql = "SELECT chain, MAX(block_height), MAX(block_time), COUNT(*) \
           FROM notarised WHERE \
           season = '"+str(season)+"' \
           GROUP BY chain;"
    cursor.execute(sql)
    return cursor.fetchall()

def get_chain_ntx_date_aggregates(cursor, day):
    sql = "SELECT chain, MAX(block_height), MAX(block_time), COUNT(*) \
           FROM notarised WHERE \
           DATE_TRUNC('day', block_datetime) = '"+str(day)+"' \
           GROUP BY chain;"
    cursor.execute(sql)
    return cursor.fetchall()

def get_mined_date_aggregates(cursor, day):
    sql = "SELECT name, COUNT(*), SUM(value), MAX(value), MAX(block_time), \
           MAX(block_height) FROM mined WHERE \
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
    return cursor.fetchall()

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
    sql = "SELECT COUNT("+col+") FROM "+table
    cursor.execute(sql)
    return cursor.fetchone()[0]

def get_sum_from_table(cursor, table, col):
    sql = "SELECT SUM("+col+") FROM "+table
    cursor.execute(sql)
    return cursor.fetchone()[0]


