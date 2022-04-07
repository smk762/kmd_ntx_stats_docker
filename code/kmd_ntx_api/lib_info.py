import requests
from django.db.models import Count, Min, Max, Sum
from datetime import datetime, timezone
import datetime as dt
from kmd_ntx_api.endpoints import ENDPOINTS
from kmd_ntx_api.pages import PAGES
from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.lib_query as query
import kmd_ntx_api.lib_info as info
import kmd_ntx_api.serializers as serializers


def get_coin_ntx_summary(season, chain):
    server = None

    chain_ntx_summary = {
            'chain_ntx_today':0,
            'chain_ntx_season':0,
            'last_ntx_time':'',
            'time_since_ntx':'',
            'last_ntx_block':'',
            'last_ntx_hash':'',
            'last_ntx_ac_block':'',
            'last_ntx_ac_hash':'',
            'ntx_lag':-1
    }
    chain_ntx_season = query.get_notarised_chain_season_data(season, server, chain).values()
    num_chain_ntx_24hr = info.get_notarised_data_24hr(season, server, chain).count()
    chain_ntx_summary.update({
        'num_chain_ntx_24hr':num_chain_ntx_24hr
    })

    # season ntx stats
    if len(chain_ntx_season) > 0:
        time_since_last_ntx = helper.get_time_since(chain_ntx_season[0]['kmd_ntx_blocktime'])[1]
        chain_ntx_summary.update({
            'num_chain_ntx_season':chain_ntx_season[0]['ntx_count'],
            'last_ntx_time':chain_ntx_season[0]['kmd_ntx_blocktime'],
            'time_since_ntx':time_since_last_ntx,
            'last_ntx_block':chain_ntx_season[0]['block_height'],
            'last_ntx_hash':chain_ntx_season[0]['kmd_ntx_blocktime'],
            'last_ntx_ac_block':chain_ntx_season[0]['ac_ntx_height'],
            'last_ntx_ac_hash':chain_ntx_season[0]['ac_ntx_blockhash'],
            'ntx_lag':chain_ntx_season[0]['ntx_lag']
        })
    return chain_ntx_summary


def get_all_coins():
    resp = []
    data = query.get_coins_data()
    for item in data:
        resp.append(item.chain)
    return resp


# TODO: Deprecate once CHMEX migrates to new endpoint
def get_btc_txid_data(category=None):
    resp = {}
    data = query.get_nn_btc_tx_data(None, None, category).exclude(category="SPAM")
    data = data.order_by('-block_height','address').values()

    for item in data:        
        address = item['address']

        if address not in resp:
            resp.update({address:[]})
        resp[address].append(item)

    return resp

 
# notary > chain > data
def get_last_nn_chain_ntx(season):
    ntx_last = query.get_last_notarised_data(season).values()
    last_nn_chain_ntx = {}
    for item in ntx_last:
        notary = item['notary']
        if notary not in last_nn_chain_ntx:
            last_nn_chain_ntx.update({notary:{}})
        chain = item['chain']
        time_since = helper.get_time_since(item['block_time'])[1]
        last_nn_chain_ntx[notary].update({
            chain:{
                "txid": item['txid'],
                "block_height": item['block_height'],
                "block_time": item['block_time'],
                "time_since": time_since
            }
        })
    return last_nn_chain_ntx   


def get_funding_totals(funding_data):
    funding_totals = {"fees": {}}
    now = int(time.time())

    for item in funding_data:
        tx_time = helper.day_hr_min_sec(now - item['block_time'])
        item.update({"time": tx_time})

        if item["notary"] not in ["unknown", "funding bot"]:
            if item["notary"] not in funding_totals:
                funding_totals.update({item["notary"]:{}})

            if item["chain"] not in funding_totals[item["notary"]]:
                funding_totals[item["notary"]].update({item["chain"]:-item["amount"]})
            else:
                val = funding_totals[item["notary"]][item["chain"]]-item["amount"]
                funding_totals[item["notary"]].update({item["chain"]:val})

            if item["chain"] not in funding_totals["fees"]:
                funding_totals["fees"].update({item["chain"]:-item["fee"]})
            else:
                val = funding_totals["fees"][item["chain"]]-item["fee"]
                funding_totals["fees"].update({item["chain"]:val})

    return funding_totals


def get_mined_count_season_by_name(request):
    season = helper.get_or_none(request, "season", SEASON)
    resp = {}

    data = query.get_mined_count_season_data(season).filter(blocks_mined__gte=10).values()
    for i in data:
        if i["name"] not in resp:
            resp.update({i["name"]: {}})
            for k, v in i.items():
                if k not in ["name", "season", "id"]:
                    resp[i["name"]].update({k:v})
        elif i["last_mined_blocktime"] > resp[i["name"]]["last_mined_blocktime"]:
            for k, v in i.items():
                if k not in ["name", "season", "id"]:
                    resp[i["name"]].update({k:v})            
    return resp


def get_nn_mining_summary(notary, season=None):
    if not season:
        season = SEASON

    url = f"{THIS_SERVER}/api/table/mined_count_season/?season={season}&name={notary}"
    mining_summary = requests.get(url).json()['results']
    if len(mining_summary) > 0:
        mining_summary = mining_summary[0]
        mining_summary.update({
            "time_since_mined": helper.get_time_since(mining_summary["last_mined_blocktime"])[1]
        })
    else:
        mining_summary = {
          "blocks_mined": 0,
          "sum_value_mined": 0,
          "max_value_mined": 0,
          "last_mined_block": "N/A",
          "last_mined_blocktime": "N/A",
          "time_since_mined": "N/A"
        }

    mined_last_24hrs = float(info.get_notary_mined_last_24hrs(notary))
    mining_summary.update({
        "mined_last_24hrs": mined_last_24hrs
    })
    
    return mining_summary


def get_seed_stat_season(season, notary=None):
     return query.get_seed_version_data(season, notary).values('name').annotate(sum_score=Sum('score'))


def get_mined_data_24hr():
    day_ago = int(time.time()) - SINCE_INTERVALS['day']
    data = query.get_mined_data().filter(block_time__gt=str(day_ago))
    return data


def get_notary_mined_last_24hrs(notary):
    data = get_mined_data_24hr().filter(name=notary)
    sum_mined = data.aggregate(Sum('value'))['value__sum']
    if not sum_mined:
        sum_mined = 0
    return sum_mined


def get_notarised_data_24hr(season=None, server=None, chain=None, notary=None):
    day_ago = int(time.time()) - SINCE_INTERVALS['day']
    return query.get_notarised_data(season, server, None, chain, notary).filter(block_time__gt=str(day_ago))


def get_dpow_coins_list(season=None, server=None, epoch=None):
    dpow_chains = query.get_scoring_epochs_data(season, server, None, epoch).values('epoch_chains')
    
    chains_list = []
    for item in dpow_chains:
        chains_list += item['epoch_chains']
    chains_list = list(set(chains_list))
    chains_list.sort()
    return chains_list


def get_testnet_addresses(season):
    addresses_dict = {}
    addresses_data = info.get_chain_addresses('KMD', "Season_5_Testnet")

    for item in addresses_data:
        if item["notary"] not in addresses_dict: 
            addresses_dict.update({item["notary"]:item['address']})
        addresses_dict.update({"jorian": "RJNieyvnmjGGFHHEQKZeQv4SyaEhvfpRvA"})
        addresses_dict.update({"hsukrd": "RA93ZHcbw94XqyaYoSF88SfBRUGgA8vVJR"})
    return addresses_dict


def get_chain_addresses(chain, season=None):
    data = query.get_addresses_data(season, None, chain)
    return data.order_by('notary').values('notary','address')


def get_nn_social(season, notary_name=None):
    nn_social_info = {}
    nn_social_data = query.get_nn_social_data(season, notary_name).values()
    for item in nn_social_data:
        nn_social_info.update(helper.items_row_to_dict(item,'notary'))

    return nn_social_info


def get_notary_ntx_24hr_summary(ntx_24hr, notary, season=None, coins_dict=None):
    if not season:
        season = SEASON
    if not coins_dict:
        coins_dict = helper.get_dpow_server_coins_dict(season)

    notary_ntx_24hr = {
            "btc_ntx": 0,
            "main_ntx": 0,
            "third_party_ntx": 0,
            "seed_node_status": 0,
            "most_ntx": "N/A",
            "score": 0
        }

    main_chains = helper.get_mainnet_chains(coins_dict)
    third_party_chains = helper.get_third_party_chains(coins_dict)   

    notary_chain_ntx_counts = {}

    for item in ntx_24hr:
        notaries = item['notaries']
        chain = item['chain']
        ntx_score = item['score_value']

        if notary in notaries:

            if chain not in notary_chain_ntx_counts:
                notary_chain_ntx_counts.update({chain:1})

            else:
                val = notary_chain_ntx_counts[chain]+1
                notary_chain_ntx_counts.update({chain:val})

            notary_ntx_24hr["score"] += ntx_score

    max_ntx_count = 0
    btc_ntx_count = 0
    main_ntx_count = 0
    third_party_ntx_count = 0

    for chain in notary_chain_ntx_counts:
        chain_ntx_count = notary_chain_ntx_counts[chain]
        if chain_ntx_count > max_ntx_count:
            max_chain = chain
            max_ntx_count = chain_ntx_count
        if chain == "KMD": 
            btc_ntx_count += chain_ntx_count
        elif chain in main_chains:
            main_ntx_count += chain_ntx_count
        elif chain in third_party_chains:
            third_party_ntx_count += chain_ntx_count

    seed_node_score = 0
    start = time.time() - SINCE_INTERVALS["day"]
    end = time.time()
    seed_data = query.get_mm2_version_stats_data(start, end-1, notary).values()
    notary_ntx_24hr["score"] = float(notary_ntx_24hr["score"])
    for item in seed_data:
        seed_node_score += round(item["score"], 2)
        notary_ntx_24hr["score"] += round(item["score"], 2)

    if max_ntx_count > 0:
        notary_ntx_24hr.update({
                "btc_ntx": btc_ntx_count,
                "main_ntx": main_ntx_count,
                "third_party_ntx": third_party_ntx_count,
                "seed_node_status": round(seed_node_score, 2),
                "most_ntx": str(max_ntx_count)+" ("+str(max_chain)+")"
            })
    return notary_ntx_24hr
 

def get_region_rank(region_season_stats_sorted, notary):
    higher_ranked_notaries = []
    for item in region_season_stats_sorted:
        if item["notary"] == notary:
            notary_score = item["score"]

    for item in region_season_stats_sorted:
        score = item['score']
        if score > notary_score:
            higher_ranked_notaries.append(notary)
    rank = len(higher_ranked_notaries)+1
    if rank == 1:
        rank = str(rank)+"st"
    elif rank == 2:
        rank = str(rank)+"nd"
    elif rank == 3:
        rank = str(rank)+"rd"
    else:
        rank = str(rank)+"th"
    return rank


# chain > data
def get_season_chain_ntx_data(season, chain=None):
    ntx_season = query.get_notarised_chain_season_data(season, None, chain).values()
    dpow_coins_list = info.get_dpow_coins_list(season)
    season_chain_ntx_data = {}
    if len(ntx_season) > 0:
        for item in ntx_season:
            time_since_last_ntx = helper.get_time_since(item['kmd_ntx_blocktime'])[1]
            if item['chain'] in dpow_coins_list:
                season_chain_ntx_data.update({
                    item['chain']: {
                        'chain_ntx_season':item['ntx_count'],
                        'last_ntx_time':item['kmd_ntx_blocktime'],
                        'time_since_ntx':time_since_last_ntx,
                        'last_ntx_block':item['block_height'],
                        'last_ntx_hash':item['kmd_ntx_blocktime'],
                        'last_ntx_ac_block':item['ac_ntx_height'],
                        'ac_block_height':item['ac_block_height'],
                        'ac_ntx_blockhash':item['ac_ntx_blockhash'],
                        'ntx_lag':item['ntx_lag']
                    }
                })
    return season_chain_ntx_data


# TODO: Deprecate once CHMEX migrates to new endpoint
# DONT MESS WITH THIS WITHOUT LETTING CHMEX KNOW !!!
def get_split_stats():
    resp = info.get_btc_txid_data("Split")
    split_summary = {}
    for address in resp:
        for tx in resp[address]:

            nn_name = tx["notary"]
            if nn_name not in split_summary:
                split_summary.update({
                    nn_name:{}
                })

            season = tx["season"]
            if season not in split_summary[nn_name]:
                split_summary[nn_name].update({
                    season: {
                        "split_count": 0,
                        "last_split_block": 0,
                        "last_split_time": 0,
                        "sum_split_utxos": 0,
                        "average_split_utxos": 0,
                        "sum_fees": 0,
                        "txids": []
                    }
                })

            fees = int(tx["fees"])/100000000
            num_outputs = int(tx["num_outputs"])
            split_summary[nn_name][season].update({
                "split_count": split_summary[nn_name][season]["split_count"]+1,
                "sum_split_utxos": split_summary[nn_name][season]["sum_split_utxos"]+num_outputs,
                "sum_fees": split_summary[nn_name][season]["sum_fees"]+fees
            })

            split_summary[nn_name][season].update({
                "average_split_utxos": split_summary[nn_name][season]["sum_split_utxos"]/split_summary[nn_name][season]["split_count"],
            })

            txid = tx["txid"]
            
            split_summary[nn_name][season]["txids"].append(txid)

            block_height = int(tx["block_height"])
            block_time = int(tx["block_time"])
            if block_time > split_summary[nn_name][season]["last_split_time"]:
                split_summary[nn_name][season].update({
                    "last_split_block": block_height,
                    "last_split_time": block_time
                })
    return split_summary


def get_testnet_stats_dict(season, testnet_chains):
    notaries = helper.get_notary_list(season, True)+["jorian","hsukrd"]
    testnet_stats_dict = helper.create_dict(notaries)

    addresses_dict = info.get_testnet_addresses(season)

    testnet_stats_dict = helper.add_numeric_dict_nest(testnet_stats_dict, "Total")
    testnet_stats_dict = helper.add_numeric_dict_nest(testnet_stats_dict, "Rank")
    testnet_stats_dict = helper.add_numeric_dict_nest(testnet_stats_dict, "24hr_Total")
    testnet_stats_dict = helper.add_numeric_dict_nest(testnet_stats_dict, "24hr_Rank")
    testnet_stats_dict = helper.add_string_dict_nest(testnet_stats_dict, "Address")

    for chain in testnet_chains:
        testnet_stats_dict = helper.add_numeric_dict_nest(testnet_stats_dict, chain)
        testnet_stats_dict = helper.add_numeric_dict_nest(testnet_stats_dict, f"24hr_{chain}")
        testnet_stats_dict = helper.add_numeric_dict_nest(testnet_stats_dict, f"Last_{chain}")

    for notary in testnet_stats_dict:
        if notary in addresses_dict:
            address = addresses_dict[notary]
            testnet_stats_dict[notary].update({"Address": address})
        else:
            logger.warning(f"[get_testnet_stats_dict] {notary} not in addresses_dict (address: {address})")
            logger.warning(f"[addresses_dict] {addresses_dict}")
            logger.warning(f"[notaries] {notaries}")
    return testnet_stats_dict


### V2 for API/INFO
def get_api_index(request):
    category = helper.get_or_none(request, "category")
    sidebar = helper.get_or_none(request, "sidebar")

    resp = []
    for endpoint in ENDPOINTS:
        endpoint_category = ENDPOINTS[endpoint]["category"]
        sidebar_status = ENDPOINTS[endpoint]["sidebar"]
        if (not category or category == endpoint_category) and (not sidebar or sidebar == sidebar_status):
            item = {"url": f"{THIS_SERVER}/api/{endpoint}"}
            item.update(ENDPOINTS[endpoint])
            resp.append(item)

    return resp


def get_pages_index(request):
    category = helper.get_or_none(request, "category")
    sidebar = helper.get_or_none(request, "sidebar")

    resp = []
    for page in PAGES:
        page_category = PAGES[page]["category"]
        sidebar_status = PAGES[page]["sidebar"]
        if (not category or category == page_category) and (not sidebar or sidebar == sidebar_status):
            item = {"url": f"{THIS_SERVER}/{page}"}
            item.update(PAGES[page])
            resp.append(item)

    return resp


def get_balances(request):
    resp = {}
    data = query.get_balances_data()
    data = helper.apply_filters_api(request, serializers.balancesSerializer, data) \
            .order_by('-season','notary', 'chain', 'balance') \
            .values()

    for item in data:
        
        season = item['season']
        if season not in resp:
            resp.update({season:{}})

        notary = item['notary']
        if notary not in resp[season]:
            resp[season].update({notary:{}})

        chain = item['chain']
        if chain not in resp[season][notary]:
            resp[season][notary].update({chain:{}})

        address = item['address']
        balance = item['balance']
        resp[season][notary][chain].update({address:balance})

    return resp


def get_base_58_coin_params(request):
    chain = helper.get_or_none(request, "chain")

    data = query.get_coins_data(chain)
    data = data.order_by('chain').values('chain', 'coins_info')

    resp = {}
    for item in data:
        coins_info = item['coins_info']
        chain = item['chain']
        if len(coins_info) > 0:
            if "pubtype" in coins_info and "wiftype" in coins_info and "p2shtype" in coins_info:
                pubtype = coins_info["pubtype"]
                wiftype = coins_info["wiftype"]
                p2shtype = coins_info["p2shtype"]
                resp.update({
                    chain: {
                        "pubtype": pubtype,
                        "wiftype": wiftype,
                        "p2shtype": p2shtype
                    }
                })
    return resp


def get_coins(request):
    resp = {}
    data = query.get_coins_data()
    data = helper.apply_filters_api(request, serializers.coinsSerializer, data) \
            .order_by('chain') \
            .values()

    for item in data:
        resp.update({
            item["chain"]:{
                "coins_info": item["coins_info"],
                "dpow": item["dpow"],
                "dpow_tenure": item["dpow_tenure"],
                "explorers": item["explorers"],
                "electrums": item["electrums"],
                "electrums_ssl": item["electrums_ssl"],
                "mm2_compatible": item["mm2_compatible"],
                "dpow_active": item["dpow_active"]
            },
        })

    return resp


def get_daemon_cli(request):
    chain = helper.get_or_none(request, "chain")

    data = query.get_coins_data(chain)
    data = data.order_by('chain').values('chain', 'coins_info')

    resp = {}
    for item in data:
        coins_info = item['coins_info']
        chain = item['chain']
        if len(coins_info) > 0:
            if "cli" in coins_info:
                cli = coins_info["cli"]
                resp.update({chain:cli})
    return resp


def get_dpow_server_coins_info(request):
    season = helper.get_or_none(request, "season", SEASON)
    server = helper.get_or_none(request, "server")
    epoch = helper.get_or_none(request, "epoch")
    chain = helper.get_or_none(request, "chain")
    timestamp = helper.get_or_none(request, "timestamp")

    if not season or not server:
        return {
            "error": "You need to specify both of the following filter parameters: ['season', 'server']"
        }
    data = query.get_scoring_epochs_data(season, server, chain, epoch, timestamp)
    data = data.values('epoch_chains')

    resp = []
    for item in data:
        resp += item['epoch_chains']

    resp = list(set(resp))
    resp.sort()

    return resp


def get_explorers(request):
    chain = helper.get_or_none(request, "chain")

    data = query.get_coins_data(chain)
    data = data.order_by('chain').values('chain', 'explorers')

    resp = {}
    for item in data:
        explorers = item['explorers']
        if len(explorers) > 0:
            chain = item['chain']
            resp.update({chain:explorers})
    return resp


def get_electrums(request):
    chain = helper.get_or_none(request, "chain")

    data = query.get_coins_data(chain)
    data = data.order_by('chain').values('chain', 'electrums')

    resp = {}
    for item in data:
        electrums = item['electrums']
        if len(electrums) > 0:
            chain = item['chain']
            resp.update({chain:electrums})
    return resp


def get_icons(request):
    chain = helper.get_or_none(request, "chain")

    data = query.get_coins_data(chain)
    data = data.order_by('chain').values('chain', 'coins_info')

    resp = {}
    for item in data:
        if "icon" in item['coins_info']:
            resp.update({item['chain']:item['coins_info']["icon"]})
    return resp


def get_mm2_coins_list():
    data = query.get_coins_data(None, True)
    data = data.order_by('chain').values('chain')

    resp = []
    for item in data:
        chain = item['chain']
        resp.append(chain)
    return resp


def get_electrums_ssl(request):
    chain = helper.get_or_none(request, "chain")

    data = query.get_coins_data(chain)
    data = data.order_by('chain').values('chain', 'electrums_ssl')

    resp = {}
    for item in data:
        electrums_ssl = item['electrums_ssl']
        if len(electrums_ssl) > 0:
            chain = item['chain']
            resp.update({chain:electrums_ssl})
    return resp


def get_launch_params(request):
    chain = helper.get_or_none(request, "chain")

    data = query.get_coins_data(chain)
    data = data.order_by('chain').values('chain', 'coins_info')

    resp = {}
    for item in data:
        coins_info = item['coins_info']
        chain = item['chain']
        if len(coins_info) > 0:
            if "launch_params" in coins_info:
                launch_params = coins_info["launch_params"]
                resp.update({chain:launch_params})
    return resp


def get_notary_mined_count_daily(request):

    if "mined_date" in request.GET:
        date_today = [int(x) for x in request.GET["mined_date"].split("-")]
        mined_date = dt.date(date_today[0], date_today[1], date_today[2])
    else:
        mined_date = dt.date.today()

    resp = {str(mined_date):{}}
    data = query.get_mined_count_daily_data()
    data = data.filter(mined_date=mined_date)
    data = data.order_by('mined_date', 'notary').values()

    for item in data:
        blocks_mined = item['blocks_mined']
        notary = item['notary']
        sum_value_mined = item['sum_value_mined']
        time_stamp = item['time_stamp']
        mined_date = item['mined_date']

        resp[str(mined_date)].update({
            notary:{
                "blocks_mined": blocks_mined,
                "sum_value_mined": sum_value_mined,
                "time_stamp": time_stamp
            }
        })
    delta = dt.timedelta(days=1)
    yesterday = mined_date-delta
    tomorrow = mined_date+delta
    url = request.build_absolute_uri('/api/info/mined_count_daily/')
    return {
        "count": len(resp[str(mined_date)]),
        "next": f"{url}?mined_date={tomorrow}",
        "previous": f"{url}?mined_date={yesterday}",
        "results": resp
    }


def get_notarised_chain_daily(request):

    if "notarised_date" in request.GET:
        date_today = [int(x) for x in request.GET["notarised_date"].split("-")]
        notarised_date = dt.date(date_today[0], date_today[1], date_today[2])
    else:
        notarised_date = dt.date.today()

    resp = {str(notarised_date):{}}
    data = query.get_notarised_chain_daily_data(notarised_date)
    data = helper.apply_filters_api(request, serializers.notarisedChainDailySerializer, data, 'daily_notarised_chain')
    data = data.order_by('notarised_date', 'chain').values()
    if len(data) > 0:
        for item in data:
            chain = item['chain']
            ntx_count = item['ntx_count']

            resp[str(notarised_date)].update({
                chain:ntx_count
            })

        delta = dt.timedelta(days=1)
        yesterday = item['notarised_date']-delta
        tomorrow = item['notarised_date']+delta
    else:
        today = dt.date.today()
        delta = dt.timedelta(days=1)
        yesterday = today-delta
        tomorrow = today+delta
    url = request.build_absolute_uri('/api/info/notarised_chain_daily/')
    return {
        "count": len(resp[str(notarised_date)]),
        "next": f"{url}?notarised_date={tomorrow}",
        "previous": f"{url}?notarised_date={yesterday}",
        "results": resp
    }


def get_notarised_count_daily(request):

    if "notarised_date" in request.GET:
        date_today = [int(x) for x in request.GET["notarised_date"].split("-")]
        notarised_date = dt.date(date_today[0], date_today[1], date_today[2])
    else:
        notarised_date = dt.date.today()

    resp = {str(notarised_date):{}}
    data = query.get_notarised_count_daily_data(notarised_date)
    data = helper.apply_filters_api(request, serializers.notarisedCountDailySerializer, data, 'daily_notarised_count')
    data = data.order_by('notarised_date', 'notary').values()
    if len(data) > 0:
        for item in data:
            notary = item['notary']

            resp[str(notarised_date)].update({
                notary:{
                    "btc_count": item['btc_count'],
                    "antara_count": item['antara_count'],
                    "third_party_count": item['third_party_count'],
                    "other_count": item['other_count'],
                    "total_ntx_count": item['total_ntx_count'],
                    "time_stamp": item['time_stamp'],
                    "coins": {}
                }
            })
            for coin in item['chain_ntx_counts']:
                resp[str(notarised_date)][notary]["coins"].update({
                    coin: {
                        "count": item['chain_ntx_counts'][coin],
                        "percentage": item['chain_ntx_pct'][coin]
                    }
                })

        delta = dt.timedelta(days=1)
        yesterday = item['notarised_date']-delta
        tomorrow = item['notarised_date']+delta
    else:
        today = dt.date.today()
        delta = dt.timedelta(days=1)
        yesterday = today-delta
        tomorrow = today+delta

    url = request.build_absolute_uri('/api/info/notarised_count_daily/')
    return {
        "count": len(resp[str(notarised_date)]),
        "next": f"{url}?notarised_date={tomorrow}",
        "previous": f"{url}?notarised_date={yesterday}",
        "results": resp
    }


def get_notarised_txid(request):
    txid = helper.get_or_none(request, "txid")

    if not txid:
        return {
            "error": "You need to specify the following filter parameter: ['txid']"
        }
    data = query.get_notarised_data(None, None, None, None, None, None, txid)
    data = data.values()

    serializer = serializers.notarisedSerializer(data, many=True)

    return serializer.data


def get_notarised_chains(request):
    season = helper.get_or_none(request, "season", SEASON)
    server = helper.get_or_none(request, "server")
    epoch = helper.get_or_none(request, "epoch")
    data = query.get_notarised_chains_data(season, server, epoch)
    data = data.distinct('chain')
    resp = []
    for item in data.values():
        resp.append(item["chain"])
    return resp


def get_notarised_servers(request):
    season = helper.get_or_none(request, "season", SEASON)
    data = query.get_notarised_chains_data(season)
    data = data.distinct('server')
    resp = []
    for item in data.values():
        resp.append(item["server"])
    return resp


def get_notary_nodes_info(request):
    season = helper.get_or_none(request, "season", SEASON)
    if not season:
        return {
            "error": "You need to specify the following filter parameter: ['season']"
        }
    data = query.get_nn_social_data(season).values('notary')

    resp = []
    for item in data:
        resp.append(item['notary'])

    resp = list(set(resp))
    resp.sort()
    return resp


def get_split_stats_table(request):
    season = helper.get_or_none(request, "season", SEASON)
    notary = helper.get_or_none(request, "notary")

    category = "Split"

    if not season:
        return {
            "error": "You need to specify the following filter parameter: ['season']"
        }
    data = query.get_nn_btc_tx_data(season, notary, category)
    data = data.order_by('-block_height','address').values()
    split_summary = {}
    for item in data:   
        notary = item["notary"]
        if notary != 'non-NN':
            if notary not in split_summary:
                split_summary.update({
                    notary:{
                        "split_count": 0,
                        "last_split_block": 0,
                        "last_split_time": 0,
                        "sum_split_utxos": 0,
                        "average_split_utxos": 0,
                        "sum_fees": 0,
                        "txids": []
                    }
                })

            fees = int(item["fees"])/100000000
            num_outputs = int(item["num_outputs"])
            split_summary[notary].update({
                "split_count": split_summary[notary]["split_count"]+1,
                "sum_split_utxos": split_summary[notary]["sum_split_utxos"]+num_outputs,
                "sum_fees": split_summary[notary]["sum_fees"]+fees
            })
            
            split_summary[notary]["txids"].append(item["txid"])

            if item["block_height"] > split_summary[notary]["last_split_time"]:
                split_summary[notary].update({
                    "last_split_block": int(item["block_height"]),
                    "last_split_time": int(item["block_time"])
                })

    for notary in split_summary:
        split_summary[notary].update({
            "average_split_utxos": split_summary[notary]["sum_split_utxos"]/split_summary[notary]["split_count"]
        })

    resp = []
    for notary in split_summary:
        row = {
            "notary": notary,
            "season": season
        }
        row.update(split_summary[notary])
        resp.append(row)
    return resp


def get_notary_btc_transactions(request):
    season = helper.get_or_none(request, "season", SEASON)
    notary = helper.get_or_none(request, "notary")
    category = helper.get_or_none(request, "category")
    address = helper.get_or_none(request, "address")

    if not season or not notary:
        return {
            "error": "You need to specify both of the following filter parameters: ['season', 'notary']"
        }

    resp = {
        "season": season,
        "notary": notary,
    }
    txid_list = []
    data = query.get_nn_btc_tx_data(season, notary, category, address).values()

    for item in data:

        if item['category'] not in resp:
            resp.update({item['category']:{}})

        if item['txid'] not in resp[item['category']]:
            resp[item['category']].update({item['txid']:[item]})
            
        else:
            resp[item['category']][item['txid']].append(item)

        txid_list.append(item['txid'])

    api_resp = {
        "count": 0,
        "results": {}
    }

    for category in resp:
        if category not in ["season", "notary"]:
            api_resp["results"].update({
                category:{
                    "count": len(resp[category]),
                    "txids": resp[category]
                }
            })
            api_resp["count"] += len(resp[category])

    return api_resp


def get_notary_ltc_transactions(request):
    season = helper.get_or_none(request, "season", SEASON)
    notary = helper.get_or_none(request, "notary")
    category = helper.get_or_none(request, "category")
    address = helper.get_or_none(request, "address")

    if not season or not notary:
        return {
            "error": "You need to specify the following filter parameter: ['season', 'notary']"
        }

    resp = {
        "season": season,
        "notary": notary,
    }
    txid_list = []
    data = query.get_nn_ltc_tx_data(season, notary, category, address).values()

    for item in data:

        if item['category'] not in resp:
            resp.update({item['category']:{}})

        if item['txid'] not in resp[item['category']]:
            resp[item['category']].update({item['txid']:[item]})
            
        else:
            resp[item['category']][item['txid']].append(item)

        txid_list.append(item['txid'])

    api_resp = {
        "count": 0,
        "results": {}
    }

    for category in resp:
        if category not in ["season", "notary"]:
            api_resp["results"].update({
                category:{
                    "count": len(resp[category]),
                    "txids": resp[category]
                }
            })
            api_resp["count"] += len(resp[category])

    return api_resp


def get_notarisation_txid_list(request):
    season = helper.get_or_none(request, "season", SEASON)
    server = helper.get_or_none(request, "server")
    epoch = helper.get_or_none(request, "epoch")
    chain = helper.get_or_none(request, "chain")
    notary = helper.get_or_none(request, "notary")

    if chain in ["BTC", "LTC", "KMD"]:
        server = chain

    if not season or not server or not chain:
        return {
            "error": "You need to specify the following filter parameters: ['season', 'server', 'chain']"
        }

    data = query.get_notarised_data(season, server, epoch, chain, notary).values('txid')

    resp = []
    for item in data:
        resp.append(item["txid"])

    resp = list(set(resp))
    return resp


def get_notary_btc_txid(request):
    txid = helper.get_or_none(request, "txid")

    if not txid:
        return {
            "error": "You need to specify the following filter parameter: ['txid']"
        }
    data = query.get_nn_btc_tx_data(None, None, None, None, txid)
    data = data.values()

    serializer = serializers.nnBtcTxSerializer(data, many=True)

    return serializer.data


def get_notary_ltc_txid(request):
    txid = helper.get_or_none(request, "txid")

    if not txid:
        return {
            "error": "You need to specify the following filter parameter: ['txid']"
        }
    data = query.get_nn_ltc_tx_data(None, None, None, None, txid)
    data = data.values()

    serializer = serializers.nnLtcTxSerializer(data, many=True)

    return serializer.data


def get_btc_txid_list(request):
    season = helper.get_or_none(request, "season", SEASON)
    notary = helper.get_or_none(request, "notary")
    category = helper.get_or_none(request, "category")
    address = helper.get_or_none(request, "address")

    if (not season or not notary) and (not season or not address):
        return {
            "error": "You need to specify the following filter parameters: ['season', 'notary'] or ['season', 'address']"
        }


    data = query.get_nn_btc_tx_data(season, notary, category, address).values('txid')

    resp = []
    for item in data:
        resp.append(item["txid"])

    resp = list(set(resp))
    return resp


def get_ltc_txid_list(request):
    season = helper.get_or_none(request, "season", SEASON)
    notary = helper.get_or_none(request, "notary")
    category = helper.get_or_none(request, "category")
    address = helper.get_or_none(request, "address")

    if (not season or not notary) and (not season or not address):
        return {
            "error": "You need to specify the following filter parameters: ['season', 'notary'] or ['season', 'address']"
        }

    data = query.get_nn_ltc_tx_data(season, notary, category, address).values('txid')

    resp = []
    for item in data:
        resp.append(item["txid"])

    resp = list(set(resp))
    return resp


def get_nn_social_info(request):
    data = query.get_nn_social_data()
    data = helper.apply_filters_api(request, serializers.nnSocialSerializer, data)

    serializer = serializers.nnSocialSerializer(data, many=True)

    return serializer.data


def get_coin_social(chain=None):

    coin_social_info = {}
    coin_social_data = query.get_coin_social_data(chain).values()
    for item in coin_social_data:
        coin_social_info.update(helper.items_row_to_dict(item,'chain'))
    return coin_social_info


def get_vote2021_info(request):
    candidate = helper.get_or_none(request, "candidate")
    block = helper.get_or_none(request, "block")
    txid = helper.get_or_none(request, "txid")
    max_block = helper.get_or_none(request, "max_block")
    max_blocktime = helper.get_or_none(request, "max_blocktime")
    max_locktime = helper.get_or_none(request, "max_locktime")

    if not max_block and not max_blocktime and not max_locktime:
        return {
            "error": "You need to specify one of the following filter parameters: ['max_block', 'max_blocktime', 'max_locktime']"
        }

    data = query.get_vote2021_data(candidate, block, txid, max_block, max_blocktime, max_locktime)
    data = data.values('candidate').annotate(num_votes=Count('votes'), sum_votes=Sum('votes'))

    resp = {}
    region_scores = {}
    for item in data:
        region = item["candidate"].split("_")[1]
        if region not in resp:
            resp.update({region:[]})
            region_scores.update({region:[]})
        resp[region].append(item)
        if item["candidate"] in DISQUALIFIED:
            region_scores[region].append(-1)
        else:
            region_scores[region].append(item["sum_votes"])


    for region in resp:
        region_scores[region].sort()
        region_scores[region].reverse()
        for item in resp[region]:
            if item["candidate"] in DISQUALIFIED:
                rank = region_scores[region].index(-1) + 1
                item.update({"sum_votes": "DISQUALIFIED"})
            else:
                rank = region_scores[region].index(item["sum_votes"]) + 1
            item.update({"region_rank": rank})
    for region in resp:
        resp[region] = sorted(resp[region], key = lambda item: item['region_rank'])
    return resp


def get_rewards_by_address_info(request):
    season = helper.get_or_none(request, "season").title()
    address = helper.get_or_none(request, "address")
    min_value = helper.get_or_none(request, "min_value")
    min_block = helper.get_or_none(request, "min_block")
    max_block = helper.get_or_none(request, "max_block")
    min_blocktime = helper.get_or_none(request, "min_blocktime")
    max_blocktime = helper.get_or_none(request, "max_blocktime")

    exclude_coinbase = True
    if "exclude_coinbase" in request.GET:
        if request.GET["exclude_coinbase"].lower() == 'false':
            exclude_coinbase = False
                    
    data = query.get_rewards_data(
                    season, address, min_value, min_block, max_block,
                    min_blocktime, max_blocktime, exclude_coinbase
                    ).values()

    resp = {
        "addresses": {},
        "num_addresses": 0,
        "num_claims": 0,
        "sum_claims": 0,
        "first_claim": 999999999999999,
        "last_claim": 0,
        "min_claim": 999999999999999,
        "max_claim": 0,
        "average_claim": 0,
        "claims_per_day": 0,
        "claims_per_month": 0,
        "claims_per_year": 0,
        "claimed_per_day": 0,
        "claimed_per_month": 0,
        "claimed_per_year": 0
    }
    for i in data:
        for address in i["input_addresses"]:
            helper.update_unique(
                resp["addresses"],
                address,
                {
                    "address_age": 0,
                    "num_claims": 0,
                    "sum_claims": 0,
                    "first_claim": 999999999999999,
                    "last_claim": 0,
                    "min_claim": 999999999999999,
                    "max_claim": 0,
                    "average_claim": 0,
                    "claims_per_month": 0,
                    "claims_per_year": 0
                }
            )
            resp["addresses"][address]["num_claims"] += 1
            resp["addresses"][address]["sum_claims"] += i['rewards_value'] / len(i["input_addresses"])

            if i["block_time"] < resp["addresses"][address]["first_claim"]:
                resp["addresses"][address]["first_claim"] = i["block_time"]

            if i["block_time"] > resp["addresses"][address]["last_claim"]:
                resp["addresses"][address]["last_claim"] = i["block_time"]

            if i["rewards_value"] / len(i["input_addresses"]) < resp["addresses"][address]["min_claim"]:
                resp["addresses"][address]["min_claim"] = round(i["rewards_value"] / len(i["input_addresses"]),3)

            if i["rewards_value"] / len(i["input_addresses"]) > resp["addresses"][address]["max_claim"]:
                resp["addresses"][address]["max_claim"] = round(i["rewards_value"] / len(i["input_addresses"]),3)

    addr_count = len(resp["addresses"])
    for address in resp["addresses"]:
        resp["addresses"][address]["address_age"] = resp["addresses"][address]["last_claim"]\
                                                  - resp["addresses"][address]["first_claim"]

        resp["addresses"][address]["average_claim"] = round(resp["addresses"][address]["sum_claims"]\
                                                    / resp["addresses"][address]["num_claims"],3)

        if resp["addresses"][address]["address_age"] > 0:
            claims_per_sec = resp["addresses"][address]["num_claims"]\
                           / resp["addresses"][address]["address_age"]
            resp["addresses"][address]["claims_per_month"] = round(claims_per_sec * SINCE_INTERVALS["month"],3)
            resp["addresses"][address]["claims_per_year"] = round(claims_per_sec * SINCE_INTERVALS["year"],3)

        resp["num_claims"] += 1
        resp["sum_claims"] += resp["addresses"][address]["sum_claims"]
        resp["addresses"][address]["sum_claims"] = round(resp["addresses"][address]["sum_claims"],3)

        if resp["first_claim"] > resp["addresses"][address]["first_claim"]:
            resp["first_claim"] = resp["addresses"][address]["first_claim"]

        if resp["last_claim"] < resp["addresses"][address]["last_claim"]:
            resp["last_claim"] = resp["addresses"][address]["last_claim"]

        if resp["min_claim"] > resp["addresses"][address]["min_claim"]:
            resp["min_claim"] = resp["addresses"][address]["min_claim"]

        if resp["max_claim"] < resp["addresses"][address]["max_claim"]:
            resp["max_claim"] = resp["addresses"][address]["max_claim"]

    resp["num_addresses"] = len(resp["addresses"])
    resp["average_claim"] = round(resp["sum_claims"] / resp["num_claims"],3)

    claim_period = resp["last_claim"] - resp["first_claim"]
    if claim_period > 0:
        claims_per_sec = resp["num_claims"] / claim_period
        claimed_per_sec = resp["sum_claims"] / claim_period
        resp["claims_per_day"] = round(claims_per_sec * SINCE_INTERVALS["day"],3)
        resp["claims_per_month"] = round(claims_per_sec * SINCE_INTERVALS["month"],3)
        resp["claims_per_year"] = round(claims_per_sec * SINCE_INTERVALS["year"],3)
        resp["claimed_per_day"] = round(claimed_per_sec * SINCE_INTERVALS["day"],3)
        resp["claimed_per_month"] = round(claimed_per_sec * SINCE_INTERVALS["month"],3)
        resp["claimed_per_year"] = round(claimed_per_sec * SINCE_INTERVALS["year"],3)

    return resp

