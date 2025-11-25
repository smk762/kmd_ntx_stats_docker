#!/usr/bin/env python3.12
from kmd_ntx_api.helper import get_or_none, get_page_server, json_resp
from kmd_ntx_api.notary_seasons import get_page_season
from kmd_ntx_api.ntx import get_notarised_date, get_ntx_tenure_table
from kmd_ntx_api.stats import get_season_stats_sorted, get_daily_stats_sorted
from kmd_ntx_api.serializers import notarisedSerializer
from kmd_ntx_api.notary_seasons import get_seasons_info
from kmd_ntx_api.helper import get_notary_list
from kmd_ntx_api.coins import get_dpow_coins_dict
from kmd_ntx_api.helper import get_notary_list, get_notary_region
from kmd_ntx_api.coins import get_dpow_coins_dict
from kmd_ntx_api.mining import get_mined_count_season_by_name
from kmd_ntx_api.table import get_notary_ntx_season_table_data, get_notary_last_ntx_rows
from kmd_ntx_api.logger import logger

def notarised_date_api(request):
    season = get_page_season(request)
    server = get_page_server(request)
    coin = get_or_none(request, "coin")
    notary = get_or_none(request, "notary")
    last_24hrs = get_or_none(request, "last_24hrs", False) == 'true'
    data = get_notarised_date(season, server, coin, notary, last_24hrs)
    serializer = notarisedSerializer(data, many=True)
    filters = ['season', 'server', 'coin', 'notary']
    return json_resp(serializer.data, filters)


def ntx_tenture_api(request):
    data = get_ntx_tenure_table(request)
    filters = ['season', 'server', 'coin']
    return json_resp(data, filters)


def season_stats_sorted_api(request):
    season = get_page_season(request)
    seasons_info = get_seasons_info()
    notary_list = get_notary_list(season, seasons_info)
    data = get_season_stats_sorted(season, notary_list)
    filters = ['season']
    return json_resp(data, filters)


def daily_stats_sorted_api(request):
    season = get_page_season(request)
    seasons_info = get_seasons_info()
    data = get_daily_stats_sorted(
        get_notary_list(season, seasons_info),
        get_dpow_coins_dict(season)
    )
    filters = ['season']
    return json_resp(data, filters)




def profile_data_api(request):
    filters = ['season', 'notary']
    season = get_page_season(request)
    seasons_info = get_seasons_info()
    if season not in seasons_info:
        return {"error": f"{season} is not in seasons list"}
    
    notary_list = get_notary_list(season, seasons_info)
    season_stats_sorted = get_season_stats_sorted(season, notary_list)

    notary = get_or_none(request, "notary")
    if notary is not None:
        if notary not in notary_list:
            return {"error": f"{notary} is not in {season} list"}


    data = {}
    for region in season_stats_sorted:
        for i in season_stats_sorted[region]:
            nn = i["notary"]
            if notary is not None and nn != notary:
                continue
            region = get_notary_region(nn)
            nn_data = {
                "season": season,
                "notary": nn,
                "region": region,
                "rank": i["rank"],
                "ntx": {
                    "last_24h": {
                    },
                    "season": {
                        "s_main": i["main"],
                        "s_ltc": i["master"],
                        "s_thirdParty": i["third_party"],
                    },
                    "score": {
                        "notarization": i["score"] - i["seed"],
                        "seed": i["seed"],
                        "total": i["score"],
                    },
                },
                "mining": {},
                "socials": {}
            }
            data.update({nn: nn_data})


    dpow_coins_dict = get_dpow_coins_dict(season)
    daily_stats_sorted = get_daily_stats_sorted(notary_list, dpow_coins_dict)
        
    for region in daily_stats_sorted:
        for i in daily_stats_sorted[region]:
            nn = i["notary"]
            if notary is not None and nn != notary:
                continue
            data[nn]["ntx"]["last_24h"].update({
                "n_main": i["main"],
                "n_ltc": i["master"],
                "n_thirdParty": i["third_party"],
                "n_seed": i["seed"],
            })
            data[nn]["mining"].update({
                "last_24h": i["mining"]
            })

    mined_season = get_mined_count_season_by_name(request)
    for nn in mined_season:
        if nn in data:
            i = mined_season[nn]
            data[nn]["mining"].update({
                "largest_block_val": i["max_value_mined"],
                "largest_block_tx": i["max_value_txid"],
                "last_mined_blocktime": i["last_mined_blocktime"],
                "blocks_mined_season": i["blocks_mined"],
                "kmd_mined_season": i["sum_value_mined"]
            })
    notary_last_ntx_rows = get_notary_last_ntx_rows(request)
    logger.info(data.keys())
    for row in notary_last_ntx_rows["results"]:
        coin = row["coin"]
        if coin == "KMD":
            coin == "LTC"
        
        blocktime = row["kmd_ntx_blocktime"]
        for nn in row["notaries"]:
            try:
                if nn == 'cipi_1_EU':
                    nn = "cipi_EU"
                if nn == 'cipi_2_EU':
                    nn = "cipi2_EU"

                if "last_coin" not in data[nn]["ntx"]:
                    data[nn]["ntx"].update({
                        "last_coin": coin,
                        "last_coin_ts": blocktime
                    })
                elif data[nn]["ntx"]["last_coin_ts"] < blocktime:
                    data[nn]["ntx"].update({
                        "last_coin": coin,
                        "last_coin_ts": blocktime
                    })
                    
                if coin == "LTC":
                    if "last_ltc_ts" not in data[nn]["ntx"]:
                        data[nn]["ntx"].update({
                            "last_ltc_ts": blocktime
                        })
                    elif data[nn]["last_ltc_ts"] < blocktime:
                        data[nn]["last_ltc_ts"].update({
                            "last_ltc_ts": blocktime
                        })
            except Exception as e:
                logger.error(e)
            
            
    for nn in data:
        continue
        notary_profile_summary_table = get_notary_ntx_season_table_data(request, nn)
        if len(notary_profile_summary_table["notary_ntx_summary_table"]) > 1:
            last_ntx_time = 0
            last_ntx_coin = ""
            last_ltc_ntx_time = 0
            notary_ntx_summary_table = notary_profile_summary_table["notary_ntx_summary_table"]
            for coin in notary_ntx_summary_table:
                if "last_ntx_blocktime" in notary_ntx_summary_table[coin]:
                    if coin == "KMD":
                        last_ltc_ntx_time = notary_ntx_summary_table[coin]["last_ntx_blocktime"]
                        
                    if notary_ntx_summary_table[coin]["last_ntx_blocktime"] > last_ntx_time:
                        last_ntx_time = notary_ntx_summary_table[coin]["last_ntx_blocktime"]
                        last_ntx_coin = coin

            data[nn]["ntx"].update({
                "last_coin": last_ntx_coin,
                "last_coin_ts": last_ntx_time,
                "last_ltc_ts": last_ltc_ntx_time
            })

        
    if nn == notary:
        data = data[notary]
    return json_resp(data, filters)
