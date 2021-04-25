
from kmd_ntx_api.lib_info import *

logger = logging.getLogger("mylogger")


def get_addresses_table(request):
    season = None
    server = None
    chain = None
    notary = None
    address = None

    if "season" in request.GET:
        season = request.GET["season"]
    if "server" in request.GET:
        server = request.GET["server"]
    if "chain" in request.GET:
        chain = request.GET["chain"]
    if "notary" in request.GET:
        notary = request.GET["notary"]
    if "address" in request.GET:
        address = request.GET["address"]

    if not season and not chain and not notary and not address:
        return {
            "error":"You need to specify at least one of the following filter parameters: ['season', 'chain', 'notary', 'address']"
        }

    data = get_addresses_data(season, server, chain, notary, address)
    data = data.values()

    resp = []
    for item in data:

        resp.append({
                "season":item['season'],
                "server":item['server'],
                "chain":item['chain'],
                "notary":item['notary'],
                "address":item['address'],
                "pubkey":item['pubkey']
        })

    return resp

def get_balances_table(request):
    season = None
    server = None
    chain = None
    notary = None
    address = None

    if "season" in request.GET:
        season = request.GET["season"]
    if "server" in request.GET:
        server = request.GET["server"]
    if "chain" in request.GET:
        chain = request.GET["chain"]
    if "notary" in request.GET:
        notary = request.GET["notary"]
    if "address" in request.GET:
        address = request.GET["address"]

    if not season and not chain and not notary and not address:
        return {
            "error":"You need to specify at least one of the following filter parameters: ['season', 'chain', 'notary', 'address']"
        }
    data = get_balances_data(season, server, chain, notary, address)
    data = data.values()

    serializer = balancesSerializer(data, many=True)

    return serializer.data


def get_coin_social_table(request):
    chain = None

    if "chain" in request.GET:
        chain = request.GET["chain"]

    data = get_coin_social_data(chain)
    data = data.order_by('chain').values()

    serializer = coinSocialSerializer(data, many=True)
    return serializer.data

def get_last_mined_table(request):
    name = None
    address = None
    season = None

    if "season" in request.GET:
        season = request.GET["season"]
    if "name" in request.GET:
        name = request.GET["name"]
    if "address" in request.GET:
        address = request.GET["address"]

    if not season and not name and not address:
        return {
            "error":"You need to specify at least one of the following filter parameters: ['season', 'name', 'address']"
        }

    data = get_mined_data(season, name, address)
    data = data.order_by('season', 'name')
    data = data.values("season", "name", "address")
    data = data.annotate(Max("block_time"), Max("block_height"))


    resp = []
    # name num sum max last
    for item in data:
        print(item)
        season = item['season']
        name = item['name']
        address = item['address']
        last_mined_block = item['block_height__max']
        last_mined_blocktime = item['block_time__max']
        if name != address:
            resp.append({
                    "name":name,
                    "address":address,
                    "last_mined_block":last_mined_block,
                    "last_mined_blocktime":last_mined_blocktime,
                    "season":season
            })

    return resp


def get_last_notarised_table(request):
    season = None
    server = None
    notary = None
    chain = None

    if "season" in request.GET:
        season = request.GET["season"]
    if "server" in request.GET:
        server = request.GET["server"]
    if "notary" in request.GET:
        notary = request.GET["notary"]
    if "chain" in request.GET:
        chain = request.GET["chain"]

    if not notary and not chain:
        return {
            "error":"You need to specify at least one of the following filter parameters: ['notary', 'chain']"
        }

    data = get_last_notarised_data(season, server, notary, chain)
    data = data.order_by('season', 'server', 'notary', 'chain').values()

    serializer = lastNotarisedSerializer(data, many=True)
    return serializer.data

def get_notary_profile_summary_table(request):
    season = None
    server = None
    notary = None
    chain = None

    if "season" in request.GET:
        season = request.GET["season"]
    if "server" in request.GET:
        server = request.GET["server"]
    if "notary" in request.GET:
        notary = request.GET["notary"]
    if "chain" in request.GET:
        chain = request.GET["chain"]

    if not notary or not season:
        return {
            "error":"You need to specify at least both of the following filter parameters: ['notary', 'season']"
        }
    resp = {}
    ntx_season_data = get_notarised_count_season_table(request)
    for item in ntx_season_data:
        chain_ntx_counts = item['chain_ntx_counts']
        for server in chain_ntx_counts:
            for epoch in chain_ntx_counts[server]["epochs"]:
                for chain in chain_ntx_counts[server]["epochs"][epoch]["chains"]:
                    if chain not in resp:
                        resp.update({
                            chain:{
                                "season":season,
                                "server":server,
                                "chain":chain,
                                "chain_score":0,
                                "chain_ntx_count":0
                            }
                        })
                    resp[chain]['chain_score'] += chain_ntx_counts[server]["epochs"][epoch]["chains"][chain]["chain_score"]
                    resp[chain]['chain_ntx_count'] += chain_ntx_counts[server]["epochs"][epoch]["chains"][chain]["chain_ntx_count"]

        chain_ntx_pct = item['chain_ntx_pct']
        for chain in chain_ntx_pct:
            if chain not in resp:
                resp.update({
                    chain: {
                        "season":season,
                        "server":server,
                        "chain":chain,
                        "chain_score":0,
                        "chain_ntx_count":0,
                        "last_block_height":0,
                        "last_block_time":0
                    }
            })
            resp[chain].update({"ntx_pct":chain_ntx_pct[chain]})

    last_ntx = get_last_notarised_table(request)

    for item in last_ntx:
        chain = item['chain']
        # filter out post season chains e.g. etomic
        if chain in resp:
            resp[chain].update({
                "last_block_height":item['block_height'],
                "last_block_time":item['block_time'],
                "since_last_block_time":get_time_since(item['block_time'])[1]
            })

    list_resp = []
    for chain in resp:
        list_resp.append(resp[chain])

    api_resp = {
        "ntx_season_data":ntx_season_data[0],
        "ntx_summary_data":list_resp,
    }
    return api_resp


def get_mined_24hrs_table(request):
    name = None
    address = None

    if "name" in request.GET:
        name = request.GET["name"]
    if "address" in request.GET:
        address = request.GET["address"]

    data = get_mined_data(None, name, address).filter(block_time__gt=str(int(time.time()-24*60*60)))
    data = data.values()

    serializer = minedSerializer(data, many=True)

    return serializer.data

def get_mined_count_season_table(request):
    name = None
    address = None
    season = None

    if "season" in request.GET:
        season = request.GET["season"]
    if "name" in request.GET:
        name = request.GET["name"]
    if "address" in request.GET:
        address = request.GET["address"]

    if not season and not name and not address:
        return {
            "error":"You need to specify at least one of the following filter parameters: ['season', 'name', 'address']"
        }

    data = get_mined_count_season_data(season, name, address)
    data = data.order_by('season', 'name').values()

    serializer = minedCountSeasonSerializer(data, many=True)

    resp = []
    for item in serializer.data:
        if item['blocks_mined'] > 5:
            resp.append(item)

    return resp


def get_notarised_24hrs_table(request):
    season = None
    server = None
    epoch = None
    chain = None
    notary = None
    address = None

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
    if "address" in request.GET:
        address = request.GET["address"]

    if not season or (not chain and not notary):
        return {
            "error":"You need to specify the following filter parameters: ['season'] and at least one of ['notary','chain']"
        }
    data = get_notarised_data(season, server, epoch, chain, notary, address).filter(block_time__gt=str(int(time.time()-24*60*60)))
    data = data.values()

    serializer = notarisedSerializer(data, many=True)

    return serializer.data


def get_notarised_chain_season_table(request):
    season = None
    server = None
    chain = None

    if "season" in request.GET:
        season = request.GET["season"]
    if "server" in request.GET:
        server = request.GET["server"]
    if "chain" in request.GET:
        chain = request.GET["chain"]
    if not season and not chain:
        return {
            "error":"You need to specify at least one of the following filter parameters: ['season', 'chain']"
        }

    data = get_notarised_chain_season_data(season, server, chain)
    data = data.order_by('season', 'server', 'chain').values()

    resp = []
    for item in data:
        season = item['season']
        server = item['server']
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

        resp.append({
            "season":season,
            "server":server,
            "chain":chain,
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
        })


    return resp


def get_notarised_count_season_table(request):
    season = None
    notary = None

    if "season" in request.GET:
        season = request.GET["season"]
    if "notary" in request.GET:
        notary = request.GET["notary"]
    if not season and not notary:
        return {
            "error":"You need to specify at least one of the following filter parameters: ['season', 'notary']"
        }

    data = get_notarised_count_season_data(season, notary)
    data = data.order_by('season', 'notary').values()

    resp = []
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

        if "seasons" in chain_ntx_counts:
            resp.append({
                    "season":season,
                    "notary":notary,
                    "btc_count":btc_count,
                    "antara_count":antara_count,
                    "third_party_count":third_party_count,
                    "other_count":other_count,
                    "total_ntx_count":total_ntx_count,
                    "chain_ntx_counts":chain_ntx_counts["seasons"][season]["servers"],
                    "chain_ntx_pct":chain_ntx_pct,
                    "time_stamp":time_stamp,
                    "chains":{}
            })


    return resp


def get_notarised_table(request):
    season = None
    server = None
    epoch = None
    chain = None
    notary = None
    address = None

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
    if "address" in request.GET:
        address = request.GET["address"]
    print(chain)
    if not season or not server or not chain or not notary:
        return {
            "error":"You need to specify all of the following filter parameters: ['season', 'server', 'chain', 'notary']"
        }
    print(chain)
    data = get_notarised_data(season, server, epoch, chain, notary, address)
    data = data.values()

    serializer = notarisedSerializer(data, many=True)

    return serializer.data


def get_notarised_tenure_table(request):
    season = None
    server = None
    chain = None

    if "season" in request.GET:
        season = request.GET["season"]
    if "server" in request.GET:
        server = request.GET["server"]
    if "chain" in request.GET:
        chain = request.GET["chain"]


    data = get_notarised_tenure_data(season, server, chain)
    data = data.order_by('season', 'server', 'chain').values()

    serializer = notarisedTenureSerializer(data, many=True)

    return serializer.data


def get_scoring_epochs_table(request):
    season = None
    server = None
    chain = None
    epoch = None
    timestamp = None

    if "season" in request.GET:
        season = request.GET["season"]
    if "server" in request.GET:
        server = request.GET["server"]
    if "chain" in request.GET:
        chain = request.GET["chain"]
    if "epoch" in request.GET:
        epoch = request.GET["epoch"]
    if "timestamp" in request.GET:
        timestamp = request.GET["timestamp"]

    if not season and not chain and not timestamp:
        return {
            "error":"You need to specify at least one of the following filter parameters: ['season', 'chain', 'timestamp']"
        }

    data = get_scoring_epochs_data(season, server, chain, epoch, timestamp)
    data = data.order_by('season', 'server', 'epoch').values()

    resp = []
    
    for item in data:

        resp.append({
                "season":item['season'],
                "server":item['server'],
                "epoch":item['epoch'].split("_")[1],
                "epoch_start":dt.fromtimestamp(item['epoch_start']),
                "epoch_end":dt.fromtimestamp(item['epoch_end']),
                "epoch_start_timestamp":item['epoch_start'],
                "epoch_end_timestamp":item['epoch_end'],
                "duration":item['epoch_end']-item['epoch_start'],
                "start_event":item['start_event'],
                "end_event":item['end_event'],
                "epoch_chains":item['epoch_chains'],
                "num_epoch_chains":len(item['epoch_chains']),
                "score_per_ntx":item['score_per_ntx']
        })
    return resp



# UPDATE PENDING
def get_notary_epoch_scores_table(notary=None, season=None):

    if not notary:
        notary_list = get_notary_list(season)
        notary = random.choice(notary_list)

    if not season:
        season = "Season_4"

    notary_epoch_scores = get_notarised_count_season_data(season, notary).values()

    epoch_chains_dict = {}
    epoch_chains_queryset = get_scoring_epochs_data(season).values()
    for item in epoch_chains_queryset:
        if item["season"] not in epoch_chains_dict:
            epoch_chains_dict.update({item["season"]:{}})
        if item["server"] not in epoch_chains_dict[item["season"]]:
            epoch_chains_dict[item["season"]].update({item["server"]:{}})
        if item["epoch"] not in epoch_chains_dict[season][item["server"]]:
            epoch_chains_dict[item["season"]][item["server"]].update({item["epoch"]:item["epoch_chains"]})
    rows = []
    total = 0

    for item in notary_epoch_scores:
        notary = item["notary"]
        chain_ntx = item["chain_ntx_counts"]["seasons"][season]

        for server in chain_ntx["servers"]:

            for epoch in chain_ntx["servers"][server]["epochs"]:
                if server == "BTC":
                    server_epoch_chains = ["BTC"]
                elif server == "KMD":
                    server_epoch_chains = ["KMD"]
                elif server == "LTC":
                    server_epoch_chains = ["LTC"]
                else:
                    server_epoch_chains = epoch_chains_dict[season][server][epoch]

                for chain in chain_ntx["servers"][server]["epochs"][epoch]["chains"]:
                    chain_stats = chain_ntx["servers"][server]["epochs"][epoch]["chains"][chain]
                    score_per_ntx = chain_ntx["servers"][server]["epochs"][epoch]["score_per_ntx"]
                    epoch_chain_ntx_count = chain_stats["chain_ntx_count"]
                    epoch_chain_score = chain_stats["chain_score"]

                    row = {
                        "notary":notary,
                        "season":season.replace("_", " "),
                        "server":server,
                        "epoch":epoch.split("_")[1],
                        "chain":chain,
                        "score_per_ntx":score_per_ntx,
                        "epoch_chain_ntx_count":epoch_chain_ntx_count,
                        "epoch_chain_score":epoch_chain_score
                    }

                    server_epoch_chains.remove(chain)
                    total += chain_stats["chain_score"]
                    rows.append(row)

    return rows, total


def get_vote2021_table(request):
    candidate = None
    block = None
    txid = None
    mined_by = None
    max_block = None
    max_blocktime = None
    max_locktime = None

    if "candidate" in request.GET:
        candidate = request.GET["candidate"]
    if "block" in request.GET:
        block = request.GET["block"]
    if "txid" in request.GET:
        txid = request.GET["txid"]
    if "mined_by" in request.GET:
        mined_by = request.GET["mined_by"]
    if "max_block" in request.GET:
        max_block = request.GET["max_block"]
    if "max_blocktime" in request.GET:
        max_blocktime = request.GET["max_blocktime"]
    if "max_locktime" in request.GET:
        max_locktime = request.GET["max_locktime"]

    data = get_vote2021_data(candidate, block, txid, max_block, max_blocktime, max_locktime, mined_by)

    if "order_by" in request.GET:
        order_by = request.GET["order_by"]
        data = data.values().order_by(f'-{order_by}')
    else:
        data = data.values().order_by(f'-block_time')

    serializer = vote2021Serializer(data, many=True)
    resp = {}
    for item in serializer.data:
        item.update({"lag":item["block_time"]-item["lock_time"]})

    return serializer.data