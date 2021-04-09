
from kmd_ntx_api.lib_info import *

logger = logging.getLogger("mylogger")

def get_epoch_scoring_table(request):
    resp = []
    
    if "season" in request.GET:
        season=request.GET["season"]
        data = get_scoring_epochs_data(season)
    else:
        data = get_scoring_epochs_data()

    data = data.order_by('season', 'server').values()
    for item in data:

        resp.append({
                "season":item['season'],
                "server":item['server'],
                "epoch":item['epoch'].split("_")[1],
                "epoch_start":dt.fromtimestamp(item['epoch_start']),
                "epoch_end":dt.fromtimestamp(item['epoch_end']),
                "duration":item['epoch_end']-item['epoch_start'],
                "start_event":item['start_event'],
                "end_event":item['end_event'],
                "epoch_chains":", ".join(item['epoch_chains']),
                "num_epoch_chains":len(item['epoch_chains']),
                "score_per_ntx":item['score_per_ntx']
        })
    return resp


def get_mined_count_season_data_table(request):

    if "season" in request.GET:
        season = request.GET["season"]
    else:
        season = get_season()

    data = get_mined_count_season_data(season).order_by('season', 'notary').values()
    logger.info(f"[get_mined_count_season_data_table] getting data for {season}")

    resp = []
    # name num sum max last
    for item in data:
        blocks_mined = item['blocks_mined']
        if blocks_mined > 10:
            notary = item['notary']
            address = item['address']
            sum_value_mined = item['sum_value_mined']
            max_value_mined = item['max_value_mined']
            last_mined_block = item['last_mined_block']
            last_mined_blocktime = item['last_mined_blocktime']
            time_stamp = item['time_stamp']
            season = item['season']

            resp.append({
                    "notary":notary,
                    "address":address,
                    "blocks_mined":blocks_mined,
                    "sum_value_mined":sum_value_mined,
                    "max_value_mined":max_value_mined,
                    "last_mined_block":last_mined_block,
                    "last_mined_blocktime":last_mined_blocktime
            })

    return resp


def get_notary_epoch_scoring_table(notary=None, season=None):

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
                '''
                if chain not in server_epoch_chains:
                    row = {
                        "notary":notary,
                        "season":season.replace("_", " "),
                        "server":server,
                        "epoch":epoch.split("_")[1],
                        "chain":chain,
                        "score_per_ntx":chain_ntx["servers"][server]["epochs"][epoch]["score_per_ntx"],
                        "epoch_chain_ntx_count":0,
                        "epoch_chain_score":0
                    }
                    rows.append(row)
                '''


    return rows, total
