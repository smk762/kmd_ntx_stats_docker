from .lib_query import *
from .lib_helper import *


def get_coin_info():
    # widget using this has been deprecated, but leaving code here for reference
    # to use in potential replacement functions.
    season = get_season()
    coins_list = get_dpow_coins_list(season)
    server_info = get_server_info(coins_list)
    coins_info = {
        "server_info":server_info,
    }
    return coins_info

def get_epochs_dict(season=None):
    if not season:
        season = get_season()

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
                "start":start,
                "end":end,
                "start_event":start_event,
                "end_event":end_event,
                "score_per_ntx":score_per_ntx
            }})

    return epochs

def get_dpow_server_coins_dict(season):
    dpow_chains = get_scoring_epochs_data(season).values('epoch_chains', 'server')
    chains_dict = {}

    for item in dpow_chains:
        epoch_chains = item['epoch_chains']
        server = item["server"]
        if server not in chains_dict:
            chains_dict.update({server:[]})
        chains_dict[server] += epoch_chains

    for server in chains_dict:
        chains_dict[server] = list(set(chains_dict[server]))
        chains_dict[server].sort()

    return chains_dict

def get_epoch_id(season, server, block_time):
    epochs = get_epochs_dict()
    for epoch_id in epochs[season][server]:
        if block_time > epochs[season][server][epoch_id]["start"]:
            if block_time < epochs[season][server][epoch_id]["end"]:
                return epoch_id


def get_btc_txid_single(txid=None):
    resp = []
    filter_kwargs = {}
    data = get_nn_btc_tx_data().filter(txid=txid)
    for item in data:
        row = {
            "txid":item.txid,
            "block_hash":item.block_hash,
            "block_height":item.block_height,
            "block_time":item.block_time,
            "block_datetime":item.block_datetime,
            "address":item.address,
            "notary":item.notary,
            "season":item.season,
            "category":item.category,
            "input_index":item.input_index,
            "input_sats":item.input_sats,
            "output_index":item.output_index,
            "output_sats":item.output_sats,
            "num_inputs":item.num_inputs,
            "num_outputs":item.num_outputs,
            "fees":item.fees
        }
        resp.append(row)
    return resp

def get_coin_ntx_summary(chain):
    now = int(time.time())
    season = get_season(now)

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
    
    # today's ntx stats
    today = datetime.date.today()
    # 24hr ntx 
    chain_ntx_24hr = get_notarised_data_24hr(season, chain).count()

    chain_ntx_summary.update({
        'chain_ntx_today':chain_ntx_24hr
    })

    # season ntx stats
    chain_ntx_season = get_notarised_chain_season_data(season, chain).values()
    if len(chain_ntx_season) > 0:
        time_since_last_ntx = now - int(chain_ntx_season[0]['kmd_ntx_blocktime'])
        time_since_last_ntx = day_hr_min_sec(time_since_last_ntx)
        chain_ntx_summary.update({
            'chain_ntx_season':chain_ntx_season[0]['ntx_count'],
            'last_ntx_time':chain_ntx_season[0]['kmd_ntx_blocktime'],
            'time_since_ntx':time_since_last_ntx,
            'last_ntx_block':chain_ntx_season[0]['block_height'],
            'last_ntx_hash':chain_ntx_season[0]['kmd_ntx_blocktime'],
            'last_ntx_ac_block':chain_ntx_season[0]['ac_ntx_height'],
            'last_ntx_ac_hash':chain_ntx_season[0]['ac_ntx_blockhash'],
            'ntx_lag':chain_ntx_season[0]['ntx_lag']
        })
    return chain_ntx_summary


def get_btc_txid_notary(notary=None, category=None):
    resp = {}
    txid_list = []
    txid_season_list = {}
    data = get_nn_btc_tx_data(None, notary, category).values()

    for item in data:

        if item['season'] not in resp:
            resp.update({item['season']:{}})
            txid_season_list.update({item['season']:[]})

        if item['category'] not in resp[item['season']]:
            resp[item['season']].update({item['category']:{}})

        if item['txid'] not in resp[item['season']][item['category']]:
            resp[item['season']][item['category']].update({item['txid']:[item]})
            
        else:
            resp[item['season']][item['category']][item['txid']].append(item)

        txid_list.append(item['txid'])
        txid_season_list[item['season']].append(item['txid'])

    api_resp = {
        "count":len(list(set(txid_list))),
        "results":{}
    }
    for season in resp:
        if season not in api_resp["results"]:
            api_resp["results"].update({season:{"count":len(list(set(txid_season_list[season])))}})
        for category in resp[season]:
            api_resp["results"][season].update({
                category:{
                    "count":len(resp[season][category]),
                    "txids":resp[season][category]
                }
            })
    return api_resp


# TODO: REVIEW - does this include dpow partial season chains?
def get_dpow_explorers():
    resp = {}
    coins_data = get_coins_data(1).values('chain','explorers')
    for item in coins_data:
        explorers = item['explorers']
        if len(explorers) > 0:
            chain = item['chain']
            resp.update({chain:explorers[0].replace('tx/','')})
    return resp


def get_all_coins():
    resp = []
    data = get_coins_data()
    for item in data:
        resp.append(item.chain)
    return resp


def get_btc_txid_data(category=None):
    resp = {}
    filter_kwargs = {}
    data = get_nn_btc_tx_data(None, None, category).exclude(category="SPAM")

    data = data.order_by('-block_height','address').values()

    for item in data:        
        address = item['address']

        if address not in resp:
            resp.update({address:[]})
        resp[address].append(item)

    return resp


def get_btc_txid_address(address, category=None):
    resp = {}
    txid_list = []
    txid_season_list = {}
    data = get_nn_btc_tx_data(None, None, category, address).values()
    for item in data:
        if item['season'] not in resp:
            resp.update({item['season']:{}})
            txid_season_list.update({item['season']:[]})
        if item['category'] not in resp[item['season']]:
            resp[item['season']].update({item['category']:{}})
        if item['txid'] not in resp[item['season']][item['category']]:
            resp[item['season']][item['category']].update({item['txid']:[item]})
        else:
            resp[item['season']][item['category']][item['txid']].append(item)
        txid_list.append(item['txid'])
        txid_season_list[item['season']].append(item['txid'])

    api_resp = {
        "count":len(list(set(txid_list))),
        "results":{}
    }
    for season in resp:
        if season not in api_resp["results"]:
            api_resp["results"].update({season:{"count":len(list(set(txid_season_list[season])))}})
        for category in resp[season]:
            api_resp["results"][season].update({
                category:{
                    "count":len(resp[season][category]),
                    "txids":resp[season][category]
                }
            })
    return api_resp


def get_coin_social(coin=None):
    season = get_season()
    coin_social_info = {}
    if coin:
        coin_social_data = get_coin_social_data(season, coin).values()
    else:
        coin_social_data = get_coin_social_data().values()
    for item in coin_social_data:
        coin_social_info.update(items_row_to_dict(item,'chain'))
    for coin in coin_social_info:
        for item in coin_social_info[coin]:
            if item in ['twitter', 'youtube', 'discord', 'telegram', 'github', 'explorer', 'website']:
                if coin_social_info[coin][item].endswith('/'):
                    coin_social_info[coin][item] = coin_social_info[coin][item][:-1]
                coin_social_info[coin][item] = coin_social_info[coin][item].replace("http://", "")
                coin_social_info[coin][item] = coin_social_info[coin][item].replace("https://", "")
                coin_social_info[coin][item] = coin_social_info[coin][item].replace("t.me/", "")
                coin_social_info[coin][item] = coin_social_info[coin][item].replace("twitter.com/", "")
                coin_social_info[coin][item] = coin_social_info[coin][item].replace("github.com/", "")
                coin_social_info[coin][item] = coin_social_info[coin][item].replace("www.youtube.com/", "")
    return coin_social_info

 

# notary > chain > data
def get_last_nn_chain_ntx(season):
    ntx_last = get_last_notarised_data(season).values()
    last_nn_chain_ntx = {}
    for item in ntx_last:
        notary = item['notary']
        if notary not in last_nn_chain_ntx:
            last_nn_chain_ntx.update({notary:{}})
        chain = item['chain']
        time_since = int(time.time()) - int(item['block_time'])
        time_since = day_hr_min_sec(time_since)
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
    funding_totals = {"fees":{}}
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


def get_nn_info(season=None):
    if not season:
        season = "Season_4"
    # widget using this has been deprecated, but leaving code here for reference
    # to use in potential replacement functions.
    #season = get_season()
    notary_list = get_notary_list(season)
    regions_info = get_regions_info(notary_list)
    nn_info = {
        "regions_info":regions_info,
    }
    return nn_info


def get_nn_mining_summary(notary, season=None):
    if not season:
        season = "Season_4"
    
    now = int(time.time())
    day_ago = now - 24*60*60
    week_ago = now - 24*60*60*7

    mining_summary = {
        "mined_last_24hrs": 0,
        "season_value_mined": 0,
        "season_blocks_mined": 0,
        "season_largest_block": 0,
        "largest_block_height": 0,
        "last_mined_datetime": -1,
        "time_since_mined": -1,
    }

    mined_this_season = get_notary_season_aggr(season, notary)
    mined_last_24hrs = get_notary_mined_last_24hrs(notary)

    if len(mined_last_24hrs) > 0:
        mining_summary.update({
            "mined_last_24hrs": float(mined_last_24hrs[0]['mined_24hrs'])
        })

    
    if len(mined_last_24hrs) > 0:
        time_since_mined = int(time.time()) - int(mined_this_season[0]['last_mined_time'])
        time_since_mined = day_hr_min_sec(time_since_mined)
        mining_summary.update({
            "season_value_mined": float(mined_this_season[0]['season_value_mined']),
            "season_blocks_mined": int(mined_this_season[0]['season_blocks_mined']),
            "season_largest_block": float(mined_this_season[0]['season_largest_block']),
            "last_mined_datetime": mined_this_season[0]['last_mined_datetime'],
            "time_since_mined": time_since_mined,
            "largest_block_height": int(mined_this_season[0]['last_mined_block']),
        })
    return mining_summary

def get_notarised_data_txid(txid=None):

    data = get_notarised_data().filter(txid=txid)

    for item in data:

        return {
            "chain":item.chain,
            "txid":item.txid,
            "block_hash":item.block_hash,
            "block_height":item.block_height,
            "block_time":item.block_time,
            "block_datetime":item.block_datetime,
            "notaries":item.notaries,
            "notary_addresses":item.notary_addresses,
            "ac_ntx_blockhash":item.ac_ntx_blockhash,
            "ac_ntx_height":item.ac_ntx_height,
            "opret":item.opret,
            "season":item.season,
            "server":item.server,
            "epoch":item.epoch,
            "scored":item.scored,
            "score_value":item.score_value,
            "btc_validated":item.btc_validated
        }

    return {"error":"TXID not found!"}


def get_mined_season(season, notary=None):
     return get_mined_data(season, notary).values('name').annotate(season_blocks_mined=Count('value'))

def get_chain_notarisation_txid_list(chain, season=None):
    resp = []
    data = get_notarised_data(season, chain)
    for item in data:
        resp.append(item.txid)

    return resp

def get_mined_data_24hr():
    return get_mined_data().filter(block_time__gt=str(int(time.time()-24*60*60)))

def get_notarised_data_24hr(season=None, chain=None):
    return get_notarised_data(season, chain).filter(block_time__gt=str(int(time.time()-24*60*60)))


def get_nn_btc_tx_txid_list(notary=None, season=None):
    data = get_nn_btc_tx_data(season, notary)
    resp = []
    for item in data:
        resp.append(item.txid)
    resp = list(set(resp))
    return resp

def get_dpow_coins_list(season=None, server=None, epoch=None):
    dpow_chains = get_scoring_epochs_data(season, server, epoch).values('epoch_chains')
    
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

    return addresses_dict


def get_notary_balances(notary, season=None):
    data = get_balances_data(season, None, notary)
    return data.order_by('-season','notary', 'chain', 'balance').values()

def get_chain_balances(chain, season=None):
    data = get_balances_data(season, chain)
    return data.order_by('-season','notary', 'chain', 'balance').values()


def get_chain_addresses(chain, season=None):
    data = get_addresses_data(season, chain)
    return data.order_by('notary').values('notary','address')


def get_notary_addresses_data(notary, season=None):
    data = get_addresses_data(season, None, notary)
    return data.order_by('chain').values('chain','address')


def get_notary_season_aggr(season, notary):
    now = int(time.time())
    return get_mined_data(season, notary).values('name').annotate(
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


def get_nn_ntx_summary(notary):
    season = get_season()
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
    ntx_last = get_last_notarised_data(season, notary).values()
    last_chain_ntx_times = {}
    for item in ntx_last:
        last_chain_ntx_times.update({item['chain']:item['block_time']})

    if len(last_chain_ntx_times) > 0:
        max_last_ntx_chain = max(last_chain_ntx_times, key=last_chain_ntx_times.get) 
        max_last_ntx_time = last_chain_ntx_times[max_last_ntx_chain]
        time_since_last_ntx = int(time.time()) - int(max_last_ntx_time)
        time_since_last_ntx = day_hr_min_sec(time_since_last_ntx)
        ntx_summary.update({
            "time_since_last_ntx":time_since_last_ntx,
            "last_ntx_chain":max_last_ntx_chain,
        })

    if "BTC" in last_chain_ntx_times:
        max_btc_ntx_time = last_chain_ntx_times["BTC"]
        time_since_last_btc_ntx = int(time.time()) - int(max_btc_ntx_time)
        time_since_last_btc_ntx = day_hr_min_sec(time_since_last_btc_ntx)
        ntx_summary.update({
            "time_since_last_btc_ntx":time_since_last_btc_ntx,
        })

    return ntx_summary


# notary > chain > count
def get_nn_season_ntx_counts(season):
    ntx_season = get_notarised_count_season_data().values()
    nn_season_ntx_counts = {}
    for item in ntx_season:
        nn_season_ntx_counts.update({
            item['notary']:item['chain_ntx_counts']
        })
    return nn_season_ntx_counts


def get_nn_social(notary_name=None, season=None):
    season = get_season()
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


def get_notary_ntx_24hr_summary(ntx_24hr, notary, season=None):
    if not season:
        season = "Season_4"

    notary_ntx_24hr = {
            "btc_ntx":0,
            "main_ntx":0,
            "third_party_ntx":0,
            "most_ntx":"N/A",
            "score":0
        }

    coins_dict = get_dpow_server_coins_dict(season)
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
        if chain == "BTC":
            btc_ntx_count += chain_ntx_count
        elif chain in main_chains:
            main_ntx_count += chain_ntx_count
        elif chain in third_party_chains:
            third_party_ntx_count += chain_ntx_count

    if max_ntx_count > 0:
        notary_ntx_24hr.update({
                "btc_ntx":btc_ntx_count,
                "main_ntx":main_ntx_count,
                "third_party_ntx":third_party_ntx_count,
                "most_ntx":str(max_ntx_count)+" ("+str(max_chain)+")"
            })
    return notary_ntx_24hr



# TODO: use notarised table values
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
 

def get_region_rank(region_notarisation_scores, notary_score):
    higher_ranked_notaries = []
    for notary in region_notarisation_scores:
        score = region_notarisation_scores[notary]['score']
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
def get_season_chain_ntx_data(season):
    ntx_season = get_notarised_chain_season_data(season).values()
    dpow_coins_list = get_dpow_coins_list(season)
    season_chain_ntx_data = {}
    if len(ntx_season) > 0:
        for item in ntx_season:
            time_since_last_ntx = int(time.time()) - int(item['kmd_ntx_blocktime'])
            time_since_last_ntx = day_hr_min_sec(time_since_last_ntx)
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
                    "num_nn_chain_ntx":num_ntx,
                    "time_since":time_since,
                    "last_ntx_block":last_ntx_block,
                    "last_ntx_txid":last_ntx_txid,
                    "participation_pct":participation_pct
                }
            })
    return season_nn_chain_ntx_data


def get_server_chains_at_time(season, server, timestamp):

    # Query notarised_tenure 
    # Return list of chains actively dpow'd at timestamp
    
    pass


def get_server_info(coins_list, season=None):
    if not season:
        season = "Season_4"
    coins_list.sort()
    coins_info = {
        'main':{ 
            "name":"Main server",
            "coins":[]
            },
        'third':{ 
            "name":"Third Party Server",
            "coins":[]
            }
    }
    if not season:
        season = "Season_4"
    coins_dict = get_dpow_server_coins_dict(season)
    server_chains = get_server_chains(season)
    for coin in coins_list:
        if coin in server_chains['main']:
            server = "main"
        elif coin in server_chains['third_party']:
            server = "third"
        coins_info[server]['coins'].append(coin)
    return coins_info




def get_split_stats():
    resp = get_btc_txid_data("splits")
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
                        "split_count":0,
                        "last_split_block":0,
                        "last_split_time":0,
                        "sum_split_utxos":0,
                        "average_split_utxos":0,
                        "sum_fees":0,
                        "txids":[]
                    }
                })

            fees = int(tx["fees"])/100000000
            num_outputs = int(tx["num_outputs"])
            split_summary[nn_name][season].update({
                "split_count":split_summary[nn_name][season]["split_count"]+1,
                "sum_split_utxos":split_summary[nn_name][season]["sum_split_utxos"]+num_outputs,
                "sum_fees":split_summary[nn_name][season]["sum_fees"]+fees
            })

            split_summary[nn_name][season].update({
                "average_split_utxos":split_summary[nn_name][season]["sum_split_utxos"]/split_summary[nn_name][season]["split_count"],
            })

            txid = tx["txid"]
            
            split_summary[nn_name][season]["txids"].append(txid)

            block_height = int(tx["block_height"])
            block_time = int(tx["block_time"])
            if block_time > split_summary[nn_name][season]["last_split_time"]:
                split_summary[nn_name][season].update({
                    "last_split_block":block_height,
                    "last_split_time":block_time
                })
    return split_summary


def get_split_stats_table():
    split_summary = get_split_stats()
    split_rows = []
    for nn in split_summary:
        if nn != 'non-NN':
            row = split_summary[nn]
            split_rows.append(row)
    return split_rows




def get_testnet_stats_dict(season, testnet_chains):
    notaries = get_notary_list(season)
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
            testnet_stats_dict[notary].update({"Address":address})
    return testnet_stats_dict


def get_sidebar_links(season=None):
    if not season:
        season = "Season_4"
    notary_list = get_notary_list(season)
    region_notaries = get_regions_info(notary_list)
    coins_dict = get_dpow_server_coins_dict(season)
    server_chains = get_server_chains(season)
    sidebar_links = {
        "server":os.getenv("SERVER"),
        "chains_menu":server_chains,
        "notaries_menu":region_notaries,
    }
    return sidebar_links

def get_server_chains(season=None):
    if not season:
        season = "Season_4"
    coins_dict = get_dpow_server_coins_dict(season)
    server_chains = {
        "main":get_mainnet_chains(coins_dict),
        "third_party":get_third_party_chains(coins_dict)
    }
    return server_chains

def get_server_chains_lists(season):

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


def get_ltc_txid_notary(season=None, notary=None, category=None):
    resp = {}
    txid_list = []
    txid_season_list = {}

    for item in get_nn_ltc_tx_data(season, notary, category).values():

        if item['season'] not in resp:
            resp.update({item['season']:{}})
            txid_season_list.update({item['season']:[]})

        if item['category'] not in resp[item['season']]:
            resp[item['season']].update({item['category']:{}})

        if item['txid'] not in resp[item['season']][item['category']]:
            resp[item['season']][item['category']].update({item['txid']:[item]})
            
        else:
            resp[item['season']][item['category']][item['txid']].append(item)

        txid_list.append(item['txid'])
        txid_season_list[item['season']].append(item['txid'])

    api_resp = {
        "count":len(list(set(txid_list))),
        "results":{}
    }
    for season in resp:
        if season not in api_resp["results"]:
            api_resp["results"].update({season:{"count":len(list(set(txid_season_list[season])))}})
        for category in resp[season]:
            api_resp["results"][season].update({
                category:{
                    "count":len(resp[season][category]),
                    "txids":resp[season][category]
                }
            })
    return api_resp

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


def get_btc_ntx_lag(request):
    data = get_notarised_data(None, "BTC").values()
    block_time_list = []
    for item in data:
        block_time_list.append(item["block_time"])
    block_time_list = list(set(block_time_list))
    block_time_list.sort()

    max_lags = []
    max_lag_vals = []
    while len(max_lags) < 25:
        max_blocktime_lag = 0
        for block_time in block_time_list:
            try:
                blocktime_lag = block_time - last_blocktime

                if blocktime_lag > max_blocktime_lag and blocktime_lag not in max_lag_vals:
                    max_blocktime_lag = blocktime_lag
                    max_lag_blocktime = block_time
            except:
                pass
            last_blocktime = block_time

        lagged_blocks = []
        for item in data:
            if item["block_time"] == max_lag_blocktime:
                lagged_blocks.append(item)

        max_lags.append({
            "max_blocktime_lag_sec":max_blocktime_lag,
            "max_blocktime_lag":day_hr_min_sec(max_blocktime_lag),
            "max_lag_blocktime":max_lag_blocktime,
            "max_lag_block_datetime":dt.fromtimestamp(max_lag_blocktime),
            "num_lagged_blocks":len(lagged_blocks),
            "lagged_blocks":lagged_blocks
        })
        max_lag_vals.append(max_blocktime_lag)
    return {"max_lags":max_lags}


def get_notary_list(season):
    notaries = get_nn_social_data(season).values('notary')
    notary_list = []
    for item in notaries:
        if item['notary'] not in notary_list:
            notary_list.append(item['notary'])
    notary_list.sort()
    return notary_list


def get_ltc_txid_list(notary=None, season=None):
    resp = []
    for item in get_nn_ltc_tx_data(season, notary):
        resp.append(item.txid)
    resp = list(set(resp))
    return resp


def get_nn_ltc_tx_txid(txid=None):
    resp = []
    filter_kwargs = {}
    data = get_nn_ltc_tx_data().filter(txid=txid)
    for item in data:
        row = {
            "txid":item.txid,
            "block_hash":item.block_hash,
            "block_height":item.block_height,
            "block_time":item.block_time,
            "block_datetime":item.block_datetime,
            "address":item.address,
            "notary":item.notary,
            "season":item.season,
            "category":item.category,
            "input_index":item.input_index,
            "input_sats":item.input_sats,
            "output_index":item.output_index,
            "output_sats":item.output_sats,
            "num_inputs":item.num_inputs,
            "num_outputs":item.num_outputs,
            "fees":item.fees
        }
        resp.append(row)
    return resp
