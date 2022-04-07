
from datetime import datetime as dt
from django.db.models import Count, Min, Max, Sum
from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_query as query
import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.serializers as serializers

logger = logging.getLogger("mylogger")


def get_addresses_table(request):
    season = helper.get_or_none(request, "season", SEASON)
    server = helper.get_or_none(request, "server")
    chain = helper.get_or_none(request, "chain")
    notary = helper.get_or_none(request, "notary")
    address = helper.get_or_none(request, "address")

    if not season and not chain and not notary and not address:
        return {
            "error": "You need to specify at least one of the following filter parameters: ['season', 'chain', 'notary', 'address']"
        }

    data = query.get_addresses_data(season, server, chain, notary, address)
    data = data.values()

    resp = []
    for item in data:

        resp.append({
                "season": item['season'],
                "server": item['server'],
                "chain": item['chain'],
                "notary": item['notary'],
                "address": item['address'],
                "pubkey": item['pubkey']
        })

    return resp


def get_balances_table(request):
    season = helper.get_or_none(request, "season", SEASON)
    server = helper.get_or_none(request, "server")
    chain = helper.get_or_none(request, "chain")
    notary = helper.get_or_none(request, "notary")
    address = helper.get_or_none(request, "address")

    if not season and not chain and not notary and not address:
        return {
            "error": "You need to specify at least one of the following filter parameters: ['season', 'chain', 'notary', 'address']"
        }
    data = query.get_balances_data(season, server, chain, notary, address)
    data = data.values()

    serializer = serializers.balancesSerializer(data, many=True)

    return serializer.data


def get_coin_social_table(request):
    chain = helper.get_or_none(request, "chain")

    data = query.get_coin_social_data(chain)
    data = data.order_by('chain').values()

    serializer = serializers.coinSocialSerializer(data, many=True)
    return serializer.data


def get_last_mined_table(request):
    season = helper.get_or_none(request, "season", SEASON)
    name = helper.get_or_none(request, "name")
    address = helper.get_or_none(request, "address")

    if not season and not name and not address:
        return {
            "error": "You need to specify at least one of the following filter parameters: ['season', 'name', 'address']"
        }

    data = query.get_mined_data(season, name, address)
    data = data.order_by('season', 'name')
    data = data.values("season", "name", "address")
    data = data.annotate(Max("block_time"), Max("block_height"))

    resp = []
    # name num sum max last
    for item in data:
        season = item['season']
        name = item['name']
        address = item['address']
        last_mined_block = item['block_height__max']
        last_mined_blocktime = item['block_time__max']
        if name != address:
            resp.append({
                    "name": name,
                    "address": address,
                    "last_mined_block": last_mined_block,
                    "last_mined_blocktime": last_mined_blocktime,
                    "season": season
            })

    return resp


def get_last_notarised_table(request):
    season = helper.get_or_none(request, "season", SEASON)
    server = helper.get_or_none(request, "server")
    chain = helper.get_or_none(request, "chain")
    notary = helper.get_or_none(request, "notary")

    if not notary and not chain:
        return {
            "error": "You need to specify at least one of the following filter parameters: ['notary', 'chain']"
        }

    data = query.get_last_notarised_data(season, server, notary, chain)
    data = data.order_by('season', 'server', 'notary', 'chain').values()

    serializer = serializers.lastNotarisedSerializer(data, many=True)
    return serializer.data


# TODO: Handle where chain not notarised
def get_notary_profile_summary_table(request):
    season = helper.get_or_none(request, "season", SEASON)
    server = helper.get_or_none(request, "server")
    chain = helper.get_or_none(request, "chain")
    notary = helper.get_or_none(request, "notary")

    if not notary or not season:
        return {
            "error": "You need to specify at least both of the following filter parameters: ['notary', 'season']"
        }
    season_main_coins = requests.get(f'{THIS_SERVER}/api/info/dpow_server_coins/?season={SEASON}&server=Main').json()["results"]
    season_3P_coins = requests.get(f'{THIS_SERVER}/api/info/dpow_server_coins/?season={SEASON}&server=Third_Party').json()["results"]

    resp = {}
    ntx_season_data = get_notarised_count_season_table(request)
    for item in ntx_season_data:
        chain_ntx_counts = item['chain_ntx_counts']
        for chain in chain_ntx_counts["coins"]:
            if chain not in resp:
                if chain in season_main_coins:
                    server = "Main"
                elif chain in season_3P_coins:
                    server = "Third_Party"
                elif chain in ["KMD", "BTC", "LTC"]:
                    server = chain
                else:
                    server = "Unknown"
                    logger.warning(f"Can't assign {chain} NTX % for {notary}")
                resp.update({
                    chain:{
                        "season": season,
                        "server": server,
                        "chain": chain,
                        "chain_score": chain_ntx_counts["coins"][chain]["notary_coin_ntx_score"],
                        "chain_ntx_count": chain_ntx_counts["coins"][chain]["notary_coin_ntx_count"]
                    }
                })

        chain_ntx_pct = item['chain_ntx_pct']
        for chain in chain_ntx_pct:
            if chain not in resp:
                if chain in season_main_coins:
                    server = "Main"
                elif chain in season_3P_coins:
                    server = "Third_Party"
                elif chain in ["KMD", "BTC", "LTC"]:
                    server = chain
                else:
                    server = "Unknown"
                    logger.warning(f"Can't assign {chain} NTX % for {notary}")
                resp.update({
                    chain: {
                        "season": season,
                        "server": server,
                        "chain": chain,
                        "chain_score": 0,
                        "chain_ntx_count": 0,
                        "last_block_height": 0,
                        "last_block_time": 0
                    }
            })
            resp[chain].update({"ntx_pct": chain_ntx_pct[chain]})

    last_ntx = get_last_notarised_table(request)
    for item in last_ntx:
        chain = item['chain']
        # filter out post season chains e.g. etomic
        if chain in resp:
            resp[chain].update({
                "last_block_height": item['block_height'],
                "last_block_time": item['block_time'],
                "since_last_block_time": helper.get_time_since(item['block_time'])[1]
            })

    list_resp = []
    for chain in resp:
        list_resp.append(resp[chain])

    api_resp = {
        "ntx_season_data": ntx_season_data,
        "ntx_summary_data": list_resp,
    }
    return api_resp


def get_mined_24hrs_table(request):
    name = helper.get_or_none(request, "name")
    address = helper.get_or_none(request, "address")
    day_ago = int(time.time()) - SINCE_INTERVALS['day']
    data = query.get_mined_data(None, name, address).filter(block_time__gt=str(day_ago))
    data = data.values()

    serializer = serializers.minedSerializer(data, many=True)

    return serializer.data


def get_mined_count_season_table(request):
    season = helper.get_or_none(request, "season", SEASON)
    name = helper.get_or_none(request, "name")
    address = helper.get_or_none(request, "address")

    if not season and not name and not address:
        return {
            "error": "You need to specify at least one of the following filter parameters: ['season', 'name', 'address']"
        }

    data = query.get_mined_count_season_data(season, name, address).filter(blocks_mined__gte=10)
    data = data.order_by('season', 'name').values()
    serializer = serializers.minedCountSeasonSerializer(data, many=True)
    return serializer.data


def get_notarised_24hrs_table(request):
    season = helper.get_or_none(request, "season", SEASON)
    server = helper.get_or_none(request, "server")
    epoch = helper.get_or_none(request, "epoch")
    chain = helper.get_or_none(request, "chain")
    notary = helper.get_or_none(request, "notary")
    address = helper.get_or_none(request, "address")

    if not season or (not chain and not notary):
        return {
            "error": "You need to specify the following filter parameters: ['season'] and at least one of ['notary','chain']"
        }
    day_ago = int(time.time()) - SINCE_INTERVALS['day']
    data = query.get_notarised_data(season, server, epoch, chain, notary, address).filter(block_time__gt=str(day_ago))
    data = data.values()

    serializer = serializers.notarisedSerializer(data, many=True)

    return serializer.data


def get_notarised_chain_season_table(request):
    season = helper.get_or_none(request, "season", SEASON)
    server = helper.get_or_none(request, "server")
    chain = helper.get_or_none(request, "chain")

    if not season and not chain:
        return {
            "error": "You need to specify at least one of the following filter parameters: ['season', 'chain']"
        }

    data = query.get_notarised_chain_season_data(season, server, chain)
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
            "season": season,
            "server": server,
            "chain": chain,
            "ntx_count": ntx_count,
            "kmd_ntx_height": block_height,
            "kmd_ntx_blockhash": kmd_ntx_blockhash,
            "kmd_ntx_txid": kmd_ntx_txid,
            "kmd_ntx_blocktime": kmd_ntx_blocktime,
            "ac_ntx_blockhash": ac_ntx_blockhash,
            "ac_ntx_height": ac_ntx_height,
            "ac_block_height": ac_block_height,
            "opret": opret,
            "ntx_lag": ntx_lag
        })


    return resp


def get_notarised_count_season_table(request):
    season = helper.get_or_none(request, "season", SEASON)
    notary = helper.get_or_none(request, "notary")

    if not season and not notary:
        return {
            "error": "You need to specify at least one of the following filter parameters: ['season', 'notary']"
        }

    data = query.get_notarised_count_season_data(season, notary)
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

        resp.append({
                "season": season,
                "notary": notary,
                "btc_count": btc_count,
                "antara_count": antara_count,
                "third_party_count": third_party_count,
                "other_count": other_count,
                "total_ntx_count": total_ntx_count,
                "chain_ntx_counts": chain_ntx_counts,
                "chain_ntx_pct": chain_ntx_pct,
                "time_stamp": time_stamp,
                "coins": {}
        })


    return resp


def get_notary_ntx_table(request):
    season = helper.get_or_none(request, "season", SEASON)
    server = helper.get_or_none(request, "server")
    epoch = helper.get_or_none(request, "epoch")
    chain = helper.get_or_none(request, "chain")
    notary = helper.get_or_none(request, "notary")

    if not season or not chain or not notary:
        return {
            "error": "You need to specify all of the following filter parameters: ['season', 'chain', 'notary']"
        }
    data = query.get_notarised_data(season, server, epoch, chain, notary).order_by('-block_time')
    data = data.values('txid', 'chain', 'block_height', 'block_time', 'ac_ntx_height', 'score_value')

    serializer = serializers.notary_ntxSerializer(data, many=True)

    return serializer.data


def get_notarised_table(request):
    season = helper.get_or_none(request, "season", SEASON)
    server = helper.get_or_none(request, "server")
    epoch = helper.get_or_none(request, "epoch")
    chain = helper.get_or_none(request, "chain")
    notary = helper.get_or_none(request, "notary")
    address = helper.get_or_none(request, "address")

    if not season or not server or not chain or not notary:
        return {
            "error": "You need to specify all of the following filter parameters: ['season', 'server', 'chain', 'notary']"
        }
    data = query.get_notarised_data(season, server, epoch, chain, notary, address).order_by('-block_time')
    data = data.values()

    serializer = serializers.notarisedSerializer(data, many=True)

    return serializer.data


def get_notarised_tenure_table(request):
    season = helper.get_or_none(request, "season", SEASON)
    server = helper.get_or_none(request, "server")
    chain = helper.get_or_none(request, "chain")

    data = query.get_notarised_tenure_data(season, server, chain)
    data = data.order_by('season', 'server', 'chain').values()

    serializer = serializers.notarisedTenureSerializer(data, many=True)

    return serializer.data


def get_scoring_epochs_table(request):
    season = helper.get_or_none(request, "season", SEASON)
    server = helper.get_or_none(request, "server")
    epoch = helper.get_or_none(request, "epoch")
    chain = helper.get_or_none(request, "chain")
    timestamp = helper.get_or_none(request, "timestamp")

    if not season and not chain and not timestamp:
        return {
            "error": "You need to specify at least one of the following filter parameters: ['season', 'chain', 'timestamp']"
        }

    data = query.get_scoring_epochs_data(season, server, chain, epoch, timestamp)
    data = data.order_by('season', 'server', 'epoch').values()

    resp = []
    
    for item in data:
        if item['epoch'].find("_") > -1:
            epoch_id = item['epoch'].split("_")[1]
        else:
            epoch_id = epoch
            
        if epoch_id not in ["Unofficial", None]:
            resp.append({
                    "season": item['season'],
                    "server": item['server'],
                    "epoch": epoch_id,
                    "epoch_start": dt.fromtimestamp(item['epoch_start']),
                    "epoch_end": dt.fromtimestamp(item['epoch_end']),
                    "epoch_start_timestamp": item['epoch_start'],
                    "epoch_end_timestamp": item['epoch_end'],
                    "duration": item['epoch_end']-item['epoch_start'],
                    "start_event": item['start_event'],
                    "end_event": item['end_event'],
                    "epoch_chains": item['epoch_chains'],
                    "num_epoch_chains": len(item['epoch_chains']),
                    "score_per_ntx": item['score_per_ntx']
            })
    return resp


# UPDATE PENDING
def get_notary_epoch_scores_table(notary=None, season=None, selected_chain=None):

    if not notary:
        notary_list = get_notary_list(season)
        notary = random.choice(notary_list)

    if not season:
        season = SEASON

    notary_epoch_scores = query.get_notarised_count_season_data(season, notary).values()

    epoch_chains_dict = {}
    epoch_chains_queryset = query.get_scoring_epochs_data(season).values()
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
        chain_ntx = item["chain_ntx_counts"]

        for server in chain_ntx["servers"]:

            for epoch in chain_ntx["servers"][server]["epochs"]:
                if epoch != "Unofficial": 
                    if server == "BTC": 
                        server_epoch_chains = ["BTC"]
                    elif server == "KMD": 
                        server_epoch_chains = ["KMD"]
                    elif server == "LTC": 
                        server_epoch_chains = ["LTC"]
                    else:
                        server_epoch_chains = epoch_chains_dict[season][server][epoch]

                    for chain in chain_ntx["servers"][server]["epochs"][epoch]["coins"]:
                        if not selected_chain or chain == selected_chain:
                            chain_stats = chain_ntx["servers"][server]["epochs"][epoch]["coins"][chain]
                            score_per_ntx = chain_ntx["servers"][server]["epochs"][epoch]["score_per_ntx"]
                            epoch_coin_ntx_count = chain_stats["notary_server_epoch_coin_ntx_count"]
                            epoch_coin_score = chain_stats["notary_server_epoch_coin_ntx_score"]
                            if epoch.find("_") > -1:
                                epoch_id = epoch.split("_")[1]
                            else:
                                epoch_id = epoch
                            row = {
                                "notary": notary,
                                "season": season.replace("_", " "),
                                "server": server,
                                "epoch": epoch_id,
                                "chain": chain,
                                "score_per_ntx": score_per_ntx,
                                "epoch_coin_ntx_count": epoch_coin_ntx_count,
                                "epoch_coin_score": epoch_coin_score
                            }
                            if chain in server_epoch_chains:
                                server_epoch_chains.remove(chain)
                            total += chain_stats["notary_server_epoch_coin_ntx_score"]
                            rows.append(row)

    return rows, total


def get_vote2021_table(request):
    candidate = helper.get_or_none(request, "candidate")
    block = helper.get_or_none(request, "block")
    txid = helper.get_or_none(request, "txid")
    mined_by = helper.get_or_none(request, "mined_by")
    max_block = helper.get_or_none(request, "max_block")
    max_blocktime = helper.get_or_none(request, "max_blocktime")
    max_locktime = helper.get_or_none(request, "max_locktime")

    data = query.get_vote2021_data(candidate, block, txid, max_block, max_blocktime, max_locktime, mined_by)

    if "order_by" in request.GET:
        order_by = request.GET["order_by"]
        data = data.values().order_by(f'-{order_by}')
    else:
        data = data.values().order_by(f'-block_time')

    serializer = serializers.vote2021Serializer(data, many=True)
    resp = {}
    for item in serializer.data:
        if item["candidate"] in DISQUALIFIED:
            item.update({"votes": -1})    
        item.update({"lag": item["block_time"]-item["lock_time"]})

    return serializer.data

