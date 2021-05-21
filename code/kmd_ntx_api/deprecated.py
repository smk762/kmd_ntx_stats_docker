# Deprecated by get_dpow_coins_list() so season removed coins are included.
def get_active_dpow_coins():
    dpow_chains = coins.objects.filter(dpow_active=1).values('chain', 'dpow')
    chains_list = []
    for item in dpow_chains:
        if item['chain'] not in chains_list:
            chains_list.append(item['chain'])
    chains_list.sort()
    return chains_list

# TODO: Delegate this to crons and table
def get_chain_sync_data(request):
    season = SEASON
    coins_data = get_coins_data(1).values('chain', 'dpow')
    context = {}
    r = requests.get('http://138.201.207.24/show_sync_node_data')
    try:
        chain_sync_data = r.json()
        sync_data_keys = list(chain_sync_data.keys())
        chain_count = 0
        sync_count = 0
        for chain in sync_data_keys:
            if chain == 'last_updated':
                last_data_update = day_hr_min_sec(
                    int(time.time()) - int(chain_sync_data['last_updated'])
                )
                chain_sync_data.update({
                    "last_data_update": last_data_update
                })
            elif chain.find('last') == -1:
                chain_count += 1
                if "last_sync_blockhash" in chain_sync_data[chain]:
                    if chain_sync_data[chain]["last_sync_blockhash"] == chain_sync_data[chain]["last_sync_dexhash"]:
                        sync_count += 1
                if 'last_sync_timestamp' in chain_sync_data[chain] :
                    last_sync_update = day_hr_min_sec(
                        int(time.time()) - int(chain_sync_data[chain]['last_sync_timestamp'])
                    )
                else:
                    last_sync_update = "-"
                chain_sync_data[chain].update({
                    "last_sync_update": last_sync_update
                })
        sync_pct = round(sync_count/chain_count*100,3)
        context.update({
            "chain_sync_data":chain_sync_data,
            "sync_count":sync_count,
            "sync_pct":sync_pct,
            "chain_count":chain_count
        })
    except Exception as e:
        logger.error(f"[get_chain_sync_data] Exception: {e}")
        messages.error(request, 'Sync Node API not Responding!')
    return context
def get_nn_social(notary_name=None, season=None):
    season = SEASON
    nn_social_info = {}
    nn_social_data = get_nn_social_data(season, notary_name).values()
    for item in nn_social_data:
        nn_social_info.update(items_row_to_dict(item,'notary'))
    for notary in nn_social_info:
        for item in nn_social_info[notary]:
            if item in ['twitter', 'youtube', 'discord', 'telegram', 'github', 'keybase']:   
                if nn_social_info[notary][item].endswith('/'):
                   nn_social_info[notary][item] = nn_social_info[notary][item][:-1]
                nn_social_info[notary][item] = nn_social_info[notary][item].replace("https://", "")
                nn_social_info[notary][item] = nn_social_info[notary][item].replace("https://", "")
                nn_social_info[notary][item] = nn_social_info[notary][item].replace("t.me/", "")
                nn_social_info[notary][item] = nn_social_info[notary][item].replace("twitter.com/", "")
                nn_social_info[notary][item] = nn_social_info[notary][item].replace("github.com/", "")
                nn_social_info[notary][item] = nn_social_info[notary][item].replace("www.youtube.com/", "")
                nn_social_info[notary][item] = nn_social_info[notary][item].replace("keybase.io/", "")

    return nn_social_info
    
# TODO: Deprecated? use notarised table values
def get_ntx_score(btc_ntx, main_ntx, third_party_ntx, season=None):
    if not season:
        season = "Season_4"
    coins_dict = get_dpow_server_coins_dict(season)
    third_party = get_third_party_chains(coins_dict)
    main_chains = get_mainnet_chains(coins_dict)
    try:
        if 'BTC' in main_chains:
            main_chains.remove('BTC')
        if 'KMD' in main_chains:
            main_chains.remove('KMD')
        return btc_ntx*0.0325 + main_ntx*0.8698/len(main_chains) + third_party_ntx*0.0977/len(third_party)
    except:
        return 0

def get_nn_ntx_summary(notary):
    season = SEASON
    now = int(time.time())
    day_ago = now - 24*60*60
    week_ago = now - 24*60*60*7

    today = datetime.date.today()
    delta = datetime.timedelta(days=1)
    week_ago = today-delta*7

    ntx_summary = {
        "today":{
            "btc_ntx":0,
            "main_ntx":0,
            "third_party_ntx":0,
            "most_ntx":str(0)+" ("+str('-')+")"
        },
        "season":{
            "btc_ntx":0,
            "main_ntx":0,
            "third_party_ntx":0,
            "most_ntx":str(0)+" ("+str('-')+")"
        },
        "time_since_last_btc_ntx":-1,
        "time_since_last_ntx":-1,
        "last_ntx_chain":'-'
    }

    # 24hr ntx 
    ntx_24hr = get_notarised_data_24hr().values()

    notary_ntx_24hr_summary = get_notary_ntx_24hr_summary(ntx_24hr, notary)
    ntx_summary.update({"today":notary_ntx_24hr_summary})


    # season ntx stats
    ntx_season = get_notarised_count_season_data(season, notary).values()

    if len(ntx_season) > 0:
        chains_ntx_season = ntx_season[0]['chain_ntx_counts']
        season_max_chain = max(chains_ntx_season, key=chains_ntx_season.get) 
        season_max_ntx = chains_ntx_season[season_max_chain]

        ntx_summary['season'].update({
            "btc_ntx":ntx_season[0]['btc_count'],
            "main_ntx":ntx_season[0]['antara_count'],
            "third_party_ntx":ntx_season[0]['third_party_count'],
            "most_ntx":season_max_chain+" ("+str(season_max_ntx)+")",
            "score":ntx_season[0]["season_score"]
        })

    #last ntx data
    ntx_last = get_last_notarised_data(season, None, notary).values()
    last_chain_ntx_times = {}
    for item in ntx_last:
        last_chain_ntx_times.update({item['chain']:item['block_time']})

    if len(last_chain_ntx_times) > 0:
        max_last_ntx_chain = max(last_chain_ntx_times, key=last_chain_ntx_times.get) 
        max_last_ntx_time = last_chain_ntx_times[max_last_ntx_chain]
        time_since_last_ntx = get_time_since(max_last_ntx_time)[1]
        ntx_summary.update({
            "time_since_last_ntx":time_since_last_ntx,
            "last_ntx_chain":max_last_ntx_chain,
        })

    if "BTC" in last_chain_ntx_times:
        max_btc_ntx_time = last_chain_ntx_times["BTC"]
        time_since_last_btc_ntx = get_time_since(max_btc_ntx_time)[1]
        ntx_summary.update({
            "time_since_last_btc_ntx":time_since_last_btc_ntx,
        })

    return ntx_summary

def btc_ntx_all(request):
    season = SEASON
    btc_ntx = get_notarised_data(season, None, None, "BTC").values()

    context = {
        "scheme_host":get_current_host(request),
        "sidebar_links":get_sidebar_links(season),
        "eco_data_link":get_eco_data_link(),
        "explorers":get_explorers(request),
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

        season = SEASON
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

        season = SEASON
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
    data = apply_filters_api(request, minedSerializer, data)
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
    API endpoint showing notary mined blocks. 
    Use filters or be patient, this is a big dataset.
    """
    serializer_class = minedSerializer
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

def get_notarised_tenure_data_api(request):
    resp = {}
    data = notarised_tenure.objects.all()
    data = apply_filters_api(request, notarisedTenureSerializer, data)
    data = data.order_by('chain', 'season').values()
    for item in data:

        if item["season"] not in resp: 
            resp.update({item["season"]:{}})

        if item["server"] not in resp[item["season"]]: 
            resp[item["season"]].update({item["server"]:{}})

        if item["chain"] not in resp[item["season"]][item["server"]]:
            resp[item["season"]][item["server"]].update({
                item["chain"]: {
                    "first_ntx_block":item["first_ntx_block"],
                    "first_ntx_block_time":item["first_ntx_block_time"],
                    "last_ntx_block":item["last_ntx_block"], 
                    "last_ntx_block_time":item["last_ntx_block_time"],
                    "official_start_block_time":item["official_start_block_time"],
                    "official_end_block_time":item["official_end_block_time"],
                    "scored_ntx_count":item["scored_ntx_count"],
                    "unscored_ntx_count":item["unscored_ntx_count"]
                }
            })

    return resp

def get_notarised_count_season_data_api(request):
    resp = {}
    data = notarised_count_season.objects.all()
    data = apply_filters_api(request, notarisedCountSeasonSerializer, data)
    # default filter if none set.
    if len(data) == notarised_count_season.objects.count() or len(data) == 0:
        season = SEASON
        data = notarised_count_season.objects.filter(season=season)

    data = data.order_by('season', 'notary').values()

    for item in data:
        season = item['season']
        notary = item['notary']
        btc_count = item['btc_count']
        antara_count = item['antara_count']
        third_party_count = item['third_party_count']
        other_count = item['other_count']
        total_ntx_count = item['total_ntx_count']
        chain_ntx_counts = item['chain_ntx_counts']
        chain_ntx_pct = item['chain_ntx_pct']
        time_stamp = item['time_stamp']

        if season not in resp:
            resp.update({season:{}})

        resp[season].update({
            notary:{
                "btc_count":btc_count,
                "antara_count":antara_count,
                "third_party_count":third_party_count,
                "other_count":other_count,
                "total_ntx_count":total_ntx_count,
                "time_stamp":time_stamp,
                "chains":{}
            }
        })
        for chain in chain_ntx_counts:
            resp[season][notary]["chains"].update({
                chain:{
                    "count":chain_ntx_counts[chain]
                }
            })
        for chain in chain_ntx_pct:
            if chain not in resp[season][notary]["chains"]:
                resp[season][notary]["chains"].update({chain:{}})
            resp[season][notary]["chains"][chain].update({
                "percentage":chain_ntx_pct[chain]
            }),


    return resp

class notarised_count_season_filter(viewsets.ViewSet):
    """
    API endpoint showing notary mined blocks
    """
    serializer_class = notarisedCountSeasonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        filters = self.serializer_class.Meta.fields
        resp = get_notarised_count_season_data_api(request)
        api_resp = wrap_api(resp, filters)
        return Response(api_resp)

def get_notarised_chain_season_data_api(request):
    resp = {}
    data = notarised_chain_season.objects.all()
    data = apply_filters_api(request, notarisedChainSeasonSerializer, data) \
            .order_by('-season', 'chain') \
            .values()

    for item in data:
        season = item['season']
        chain = item['chain']
        ntx_lag = item['ntx_lag']
        ntx_count = item['ntx_count']
        block_height = item['block_height']
        kmd_ntx_txid = item['kmd_ntx_txid']
        kmd_ntx_blockhash = item['kmd_ntx_blockhash']
        kmd_ntx_blocktime = item['kmd_ntx_blocktime']
        opret = item['opret']
        ac_ntx_blockhash = item['ac_ntx_blockhash']
        ac_ntx_height = item['ac_ntx_height']
        ac_block_height = item['ac_block_height']

        if season not in resp:
            resp.update({season:{}})

        resp[season].update({
            chain:{
                "ntx_count":ntx_count,
                "kmd_ntx_height":block_height,
                "kmd_ntx_blockhash":kmd_ntx_blockhash,
                "kmd_ntx_txid":kmd_ntx_txid,
                "kmd_ntx_blocktime":kmd_ntx_blocktime,
                "ac_ntx_blockhash":ac_ntx_blockhash,
                "ac_ntx_height":ac_ntx_height,
                "ac_block_height":ac_block_height,
                "opret":opret,
                "ntx_lag":ntx_lag
            }
        })


    return resp


# TODO: add to lib_api_filtered
class last_ntx_filter(viewsets.ViewSet):
    """
    API endpoint showing notary rewards pending
    """
    serializer_class = lastNotarisedSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        last_ntx_data = get_last_notarised_data().values()
        return Response(last_ntx_data)



class notarised_chain_season_filter(viewsets.ViewSet):
    """
    API endpoint showing notary mined blocks
    """
    serializer_class = notarisedChainSeasonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        filters = self.serializer_class.Meta.fields
        resp = get_notarised_chain_season_data_api(request)
        api_resp = wrap_api(resp, filters)
        return Response(api_resp)

class notarised_tenure_filter(viewsets.ViewSet):
    """
    Returns chain notarisation tenure, nested by Season > Chain \n
    Default filter returns current NN Season \n

    """
    serializer_class = notarisedTenureSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        filters = self.serializer_class.Meta.fields
        resp = get_notarised_tenure_data_api(request)
        api_resp = wrap_api(resp, filters)
        return Response(api_resp)

class mined_count_season_filter(viewsets.ViewSet):
    """
    API endpoint showing mined blocks by notary/address (minimum 10 blocks mined)
    """
    serializer_class = minedCountSeasonSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        """
        """
        filters = self.serializer_class.Meta.fields
        resp = get_mined_count_season_data_api(request)
        api_resp = wrap_api(resp, filters)
        return Response(api_resp)

def get_mined_count_season_data_api(request):
    resp = {}
    data = mined_count_season.objects.all()
    data = apply_filters_api(request, minedCountSeasonSerializer, data)
    if len(data) == len(mined_count_season.objects.all()):
        season = SEASON
        data = mined_count_season.objects.filter(season=season)
    data = data.order_by('season', 'name').values()

    for item in data:
        blocks_mined = item['blocks_mined']
        if blocks_mined > 10:
            notary = item['name']
            sum_value_mined = item['sum_value_mined']
            max_value_mined = item['max_value_mined']
            last_mined_block = item['last_mined_block']
            last_mined_blocktime = item['last_mined_blocktime']
            time_stamp = item['time_stamp']
            season = item['season']

            if season not in resp:
                resp.update({season:{}})

            resp[season].update({
                notary:{
                    "blocks_mined":blocks_mined,
                    "sum_value_mined":sum_value_mined,
                    "max_value_mined":max_value_mined,
                    "last_mined_block":last_mined_block,
                    "last_mined_blocktime":last_mined_blocktime,
                    "time_stamp":time_stamp
                }
            })

    return resp

class addresses_filter(viewsets.ViewSet):
    """
    Returns Source Notary Node addresses data \n
    Default filter returns current NN Season \n

    """
    serializer_class = addressesSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, OrderingFilter]

    def create(self, validated_data):
        return Task(id=None, **validated_data)

    def get(self, request, format=None):
        filters = self.serializer_class.Meta.fields
        if 'chain' not in request.GET and 'notary' not in request.GET and 'season' not in request.GET:
            return JsonResponse({
                "error":"You need to specify at least one of the following filter parameters: ['chain', 'notary', 'season']",
                "filters":filters,
                })
        resp = get_addresses_data_api(request)
        return JsonResponse({
            "count":len(resp),
            "filters":filters,
            "results":resp
            })

def update_season_mined_count_tbl(conn, cursor, row_data):
    try:
        sql = "INSERT INTO  mined_count_season \
            (name, address, season, blocks_mined, sum_value_mined, \
            max_value_mined, last_mined_blocktime, last_mined_block, \
            time_stamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s) \
            ON CONFLICT ON CONSTRAINT unique_name_season_mined DO UPDATE SET \
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

def update_mined_count_daily_tbl(conn, cursor, row_data):
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
          ON CONFLICT ON CONSTRAINT unique_notarised_chain_daily DO UPDATE \
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


