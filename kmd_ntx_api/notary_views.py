#!/usr/bin/env python3

import time
from django.shortcuts import render

from kmd_ntx_api.lib_helper import *
from kmd_ntx_api.lib_info import *
from kmd_ntx_api.lib_query import *

def notary_profile_view(request, notary=None):
    # Populate sidebar
    season = get_season()
    notaries_list = get_notary_list(season)
    active_dpow_coins = get_active_dpow_coins()

    context = {
        "sidebar_links":get_sidebar_links(notaries_list ,active_dpow_coins),
        "eco_data_link":get_eco_data_link()
    }

    if notary:

        region = get_notary_region(notary)

        notary_balances = get_notary_balances(notary, season)

        coin_notariser_ranks = get_coin_notariser_ranks(season)
        
        notarisation_scores = get_notarisation_scores(season, coin_notariser_ranks)
        
        notary_balances_list, notary_balances_graph = get_notary_balances_data(active_dpow_coins, notary_balances)

        context.update({
            "notary_name": notary,
            "notary_addresses": get_notary_addresses(notary, season),
            "nn_social": get_nn_social(notary), # Social Media Links
            "ntx_summary": get_nn_ntx_summary(notary), # Notarisation Summary
            "mining_summary": get_nn_mining_summary(notary), #  Mining Summary
            "rank": get_region_rank(notarisation_scores[region], notarisation_scores[region][notary]['score']),
            "notary_balances_graph_data": notary_balances_graph, # Balances in graph format
            "notary_balances_table_data": notary_balances_list, # Balances in table format
            "season_nn_chain_ntx_data": get_season_nn_chain_ntx_data(season), # Season Notarisation Stats
            "explorers": get_dpow_explorers() # For hyperlinking addresses
            # "region_score_stats": get_region_score_stats(notarisation_scores),
            # "notary_ntx_counts":coin_notariser_ranks[region][notary],
        })

        return render(request, 'notary_profile.html', context)

    else:
        context.update({
            "nn_social":get_nn_social(),
            "nn_info":get_nn_info()
        })

        return render(request, 'notary_profile_index.html', context)