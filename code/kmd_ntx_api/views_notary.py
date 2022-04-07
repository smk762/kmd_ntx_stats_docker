#!/usr/bin/env python3

import time
from datetime import datetime as dt

from django.shortcuts import render

from kmd_ntx_api.lib_const import *
import kmd_ntx_api.lib_info as info
import kmd_ntx_api.lib_helper as helper
import kmd_ntx_api.lib_stats as stats
import kmd_ntx_api.lib_graph as graph
import kmd_ntx_api.lib_query as query

from kmd_ntx_api.api_table import notary_ntx_table

def notary_mining_view(request, notary=None):
    context = helper.get_base_context(request)
    if not notary:
        return render(request, 'dash_index.html', context)

    notary_mining = query.get_mined_data(None, notary).values().order_by('block_height')
    notary_list = helper.get_notary_list(season)
    explorers = info.get_explorers(request)

    context.update({
        "page_title": f"{notary} Notary KMD Mining",
        "notary_mining":notary_mining,
        "explorers":explorers
    })

    return render(request, 'notary_mining.html', context)

def notary_chain_ntx_detail_view(request):
    context = helper.get_base_context(request)
    notary = helper.get_or_none(request, "notary")
    chain = helper.get_or_none(request, "chain")
    server = helper.get_or_none(request, "server")

    url = f"{THIS_SERVER}/api/table/notary_ntx"
    chain_ntx_table = requests.get(f"{url}/?season={season}&server={server}&notary={notary}&chain={chain}").json()['results']

    context.update({
        "page_title":"Notary Profile Index",
        "notary":notary,
        "chain":chain,
        "chain_ntx": chain_ntx_table
    })

    return render(request, 'notary/notary_chain_ntx_detail.html', context)

def notary_profile_view(request, notary=None):
    context = helper.get_base_context(request)
    
    context.update({
        "page_title":"Notary Profile Index",
    })
    season = helper.get_page_season(request)
    notary_list = helper.get_notary_list(season)

    if notary:
        if notary in notary_list:

            url = f"{THIS_SERVER}/api/table/notary_profile_summary"
            notary_profile_summary_table = requests.get(f"{url}/?season={season}&notary={notary}").json()['results']

            url = f"{THIS_SERVER}/api/table/balances"
            notary_balances_tbl = requests.get(f"{url}/?season={season}&notary={notary}").json()['results']

            notarised_count_season_data = notary_profile_summary_table['ntx_season_data'][0]
            url = f"{THIS_SERVER}/api/graph/balances/?season={season}&notary={notary}"
            notary_balances_graph = requests.get(url).json()["results"]
            notarised_data_24hr = info.get_notarised_data_24hr(season, None, None, notary)
            season_stats_sorted = stats.get_season_stats_sorted(season)
            main_notarised_24hr = notarised_data_24hr.filter(server='Main').count()
            third_notarised_24hr = notarised_data_24hr.filter(server='Third_Party').count()
            ltc_notarised_24hr = notarised_data_24hr.filter(server='KMD').count()
            region = helper.get_notary_region(notary)

            ntx_score = 0
            seed_score = 0
            last_ntx_time = 0
            last_ltc_ntx_time = 0
            last_ntx_chain = ""
            for item in notary_profile_summary_table['ntx_summary_data']:
                ntx_score += item["chain_score"]
                if "last_block_time" in item:
                    if item["chain"] == "LTC":
                        last_ltc_ntx_time = item["last_block_time"]
                    if item["last_block_time"] > last_ntx_time:
                        last_ntx_time = item["last_block_time"]
                        last_ntx_chain = item["chain"]

            seed_score_data = info.get_seed_stat_season(season, notary).values()
            for item in seed_score_data:
                seed_score += item["score"]
            season_score = ntx_score + seed_score
            rank = info.get_region_rank(season_stats_sorted[region], notary)
            context.update({
                "page_title":f"{notary} Notary Profile",
                "notary_name": notary,
                "nn_social": info.get_nn_social(season, notary), # Social Media Links
                "season_btc_count": notarised_count_season_data['btc_count'],
                "season_main_count": notarised_count_season_data['antara_count'],
                "season_third_party_count": notarised_count_season_data['third_party_count'],
                "24hr_ltc_count": ltc_notarised_24hr,
                "24hr_main_count": main_notarised_24hr,
                "24hr_third_party_count": third_notarised_24hr,
                "seed_score":seed_score,
                "ntx_score":ntx_score,
                "season_score":season_score,
                "last_ltc_ntx_time": helper.get_time_since(last_ltc_ntx_time)[1],
                "last_ntx_time": helper.get_time_since(last_ntx_time)[1],
                "last_ntx_chain":last_ntx_chain,
                "mining_summary": info.get_nn_mining_summary(notary), #  Mining Summary
                "explorers": info.get_explorers(request), # For hyperlinking addresses
                "icons": info.get_icons(request), # For hyperlinking addresses
                "rank": rank,
                "ntx_summary_data":notary_profile_summary_table['ntx_summary_data'],
                "notary_balances_graph_data": notary_balances_graph, # Balances in graph format
                "notary_balances": notary_balances_tbl, # Balances in table format
            })

            return render(request, 'notary_profile.html', context)

    context.update({
        "nn_social": info.get_nn_social(season),
        "nn_regions": helper.get_regions_info(season)
    })

    return render(request, 'notary_profile_index.html', context)

def vote2021_view(request):
    context = helper.get_base_context(request)
    season = get_page_season(request)

    if "max_locktime" in request.GET:
        params = f'?max_locktime={request.GET["max_locktime"]}'
    elif "max_block" in request.GET:
        params = f'?max_block={request.GET["max_block"]}'
    else:
        params = f'?max_locktime=1619179199'

    url = f"{THIS_SERVER}/api/info/vote2021_stats"
    vote2021_table = requests.get(f"{url}/{params}").json()

    if 'results' in vote2021_table:
        vote2021_table = vote2021_table["results"]

    context.update({
        "page_title":"Notary VOTE 2021",
        "params": params,
        "vote2021_table": vote2021_table
    })

    return render(request, 'vote2021.html', context)


def vote2021_detail_view(request):
    context = helper.get_base_context(request)

    candidate = None
    if "candidate" in request.GET:
        params = f'?candidate={request.GET["candidate"]}'
    else:
        return vote2021_view(request)
    if "max_locktime" in request.GET:
        params += f'&max_locktime={request.GET["max_locktime"]}'
    elif "max_block" in request.GET:
        params += f'&max_block={request.GET["max_block"]}'
    else:
        params += f'&max_locktime=1619179199'

    url = f"{THIS_SERVER}/api/table/vote2021"
    vote2021_detail_table = requests.get(f"{url}/{params}").json()

    if 'results' in vote2021_detail_table:
        vote2021_detail_table = vote2021_detail_table["results"]

    for item in vote2021_detail_table:
        date_time = dt.fromtimestamp(item["lock_time"])

        item.update({"lock_time_human":date_time.strftime("%m/%d/%Y, %H:%M:%S")})

    candidate = request.GET["candidate"].replace(".", "-")

    context.update({
        "page_title":"Notary VOTE 2021",
        "candidate": candidate,
        "params": params,
        "vote2021_detail_table": vote2021_detail_table
    })

    return render(request, 'vote2021_detail.html', context)


def s5_address_confirmation(request):
    # Populate sidebar
    context = helper.get_base_context(request)

    addr_confirmed_in_PR = [
        "alien_AR",
        "alien_EU",
        "alien_NA",
        "alienx_EU",
        "alienx_NA",
        "computergenie_NA",
        "dappvader_SH",
        "drkush_SH",
        "goldenman_AR",
        "kolo_AR",
        "node-9_EU",
        "node-9_NA",
        "nodeone_NA",
        "nutellaLicka_SH",
        "ptyx_NA",
        "phit_SH",
        "sheeba_SH",
        "slyris_EU",
        "strob_SH",
        "strob_NA",
        "strobnidan_SH",
        "tonyl_AR",
        "tonyl_DEV",
        "strobnidan_SH",
        "webworker01_NA",
        "van_EU"
    ]
    pub_confirmed_in_PR = [
        "alien_AR",
        "alien_EU",
        "alien_NA",
        "alienx_EU",
        "alienx_NA",
        "artem_DEV",
        "artempikulin_AR",
        "ca333_EU",
        "chmex_AR",
        "chmex_EU",
        "chmex_SH",
        "cipi_EU",
        "cipi_AR",
        "cipi_NA",
        "cipi2_EU",
        "collider_SH",
        "karasugoi_NA",
        "komodopioneers_EU",
        "madmax_AR",
        "madmax_EU",
        "madmax_NA",
        "marmarachain_EU",
        "majora31_SH",
        "karasugoi_NA",
        "metaphilibert_SH",
        "mrlynch_AR",
        "metaphilibert_SH",
        "pbca26_NA",
        "pbca26_SH",
        "smdmitry_AR",
        "smdmitry_EU",
        "pbca26_SH",
        "mcrypt_AR",
        "mcrypt_SH",
        "yurii_DEV"
    ]
    pub_confirmed_in_DM = [
        "gcharang_DEV",
        "mylo_SH",
        "hyper_NA",
        "tokel_AR",
        "shadowbit_AR",
        "shadowbit_EU",
        "shadowbit_DEV",
        "ocean_AR",
        "alrighttt_DEV",
        "ca333_DEV"
    ]
    addr_confirmed_in_DM = [
        "dragonhound_DEV",
        "dragonhound_NA",
    ]

    kmd_addresses = requests.get(f"{THIS_SERVER}/api/table/addresses/?season=Season_5&chain=KMD").json()["results"]
    ltc_addresses = requests.get(f"{THIS_SERVER}/api/table/addresses/?season=Season_5&chain=LTC&server=Main").json()["results"]
    addresses = kmd_addresses + ltc_addresses

    for item in addresses:
        if item["notary"] in pub_confirmed_in_PR:
            item.update({"confirmed":"Pubkey (PR)"})
        elif item["notary"] in addr_confirmed_in_PR:
            item.update({"confirmed":"Address (PR)"})
        elif item["notary"] in pub_confirmed_in_DM:
            item.update({"confirmed":"Pubkey (DM)"})
        elif item["notary"] in addr_confirmed_in_DM:
            item.update({"confirmed":"Address (DM)"})

    context.update({
        "page_title":"Address Confirmation",
        "explorers": info.get_explorers(request),
        "addresses":addresses,
    })

    return render(request, 's5_address_confirmation.html', context)


