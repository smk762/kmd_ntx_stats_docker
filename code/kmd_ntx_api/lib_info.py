import requests
from .lib_query import *
from .lib_helper import *
from kmd_ntx_api.endpoints import ENDPOINTS
from kmd_ntx_api.pages import PAGES

def get_epochs_dict(season=None):
    if not season:
        season = SEASON

    epoch_data = get_scoring_epochs_data(season).values()
    epochs = {}
    for item in epoch_data:

        server = item['server']
        epoch_id = item['epoch']
        start = item['epoch_start']
        end = item['epoch_end']
        start_event = item['start_event']
        end_event = item['end_event']
        epoch_chains = item['epoch_chains']
        score_per_ntx = item['score_per_ntx']

        if season not in epochs:
            epochs.update({season:{}})

        if server not in epochs[season]:
            epochs[season].update({server:{}})

        if epoch_id not in epochs[season][server]:
            epochs[season][server].update({epoch_id:{
                "start": start,
                "end": end,
                "start_event": start_event,
                "end_event": end_event,
                "score_per_ntx": score_per_ntx
            }})

    return epochs


def get_epoch_id(season, server, block_time):
    epochs = get_epochs_dict()
    for epoch_id in epochs[season][server]:
        if block_time > epochs[season][server][epoch_id]["start"]:
            if block_time < epochs[season][server][epoch_id]["end"]:
                return epoch_id


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
    chain_ntx_season = get_notarised_chain_season_data(season, server, chain).values()

    num_chain_ntx_24hr = get_notarised_data_24hr(season, server, chain).count()

    chain_ntx_summary.update({
        'num_chain_ntx_24hr':num_chain_ntx_24hr
    })

    # season ntx stats
    if len(chain_ntx_season) > 0:
        time_since_last_ntx = get_time_since(chain_ntx_season[0]['kmd_ntx_blocktime'])[1]
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
    data = get_coins_data()
    for item in data:
        resp.append(item.chain)
    return resp


# TODO: Deprecate once CHMEX migrates to new endpoint
def get_btc_txid_data(category=None):
    resp = {}
    data = get_nn_btc_tx_data(None, None, category).exclude(category="SPAM")
    data = data.order_by('-block_height','address').values()

    for item in data:        
        address = item['address']

        if address not in resp:
            resp.update({address:[]})
        resp[address].append(item)

    return resp


 
# notary > chain > data
def get_last_nn_chain_ntx(season):
    ntx_last = get_last_notarised_data(season).values()
    last_nn_chain_ntx = {}
    for item in ntx_last:
        notary = item['notary']
        if notary not in last_nn_chain_ntx:
            last_nn_chain_ntx.update({notary:{}})
        chain = item['chain']
        time_since = get_time_since(item['block_time'])[1]
        last_nn_chain_ntx[notary].update({
            chain:{
                "txid": item['txid'],
                "block_height": item['block_height'],
                "block_time": item['block_time'],
                "time_since": time_since
            }
        })
    return last_nn_chain_ntx   


def get_low_balances(notary_list, balances_dict, ignore_chains):
    low_balances_dict = {}
    sufficient_balance_count = 0
    low_balance_count = 0
    for notary in notary_list:
        if notary in balances_dict:
            for chain in balances_dict[notary]:
                if chain not in ignore_chains:
                    bal = balances_dict[notary][chain]
                    if bal < 0.03:
                        if notary not in low_balances_dict:
                            low_balances_dict.update({notary:{}})
                        if chain not in low_balances_dict[notary]:
                                low_balances_dict[notary].update({chain:str(round(bal.normalize(),4))})
                        low_balance_count += 1
                    else:
                        sufficient_balance_count += 1
    return low_balances_dict, low_balance_count, sufficient_balance_count


def get_funding_totals(funding_data):
    funding_totals = {"fees": {}}
    now = int(time.time())

    for item in funding_data:
        tx_time = day_hr_min_sec(now - item['block_time'])
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


def get_nn_info(season):
    notary_list = get_notary_list(season)
    regions_info = get_regions_info(notary_list)
    nn_info = {
        "regions_info": regions_info,
    }
    return nn_info


def get_nn_mining_summary(notary, season=None):
    if not season:
        season = SEASON

    url = f"{THIS_SERVER}/api/table/mined_count_season/?season={season}&name={notary}"
    mining_summary = requests.get(url).json()['results']
    if len(mining_summary) > 0:
        mining_summary = mining_summary[0]
        mining_summary.update({
            "time_since_mined": get_time_since(mining_summary["last_mined_blocktime"])[1]
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

    mined_last_24hrs = get_notary_mined_last_24hrs(notary)

    if len(mined_last_24hrs) > 0:
        mined_sum_24hr = float(mined_last_24hrs[0]['mined_24hrs'])
    else:
        mined_sum_24hr = 0

    mining_summary.update({
        "mined_last_24hrs": mined_sum_24hr
    })
    
    return mining_summary


def get_notarised_data_txid(txid=None):

    data = get_notarised_data().filter(txid=txid)

    for item in data:

        return {
            "chain": item.chain,
            "txid": item.txid,
            "block_hash": item.block_hash,
            "block_height": item.block_height,
            "block_time": item.block_time,
            "block_datetime": item.block_datetime,
            "notaries": item.notaries,
            "notary_addresses": item.notary_addresses,
            "ac_ntx_blockhash": item.ac_ntx_blockhash,
            "ac_ntx_height": item.ac_ntx_height,
            "opret": item.opret,
            "season": item.season,
            "server": item.server,
            "epoch": item.epoch,
            "scored": item.scored,
            "score_value": item.score_value,
        }

    return {"error": "TXID not found!"}


def get_mined_season(season, notary=None):
     return get_mined_data(season, notary).values('name').annotate(season_blocks_mined=Count('value'))

# Deprecate later
def get_mined_data_24hr():
    return get_mined_data().filter(block_time__gt=str(int(time.time()-24*60*60)))


def get_notarised_data_24hr(season=None, server=None, chain=None, notary=None):
    return get_notarised_data(season, server, None, chain, notary).filter(block_time__gt=str(int(time.time()-24*60*60)))


def get_dpow_coins_list(season=None, server=None, epoch=None):
    dpow_chains = get_scoring_epochs_data(season, server, None, epoch).values('epoch_chains')
    
    chains_list = []
    for item in dpow_chains:
        chains_list += item['epoch_chains']
    chains_list = list(set(chains_list))
    chains_list.sort()
    return chains_list


def get_testnet_addresses(season):
    addresses_dict = {}
    addresses_data = get_chain_addresses('KMD', "Season_5_Testnet")

    for item in addresses_data:
        if item["notary"] not in addresses_dict: 
            addresses_dict.update({item["notary"]:item['address']})
        addresses_dict.update({"jorian": "RJNieyvnmjGGFHHEQKZeQv4SyaEhvfpRvA"})
        addresses_dict.update({"hsukrd": "RA93ZHcbw94XqyaYoSF88SfBRUGgA8vVJR"})
    return addresses_dict


def get_notary_balances(notary, season=None):
    data = get_balances_data(season, None, None, notary)
    return data.values()


def get_chain_balances(chain, season=None):
    data = get_balances_data(season, None, chain, None)
    return data.values()


def get_chain_addresses(chain, season=None):
    data = get_addresses_data(season, None, chain)
    return data.order_by('notary').values('notary','address')


def get_notary_addresses_data(notary, season=None):
    data = get_addresses_data(season, None, None, notary)
    return data.order_by('chain').values('chain','address')


def get_notary_season_aggr(season, name):
    return get_mined_data(season, name).values('name').annotate(
                season_value_mined=Sum('value'),\
                season_blocks_mined=Count('value'),
                season_largest_block=Max('value'),
                last_mined_datetime=Max('block_datetime'),
                last_mined_block=Max('block_height'),
                last_mined_time=Max('block_time')
            )


def get_notary_mined_last_24hrs(notary):
    now = int(time.time())
    day_ago = now - 24*60*60
    data = get_mined_data(None, notary)
    return data.filter(block_time__gte=str(day_ago), block_time__lte=str(now)) \
                      .values('name').annotate(mined_24hrs=Sum('value'))



# notary > chain > count
def get_nn_season_ntx_counts(season):
    ntx_season = get_notarised_count_season_data().values()
    nn_season_ntx_counts = {}
    for item in ntx_season:
        nn_season_ntx_counts.update({
            item['notary']:item['chain_ntx_counts']
        })
    return nn_season_ntx_counts


def get_nn_social(season, notary_name=None):
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


def get_notary_ntx_24hr_summary(ntx_24hr, notary, season=None, coins_dict=None):
    if not season:
        season = SEASON
    if not coins_dict:
        coins_dict = get_dpow_server_coins_dict(season)

    notary_ntx_24hr = {
            "btc_ntx": 0,
            "main_ntx": 0,
            "third_party_ntx": 0,
            "most_ntx": "N/A",
            "score": 0
        }

    main_chains = get_mainnet_chains(coins_dict)
    third_party_chains = get_third_party_chains(coins_dict)   

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

    if max_ntx_count > 0:
        notary_ntx_24hr.update({
                "btc_ntx": btc_ntx_count,
                "main_ntx": main_ntx_count,
                "third_party_ntx": third_party_ntx_count,
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
    ntx_season = get_notarised_chain_season_data(season, None, chain).values()
    dpow_coins_list = get_dpow_coins_list(season)
    season_chain_ntx_data = {}
    if len(ntx_season) > 0:
        for item in ntx_season:
            time_since_last_ntx = get_time_since(item['kmd_ntx_blocktime'])[1]
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


def get_season_nn_chain_ntx_data(season):
    notary_list = get_notary_list(season)
    coins_list = get_dpow_coins_list(season)
    nn_season_ntx_counts = get_nn_season_ntx_counts(season)
    season_chain_ntx_data = get_season_chain_ntx_data(season)
    last_nn_chain_ntx = get_last_nn_chain_ntx(season)
    season_nn_chain_ntx_data = {}
    for notary in notary_list:
        for chain in coins_list:
            total_chain_ntx = 0
            last_ntx_block = 0
            num_nn_chain_ntx = 0
            time_since = "N/A"
            participation_pct = 0
            if chain in season_chain_ntx_data:
                total_chain_ntx = season_chain_ntx_data[chain]['chain_ntx_season']
            else:
                total_chain_ntx = 0

            if notary in nn_season_ntx_counts:
                num_nn_chain_ntx = nn_season_ntx_counts[notary]
            else:
                num_nn_chain_ntx = 0

            if notary in last_nn_chain_ntx:
                if chain in last_nn_chain_ntx[notary]:
                    time_since = last_nn_chain_ntx[notary][chain]["time_since"]
                    last_ntx_block = last_nn_chain_ntx[notary][chain]['block_height']
                    last_ntx_txid = last_nn_chain_ntx[notary][chain]['txid']
                else:
                    time_since = ''
                    last_ntx_block = ''
                    last_ntx_txid = ''
            else:
                time_since = ''
                last_ntx_block = ''
                last_ntx_txid = ''

            if total_chain_ntx != 0 and not isinstance(num_nn_chain_ntx, int):
                if chain in num_nn_chain_ntx:
                    participation_pct = round(num_nn_chain_ntx[chain]/total_chain_ntx*100,2)
                else:
                    participation_pct = 0
            else:
                participation_pct = 0

            if notary not in season_nn_chain_ntx_data:
                season_nn_chain_ntx_data.update({notary:{}})
            if not isinstance(num_nn_chain_ntx, int):
                if chain in num_nn_chain_ntx:
                    num_ntx = num_nn_chain_ntx[chain]
                else:
                    num_ntx = 0
            else:
                num_ntx = 0

            season_nn_chain_ntx_data[notary].update({
                chain: {
                    "num_nn_chain_ntx": num_ntx,
                    "time_since": time_since,
                    "last_ntx_block": last_ntx_block,
                    "last_ntx_txid": last_ntx_txid,
                    "participation_pct": participation_pct
                }
            })
    return season_nn_chain_ntx_data


def get_dpow_server_coins_dict_at_time(season, server, timestamp):

    # Query notarised_tenure 
    # Return list of chains actively dpow'd at timestamp
    
    pass



# TODO: Deprecate once CHMEX migrates to new endpoint
# DONT MESS WITH THIS WITHOUT LETTING CHMEX KNOW !!!
def get_split_stats():
    resp = get_btc_txid_data("Split")
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
    notaries = get_notary_list(season)+["jorian","hsukrd"]
    testnet_stats_dict = create_dict(notaries)

    addresses_dict = get_testnet_addresses(season)

    testnet_stats_dict = add_numeric_dict_nest(testnet_stats_dict, "Total")
    testnet_stats_dict = add_numeric_dict_nest(testnet_stats_dict, "Rank")
    testnet_stats_dict = add_numeric_dict_nest(testnet_stats_dict, "24hr_Total")
    testnet_stats_dict = add_numeric_dict_nest(testnet_stats_dict, "24hr_Rank")
    testnet_stats_dict = add_string_dict_nest(testnet_stats_dict, "Address")

    for chain in testnet_chains:
        testnet_stats_dict = add_numeric_dict_nest(testnet_stats_dict, chain)
        testnet_stats_dict = add_numeric_dict_nest(testnet_stats_dict, f"24hr_{chain}")
        testnet_stats_dict = add_numeric_dict_nest(testnet_stats_dict, f"Last_{chain}")

    for notary in testnet_stats_dict:
        if notary in addresses_dict:
            address = addresses_dict[notary]
            testnet_stats_dict[notary].update({"Address": address})
        else:
            logger.warning(f"[get_testnet_stats_dict] {notary} not in addresses_dict (address: {address})")
            logger.warning(f"[addresses_dict] {addresses_dict}")
            logger.warning(f"[notaries] {notaries}")
    return testnet_stats_dict


def get_sidebar_links(season):
    notary_list = get_notary_list(season)
    region_notaries = get_regions_info(notary_list)
    coins_dict = get_dpow_server_coins_dict(season)
    coins_dict["Main"] += ["KMD", "LTC"]
    coins_dict["Main"].sort()
    sidebar_links = {
        "server": os.getenv("SERVER"),
        "chains_menu": coins_dict,
        "notaries_menu": region_notaries,
    }
    return sidebar_links


def get_dpow_server_coins_dict_lists(season):

    dpow_chains = get_scoring_epochs_data(season).values('epoch_chains', 'server')
    
    main_chains = []
    third_chains = []

    for item in dpow_chains:
        epoch_chains = item['epoch_chains']
        server = item["server"]
        if server == "Main": 
            main_chains += epoch_chains
        elif server == "Third_Party": 
            third_chains += epoch_chains
    main_chains = list(set(main_chains))
    third_chains = list(set(third_chains))
    third_chains.append("KMD_3P")
    main_chains.sort()
    third_chains.sort()

    return main_chains, third_chains


def get_notary_list(season):
    notaries = get_nn_social_data(season).values('notary')
    notary_list = []
    for item in notaries:
        if item['notary'] not in notary_list:
            notary_list.append(item['notary'])
    notary_list.sort()
    return notary_list


### V2 for API/INFO

def get_api_index(request):
    category = None
    sidebar = None

    if "category" in request.GET:
        category = request.GET["category"]
    if "sidebar" in request.GET:
        sidebar = request.GET["sidebar"]

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
    category = None
    sidebar = None

    if "category" in request.GET:
        category = request.GET["category"]
    if "sidebar" in request.GET:
        sidebar = request.GET["sidebar"]

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
    data = get_balances_data()
    data = apply_filters_api(request, balancesSerializer, data) \
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
    chain = None
    if "chain" in request.GET:
        chain = request.GET["chain"]

    data = get_coins_data(chain)
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
    data = get_coins_data()
    data = apply_filters_api(request, coinsSerializer, data) \
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
    chain = None
    if "chain" in request.GET:
        chain = request.GET["chain"]

    data = get_coins_data(chain)
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
    season = None
    server = None
    chain = None
    epoch = None
    timestamp = None

    if "season" in request.GET:
        season = request.GET["season"]
    if "server" in request.GET:
        server = request.GET["server"]
    if "epoch" in request.GET:
        epoch = request.GET["epoch"]
    if "timestamp" in request.GET:
        timestamp = request.GET["timestamp"]

    if not season or not server:
        return {
            "error": "You need to specify both of the following filter parameters: ['season', 'server']"
        }
    data = get_scoring_epochs_data(season, server, chain, epoch, timestamp)
    data = data.values('epoch_chains')

    resp = []
    for item in data:
        resp += item['epoch_chains']

    resp = list(set(resp))
    resp.sort()

    return resp


def get_explorers(request):
    chain = None
    if "chain" in request.GET:
        chain = request.GET["chain"]

    data = get_coins_data(chain)
    data = data.order_by('chain').values('chain', 'explorers')

    resp = {}
    for item in data:
        explorers = item['explorers']
        if len(explorers) > 0:
            chain = item['chain']
            resp.update({chain:explorers})
    return resp


def get_electrums(request):
    chain = None
    if "chain" in request.GET:
        chain = request.GET["chain"]

    data = get_coins_data(chain)
    data = data.order_by('chain').values('chain', 'electrums')

    resp = {}
    for item in data:
        electrums = item['electrums']
        if len(electrums) > 0:
            chain = item['chain']
            resp.update({chain:electrums})
    return resp

def get_mm2_coins_list():
    data = get_coins_data(None, True)
    data = data.order_by('chain').values('chain')

    resp = []
    for item in data:
        chain = item['chain']
        resp.append(chain)
    return resp


def get_electrums_ssl(request):
    chain = None
    if "chain" in request.GET:
        chain = request.GET["chain"]

    data = get_coins_data(chain)
    data = data.order_by('chain').values('chain', 'electrums_ssl')

    resp = {}
    for item in data:
        electrums_ssl = item['electrums_ssl']
        if len(electrums_ssl) > 0:
            chain = item['chain']
            resp.update({chain:electrums_ssl})
    return resp


def get_launch_params(request):
    chain = None
    if "chain" in request.GET:
        chain = request.GET["chain"]

    data = get_coins_data(chain)
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
        mined_date = datetime.date(date_today[0], date_today[1], date_today[2])
    else:
        mined_date = datetime.date.today()

    resp = {str(mined_date):{}}
    data = mined_count_daily.objects.filter(mined_date=mined_date)
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
    delta = datetime.timedelta(days=1)
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
        notarised_date = datetime.date(date_today[0], date_today[1], date_today[2])
    else:
        notarised_date = datetime.date.today()

    resp = {str(notarised_date):{}}
    data = notarised_chain_daily.objects.filter(notarised_date=notarised_date)
    data = apply_filters_api(request, notarisedChainDailySerializer, data, 'daily_notarised_chain')
    data = data.order_by('notarised_date', 'chain').values()
    if len(data) > 0:
        for item in data:
            chain = item['chain']
            ntx_count = item['ntx_count']

            resp[str(notarised_date)].update({
                chain:ntx_count
            })

        delta = datetime.timedelta(days=1)
        yesterday = item['notarised_date']-delta
        tomorrow = item['notarised_date']+delta
    else:
        today = datetime.date.today()
        delta = datetime.timedelta(days=1)
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
        notarised_date = datetime.date(date_today[0], date_today[1], date_today[2])
    else:
        notarised_date = datetime.date.today()

    resp = {str(notarised_date):{}}
    data = get_notarised_count_daily_data(notarised_date)
    data = apply_filters_api(request, notarisedCountDailySerializer, data, 'daily_notarised_count')
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
                    "chains": {}
                }
            })
            for chain in item['chain_ntx_counts']:
                resp[str(notarised_date)][notary]["chains"].update({
                    chain:{
                        "count": item['chain_ntx_counts'][chain],
                        "percentage": item['chain_ntx_pct'][chain]
                    }
                })

        delta = datetime.timedelta(days=1)
        yesterday = item['notarised_date']-delta
        tomorrow = item['notarised_date']+delta
    else:
        today = datetime.date.today()
        delta = datetime.timedelta(days=1)
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
    txid = None

    if "txid" in request.GET:
        txid = request.GET["txid"]

    if not txid:
        return {
            "error": "You need to specify the following filter parameter: ['txid']"
        }
    data = get_notarised_data(None, None, None, None, None, None, txid)
    data = data.values()

    serializer = notarisedSerializer(data, many=True)

    return serializer.data


def get_notary_nodes_info(request):
    season = None

    if "season" in request.GET:
        season = request.GET["season"]

    if not season:
        return {
            "error": "You need to specify the following filter parameter: ['season']"
        }
    data = get_nn_social_data(season).values('notary')

    resp = []
    for item in data:
        resp.append(item['notary'])

    resp = list(set(resp))
    resp.sort()
    return resp


def get_split_stats_table(request):
    season = None
    notary = None

    category = "Split"

    if "season" in request.GET:
        season = request.GET["season"]
    if "notary" in request.GET:
        notary = request.GET["notary"]

    if not season:
        return {
            "error": "You need to specify the following filter parameter: ['season']"
        }
    data = get_nn_btc_tx_data(season, notary, category)
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
    logger.info(request.GET)
    season = None
    notary = None
    category = None
    address = None

    if "season" in request.GET:
        season = request.GET["season"]
    if "notary" in request.GET:
        notary = request.GET["notary"]
    if "category" in request.GET:
        category = request.GET["category"]
    if "address" in request.GET:
        address = request.GET["address"]

    if not season or not notary:
        return {
            "error": "You need to specify both of the following filter parameters: ['season', 'notary']"
        }

    resp = {
        "season": season,
        "notary": notary,
    }
    txid_list = []
    data = get_nn_btc_tx_data(season, notary, category, address).values()

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
    season = None
    notary = None
    category = None
    address = None

    if "season" in request.GET:
        season = request.GET["season"]
    if "notary" in request.GET:
        notary = request.GET["notary"]
    if "category" in request.GET:
        category = request.GET["category"]
    if "address" in request.GET:
        address = request.GET["address"]

    if not season or not notary:
        return {
            "error": "You need to specify the following filter parameter: ['season', 'notary']"
        }

    resp = {
        "season": season,
        "notary": notary,
    }
    txid_list = []
    print(season)
    data = get_nn_ltc_tx_data(season, notary, category, address).values()

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
    season = None
    server = None
    epoch = None
    chain = None
    notary = None

    if "season" in request.GET:
        season = request.GET["season"]
    if "server" in request.GET:
        server = request.GET["server"]
    if "epoch" in request.GET:
        epoch = request.GET["epoch"]
    if "chain" in request.GET:
        chain = request.GET["chain"]
    if "notary" in request.GET:
        notary = request.GET["notary"]

    if chain in ["BTC", "LTC", "KMD"]:
        server = chain

    if not season or not server or not chain:
        return {
            "error": "You need to specify the following filter parameters: ['season', 'server', 'chain']"
        }

    data = get_notarised_data(season, server, epoch, chain, notary).values('txid')

    resp = []
    for item in data:
        resp.append(item["txid"])

    resp = list(set(resp))
    return resp


def get_notary_btc_txid(request):
    txid = None

    if "txid" in request.GET:
        txid = request.GET["txid"]

    if not txid:
        return {
            "error": "You need to specify the following filter parameter: ['txid']"
        }
    data = get_nn_btc_tx_data(None, None, None, None, txid)
    data = data.values()

    serializer = nnBtcTxSerializer(data, many=True)

    return serializer.data


def get_notary_ltc_txid(request):
    txid = None

    if "txid" in request.GET:
        txid = request.GET["txid"]

    if not txid:
        return {
            "error": "You need to specify the following filter parameter: ['txid']"
        }
    data = get_nn_ltc_tx_data(None, None, None, None, txid)
    data = data.values()

    serializer = nnLtcTxSerializer(data, many=True)

    return serializer.data


def get_btc_txid_list(request):
    season = None
    notary = None
    category = None
    address = None

    if "season" in request.GET:
        season = request.GET["season"]
    if "notary" in request.GET:
        notary = request.GET["notary"]
    if "category" in request.GET:
        category = request.GET["category"]
    if "address" in request.GET:
        address = request.GET["address"]

    if not season or not notary:
        return {
            "error": "You need to specify the following filter parameters: ['season', 'notary']"
        }

    data = get_nn_btc_tx_data(season, notary, category, address).values('txid')

    resp = []
    for item in data:
        resp.append(item["txid"])

    resp = list(set(resp))
    return resp


def get_ltc_txid_list(request):
    season = None
    notary = None
    category = None
    address = None

    if "season" in request.GET:
        season = request.GET["season"]
    if "notary" in request.GET:
        notary = request.GET["notary"]
    if "category" in request.GET:
        category = request.GET["category"]
    if "address" in request.GET:
        address = request.GET["address"]

    if not season or not notary:
        return {
            "error": "You need to specify the following filter parameters: ['season', 'notary']"
        }

    data = get_nn_ltc_tx_data(season, notary, category, address).values('txid')

    resp = []
    for item in data:
        resp.append(item["txid"])

    resp = list(set(resp))
    return resp

def get_nn_social_info(request):
    data = get_nn_social_data()
    data = apply_filters_api(request, nnSocialSerializer, data)

    serializer = nnSocialSerializer(data, many=True)

    return serializer.data


def get_coin_social(chain=None):

    coin_social_info = {}
    coin_social_data = get_coin_social_data(chain).values()
    for item in coin_social_data:
        coin_social_info.update(items_row_to_dict(item,'chain'))
    for chain in coin_social_info:
        for item in coin_social_info[chain]:
            if item in ['twitter', 'youtube', 'discord', 'telegram', 'github', 'explorer', 'website']:
                if coin_social_info[chain][item].endswith('/'):
                    coin_social_info[chain][item] = coin_social_info[chain][item][:-1]
                coin_social_info[chain][item] = coin_social_info[chain][item].replace("http://", "")
                coin_social_info[chain][item] = coin_social_info[chain][item].replace("https://", "")
                coin_social_info[chain][item] = coin_social_info[chain][item].replace("t.me/", "")
                coin_social_info[chain][item] = coin_social_info[chain][item].replace("twitter.com/", "")
                coin_social_info[chain][item] = coin_social_info[chain][item].replace("github.com/", "")
                coin_social_info[chain][item] = coin_social_info[chain][item].replace("www.youtube.com/", "")
    return coin_social_info

def get_vote2021_info(request):
    candidate = None
    block = None
    txid = None
    max_block = None
    max_blocktime = None
    max_locktime = None

    if "candidate" in request.GET:
        candidate = request.GET["candidate"]
    if "block" in request.GET:
        block = request.GET["block"]
    if "txid" in request.GET:
        txid = request.GET["txid"]
    if "max_block" in request.GET:
        max_block = request.GET["max_block"]
    if "max_blocktime" in request.GET:
        max_blocktime = request.GET["max_blocktime"]
    if "max_locktime" in request.GET:
        max_locktime = request.GET["max_locktime"]

    if not max_block and not max_blocktime and not max_locktime:
        return {
            "error": "You need to specify one of the following filter parameters: ['max_block', 'max_blocktime', 'max_locktime']"
        }

    data = get_vote2021_data(candidate, block, txid, max_block, max_blocktime, max_locktime)
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