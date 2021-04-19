#!/usr/bin/env python3

import time
from django.shortcuts import render

from kmd_ntx_api.lib_info import *
from kmd_ntx_api.lib_stats import *
from kmd_ntx_api.lib_graph import *

def notary_profile_view(request, notary=None, season=None):
    # Populate sidebar
    if not season:
        season="Season_4"
    
    context = {
        "sidebar_links":get_sidebar_links(season),
        "eco_data_link":get_eco_data_link()
    }

    if notary:

        url = f"{THIS_SERVER}/api/table/notary_profile_summary"
        notary_profile_summary_table = requests.get(f"{url}/?season={season}&notary={notary}").json()['results']
        notarised_count_season_data = notary_profile_summary_table['ntx_season_data']

        region = get_notary_region(notary)

        # coin_notariser_ranks = get_coin_notariser_ranks(season)
        
        notarisation_scores = get_notarisation_scores(season)
        

        url = f"{THIS_SERVER}/api/table/balances"
        notary_balances = requests.get(f"{url}/?season={season}&notary={notary}").json()['results']

        notary_balances_list, notary_balances_graph = get_notary_balances_graph(notary, season)

        notarised_data_24hr = get_notarised_data_24hr(season, None, None, notary)
        main_notarised_24hr = notarised_data_24hr.filter(server='Main').count()
        third_notarised_24hr = notarised_data_24hr.filter(server='Third_Party').count()
        btc_notarised_24hr = notarised_data_24hr.filter(server='KMD').count()

        season_score = 0
        last_ntx_time = 0
        for item in notary_profile_summary_table['ntx_summary_data']:
            season_score += item["chain_score"]
            if "last_block_time" in item:
                if item["chain"] == "BTC":
                    last_btc_ntx_time = item["last_block_time"]
                if item["last_block_time"] > last_ntx_time:
                    last_ntx_time = item["last_block_time"]
                    last_ntx_chain = item["chain"]

        context.update({
            "notary_name": notary,
            "nn_social": get_nn_social(notary), # Social Media Links
            "season_btc_count": notarised_count_season_data['btc_count'],
            "season_main_count": notarised_count_season_data['antara_count'],
            "season_third_party_count": notarised_count_season_data['third_party_count'],
            "24hr_btc_count": btc_notarised_24hr,
            "24hr_main_count": main_notarised_24hr,
            "24hr_third_party_count": third_notarised_24hr,
            "season_score":season_score,
            "last_btc_ntx_time":get_time_since(last_btc_ntx_time)[1],
            "last_ntx_time":get_time_since(last_ntx_time)[1],
            "last_ntx_chain":last_ntx_chain,
            "mining_summary": get_nn_mining_summary(notary), #  Mining Summary
            "explorers": get_explorers(request), # For hyperlinking addresses
            "rank": get_region_rank(notarisation_scores[region], notarisation_scores[region][notary]['score']),
            "ntx_summary_data":notary_profile_summary_table['ntx_summary_data'],

            "notary_balances_graph_data": notary_balances_graph, # Balances in graph format
            "notary_balances": notary_balances, # Balances in table format
        })

        return render(request, 'notary_profile.html', context)

    else:
        context.update({
            "nn_social":get_nn_social(),
            "nn_info":get_nn_info()
        })

        return render(request, 'notary_profile_index.html', context)